import type { Env } from "../_lib/env";

const STRIPE_JS_URL = "https://js.stripe.com/endive/stripe.js";

/** Publishable key for static checkout pages (Functions cannot inject into HTML). */
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const publishableKey = context.env.STRIPE_PUBLISHABLE_KEY?.trim() || null;
  return Response.json(
    { publishableKey, stripeJsUrl: STRIPE_JS_URL },
    {
      headers: {
        "Cache-Control": "no-store",
      },
    },
  );
};
