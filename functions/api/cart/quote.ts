import { ktechCatalogAdapter } from "../../_lib/catalog";
import type { Env } from "../../_lib/env";
import { parseCartBody, priceCart, shippingConfigFromEnv } from "../../../shared/merch/server";

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const body = await context.request.json().catch(() => ({}));
  const priced = await priceCart(
    parseCartBody(body),
    ktechCatalogAdapter,
    shippingConfigFromEnv(context.env),
  );
  if (!priced.ok) {
    return Response.json({ ok: false, error: priced.error }, { status: 400 });
  }
  return Response.json({ ok: true, cart: priced.cart });
};
