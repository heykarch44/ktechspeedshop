import type { ShippingConfig } from "./contract";

export const DEFAULT_FLAT_CENTS = 600;
export const DEFAULT_FREE_OVER_CENTS = 7500;

/** Flat shipping, free at/over threshold. Zero when subtotal is empty. */
export function shippingCents(
  subtotal: number,
  opts: ShippingConfig = {
    flatCents: DEFAULT_FLAT_CENTS,
    freeOverCents: DEFAULT_FREE_OVER_CENTS,
  },
): number {
  const flat = Math.max(0, opts.flatCents);
  const freeOver = Math.max(0, opts.freeOverCents);
  if (subtotal <= 0) return 0;
  if (freeOver > 0 && subtotal >= freeOver) return 0;
  return flat;
}

export function shippingConfigFromEnv(env: {
  MERCH_SHIPPING_CENTS?: string;
  MERCH_FREE_SHIP_CENTS?: string;
}): ShippingConfig {
  return {
    flatCents: parseIntCents(env.MERCH_SHIPPING_CENTS, DEFAULT_FLAT_CENTS),
    freeOverCents: parseIntCents(env.MERCH_FREE_SHIP_CENTS, DEFAULT_FREE_OVER_CENTS),
  };
}

function parseIntCents(raw: string | undefined, fallback: number): number {
  if (raw == null || raw.trim() === "") return fallback;
  const n = Number.parseInt(raw, 10);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
}
