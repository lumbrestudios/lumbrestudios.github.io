# Chance Darts marketing microsite

This is the static Lumbre Studios marketing website. It does not contain or deploy the Chance Darts scoring app or the separate browser Live Display receiver.

## Edit and build

From the website repository root:

```sh
python3 tools/microsite/build.py
python3 tools/microsite/validate.py
```

Python 3 and Node (for JavaScript syntax validation) are the only development tools required. There are no npm dependencies, runtime frameworks, external fonts, analytics or cookies.

- `watch-images.json`: owner-supplied Apple Watch screenshot metadata; original PNGs are in `assets/screenshots/chance-darts/watch/`.
- `content.py`: feature copy, navigation labels and Help articles.
- `release.json`: verified release status, store links, minimum platforms and release notes. Check the public storefront before changing availability; approval alone is insufficient.
- `build.py`: shared semantic templates and sitemap generation.
- `../../chance-darts/chance-darts.css`: scoped product styling.
- `../../chance-darts/chance-darts.js`: accessible navigation disclosure, native image dialog, Help filtering and explicit campaign parameter forwarding.

Commit the generated HTML and sitemap alongside source changes. GitHub Pages serves these files directly; it does not need to execute Python. The other studio pages, shared styles, privacy/support documents, approved assets, CNAME and robots.txt are preserved.

## Local preview

```sh
python3 tools/microsite/preview.py
```

Open http://127.0.0.1:4173/chance-darts/ . Stop with Ctrl-C. If the review server already uses that port, visit it or select a different port. This preview is loopback-only and is not reachable from another device.

## Campaign links

Every feature route is a standalone landing page. Example:

```text
https://lumbrestudios.app/chance-darts/online-play/?utm_source=facebook&utm_medium=paid_social&utm_campaign=connected_play
```

JavaScript carries explicitly supplied `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `ct`, `pt` and `mt` parameters across product navigation and App Store CTAs. Canonicals remain clean. There are no pixels, cookies, local storage, redirects, attribution services or automatic App Store campaign-token creation. App Store reporting depends on the owner's valid Apple campaign tokens; UTM forwarding alone does not promise Apple attribution. Without JavaScript, all content and links work, but parameter forwarding and Help filtering are unavailable.

## Verification limits and release boundary

The validator checks 15 pages, internal links/anchors, assets, unique metadata, structured-data JSON, sitemap preservation, JavaScript syntax and byte preservation of non-product production files against `14d6f7ae1923dcfe4b337bd1108debd716b2be76`.

Browser QA could not run in the authoring session: the embedded browser service was unavailable and Safari computer-use access was not approved. Before approving production, inspect responsive overflow, keyboard navigation, menu dismissal, image dialog focus/escape, search results, zoom, reduced motion and current store links in a browser.

No deployment is authorised until the owner has reviewed and approved the microsite. Production uses GitHub Pages, `main`, repository root, and the existing `lumbrestudios.app` CNAME. The full review, evidence and recovery bundles are in the parent review directory and must not be copied into the published repository.

## SEO source and certification

`seo.json` stores the intent map, unique titles/descriptions and genuine social artwork for all 15 pages. Its `updated` date is the last significant SEO content change, not build time; update it only when a real change warrants sitemap lastmod. No search-volume estimates are implied.

`python3 tools/microsite/audit_seo.py` adds approved-body preservation, social-image, schema-reference, sitemap-date and non-browser payload checks. This audit also needs ImageMagick and Brotli on PATH; the standard build/validator still use Python and Node only. The audit compares against the recoverable owner-approved pre-SEO tag. No browser or Core Web Vitals result is implied by a passing static audit.

The private preview binds to 127.0.0.1 and sends X-Robots-Tag: noindex, nofollow on every response. These headers are not included in production HTML. Do not expose or tunnel the preview. CSS and JavaScript remain byte-identical to the owner-approved design. Watch WebP derivatives are lossless with decoded pixels checked against preserved PNGs; lightboxes still open those PNGs. Social PNGs are lossless format conversions of existing WebP artwork, with genuine original screenshots used where suitable. No screenshots were generated or captured.

### Owner actions after a separately approved deployment

1. Confirm all 15 HTTPS canonical routes, assets, sitemap and robots return expected HTTP statuses; missing routes must return 404. Inspect source canonical URLs on slashless, index.html and UTM variants.
2. Review GitHub Pages Settings > Pages > Enforce HTTPS. The audit observed HTTP 200 without HTTPS redirection and the github.io alias redirecting to HTTP. Enabling HTTPS enforcement is an owner hosting action, not performed here. Recheck redirects afterwards. GitHub Pages serves index.html and query aliases; canonical tags, clean navigation and sitemap consolidate those signals. Google canonical selection cannot be guaranteed before indexing.
3. Complete desktop/mobile browser checks, Google Rich Results Test and real social-sharing previews. Record Lighthouse mobile/desktop lab results separately from field CWV. Field targets at the 75th percentile: LCP <=2.5s, INP <=200ms, CLS <=0.1; new pages may initially lack enough data.
4. Open the existing Search Console property. A public Google DNS verification TXT record exists, but account access/ownership was not verified. Preserve it. If verification is needed, use the existing domain record where authorised, or an approved URL-prefix verification method. No DNS/account changes were made.
5. Submit https://lumbrestudios.app/sitemap.xml in the verified property after deployment; inspect the overview and priority new pages using URL Inspection, check selected canonical/rendered content, and request indexing where appropriate. Submission does not guarantee indexing.
6. In an owner-verified Bing Webmaster Tools property, submit the same production sitemap; importing an existing Search Console property is an owner option. No Bing verification marker was found locally; this does not prove no Bing account exists.
7. Review indexing, crawl/404/canonical errors and mobile/desktop CWV after launch. Review Search Console queries, landing pages, country/device performance and conversions after enough data accumulates; adjust intent targeting based on evidence. Monitor weekly initially and monthly thereafter.

No accounts, external submissions, DNS, hosting, backend or production changes were made. The complete SEO review and evidence remain outside the publishable root, in the parent review directory.
