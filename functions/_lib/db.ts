/** D1 merch order helpers (K-Tech `merch_orders` schema). */

import type { PaidOrder } from "../../shared/merch/server";

export type MerchOrderItemRow = {
  slug: string;
  title: string;
  size: string;
  qty: number;
  unit_cents: number;
  line_cents: number;
};

export type MerchOrder = {
  id: string;
  stripe_session_id: string;
  email: string | null;
  name: string | null;
  phone: string | null;
  shipping_address: string | null;
  items: string;
  subtotal_cents: number;
  shipping_cents: number;
  total_cents: number;
  status: string;
  tracking: string | null;
  created_at: string;
  shipped_at: string | null;
};

function paidItemsToRows(order: PaidOrder): MerchOrderItemRow[] {
  return order.items.map((item) => {
    const pipe = item.id.indexOf("|");
    const slug = pipe >= 0 ? item.id.slice(0, pipe) : item.id;
    const size = pipe >= 0 ? item.id.slice(pipe + 1) : item.label;
    return {
      slug,
      title: item.title,
      size: size || item.label,
      qty: item.qty,
      unit_cents: item.unit_cents,
      line_cents: item.line_cents,
    };
  });
}

export async function upsertMerchOrder(
  db: D1Database,
  order: {
    id: string;
    stripe_session_id: string;
    email: string | null;
    name: string | null;
    phone: string | null;
    shipping_address: string | null;
    items: MerchOrderItemRow[];
    subtotal_cents: number;
    shipping_cents: number;
    total_cents: number;
    status?: string;
  },
): Promise<{ inserted: boolean }> {
  const existing = await db
    .prepare(`SELECT id FROM merch_orders WHERE stripe_session_id = ? LIMIT 1`)
    .bind(order.stripe_session_id)
    .first<{ id: string }>();
  if (existing) return { inserted: false };

  await db
    .prepare(
      `INSERT INTO merch_orders
        (id, stripe_session_id, email, name, phone, shipping_address, items, subtotal_cents, shipping_cents, total_cents, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      order.id,
      order.stripe_session_id,
      order.email,
      order.name,
      order.phone,
      order.shipping_address,
      JSON.stringify(order.items),
      order.subtotal_cents,
      order.shipping_cents,
      order.total_cents,
      order.status || "paid",
    )
    .run();
  return { inserted: true };
}

/** Shared webhook hook — maps PaidOrder into the existing D1 row shape. */
export async function savePaidOrder(
  db: D1Database,
  order: PaidOrder,
): Promise<{ inserted: boolean }> {
  return upsertMerchOrder(db, {
    id: newOrderId(),
    stripe_session_id: order.stripe_session_id,
    email: order.email,
    name: order.name,
    phone: order.phone,
    shipping_address: order.shipping_address,
    items: paidItemsToRows(order),
    subtotal_cents: order.subtotal_cents,
    shipping_cents: order.shipping_cents,
    total_cents: order.total_cents,
    status: "paid",
  });
}

export async function getMerchOrderBySessionId(
  db: D1Database,
  sessionId: string,
): Promise<MerchOrder | null> {
  return (
    (await db
      .prepare(`SELECT * FROM merch_orders WHERE stripe_session_id = ? LIMIT 1`)
      .bind(sessionId)
      .first<MerchOrder>()) || null
  );
}

export function newOrderId(): string {
  return crypto.randomUUID();
}

export function formatAddress(
  addr: Record<string, string | null> | null | undefined,
  name?: string | null,
): string | null {
  if (!addr && !name) return null;
  const lines = [
    name || null,
    addr?.line1 || null,
    addr?.line2 || null,
    [addr?.city, addr?.state, addr?.postal_code].filter(Boolean).join(", ") || null,
    addr?.country || null,
  ].filter(Boolean);
  return lines.length ? lines.join("\n") : null;
}
