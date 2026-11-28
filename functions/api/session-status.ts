import type { Env } from "../_lib/env";
import {
  formatSessionStatus,
  isStripeConfigured,
  retrieveCheckoutSession,
} from "../../shared/merch/server";

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

  return Response.json(formatSessionStatus(session));
};
