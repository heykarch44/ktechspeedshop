import {
  cartLinesFromMetadata,
  merchShippingConfig,
  priceCartFromCatalog,
} from "../../_lib/cart";
import { formatAddress, newOrderId, upsertMerchOrder } from "../../_lib/db";
import { merchOrderAdminEmail, merchOrderReceiptEmail, sendEmail } from "../../_lib/email";
import type { Env } from "../../_lib/env";
import {
  type StripeCheckoutSession,
  verifyStripeWebhookSignature,
} from "../../_lib/stripe";

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const payload = await context.request.text();
  const secret = context.env.STRIPE_WEBHOOK_SECRET?.trim();
  if (!secret) {
    return Response.json({ error: "Webhook not configured." }, { status: 400 });
  }

  const verified = await verifyStripeWebhookSignature({
    payload,
    signatureHeader:
      context.request.headers.get("Stripe-Signature") ||
      context.request.headers.get("stripe-signature"),
    secret,
  });
  if (!verified.ok) {
    return Response.json({ error: verified.error }, { status: 400 });
  }

  let event: { type?: string; data?: { object?: StripeCheckoutSession } };
  try {
    event = JSON.parse(payload);
  } catch {
    return Response.json({ error: "Invalid JSON." }, { status: 400 });
  }

  if (event.type !== "checkout.session.completed") {
    return Response.json({ received: true });
  }

  const session = event.data?.object;
  if (!session?.id) {
    return Response.json({ error: "Missing session." }, { status: 400 });
  }

  // Shared Stripe account also serves c10united.com — only handle ktech sessions.
  if (session.metadata?.site !== "ktech") {
    return Response.json({ received: true, ignored: true });
  }

  const ship = merchShippingConfig(context.env);
  const priced = priceCartFromCatalog(cartLinesFromMetadata(session.metadata?.cart), ship);
  if (!priced.ok) {
    console.error("[merch webhook] could not re-price cart", priced.error);
    return Response.json({ received: true, note: "reprice-failed" });
  }

  const items = priced.cart.items;
  const subtotal = priced.cart.subtotal_cents;
  const shipping =
    session.shipping_cost?.amount_total != null
      ? session.shipping_cost.amount_total
      : priced.cart.shipping_cents;
  const total = session.amount_total != null ? session.amount_total : subtotal + shipping;

  const shippingDetails =
    session.collected_information?.shipping_details || session.shipping_details || null;
  const shippingAddr = formatAddress(
    shippingDetails?.address || session.customer_details?.address || null,
    shippingDetails?.name || session.customer_details?.name || null,
  );

  const orderId = newOrderId();
  const email = session.customer_details?.email || null;
  const name = shippingDetails?.name || session.customer_details?.name || null;
  const phone = session.customer_details?.phone || null;

  const { inserted } = await upsertMerchOrder(context.env.DB, {
    id: orderId,
    stripe_session_id: session.id,
    email,
    name,
    phone,
    shipping_address: shippingAddr,
    items,
    subtotal_cents: subtotal,
    shipping_cents: shipping,
    total_cents: total,
    status: "paid",
  });

  if (inserted) {
    const notifyTo =
      context.env.ORDER_NOTIFY_EMAIL?.trim() || "shop@ktechspeedshop.com";
    const origin = new URL(context.request.url).origin;
    const shopUrl = `${origin}/shop`;

    const adminMail = merchOrderAdminEmail({
      orderId,
      email,
      name,
      phone,
      items,
      subtotalCents: subtotal,
      shippingCents: shipping,
      totalCents: total,
      shippingAddress: shippingAddr,
    });
    await sendEmail(context.env, {
      to: notifyTo,
      subject: adminMail.subject,
      html: adminMail.html,
      text: adminMail.text,
      idempotencyKey: `ktech-admin/${session.id}`,
    });

    if (email) {
      const receipt = merchOrderReceiptEmail({
        orderId,
        name,
        items,
        subtotalCents: subtotal,
        shippingCents: shipping,
        totalCents: total,
        siteUrl: shopUrl,
      });
      await sendEmail(context.env, {
        to: email,
        subject: receipt.subject,
        html: receipt.html,
        text: receipt.text,
        idempotencyKey: `ktech-receipt/${session.id}`,
      });
    }
  }

  return Response.json({ received: true });
};
