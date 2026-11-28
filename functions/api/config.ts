import type { Env } from "../_lib/env";

/** Publishable key for static checkout pages (Functions cannot inject into HTML). */
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const publishableKey = context.env.STRIPE_PUBLISHABLE_KEY?.trim() || null;
  return Response.json(
    { publishableKey },
    {
      headers: {
        "Cache-Control": "no-store",
      },
    },
  );
};
