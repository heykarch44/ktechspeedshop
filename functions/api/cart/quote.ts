import { merchShippingConfig, parseCartBody, priceCartFromCatalog } from "../../_lib/cart";
import type { Env } from "../../_lib/env";

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const body = await context.request.json().catch(() => ({}));
  const ship = merchShippingConfig(context.env);
  const priced = priceCartFromCatalog(parseCartBody(body), ship);
  if (!priced.ok) {
    return Response.json({ ok: false, error: priced.error }, { status: 400 });
  }
  return Response.json({ ok: true, cart: priced.cart });
};
