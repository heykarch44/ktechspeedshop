import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  buildCheckoutSessionFormBody,
  isStripeConfigured,
  verifyStripeWebhookSignature,
} from "./stripe";

describe("buildCheckoutSessionFormBody", () => {
  it("uses embedded_page ui_mode, return_url with session template, site tag + branding", () => {
    const body = buildCheckoutSessionFormBody({
      items: [
        {
          id: "speedshop-tee|L",
          title: "K-TECH tee",
          label: "L",
          qty: 1,
          unit_cents: 2800,
          line_cents: 2800,
        },
      ],
      shippingCents: 600,
      returnUrl: "https://example.com/shop/thanks/?session_id={CHECKOUT_SESSION_ID}",
      metadataCart: "speedshop-tee|L:1",
      siteTag: "ktech",
      branding: {
        backgroundColor: "#F1E7D4",
        buttonColor: "#D3541A",
        displayName: "Example Shop",
        borderStyle: "rectangular",
        fontFamily: "roboto",
      },
    });

    assert.match(body, /ui_mode=embedded_page/);
    assert.match(body, /return_url=/);
    assert.match(
      body,
      /session_id%3D%7BCHECKOUT_SESSION_ID%7D|session_id=\{CHECKOUT_SESSION_ID\}/,
    );
    assert.match(body, /redirect_on_completion=if_required/);
    assert.match(body, /metadata%5Bsite%5D=ktech|metadata\[site\]=ktech/);
    assert.match(body, /branding_settings/);
    assert.doesNotMatch(body, /success_url=/);
    assert.doesNotMatch(body, /cancel_url=/);
  });
});

describe("isStripeConfigured", () => {
  it("requires both secret and publishable keys", () => {
    assert.equal(isStripeConfigured({}), false);
    assert.equal(isStripeConfigured({ STRIPE_SECRET_KEY: "sk_test" }), false);
    assert.equal(isStripeConfigured({ STRIPE_PUBLISHABLE_KEY: "pk_test" }), false);
    assert.equal(
      isStripeConfigured({ STRIPE_SECRET_KEY: "sk_test", STRIPE_PUBLISHABLE_KEY: "pk_test" }),
      true,
    );
  });
});

describe("verifyStripeWebhookSignature", () => {
  it("accepts a valid HMAC-SHA256 signature within tolerance", async () => {
    const secret = "whsec_test_secret";
    const payload = '{"type":"checkout.session.completed"}';
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

    const ok = await verifyStripeWebhookSignature({
      payload,
      signatureHeader: `t=${timestamp},v1=${v1}`,
      secret,
    });
    assert.equal(ok.ok, true);
  });

  it("rejects missing or mismatched signatures", async () => {
    const missing = await verifyStripeWebhookSignature({
      payload: "{}",
      signatureHeader: null,
      secret: "whsec_x",
    });
    assert.equal(missing.ok, false);

    const bad = await verifyStripeWebhookSignature({
      payload: "{}",
      signatureHeader: `t=${Math.floor(Date.now() / 1000)},v1=deadbeef`,
      secret: "whsec_x",
    });
    assert.equal(bad.ok, false);
  });
});
