/**
 * Server-side cart pricing from the static catalog.
 * Never trust client unit prices.
 */

import { merch, merchUnitCents, type Merch } from "../../src/data/catalog";

export type CartLineInput = {
  slug: string;
  size: string;
  qty: number;
};

export type MerchOrderItem = {
  slug: string;
  title: string;
  size: string;
  qty: number;
  unit_cents: number;
  line_cents: number;
};

export type PricedCart = {
  items: MerchOrderItem[];
  subtotal_cents: number;
  shipping_cents: number;
  total_cents: number;
};

export function merchShippingConfig(env: {
  MERCH_SHIPPING_CENTS?: string;
  MERCH_FREE_SHIP_CENTS?: string;
}): { shippingCents: number; freeShipCents: number } {
  return {
    shippingCents: parseIntCents(env.MERCH_SHIPPING_CENTS, 600),
    freeShipCents: parseIntCents(env.MERCH_FREE_SHIP_CENTS, 7500),
  };
}

function parseIntCents(raw: string | undefined, fallback: number): number {
  if (raw == null || raw.trim() === "") return fallback;
  const n = Number.parseInt(raw, 10);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
}

export function shippingCentsForSubtotal(
  subtotal: number,
  shippingCents: number,
  freeShipCents: number,
): number {
  if (subtotal <= 0) return 0;
  if (freeShipCents > 0 && subtotal >= freeShipCents) return 0;
  return Math.max(0, shippingCents);
}

export function parseCartBody(body: unknown): CartLineInput[] {
  const items = (body as { items?: unknown })?.items;
  if (!Array.isArray(items)) return [];
  return items.map((row) => {
    const r = row as { slug?: unknown; size?: unknown; qty?: unknown };
    return {
      slug: String(r.slug ?? "").trim(),
      size: String(r.size ?? "").trim(),
      qty: Number(r.qty),
    };
  });
}

function findMerch(slug: string): Merch | undefined {
  return merch.find((m) => m.slug === slug);
}

/** Re-price cart lines from catalog. Rejects unknown slug/size and qty outside 1..99. */
export function priceCartFromCatalog(
  lines: CartLineInput[],
  opts: { shippingCents: number; freeShipCents: number },
): { ok: true; cart: PricedCart } | { ok: false; error: string } {
  const cleaned: CartLineInput[] = [];
  for (const line of lines) {
    const slug = String(line.slug || "").trim();
    const size = String(line.size || "").trim();
    const qty = Math.floor(Number(line.qty));
    if (!slug || !size) return { ok: false, error: "Each item needs a product and size." };
    if (!Number.isFinite(qty) || qty < 1 || qty > 99) {
      return { ok: false, error: "Quantity must be between 1 and 99." };
    }
    cleaned.push({ slug, size, qty });
  }
  if (!cleaned.length) return { ok: false, error: "Cart is empty." };

  // Merge duplicate slug+size
  const qtyByKey = new Map<string, CartLineInput>();
  for (const line of cleaned) {
    const key = `${line.slug}|${line.size}`;
    const existing = qtyByKey.get(key);
    if (existing) {
      const next = existing.qty + line.qty;
      if (next > 99) return { ok: false, error: "Quantity too high (max 99 per item)." };
      existing.qty = next;
    } else {
      qtyByKey.set(key, { ...line });
    }
  }

  const items: MerchOrderItem[] = [];
  for (const line of qtyByKey.values()) {
    const product = findMerch(line.slug);
    if (!product) return { ok: false, error: `Unknown product: ${line.slug}` };
    if (!product.sizes.includes(line.size)) {
      return { ok: false, error: `Size ${line.size} is not available for ${product.title}.` };
    }
    const unit = merchUnitCents(product, line.size);
    items.push({
      slug: product.slug,
      title: product.title,
      size: line.size,
      qty: line.qty,
      unit_cents: unit,
      line_cents: unit * line.qty,
    });
  }

  const subtotal = items.reduce((sum, i) => sum + i.line_cents, 0);
  const shipping = shippingCentsForSubtotal(subtotal, opts.shippingCents, opts.freeShipCents);
  return {
    ok: true,
    cart: {
      items,
      subtotal_cents: subtotal,
      shipping_cents: shipping,
      total_cents: subtotal + shipping,
    },
  };
}

/** Compact metadata: slug|size:qty,... (<=500 chars for Stripe). */
export function compactCartMetadata(items: MerchOrderItem[]): string {
  return items.map((i) => `${i.slug}|${i.size}:${i.qty}`).join(",").slice(0, 500);
}

/** Parse compact cart metadata back into cart lines. */
export function cartLinesFromMetadata(raw: string | null | undefined): CartLineInput[] {
  const text = raw?.trim();
  if (!text) return [];
  return text.split(",").map((part) => {
    const [left, qtyRaw] = part.split(":");
    const pipe = (left || "").indexOf("|");
    if (pipe < 0) {
      return { slug: (left || "").trim(), size: "", qty: Number(qtyRaw) || 0 };
    }
    return {
      slug: left.slice(0, pipe).trim(),
      size: left.slice(pipe + 1).trim(),
      qty: Number(qtyRaw) || 0,
    };
  });
}
