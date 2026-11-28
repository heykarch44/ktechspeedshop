import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  cartLinesFromMetadata,
  compactCartMetadata,
  normalizeCartLines,
  parseCartBody,
  priceCart,
} from "./cart";
import type { CatalogAdapter, CatalogLine } from "./contract";
import { shippingCents } from "./shipping";

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

const catalog = adapterFrom([
  { id: "speedshop-tee|L", title: "K-TECH tee", label: "L", unit_cents: 2800 },
  { id: "shop-hoodie|2XL", title: "K-TECH hoodie", label: "2XL", unit_cents: 6000 },
  { id: "shop-hoodie|3XL", title: "K-TECH hoodie", label: "3XL", unit_cents: 6100 },
  { id: "ktech-trucker|One size", title: "K-TECH trucker", label: "One size", unit_cents: 3200 },
  { id: "var-tee-m", title: "C10 Tee", label: "M", unit_cents: 2500 },
]);

const ship = { flatCents: 600, freeOverCents: 7500 };

describe("priceCart (id-based)", () => {
  it("prices known id from catalog adapter", async () => {
    const priced = await priceCart([{ id: "speedshop-tee|L", qty: 2 }], catalog, ship);
    assert.equal(priced.ok, true);
    if (!priced.ok) return;
    assert.equal(priced.cart.items[0]?.unit_cents, 2800);
    assert.equal(priced.cart.items[0]?.id, "speedshop-tee|L");
    assert.equal(priced.cart.items[0]?.label, "L");
    assert.equal(priced.cart.subtotal_cents, 5600);
    assert.equal(priced.cart.shipping_cents, 600);
    assert.equal(priced.cart.total_cents, 6200);
    assert.equal(priced.cart.free_ship_cents, 7500);
  });

  it("applies 2XL / 3XL size deltas via adapter unit prices", async () => {
    const xl = await priceCart([{ id: "shop-hoodie|2XL", qty: 1 }], catalog, ship);
    const xxxl = await priceCart([{ id: "shop-hoodie|3XL", qty: 1 }], catalog, ship);
    assert.equal(xl.ok && xl.cart.items[0]?.unit_cents, 6000);
    assert.equal(xxxl.ok && xxxl.cart.items[0]?.unit_cents, 6100);
  });

  it("rejects unknown id or bad qty", async () => {
    assert.equal((await priceCart([{ id: "nope", qty: 1 }], catalog, ship)).ok, false);
    assert.equal(
      (await priceCart([{ id: "ktech-trucker|One size", qty: 0 }], catalog, ship)).ok,
      false,
    );
    assert.equal(
      (await priceCart([{ id: "ktech-trucker|One size", qty: 100 }], catalog, ship)).ok,
      false,
    );
  });
});

describe("shippingCents", () => {
  it("gives free shipping at threshold", () => {
    assert.equal(shippingCents(7499, ship), 600);
    assert.equal(shippingCents(7500, ship), 0);
    assert.equal(shippingCents(0, ship), 0);
  });
});

describe("legacy line mapping", () => {
  it("maps variantId and slug+size into id", () => {
    assert.deepEqual(normalizeCartLines([{ variantId: "var-tee-m", qty: 2 }]), [
      { id: "var-tee-m", qty: 2 },
    ]);
    assert.deepEqual(
      normalizeCartLines([{ slug: "speedshop-tee", size: "L", qty: 1 }]),
      [{ id: "speedshop-tee|L", qty: 1 }],
    );
    assert.deepEqual(normalizeCartLines([{ id: "already|M", qty: 3 }]), [
      { id: "already|M", qty: 3 },
    ]);
  });

  it("parseCartBody accepts legacy and id shapes then prices", async () => {
    const legacy = parseCartBody({
      items: [{ slug: "speedshop-tee", size: "L", qty: 1 }],
    });
    const priced = await priceCart(legacy, catalog, ship);
    assert.equal(priced.ok, true);
    if (!priced.ok) return;
    assert.equal(priced.cart.items[0]?.id, "speedshop-tee|L");

    const c10 = parseCartBody({ items: [{ variantId: "var-tee-m", qty: 1 }] });
    const priced2 = await priceCart(c10, catalog, ship);
    assert.equal(priced2.ok, true);
    if (!priced2.ok) return;
    assert.equal(priced2.cart.items[0]?.id, "var-tee-m");
  });
});

describe("compactCartMetadata", () => {
  it("round-trips id:qty including pipe ids (old K-Tech format)", () => {
    const meta = compactCartMetadata([{ id: "speedshop-tee|L", qty: 2 }]);
    assert.equal(meta, "speedshop-tee|L:2");
    const lines = cartLinesFromMetadata(meta);
    assert.deepEqual(lines, [{ id: "speedshop-tee|L", qty: 2 }]);
  });

  it("parses plain variant id metadata (C10 / new format)", () => {
    const meta = compactCartMetadata([{ id: "var-tee-m", qty: 3 }]);
    assert.equal(meta, "var-tee-m:3");
    assert.deepEqual(cartLinesFromMetadata(meta), [{ id: "var-tee-m", qty: 3 }]);
  });

  it("parses multi-item metadata with mixed id shapes", () => {
    const lines = cartLinesFromMetadata("speedshop-tee|L:2,var-tee-m:1");
    assert.deepEqual(lines, [
      { id: "speedshop-tee|L", qty: 2 },
      { id: "var-tee-m", qty: 1 },
    ]);
  });
});
