# K-TECH Speedshop

Custom C10 builds, parts, merch, and projects for sale. Static Astro site for Cloudflare Pages.

## Run locally

```bash
npm install
npm run dev
```

## Deploy

Cloudflare Pages (git):

- Framework preset: **Astro**
- Build command: `npm run build`
- Output directory: `dist`
- Node version: `22`

If the `*.pages.dev` URL is blank or 404, the project was probably created before those settings existed. Save the build settings above and **Retry deployment**.

Or from this folder:

```bash
npm run deploy
```

Point the custom domain at the Pages project when you are ready.

## Edit the shop

| What | File |
| --- | --- |
| Shop name, email, Instagram | `src/data/site.ts` |
| Builds, for-sale trucks, parts, merch | `src/data/catalog.ts` |
| Project trucks | `src/content/projects/` |
| Dated build updates (photos + video) | `src/content/updates/` |
| Journal / SEO articles | `src/content/journal/` |
| Photos | `public/images/` |
| Shop videos | `public/videos/` |

## Add a project update

1. Drop photos in `public/images/projects/<truck-slug>/` (or drag them into this chat).
2. Copy an existing file in `src/content/updates/`.
3. Set `project`, `title`, `pubDate`, `images`, and optional `video`.

`video` can be a YouTube URL, a Vimeo URL, or a file like `/videos/ls-mockup.mp4`.

Replace the generated truck photos with real shop shots before you treat the site as live inventory. Update Instagram and email first — those are the buy buttons.

## SEO without ads

The site is static HTML, fast, and already has:

- Unique titles and descriptions on every page
- `sitemap-index.xml` and `robots.txt`
- Schema.org `AutomotiveBusiness`
- Journal posts targeting C10 search terms
- Descriptive image alt text

Next wins: your city and phone in `site.ts`, real build photos, and a new journal post whenever a truck leaves the shop.
