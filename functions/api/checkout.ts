import {
  compactCartMetadata,
  merchShippingConfig,
  parseCartBody,
  priceCartFromCatalog,
} from "../_lib/cart";
import type { Env } from "../_lib/env";
import { createCheckoutSession, isStripeConfigured } from "../_lib/stripe";

export const onRequestPost: PagesFunction<Env> = async (context) => {
  if (!isStripeConfigured(context.env)) {
    return Response.json(
      { ok: false, error: "Checkout opening soon. Payments are not connected yet." },
      { status: 503 },
    );
  }

  const body = await context.request.json().catch(() => ({}));
  const ship = merchShippingConfig(context.env);
  const priced = priceCartFromCatalog(parseCartBody(body), ship);
  if (!priced.ok) {
    return Response.json({ ok: false, error: priced.error }, { status: 400 });
  }

  const origin = new URL(context.request.url).origin;
  const metadataCart = compactCartMetadata(priced.cart.items);

  const result = await createCheckoutSession({
    secretKey: context.env.STRIPE_SECRET_KEY!.trim(),
    items: priced.cart.items,
    shippingCents: priced.cart.shipping_cents,
    returnUrl: `${origin}/shop/thanks?session_id={CHECKOUT_SESSION_ID}`,
    metadataCart,
  });

  if (!result.ok) {
    return Response.json({ ok: false, error: result.error }, { status: result.status });
  }
  return Response.json({ ok: true, clientSecret: result.clientSecret, id: result.id });
};
