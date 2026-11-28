import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  cartLinesFromMetadata,
  compactCartMetadata,
  priceCartFromCatalog,
  shippingCentsForSubtotal,
} from "./cart";

describe("priceCartFromCatalog", () => {
  const ship = { shippingCents: 600, freeShipCents: 7500 };

  it("prices known slug/size from catalog", () => {
    const priced = priceCartFromCatalog(
      [{ slug: "speedshop-tee", size: "L", qty: 2 }],
      ship,
    );
    assert.equal(priced.ok, true);
    if (!priced.ok) return;
    assert.equal(priced.cart.items[0]?.unit_cents, 2800);
    assert.equal(priced.cart.subtotal_cents, 5600);
    assert.equal(priced.cart.shipping_cents, 600);
    assert.equal(priced.cart.total_cents, 6200);
  });

  it("applies 2XL / 3XL size deltas", () => {
    const xl = priceCartFromCatalog([{ slug: "shop-hoodie", size: "2XL", qty: 1 }], ship);
    const xxxl = priceCartFromCatalog([{ slug: "shop-hoodie", size: "3XL", qty: 1 }], ship);
    assert.equal(xl.ok && xl.cart.items[0]?.unit_cents, 6000);
    assert.equal(xxxl.ok && xxxl.cart.items[0]?.unit_cents, 6100);
  });

  it("rejects unknown slug or size and bad qty", () => {
    assert.equal(priceCartFromCatalog([{ slug: "nope", size: "L", qty: 1 }], ship).ok, false);
    assert.equal(
      priceCartFromCatalog([{ slug: "ktech-trucker", size: "XL", qty: 1 }], ship).ok,
      false,
    );
    assert.equal(
      priceCartFromCatalog([{ slug: "ktech-trucker", size: "One size", qty: 0 }], ship).ok,
      false,
    );
    assert.equal(
      priceCartFromCatalog([{ slug: "ktech-trucker", size: "One size", qty: 100 }], ship).ok,
      false,
    );
  });

  it("gives free shipping at threshold", () => {
    assert.equal(shippingCentsForSubtotal(7499, 600, 7500), 600);
    assert.equal(shippingCentsForSubtotal(7500, 600, 7500), 0);
  });
});

describe("compactCartMetadata", () => {
  it("round-trips slug|size:qty", () => {
    const meta = compactCartMetadata([
      {
        slug: "speedshop-tee",
        title: "K-TECH tee",
        size: "L",
        qty: 2,
        unit_cents: 2800,
        line_cents: 5600,
      },
    ]);
    assert.equal(meta, "speedshop-tee|L:2");
    const lines = cartLinesFromMetadata(meta);
    assert.deepEqual(lines, [{ slug: "speedshop-tee", size: "L", qty: 2 }]);
  });
});
