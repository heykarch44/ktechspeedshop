/**
 * Shared merch cart / checkout contract types (framework-agnostic).
 */

export type CartLine = {
  id: string;
  qty: number;
};

/** Catalog row returned by the site-specific lookup adapter. */
export type CatalogLine = {
  id: string;
  title: string;
  label: string;
  unit_cents: number;
  image?: string;
};

export type QuoteLine = CatalogLine & {
  qty: number;
  line_cents: number;
};

export type PricedCart = {
  items: QuoteLine[];
  subtotal_cents: number;
  shipping_cents: number;
  total_cents: number;
  free_ship_cents: number;
};

export type ShippingConfig = {
  flatCents: number;
  freeOverCents: number;
};

/** Site catalog adapter — only data-access difference between hosts. */
export type CatalogAdapter = {
  lookupLines: (ids: string[]) => Promise<Map<string, CatalogLine>>;
};

export type StripeBranding = {
  displayName?: string;
  backgroundColor?: string;
  buttonColor?: string;
  fontFamily?: string;
  borderStyle?: string;
};

export type PaidOrderItem = {
  id: string;
  title: string;
  label: string;
  qty: number;
  unit_cents: number;
  line_cents: number;
  image?: string;
};

export type PaidOrder = {
  stripe_session_id: string;
  email: string | null;
  name: string | null;
  phone: string | null;
  shipping_address: string | null;
  items: PaidOrderItem[];
  subtotal_cents: number;
  shipping_cents: number;
  total_cents: number;
  metadata: Record<string, string>;
};

export type WebhookHooks = {
  saveOrder: (order: PaidOrder) => Promise<{ inserted: boolean }>;
  notify: (order: PaidOrder) => Promise<void>;
};

export type SessionStatusOk = {
  ok: true;
  status: "complete" | "open" | "expired" | string;
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
};
