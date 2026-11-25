# Chance Darts marketing microsite

This is the static Lumbre Studios marketing website. It does not contain or deploy the Chance Darts scoring app or the separate browser Live Display receiver.

## Edit and build

From the website repository root:

```sh
python3 tools/microsite/build.py
python3 tools/microsite/validate.py
```

Python 3 and Node (for JavaScript syntax validation) are the only development tools required. There are no npm dependencies, runtime frameworks, external fonts, analytics or cookies.

- `content.py`: feature copy, navigation labels and Help articles.
- `release.json`: verified release status, store links, minimum platforms and release notes. Check the public storefront before changing availability; approval alone is insufficient.
- `build.py`: shared semantic templates and sitemap generation.
- `../../chance-darts/chance-darts.css`: scoped product styling.
- `../../chance-darts/chance-darts.js`: accessible navigation disclosure, native image dialog, Help filtering and explicit campaign parameter forwarding.

Commit the generated HTML and sitemap alongside source changes. GitHub Pages serves these files directly; it does not need to execute Python. The other studio pages, shared styles, privacy/support documents, approved assets, CNAME and robots.txt are preserved.

## Local preview

```sh
python3 -m http.server 4173 --bind 127.0.0.1
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
