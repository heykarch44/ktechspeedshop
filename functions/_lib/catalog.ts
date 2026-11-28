/**
 * K-Tech catalog adapter for shared merch — ids are `<slug>|<size>`.
 */

import { merch, merchUnitCents } from "../../src/data/catalog";
import type { CatalogAdapter, CatalogLine } from "../../shared/merch/server";

export const SITE_TAG = "ktech";

export const STRIPE_BRANDING = {
  displayName: "K-TECH Speedshop",
  backgroundColor: "#F1E7D4",
  buttonColor: "#D3541A",
  borderStyle: "rectangular",
  fontFamily: "roboto",
} as const;

export function parseVariantId(id: string): { slug: string; size: string } | null {
  const pipe = id.indexOf("|");
  if (pipe < 0) return null;
  const slug = id.slice(0, pipe).trim();
  const size = id.slice(pipe + 1).trim();
  if (!slug || !size) return null;
  return { slug, size };
}

export function variantId(slug: string, size: string): string {
  return `${slug}|${size}`;
}

export const ktechCatalogAdapter: CatalogAdapter = {
  async lookupLines(ids: string[]): Promise<Map<string, CatalogLine>> {
    const out = new Map<string, CatalogLine>();
    for (const id of ids) {
      const parsed = parseVariantId(id);
      if (!parsed) continue;
      const product = merch.find((m) => m.slug === parsed.slug);
      if (!product) continue;
      if (!product.sizes.includes(parsed.size)) continue;
      out.set(id, {
        id,
        title: product.title,
        label: parsed.size,
        unit_cents: merchUnitCents(product, parsed.size),
        image: product.cover,
      });
    }
    return out;
  },
};
