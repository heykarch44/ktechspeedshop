/** D1 merch order helpers. */

import type { MerchOrderItem } from "./cart";

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

export async function upsertMerchOrder(
  db: D1Database,
  order: {
    id: string;
    stripe_session_id: string;
    email: string | null;
    name: string | null;
    phone: string | null;
    shipping_address: string | null;
    items: MerchOrderItem[];
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
