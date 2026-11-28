/**
 * K-Tech order notify hook (Resend) for shared webhook.
 */

import type { PaidOrder } from "../../shared/merch/server";
import { merchOrderAdminEmail, merchOrderReceiptEmail, sendEmail } from "./email";
import type { Env } from "./env";

export async function notifyPaidOrder(
  env: Env,
  order: PaidOrder,
  opts?: { shopUrl?: string },
): Promise<void> {
  if (!env.RESEND_API_KEY?.trim()) return;

  const items = order.items.map((i) => ({
    title: i.title,
    size: i.label,
    qty: i.qty,
    line_cents: i.line_cents,
  }));

  const notifyTo = env.ORDER_NOTIFY_EMAIL?.trim() || "shop@ktechspeedshop.com";
  const shopUrl = opts?.shopUrl || "https://ktechspeedshop.com/shop/";

  const adminMail = merchOrderAdminEmail({
    orderId: order.stripe_session_id,
    email: order.email,
    name: order.name,
    phone: order.phone,
    items,
    subtotalCents: order.subtotal_cents,
    shippingCents: order.shipping_cents,
    totalCents: order.total_cents,
    shippingAddress: order.shipping_address,
  });
  await sendEmail(env, {
    to: notifyTo,
    subject: adminMail.subject,
    html: adminMail.html,
    text: adminMail.text,
    idempotencyKey: `ktech-admin/${order.stripe_session_id}`,
  });

  if (order.email) {
    const receipt = merchOrderReceiptEmail({
      orderId: order.stripe_session_id,
      name: order.name,
      items,
      subtotalCents: order.subtotal_cents,
      shippingCents: order.shipping_cents,
      totalCents: order.total_cents,
      siteUrl: shopUrl,
    });
    await sendEmail(env, {
      to: order.email,
      subject: receipt.subject,
      html: receipt.html,
      text: receipt.text,
      idempotencyKey: `ktech-receipt/${order.stripe_session_id}`,
    });
  }
}
