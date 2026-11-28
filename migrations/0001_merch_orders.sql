-- Merch orders from Stripe Embedded Checkout (additive only).
CREATE TABLE IF NOT EXISTS merch_orders (
  id TEXT PRIMARY KEY,
  stripe_session_id TEXT NOT NULL UNIQUE,
  email TEXT,
  name TEXT,
  phone TEXT,
  shipping_address TEXT,
  items TEXT,
  subtotal_cents INTEGER,
  shipping_cents INTEGER,
  total_cents INTEGER,
  status TEXT DEFAULT 'paid',
  tracking TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  shipped_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_merch_orders_created_at ON merch_orders (created_at);
