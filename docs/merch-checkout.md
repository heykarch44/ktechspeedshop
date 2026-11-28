# Merch cart + Stripe Embedded Checkout

On-site cart and Embedded Checkout for K-TECH Speedshop merch. Buyers stay on `ktechspeedshop.com`. Product prices come from `src/data/catalog.ts` (server re-prices; the client never sets unit prices). D1 stores paid orders only.

## Shared framework

Cart/checkout logic lives in **`shared/merch/`** (v1.0.0) — the same package is copied into C10 United. Keep both copies **byte-identical**: after any change, copy `shared/merch/` to the other repo, run `node shared/merch/scripts/sync-merch-core.mjs` in both, and confirm `shared/merch/CHECKSUM` matches. See `shared/merch/README.md`.

K-Tech site layer (thin):

- Catalog adapter: `functions/_lib/catalog.ts` (ids `<slug>|<size>`, 2XL +$2 / 3XL +$3)
- D1 + Resend hooks: `functions/_lib/db.ts`, `functions/_lib/notify.ts`, `functions/_lib/email.ts`
- API wrappers: `functions/api/**` → shared server helpers
- Pages: `data-merch-add` / `data-merch-mount` shells; config + assets loaded from `Base.astro`

## Flow

1. `/shop/` — size + qty + Add to cart (`localStorage` key `ktech_cart_v2`, lines `{id,qty}`)
2. `/shop/cart/` — quote via `POST /api/cart/quote`
3. `/shop/checkout/` — Embedded Checkout via `POST /api/checkout` + Stripe.js (`https://js.stripe.com/endive/stripe.js`)
4. Stripe webhook `POST /api/stripe/webhook` — verify signature, ignore non-`metadata.site=ktech` events, upsert `merch_orders`, optional Resend emails
5. `/shop/thanks/` — `GET /api/session-status?session_id=`

Shipping: **$6 flat** (`MERCH_SHIPPING_CENTS`, default `600`), free at/over **$75** (`MERCH_FREE_SHIP_CENTS`, default `7500`). Placeholders — adjust later. **No sales tax** handling yet.

## Env vars (Pages → Settings → Variables and Secrets)

Set these in **both Production and Preview** for project `ktechspeedshop`:

| Name | Kind | Required | Notes |
| --- | --- | --- | --- |
| `STRIPE_SECRET_KEY` | Secret | Yes for payments | `sk_…` |
| `STRIPE_WEBHOOK_SECRET` | Secret | Yes for webhooks | `whsec_…` from Stripe webhook endpoint |
| `STRIPE_PUBLISHABLE_KEY` | Variable | Yes for payments | `pk_…` (readable by `/api/config`) |
| `RESEND_API_KEY` | Secret | Optional | Without it, order emails are no-ops |
| `EMAIL_FROM` | Variable | With Resend | Verified sender, e.g. `K-TECH Speedshop <shop@ktechspeedshop.com>` |
| `ORDER_NOTIFY_EMAIL` | Variable | Optional | Default `shop@ktechspeedshop.com` |
| `MERCH_SHIPPING_CENTS` | Variable | Optional | Default `600` |
| `MERCH_FREE_SHIP_CENTS` | Variable | Optional | Default `7500` |

CLI examples:

```bash
npx wrangler pages secret put STRIPE_SECRET_KEY --project-name=ktechspeedshop
npx wrangler pages secret put STRIPE_WEBHOOK_SECRET --project-name=ktechspeedshop
npx wrangler pages secret put RESEND_API_KEY --project-name=ktechspeedshop
```

Add `STRIPE_PUBLISHABLE_KEY` (and optional vars) in the Cloudflare dashboard under Workers & Pages → **ktechspeedshop** → Settings → Variables and Secrets for Production **and** Preview.

D1 binding `DB` → database `ktechspeedshop` is in `wrangler.jsonc`. If a Pages preview build does not pick it up, bind `DB` manually in the dashboard.

## Stripe webhook

Register a **separate** endpoint from c10united.com’s:

- URL: `https://ktechspeedshop.com/api/stripe/webhook`
- Event: `checkout.session.completed`
- Copy the signing secret into `STRIPE_WEBHOOK_SECRET`

Sessions are tagged `metadata[site]=ktech`. The webhook ignores other sites on the shared Stripe account and returns 200.

## Read orders

```bash
npx wrangler d1 execute ktechspeedshop --remote --command "SELECT * FROM merch_orders ORDER BY created_at DESC LIMIT 20"
```

## Files

| Path | Role |
| --- | --- |
| `shared/merch/` | Shared client + server (keep in sync with C10 United) |
| `public/js/merch-core.js` / `.css` | Generated copies (sync script + `prebuild --check`) |
| `src/data/catalog.ts` | Merch products + `priceCents` / `sizes` |
| `functions/api/*` | Thin wrappers: quote, checkout, config, session-status, webhook |
| `functions/_lib/*` | Catalog adapter, D1, email/notify, env |
| `migrations/0001_merch_orders.sql` | Orders table |
| `src/pages/shop.astro` / `src/pages/shop/**` | Shop UI shells |
| `src/layouts/Base.astro` | Loads merch config + core CSS/JS |
