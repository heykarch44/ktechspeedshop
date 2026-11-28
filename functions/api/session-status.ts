import type { Env } from "../_lib/env";
import { isStripeConfigured, retrieveCheckoutSession } from "../_lib/stripe";

export const onRequestGet: PagesFunction<Env> = async (context) => {
  if (!isStripeConfigured(context.env)) {
    return Response.json(
      { ok: false, error: "Checkout opening soon. Payments are not connected yet." },
      { status: 503 },
    );
  }

  const url = new URL(context.request.url);
  const sessionId = (url.searchParams.get("session_id") || "").trim();
  if (!sessionId) {
    return Response.json({ ok: false, error: "Missing session_id." }, { status: 400 });
  }

  const session = await retrieveCheckoutSession(context.env.STRIPE_SECRET_KEY!.trim(), sessionId);
  if (!session) {
    return Response.json({ ok: false, error: "Session not found." }, { status: 404 });
  }

  return Response.json({
    ok: true,
    status: session.status || null,
    payment_status: session.payment_status || null,
    customer_email: session.customer_details?.email || null,
    customer_name: session.customer_details?.name || session.shipping_details?.name || null,
    amount_subtotal: session.amount_subtotal ?? null,
    amount_total: session.amount_total ?? null,
    shipping_cents: session.shipping_cost?.amount_total ?? null,
  });
};
