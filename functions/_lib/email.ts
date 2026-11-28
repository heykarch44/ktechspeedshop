/**
 * Transactional email via Resend HTTP API.
 * No-op until RESEND_API_KEY + EMAIL_FROM are both set.
 */

export type EmailEnv = {
  RESEND_API_KEY?: string;
  EMAIL_FROM?: string;
};

export type SendEmailInput = {
  to: string;
  subject: string;
  html: string;
  text: string;
  idempotencyKey?: string;
};

export type SendEmailResult = { sent: false } | { sent: true; id: string };

let missingConfigLogged = false;

export function isEmailConfigured(env: EmailEnv): boolean {
  return Boolean(env.RESEND_API_KEY?.trim() && env.EMAIL_FROM?.trim());
}

export async function sendEmail(env: EmailEnv, input: SendEmailInput): Promise<SendEmailResult> {
  const apiKey = env.RESEND_API_KEY?.trim();
  const from = env.EMAIL_FROM?.trim();
  if (!apiKey || !from) {
    if (!missingConfigLogged) {
      missingConfigLogged = true;
      console.info("[email] RESEND_API_KEY / EMAIL_FROM not set — sendEmail is a no-op");
    }
    return { sent: false };
  }

  const to = input.to.trim();
  if (!to) return { sent: false };

  try {
    const headers: Record<string, string> = {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    };
    if (input.idempotencyKey) {
      headers["Idempotency-Key"] = input.idempotencyKey.slice(0, 256);
    }

    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers,
      body: JSON.stringify({
        from,
        to: [to],
        subject: input.subject,
        html: input.html,
        text: input.text,
      }),
    });

    if (!res.ok) {
      const body = await res.text().catch(() => "");
      console.error(`[email] Resend ${res.status}: ${body.slice(0, 300)}`);
      return { sent: false };
    }

    const data = (await res.json().catch(() => ({}))) as { id?: string };
    if (!data.id) {
      console.error("[email] Resend response missing id");
      return { sent: false };
    }
    return { sent: true, id: data.id };
  } catch (err) {
    console.error("[email] send failed", err);
    return { sent: false };
  }
}

const ACCENT = "#D3541A";
const PAPER = "#F1E7D4";
const INK = "#0b0a09";
const MUTED = "#5c5348";

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatUsdCents(cents: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(cents / 100);
}

function brandedHtml(opts: {
  headline: string;
  bodyHtml: string;
  ctaLabel?: string;
  ctaUrl?: string;
}): string {
  const cta =
    opts.ctaLabel && opts.ctaUrl
      ? `<p style="margin:28px 0 0;">
          <a href="${escapeHtml(opts.ctaUrl)}"
             style="display:inline-block;background:${ACCENT};color:#fff;text-decoration:none;
                    font-family:Figtree,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
                    font-size:15px;font-weight:600;padding:12px 22px;">
            ${escapeHtml(opts.ctaLabel)}
          </a>
        </p>`
      : "";

  return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;padding:0;background:${PAPER};">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${PAPER};">
    <tr><td align="center" style="padding:32px 16px;">
      <table role="presentation" width="560" cellpadding="0" cellspacing="0"
             style="max-width:560px;width:100%;background:#fff;border:1px solid #e4d9c4;">
        <tr><td style="padding:28px 28px 8px;border-bottom:3px solid ${ACCENT};">
          <div style="font-family:Oswald,Figtree,system-ui,sans-serif;
                      font-size:13px;font-weight:700;letter-spacing:0.14em;color:${ACCENT};">
            K-TECH SPEEDSHOP
          </div>
        </td></tr>
        <tr><td style="padding:28px;font-family:Figtree,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:${INK};">
          <h1 style="margin:0 0 12px;font-size:22px;font-weight:700;line-height:1.25;">
            ${escapeHtml(opts.headline)}
          </h1>
          <div style="font-size:15px;line-height:1.55;color:${MUTED};">
            ${opts.bodyHtml}
          </div>
          ${cta}
        </td></tr>
        <tr><td style="padding:16px 28px 24px;font-family:Figtree,system-ui,sans-serif;
                       font-size:12px;color:${MUTED};border-top:1px solid #ece4d4;">
          K-TECH Speedshop — custom C10 builds and merch. Not affiliated with GM or Chevrolet.
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`;
}

export type MerchEmailLine = {
  title: string;
  size: string;
  qty: number;
  line_cents: number;
};

export function merchOrderAdminEmail(opts: {
  orderId: string;
  email: string | null;
  name: string | null;
  phone: string | null;
  items: MerchEmailLine[];
  subtotalCents: number;
  shippingCents: number;
  totalCents: number;
  shippingAddress?: string | null;
}): { subject: string; html: string; text: string } {
  const subject = `New merch order — ${formatUsdCents(opts.totalCents)}`;
  const linesHtml = opts.items
    .map(
      (i) =>
        `<li style="margin:0 0 6px;"><strong style="color:${INK};">${escapeHtml(i.title)}</strong> (${escapeHtml(i.size)}) × ${i.qty} — ${escapeHtml(formatUsdCents(i.line_cents))}</li>`,
    )
    .join("");
  const addr = opts.shippingAddress
    ? `<p style="margin:12px 0 0;white-space:pre-line;">${escapeHtml(opts.shippingAddress)}</p>`
    : "";
  const phone = opts.phone ? `<p style="margin:8px 0 0;">Phone: ${escapeHtml(opts.phone)}</p>` : "";
  const html = brandedHtml({
    headline: "New merch order",
    bodyHtml: `<p style="margin:0 0 12px;">Order <strong style="color:${INK};">${escapeHtml(opts.orderId.slice(0, 8))}</strong> from ${escapeHtml(opts.name || "Customer")} (${escapeHtml(opts.email || "no email")}).</p>
      <ul style="margin:0 0 12px;padding-left:18px;">${linesHtml}</ul>
      <p style="margin:0;">Subtotal ${escapeHtml(formatUsdCents(opts.subtotalCents))} · Shipping ${escapeHtml(formatUsdCents(opts.shippingCents))} · <strong style="color:${INK};">Total ${escapeHtml(formatUsdCents(opts.totalCents))}</strong></p>
      ${phone}${addr}`,
  });
  const text = [
    "K-TECH SPEEDSHOP",
    "",
    `New merch order ${opts.orderId}`,
    `Customer: ${opts.name || "—"} <${opts.email || "—"}>`,
    opts.phone ? `Phone: ${opts.phone}` : "",
    ...opts.items.map((i) => `- ${i.title} (${i.size}) × ${i.qty}: ${formatUsdCents(i.line_cents)}`),
    `Subtotal ${formatUsdCents(opts.subtotalCents)} · Shipping ${formatUsdCents(opts.shippingCents)} · Total ${formatUsdCents(opts.totalCents)}`,
    opts.shippingAddress || "",
  ]
    .filter(Boolean)
    .join("\n");
  return { subject, html, text };
}

export function merchOrderReceiptEmail(opts: {
  orderId: string;
  name: string | null;
  items: MerchEmailLine[];
  subtotalCents: number;
  shippingCents: number;
  totalCents: number;
  siteUrl: string;
}): { subject: string; html: string; text: string } {
  const subject = "Your K-TECH Speedshop merch order";
  const linesHtml = opts.items
    .map(
      (i) =>
        `<li style="margin:0 0 6px;"><strong style="color:${INK};">${escapeHtml(i.title)}</strong> (${escapeHtml(i.size)}) × ${i.qty} — ${escapeHtml(formatUsdCents(i.line_cents))}</li>`,
    )
    .join("");
  const greet = opts.name?.trim() ? `Hi ${escapeHtml(opts.name.trim())},` : "Thanks for your order.";
  const html = brandedHtml({
    headline: "Order confirmed",
    bodyHtml: `<p style="margin:0 0 12px;">${greet}</p>
      <p style="margin:0 0 12px;">We received your K-TECH Speedshop merch order <strong style="color:${INK};">${escapeHtml(opts.orderId.slice(0, 8))}</strong>.</p>
      <ul style="margin:0 0 12px;padding-left:18px;">${linesHtml}</ul>
      <p style="margin:0;">Subtotal ${escapeHtml(formatUsdCents(opts.subtotalCents))} · Shipping ${escapeHtml(formatUsdCents(opts.shippingCents))} · <strong style="color:${INK};">Total ${escapeHtml(formatUsdCents(opts.totalCents))}</strong></p>
      <p style="margin:12px 0 0;">We'll email again when it ships.</p>`,
    ctaLabel: "Back to shop",
    ctaUrl: opts.siteUrl,
  });
  const text = [
    "K-TECH SPEEDSHOP",
    "",
    opts.name?.trim() ? `Hi ${opts.name.trim()},` : "Thanks for your order.",
    `Order ${opts.orderId} confirmed.`,
    ...opts.items.map((i) => `- ${i.title} (${i.size}) × ${i.qty}: ${formatUsdCents(i.line_cents)}`),
    `Subtotal ${formatUsdCents(opts.subtotalCents)} · Shipping ${formatUsdCents(opts.shippingCents)} · Total ${formatUsdCents(opts.totalCents)}`,
    "We'll email again when it ships.",
    opts.siteUrl,
  ].join("\n");
  return { subject, html, text };
}
