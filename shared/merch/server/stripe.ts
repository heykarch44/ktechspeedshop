/**
 * Minimal Stripe REST helpers (Web APIs only — no Node SDK, no framework types).
 * Form-encoded Checkout Sessions + webhook signature verification via Web Crypto.
 */

import type { QuoteLine, StripeBranding } from "./contract";

export function isStripeConfigured(env: {
  STRIPE_SECRET_KEY?: string;
  STRIPE_PUBLISHABLE_KEY?: string;
}): boolean {
  return Boolean(env.STRIPE_SECRET_KEY?.trim() && env.STRIPE_PUBLISHABLE_KEY?.trim());
}

function toFormBody(params: Record<string, string | number | undefined | null>): string {
  const parts: string[] = [];
  for (const [key, value] of Object.entries(params)) {
    if (value == null || value === "") continue;
    parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
  }
  return parts.join("&");
}

export type CreateCheckoutSessionInput = {
  secretKey: string;
  items: QuoteLine[];
  shippingCents: number;
  returnUrl: string;
  metadataCart: string;
  siteTag: string;
  branding?: StripeBranding;
};

export type CreateCheckoutSessionResult =
  | { ok: true; id: string; clientSecret: string }
  | { ok: false; error: string; status: number };

/** Form body for Embedded Checkout Sessions — exported for unit tests. */
export function buildCheckoutSessionFormBody(
  input: Omit<CreateCheckoutSessionInput, "secretKey">,
): string {
  const params: Record<string, string | number> = {
    mode: "payment",
    ui_mode: "embedded_page",
    return_url: input.returnUrl,
    redirect_on_completion: "if_required",
    billing_address_collection: "auto",
    "phone_number_collection[enabled]": "true",
    "shipping_address_collection[allowed_countries][0]": "US",
    "metadata[cart]": input.metadataCart.slice(0, 500),
    "metadata[shipping_cents]": String(input.shippingCents),
    "metadata[site]": input.siteTag,
  };

  const branding = input.branding;
  if (branding?.backgroundColor) {
    params["branding_settings[background_color]"] = branding.backgroundColor;
  }
  if (branding?.buttonColor) {
    params["branding_settings[button_color]"] = branding.buttonColor;
  }
  if (branding?.displayName) {
    params["branding_settings[display_name]"] = branding.displayName;
  }
  if (branding?.borderStyle) {
    params["branding_settings[border_style]"] = branding.borderStyle;
  }
  if (branding?.fontFamily) {
    params["branding_settings[font_family]"] = branding.fontFamily;
  }

  input.items.forEach((item, i) => {
    params[`line_items[${i}][quantity]`] = item.qty;
    params[`line_items[${i}][price_data][currency]`] = "usd";
    params[`line_items[${i}][price_data][unit_amount]`] = item.unit_cents;
    params[`line_items[${i}][price_data][product_data][name]`] = `${item.title} (${item.label})`;
    params[`line_items[${i}][price_data][product_data][metadata][id]`] = item.id;
  });

  params["shipping_options[0][shipping_rate_data][type]"] = "fixed_amount";
  params["shipping_options[0][shipping_rate_data][fixed_amount][amount]"] = input.shippingCents;
  params["shipping_options[0][shipping_rate_data][fixed_amount][currency]"] = "usd";
  params["shipping_options[0][shipping_rate_data][display_name]"] =
    input.shippingCents === 0 ? "Free shipping" : "Standard shipping";

  return toFormBody(params);
}

export async function createCheckoutSession(
  input: CreateCheckoutSessionInput,
): Promise<CreateCheckoutSessionResult> {
  try {
    const res = await fetch("https://api.stripe.com/v1/checkout/sessions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${input.secretKey}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: buildCheckoutSessionFormBody(input),
    });
    const data = (await res.json().catch(() => ({}))) as {
      id?: string;
      client_secret?: string | null;
      error?: { message?: string };
    };
    if (!res.ok || !data.id || !data.client_secret) {
      const msg = data.error?.message || `Stripe error (${res.status})`;
      console.error("[stripe] checkout session failed", msg);
      return { ok: false, error: msg, status: 502 };
    }
    return { ok: true, id: data.id, clientSecret: data.client_secret };
  } catch (err) {
    console.error("[stripe] checkout session request failed", err);
    return { ok: false, error: "Could not reach Stripe.", status: 502 };
  }
}

export type StripeCheckoutSession = {
  id: string;
  payment_status?: string;
  customer_details?: {
    email?: string | null;
    name?: string | null;
    phone?: string | null;
    address?: Record<string, string | null> | null;
  } | null;
  shipping_details?: {
    name?: string | null;
    address?: Record<string, string | null> | null;
  } | null;
  collected_information?: {
    shipping_details?: {
      name?: string | null;
      address?: Record<string, string | null> | null;
    } | null;
  } | null;
  amount_subtotal?: number | null;
  amount_total?: number | null;
  shipping_cost?: { amount_total?: number | null } | null;
  metadata?: Record<string, string> | null;
  status?: string;
  line_items?: {
    data?: Array<{
      quantity?: number | null;
      amount_total?: number | null;
      amount_subtotal?: number | null;
      price?: {
        unit_amount?: number | null;
        product?:
          | string
          | {
              name?: string | null;
              metadata?: Record<string, string> | null;
            }
          | null;
      } | null;
      description?: string | null;
    }>;
  } | null;
};

export async function retrieveCheckoutSession(
  secretKey: string,
  sessionId: string,
): Promise<StripeCheckoutSession | null> {
  try {
    const url = new URL(
      `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(sessionId)}`,
    );
    url.searchParams.append("expand[]", "line_items.data.price.product");
    const res = await fetch(url.toString(), {
      headers: { Authorization: `Bearer ${secretKey}` },
    });
    if (!res.ok) return null;
    return (await res.json()) as StripeCheckoutSession;
  } catch {
    return null;
  }
}

/** Map a Stripe session into the shared session-status JSON shape. */
export function formatSessionStatus(session: StripeCheckoutSession): {
  ok: true;
  status: string;
  paymentStatus: string | null;
  email: string | null;
  amount_total_cents: number | null;
  shipping_cents: number | null;
  items: Array<{
    id?: string;
    title: string;
    label?: string;
    qty: number;
    unit_cents?: number;
    line_cents?: number;
  }>;
} {
  const items = (session.line_items?.data || []).map((li) => {
    const product = li.price?.product;
    const productObj = product && typeof product === "object" ? product : null;
    const name = productObj?.name || li.description || "Item";
    const id = productObj?.metadata?.id;
    const paren = name.match(/^(.*)\s+\(([^)]+)\)\s*$/);
    return {
      ...(id ? { id } : {}),
      title: paren ? paren[1]! : name,
      ...(paren ? { label: paren[2] } : {}),
      qty: li.quantity ?? 1,
      ...(li.price?.unit_amount != null ? { unit_cents: li.price.unit_amount } : {}),
      ...(li.amount_total != null ? { line_cents: li.amount_total } : {}),
    };
  });

  return {
    ok: true,
    status: session.status || "open",
    paymentStatus: session.payment_status || null,
    email: session.customer_details?.email || null,
    amount_total_cents: session.amount_total ?? null,
    shipping_cents: session.shipping_cost?.amount_total ?? null,
    items,
  };
}

/** Verify Stripe-Signature using HMAC-SHA256 (Web Crypto). Tolerance 5 minutes. */
export async function verifyStripeWebhookSignature(opts: {
  payload: string;
  signatureHeader: string | null;
  secret: string;
  toleranceSec?: number;
}): Promise<{ ok: true } | { ok: false; error: string }> {
  const header = opts.signatureHeader?.trim();
  if (!header) return { ok: false, error: "Missing Stripe-Signature header." };
  if (!opts.secret.trim()) return { ok: false, error: "Webhook secret not configured." };

  const parts = Object.fromEntries(
    header.split(",").map((p) => {
      const [k, ...rest] = p.split("=");
      return [k.trim(), rest.join("=").trim()];
    }),
  ) as Record<string, string>;

  const timestamp = parts.t;
  const v1 = parts.v1;
  if (!timestamp || !v1) return { ok: false, error: "Invalid Stripe-Signature header." };

  const ts = Number.parseInt(timestamp, 10);
  if (!Number.isFinite(ts)) return { ok: false, error: "Invalid signature timestamp." };

  const tolerance = opts.toleranceSec ?? 300;
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - ts) > tolerance) {
    return { ok: false, error: "Signature timestamp outside tolerance." };
  }

  const signedPayload = `${timestamp}.${opts.payload}`;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(opts.secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sigBuf = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(signedPayload));
  const expected = bufferToHex(sigBuf);

  if (!timingSafeEqualHex(expected, v1)) {
    return { ok: false, error: "Signature mismatch." };
  }
  return { ok: true };
}

function bufferToHex(buf: ArrayBuffer): string {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function timingSafeEqualHex(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i++) {
    out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return out === 0;
}
