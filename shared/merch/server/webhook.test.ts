import assert from "node:assert/strict";
import { describe, it } from "node:test";
import type { CatalogAdapter, CatalogLine, PaidOrder } from "./contract";
import { handleStripeWebhook } from "./webhook";

function adapterFrom(rows: CatalogLine[]): CatalogAdapter {
  const map = new Map(rows.map((r) => [r.id, r]));
  return {
    async lookupLines(ids) {
      const out = new Map<string, CatalogLine>();
      for (const id of ids) {
        const row = map.get(id);
        if (row) out.set(id, row);
      }
      return out;
    },
  };
}

async function sign(payload: string, secret: string): Promise<string> {
  const timestamp = Math.floor(Date.now() / 1000);
  const signedPayload = `${timestamp}.${payload}`;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sigBuf = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(signedPayload));
  const v1 = [...new Uint8Array(sigBuf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return `t=${timestamp},v1=${v1}`;
}

const catalog = adapterFrom([
  { id: "speedshop-tee|L", title: "K-TECH tee", label: "L", unit_cents: 2800 },
]);

const shipping = { flatCents: 600, freeOverCents: 7500 };
const secret = "whsec_test";

describe("handleStripeWebhook ignore rules", () => {
  it("ignores non-checkout.session.completed events", async () => {
    const payload = JSON.stringify({ type: "payment_intent.succeeded", data: { object: {} } });
    const signatureHeader = await sign(payload, secret);
    const res = await handleStripeWebhook({
      payload,
      signatureHeader,
      secret,
      siteTag: "ktech",
      repriceAdapter: catalog,
      shipping,
      hooks: {
        saveOrder: async () => ({ inserted: true }),
        notify: async () => {},
      },
    });
    assert.equal(res.status, 200);
    const body = (await res.json()) as { received?: boolean; ignored?: boolean };
    assert.equal(body.received, true);
    assert.equal(body.ignored, true);
  });

  it("ignores sessions whose metadata.site does not match siteTag", async () => {
    const payload = JSON.stringify({
      type: "checkout.session.completed",
      data: {
        object: {
          id: "cs_other",
          metadata: { site: "c10", cart: "speedshop-tee|L:1" },
          customer_details: {},
        },
      },
    });
    const signatureHeader = await sign(payload, secret);
    let saved = false;
    const res = await handleStripeWebhook({
      payload,
      signatureHeader,
      secret,
      siteTag: "ktech",
      repriceAdapter: catalog,
      shipping,
      hooks: {
        saveOrder: async () => {
          saved = true;
          return { inserted: true };
        },
        notify: async () => {},
      },
    });
    assert.equal(res.status, 200);
    const body = (await res.json()) as { received?: boolean; ignored?: boolean };
    assert.equal(body.ignored, true);
    assert.equal(saved, false);
  });

  it("saves and notifies on matching completed session", async () => {
    const payload = JSON.stringify({
      type: "checkout.session.completed",
      data: {
        object: {
          id: "cs_ok",
          metadata: { site: "ktech", cart: "speedshop-tee|L:1" },
          amount_total: 3400,
          shipping_cost: { amount_total: 600 },
          customer_details: { email: "a@b.co", name: "Pat" },
        },
      },
    });
    const signatureHeader = await sign(payload, secret);
    const orders: PaidOrder[] = [];
    const notified: PaidOrder[] = [];
    const res = await handleStripeWebhook({
      payload,
      signatureHeader,
      secret,
      siteTag: "ktech",
      repriceAdapter: catalog,
      shipping,
      hooks: {
        saveOrder: async (order) => {
          orders.push(order);
          return { inserted: true };
        },
        notify: async (order) => {
          notified.push(order);
        },
      },
    });
    assert.equal(res.status, 200);
    assert.equal(orders.length, 1);
    assert.equal(orders[0]?.items[0]?.id, "speedshop-tee|L");
    assert.equal(notified.length, 1);
  });

  it("does not notify when saveOrder reports not inserted", async () => {
    const payload = JSON.stringify({
      type: "checkout.session.completed",
      data: {
        object: {
          id: "cs_dup",
          metadata: { site: "ktech", cart: "speedshop-tee|L:1" },
          customer_details: {},
        },
      },
    });
    const signatureHeader = await sign(payload, secret);
    let notifyCount = 0;
    await handleStripeWebhook({
      payload,
      signatureHeader,
      secret,
      siteTag: "ktech",
      repriceAdapter: catalog,
      shipping,
      hooks: {
        saveOrder: async () => ({ inserted: false }),
        notify: async () => {
          notifyCount += 1;
        },
      },
    });
    assert.equal(notifyCount, 0);
  });
});
