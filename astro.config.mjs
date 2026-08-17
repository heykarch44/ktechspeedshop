import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://ktechspeedshop.com",
  output: "static",
  compressHTML: true,
  integrations: [
    sitemap({
      changefreq: "weekly",
      priority: 0.7,
    }),
  ],
  build: {
    inlineStylesheets: "auto",
  },
});
