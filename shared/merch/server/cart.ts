/**
 * Cart parse / re-price / metadata helpers.
 * Server always re-prices via the catalog adapter; never trusts client unit prices.
 */

import type {
  CartLine,
  CatalogAdapter,
  CatalogLine,
  PricedCart,
  QuoteLine,
  ShippingConfig,
} from "./contract";
import { DEFAULT_FLAT_CENTS, DEFAULT_FREE_OVER_CENTS, shippingCents } from "./shipping";

/** Map raw request rows to `{id, qty}`, accepting legacy shapes. */
export function normalizeCartLines(raw: unknown[]): CartLine[] {
  return raw.map((row) => {
    const r = row as {
      id?: unknown;
      qty?: unknown;
      variantId?: unknown;
      slug?: unknown;
      size?: unknown;
    };
    const qty = Number(r.qty);
    const idDirect = String(r.id ?? "").trim();
    if (idDirect) return { id: idDirect, qty };

    const variantId = String(r.variantId ?? "").trim();
    if (variantId) return { id: variantId, qty };

    const slug = String(r.slug ?? "").trim();
    const size = String(r.size ?? "").trim();
    if (slug && size) return { id: `${slug}|${size}`, qty };
    if (slug) return { id: slug, qty };

    return { id: "", qty };
  });
}

export function parseCartBody(body: unknown): CartLine[] {
  const items = (body as { items?: unknown })?.items;
  if (!Array.isArray(items)) return [];
  return normalizeCartLines(items);
}

/** Compact metadata: id:qty,... (<=500 chars for Stripe). */
export function compactCartMetadata(items: Array<{ id: string; qty: number }>): string {
  return items
    .map((i) => `${i.id}:${i.qty}`)
    .join(",")
    .slice(0, 500);
}

/**
 * Parse compact cart metadata into cart lines.
 * Supports new `id:qty` (id may contain `|`) and legacy `slug|size:qty`.
 */
export function cartLinesFromMetadata(raw: string | null | undefined): CartLine[] {
  const text = raw?.trim();
  if (!text) return [];
  return text.split(",").map((part) => {
    const trimmed = part.trim();
    if (!trimmed) return { id: "", qty: 0 };
    const colon = trimmed.lastIndexOf(":");
    if (colon < 0) return { id: trimmed, qty: 0 };
    return {
      id: trimmed.slice(0, colon).trim(),
      qty: Number(trimmed.slice(colon + 1)) || 0,
    };
  });
}

/** Re-price cart lines via adapter. Rejects unknown id and qty outside 1..99. */
export async function priceCart(
  lines: CartLine[],
  adapter: CatalogAdapter,
  shipping: ShippingConfig = {
    flatCents: DEFAULT_FLAT_CENTS,
    freeOverCents: DEFAULT_FREE_OVER_CENTS,
  },
): Promise<{ ok: true; cart: PricedCart } | { ok: false; error: string }> {
  const cleaned: CartLine[] = [];
  for (const line of lines) {
    const id = String(line.id || "").trim();
    const qty = Math.floor(Number(line.qty));
    if (!id) return { ok: false, error: "Each item needs a product id." };
    if (!Number.isFinite(qty) || qty < 1 || qty > 99) {
      return { ok: false, error: "Quantity must be between 1 and 99." };
    }
    cleaned.push({ id, qty });
  }
  if (!cleaned.length) return { ok: false, error: "Cart is empty." };

  const qtyById = new Map<string, number>();
  for (const line of cleaned) {
    const next = (qtyById.get(line.id) || 0) + line.qty;
    if (next > 99) return { ok: false, error: "Quantity too high (max 99 per item)." };
    qtyById.set(line.id, next);
  }

  const ids = [...qtyById.keys()];
  let found: Map<string, CatalogLine>;
  try {
    found = await adapter.lookupLines(ids);
  } catch (err) {
    console.error("[merch] catalog lookup failed", err);
    return { ok: false, error: "Could not look up products." };
  }

  const items: QuoteLine[] = [];
  for (const id of ids) {
    const row = found.get(id);
    if (!row) return { ok: false, error: `Unknown product: ${id}` };
    const qty = qtyById.get(id)!;
    items.push({
      id: row.id,
      title: row.title,
      label: row.label,
      qty,
      unit_cents: row.unit_cents,
      line_cents: row.unit_cents * qty,
      ...(row.image ? { image: row.image } : {}),
    });
  }

  const subtotal = items.reduce((sum, i) => sum + i.line_cents, 0);
  const ship = shippingCents(subtotal, shipping);
  return {
    ok: true,
    cart: {
      items,
      subtotal_cents: subtotal,
      shipping_cents: ship,
      total_cents: subtotal + ship,
      free_ship_cents: shipping.freeOverCents,
    },
  };
}
