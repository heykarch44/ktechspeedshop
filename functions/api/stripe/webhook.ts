import { ktechCatalogAdapter, SITE_TAG } from "../../_lib/catalog";
import { savePaidOrder } from "../../_lib/db";
import type { Env } from "../../_lib/env";
import { notifyPaidOrder } from "../../_lib/notify";
import { handleStripeWebhook, shippingConfigFromEnv } from "../../../shared/merch/server";

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const payload = await context.request.text();
  const secret = context.env.STRIPE_WEBHOOK_SECRET?.trim();
  if (!secret) {
    return Response.json({ error: "Webhook not configured." }, { status: 400 });
  }

  const origin = new URL(context.request.url).origin;
  return handleStripeWebhook({
    payload,
    signatureHeader:
      context.request.headers.get("Stripe-Signature") ||
      context.request.headers.get("stripe-signature"),
    secret,
    siteTag: SITE_TAG,
    repriceAdapter: ktechCatalogAdapter,
    shipping: shippingConfigFromEnv(context.env),
    hooks: {
      saveOrder: (order) => savePaidOrder(context.env.DB, order),
      notify: (order) =>
        notifyPaidOrder(context.env, order, { shopUrl: `${origin}/shop/` }),
    },
  });
};
