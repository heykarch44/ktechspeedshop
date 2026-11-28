/** Cloudflare Pages Function env bindings for merch checkout. */
export type Env = {
  DB: D1Database;
  STRIPE_SECRET_KEY?: string;
  STRIPE_PUBLISHABLE_KEY?: string;
  STRIPE_WEBHOOK_SECRET?: string;
  RESEND_API_KEY?: string;
  EMAIL_FROM?: string;
  ORDER_NOTIFY_EMAIL?: string;
  MERCH_SHIPPING_CENTS?: string;
  MERCH_FREE_SHIP_CENTS?: string;
};
