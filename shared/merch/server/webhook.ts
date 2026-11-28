/**
 * Shared Stripe webhook handler for checkout.session.completed.
 */

import {
  cartLinesFromMetadata,
  priceCart,
} from "./cart";
import type {
  CatalogAdapter,
  PaidOrder,
  ShippingConfig,
  WebhookHooks,
} from "./contract";
import {
  type StripeCheckoutSession,
  verifyStripeWebhookSignature,
} from "./stripe";

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

export async function handleStripeWebhook(opts: {
  payload: string;
  signatureHeader: string | null;
  secret: string;
  siteTag: string;
  repriceAdapter: CatalogAdapter;
  shipping: ShippingConfig;
  hooks: WebhookHooks;
}): Promise<Response> {
  const verified = await verifyStripeWebhookSignature({
    payload: opts.payload,
    signatureHeader: opts.signatureHeader,
    secret: opts.secret,
  });
  if (!verified.ok) {
    return Response.json({ error: verified.error }, { status: 400 });
  }

  let event: { type?: string; data?: { object?: StripeCheckoutSession } };
  try {
    event = JSON.parse(opts.payload);
  } catch {
    return Response.json({ error: "Invalid JSON." }, { status: 400 });
  }

  if (event.type !== "checkout.session.completed") {
    return Response.json({ received: true, ignored: true });
  }

  const session = event.data?.object;
  if (!session?.id) {
    return Response.json({ error: "Missing session." }, { status: 400 });
  }

  if (session.metadata?.site !== opts.siteTag) {
    return Response.json({ received: true, ignored: true });
  }

  const priced = await priceCart(
    cartLinesFromMetadata(session.metadata?.cart),
    opts.repriceAdapter,
    opts.shipping,
  );
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

  const order: PaidOrder = {
    stripe_session_id: session.id,
    email: session.customer_details?.email || null,
    name: shippingDetails?.name || session.customer_details?.name || null,
    phone: session.customer_details?.phone || null,
    shipping_address: shippingAddr,
    items: items.map((i) => ({
      id: i.id,
      title: i.title,
      label: i.label,
      qty: i.qty,
      unit_cents: i.unit_cents,
      line_cents: i.line_cents,
      ...(i.image ? { image: i.image } : {}),
    })),
    subtotal_cents: subtotal,
    shipping_cents: shipping,
    total_cents: total,
    metadata: { ...(session.metadata || {}) },
  };

  const { inserted } = await opts.hooks.saveOrder(order);
  if (inserted) {
    await opts.hooks.notify(order);
  }

  return Response.json({ received: true });
}
