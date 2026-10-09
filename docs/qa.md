# QA report, Oct 9 2026 (Playbook prompts 16 to 20)

Run on branch `build` after the last content change. Every result below comes from a script in
`scripts/` or a headless Chromium run; nothing is marked passed without being run.

## Summary

| Check | Result |
|---|---|
| `python3 build.py` | 84 pages and 6 blog posts built; `build.py --check`: 0 files differ from the committed output |
| `python3 scripts/check.py` | 91 pages, **0 errors**, 9 warnings (listed below) |
| Old URLs (`scripts/check_urls.py`) | 89 old URLs and redirect rules, **0 failures** |
| Town text (`scripts/check_town_text.py`) | 60 pages, 2,460 original text blocks, **0 changed** |
| Duplication (`scripts/similarity.py`) | new vs new max **1.4%**, new vs town max **1.1%** (limit 15%) |
| Blog writers dry run (`scripts/test_blog_writers.py`) | **PASS**: both writers' posts use the site design and land in blog/index.html and sitemap.xml; no sitemap URL lost |
| Forced 301! redirects | **Fire** under Netlify CLI 17.38 (`netlify dev --offline`): `/custom-signs/hallsville-tx` 301 to `.html`, `/furniture-repair/kilgore-tx` 301, `/furniture-restoration/kilgore-tx.html` 301 to `/furniture-repair/kilgore-tx.html`, `/cabinets-and-built-ins/` 301 to `/custom-cabinets/`; `/src/data/site.json` and `/CLAUDE.md` return 404 |
| Horizontal overflow | 93 pages at 1440, 1024, 768 and 390 px (372 loads): **0** pages overflow, **0** JavaScript errors |
| Text contrast | 93 pages at 1440 and 390 px: **0** text elements below WCAG AA (4.5:1, 3:1 for large text) |
| Visible em/en dashes | **0** across all 93 HTML files (the quote form keeps one inside a hidden `value` so submissions are unchanged) |
| Banned phrases | **0** on new or rewritten pages; 5 kept word for word on 3 town pages (decisions.md 12) |
| Quote form | Same name, method, action, honeypot, encoding and every field tag as commit 6531506 |
| shop-upload.html, write.html | Still load their scripts and call `shop-auth` and `blog-post`; noindex kept; inline scripts parse |
| Independent fact-check | Run by three separate sub-agents; findings fixed (docs/fact-check.md) |

## Not verified (needs the live site or a person)

- The Netlify form submission itself, Netlify function behavior with real secrets (password check, GitHub
  commit) and the Cloudinary upload were not exercised: no deploy was allowed. The code paths were checked
  by reading and by the dry run.
- The Spanish translation itself. In Chromium, the ES button sets the `googtrans=/en/es` cookie, reloads, shows ES as selected and requests Google's translate script; whether Google returns the translated page was not checked. The mobile menu and its submenus open and close in the same run.
- External source links could not be loaded from this environment (see docs/fact-check.md).

## Warnings from check.py

- /blog/refinishing-vs-restoring-what-each-does-to-an-antique-s-valu-1790967226299.html: title is 80 chars
- /blog/why-furniture-joints-loosen-in-east-texas-humidity-and-the-f-1790708477602.html: title is 80 chars
- /custom-cabinets/marshall-tx.html: description is 172 chars
- /custom-signs/lindale-tx.html: kept word for word: banned /\bcheapest\b/ in: ...treet until somebody does something about it. The cheapest thing that changes that is at the front door: a h...
- /custom-signs/lindale-tx.html: kept word for word: banned /\bcheapest\b/ in: ... house number for a new-build? Yes, and it is the cheapest thing that makes a subdivision frontage look like...
- /custom-signs/white-oak-tx.html: kept word for word: banned /\bcheapest\b/ in: ...rch pieces In a town of newer houses, this is the cheapest thing that makes a frontage look like somebody's ...
- /custom-signs/white-oak-tx.html: kept word for word: banned /\bcheapest\b/ in: ...ouse number for a newer house? Yes, and it is the cheapest thing that makes a frontage look like somebody's....
- /furniture-repair/hallsville-tx.html: kept word for word: banned /\bwarrant(?:y|ies)\b/ in: ...nd built by somebody who was not thinking about a warranty. Those pieces are a pleasure to work on. They com...
- /furniture-repair/kilgore-tx.html: description is 174 chars

## Duplication (Jaccard, 5-word shingles)

| Comparison | Pairs | Max | Mean | Min |
|---|---:|---:|---:|---:|
| New vs new | 210 | 1.4% | 0.1% | 0.0% |
| New vs town pages | 1260 | 1.1% | 0.1% | 0.0% |

Highest pairs:

| Jaccard | Page | Page |
|---:|---|---|
| 1.4% | /custom-cabinets/cabinet-refacing/ | /custom-cabinets/what-is-cabinet-refacing/ |
| 1.3% | /furniture-repair/chair-caning-and-repair/ | /furniture-repair/how-chair-caning-is-repaired/ |
| 1.3% | /custom-furniture/custom-dining-tables/ | /custom-furniture/ |
| 1.1% | / | /furniture-repair/new-london-tx.html |
| 1.1% | / | /furniture-repair/troup-tx.html |
| 1.1% | /furniture-repair/furniture-refinishing/ | /furniture-repair/ |
| 1.0% | / | /furniture-repair/marshall-tx.html |
| 1.0% | / | /furniture-repair/gilmer-tx.html |
| 0.9% | /furniture-repair/ | / |
| 0.9% | /furniture-repair/furniture-refinishing/ | /furniture-repair/furniture-veneer-repair/ |
| 0.7% | /custom-cabinets/ | /furniture-repair/table-refinishing/ |
| 0.7% | /custom-furniture/custom-dining-tables/ | /custom-furniture/dining-table-size-for-8/ |

## Route inventory and status

All 89 sitemap URLs pass check.py (title, description, canonical, Open Graph, one H1, one valid
JSON-LD block, hero, links and images resolve). Plus `/thanks.html` and `/404.html` (noindex, not in the
sitemap) and Grace's two tools.

| URL | Type | Result |
|---|---|---|
| `/` | Homepage (rewritten) | PASS |
| `/custom-cabinets/` | Hub (rewritten) | PASS |
| `/custom-cabinets/arp-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/big-sandy-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/built-in-shelves/` | New page | PASS |
| `/custom-cabinets/cabinet-painting-cost/` | New page | PASS |
| `/custom-cabinets/cabinet-painting/` | New page | PASS |
| `/custom-cabinets/cabinet-refacing/` | New page | PASS |
| `/custom-cabinets/gilmer-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/gladewater-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/hallsville-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/henderson-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/kilgore-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/lindale-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/longview-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/marshall-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/new-london-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/overton-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/troup-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/tyler-tx.html` | Town page (text kept) | PASS |
| `/custom-cabinets/what-is-cabinet-refacing/` | New page | PASS |
| `/custom-cabinets/white-oak-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/` | Hub (rewritten) | PASS |
| `/custom-furniture/arp-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/big-sandy-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/custom-dining-tables/` | New page | PASS |
| `/custom-furniture/dining-table-size-for-8/` | New page | PASS |
| `/custom-furniture/gilmer-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/gladewater-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/hallsville-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/henderson-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/kilgore-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/lindale-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/longview-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/marshall-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/new-london-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/overton-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/troup-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/tyler-tx.html` | Town page (text kept) | PASS |
| `/custom-furniture/white-oak-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/` | Hub (rewritten) | PASS |
| `/custom-signs/arp-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/big-sandy-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/gilmer-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/gladewater-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/hallsville-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/henderson-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/kilgore-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/lindale-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/longview-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/marshall-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/new-london-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/overton-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/troup-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/tyler-tx.html` | Town page (text kept) | PASS |
| `/custom-signs/white-oak-tx.html` | Town page (text kept) | PASS |
| `/deck-repair/` | New page | PASS |
| `/furniture-repair/` | Hub (rewritten) | PASS |
| `/furniture-repair/antique-furniture-restoration/` | New page | PASS |
| `/furniture-repair/arp-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/big-sandy-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/chair-caning-and-repair/` | New page | PASS |
| `/furniture-repair/furniture-refinishing-cost/` | New page | PASS |
| `/furniture-repair/furniture-refinishing/` | New page | PASS |
| `/furniture-repair/furniture-veneer-repair/` | New page | PASS |
| `/furniture-repair/gilmer-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/gladewater-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/hallsville-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/henderson-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/how-chair-caning-is-repaired/` | New page | PASS |
| `/furniture-repair/kilgore-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/lindale-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/longview-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/marshall-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/new-london-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/overton-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/table-refinishing/` | New page | PASS |
| `/furniture-repair/troup-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/tyler-tx.html` | Town page (text kept) | PASS |
| `/furniture-repair/white-oak-tx.html` | Town page (text kept) | PASS |
| `/gallery/` | Gallery (kept) | PASS |
| `/porch-repair/` | New page | PASS |
| `/blog/` | Blog | PASS |
| `/blog/how-to-clean-a-wood-table-without-damaging-the-finish-1791314134922.html` | Blog | PASS |
| `/blog/refinishing-vs-restoring-what-each-does-to-an-antique-s-valu-1790967226299.html` | Blog | PASS |
| `/blog/why-furniture-joints-loosen-in-east-texas-humidity-and-the-f-1790708477602.html` | Blog | PASS |
| `/blog/solid-wood-or-veneer-how-to-tell-before-you-sand-1790434813632.html` | Blog | PASS |
| `/blog/another-satisfied-customer-1789685075176.html` | Blog | PASS |
| `/blog/chester-drawer-that-needed-new-life-1788487000828.html` | Blog | PASS |

## Every pre-rebuild URL

| Old URL or rule | Result | Note |
|---|---|---|
| `/` | PASS |  |
| `/apple-touch-icon.png` | PASS |  |
| `/blog/` | PASS |  |
| `/blog/another-satisfied-customer-1789685075176.html` | PASS |  |
| `/blog/chester-drawer-that-needed-new-life-1788487000828.html` | PASS |  |
| `/blog/how-to-clean-a-wood-table-without-damaging-the-finish-1791314134922.html` | PASS |  |
| `/blog/refinishing-vs-restoring-what-each-does-to-an-antique-s-valu-1790967226299.html` | PASS |  |
| `/blog/solid-wood-or-veneer-how-to-tell-before-you-sand-1790434813632.html` | PASS |  |
| `/blog/why-furniture-joints-loosen-in-east-texas-humidity-and-the-f-1790708477602.html` | PASS |  |
| `/custom-cabinets/` | PASS |  |
| `/custom-cabinets/arp-tx.html` | PASS | /custom-cabinets/arp-tx 301! kept |
| `/custom-cabinets/big-sandy-tx.html` | PASS | /custom-cabinets/big-sandy-tx 301! kept |
| `/custom-cabinets/gilmer-tx.html` | PASS | /custom-cabinets/gilmer-tx 301! kept |
| `/custom-cabinets/gladewater-tx.html` | PASS | /custom-cabinets/gladewater-tx 301! kept |
| `/custom-cabinets/hallsville-tx.html` | PASS | /custom-cabinets/hallsville-tx 301! kept |
| `/custom-cabinets/henderson-tx.html` | PASS | /custom-cabinets/henderson-tx 301! kept |
| `/custom-cabinets/kilgore-tx.html` | PASS | /custom-cabinets/kilgore-tx 301! kept |
| `/custom-cabinets/lindale-tx.html` | PASS | /custom-cabinets/lindale-tx 301! kept |
| `/custom-cabinets/longview-tx.html` | PASS | /custom-cabinets/longview-tx 301! kept |
| `/custom-cabinets/marshall-tx.html` | PASS | /custom-cabinets/marshall-tx 301! kept |
| `/custom-cabinets/new-london-tx.html` | PASS | /custom-cabinets/new-london-tx 301! kept |
| `/custom-cabinets/overton-tx.html` | PASS | /custom-cabinets/overton-tx 301! kept |
| `/custom-cabinets/troup-tx.html` | PASS | /custom-cabinets/troup-tx 301! kept |
| `/custom-cabinets/tyler-tx.html` | PASS | /custom-cabinets/tyler-tx 301! kept |
| `/custom-cabinets/white-oak-tx.html` | PASS | /custom-cabinets/white-oak-tx 301! kept |
| `/custom-furniture/` | PASS |  |
| `/custom-furniture/arp-tx.html` | PASS | /custom-furniture/arp-tx 301! kept |
| `/custom-furniture/big-sandy-tx.html` | PASS | /custom-furniture/big-sandy-tx 301! kept |
| `/custom-furniture/gilmer-tx.html` | PASS | /custom-furniture/gilmer-tx 301! kept |
| `/custom-furniture/gladewater-tx.html` | PASS | /custom-furniture/gladewater-tx 301! kept |
| `/custom-furniture/hallsville-tx.html` | PASS | /custom-furniture/hallsville-tx 301! kept |
| `/custom-furniture/henderson-tx.html` | PASS | /custom-furniture/henderson-tx 301! kept |
| `/custom-furniture/kilgore-tx.html` | PASS | /custom-furniture/kilgore-tx 301! kept |
| `/custom-furniture/lindale-tx.html` | PASS | /custom-furniture/lindale-tx 301! kept |
| `/custom-furniture/longview-tx.html` | PASS | /custom-furniture/longview-tx 301! kept |
| `/custom-furniture/marshall-tx.html` | PASS | /custom-furniture/marshall-tx 301! kept |
| `/custom-furniture/new-london-tx.html` | PASS | /custom-furniture/new-london-tx 301! kept |
| `/custom-furniture/overton-tx.html` | PASS | /custom-furniture/overton-tx 301! kept |
| `/custom-furniture/troup-tx.html` | PASS | /custom-furniture/troup-tx 301! kept |
| `/custom-furniture/tyler-tx.html` | PASS | /custom-furniture/tyler-tx 301! kept |
| `/custom-furniture/white-oak-tx.html` | PASS | /custom-furniture/white-oak-tx 301! kept |
| `/custom-signs/` | PASS |  |
| `/custom-signs/arp-tx.html` | PASS | /custom-signs/arp-tx 301! kept |
| `/custom-signs/big-sandy-tx.html` | PASS | /custom-signs/big-sandy-tx 301! kept |
| `/custom-signs/gilmer-tx.html` | PASS | /custom-signs/gilmer-tx 301! kept |
| `/custom-signs/gladewater-tx.html` | PASS | /custom-signs/gladewater-tx 301! kept |
| `/custom-signs/hallsville-tx.html` | PASS | /custom-signs/hallsville-tx 301! kept |
| `/custom-signs/henderson-tx.html` | PASS | /custom-signs/henderson-tx 301! kept |
| `/custom-signs/kilgore-tx.html` | PASS | /custom-signs/kilgore-tx 301! kept |
| `/custom-signs/lindale-tx.html` | PASS | /custom-signs/lindale-tx 301! kept |
| `/custom-signs/longview-tx.html` | PASS | /custom-signs/longview-tx 301! kept |
| `/custom-signs/marshall-tx.html` | PASS | /custom-signs/marshall-tx 301! kept |
| `/custom-signs/new-london-tx.html` | PASS | /custom-signs/new-london-tx 301! kept |
| `/custom-signs/overton-tx.html` | PASS | /custom-signs/overton-tx 301! kept |
| `/custom-signs/troup-tx.html` | PASS | /custom-signs/troup-tx 301! kept |
| `/custom-signs/tyler-tx.html` | PASS | /custom-signs/tyler-tx 301! kept |
| `/custom-signs/white-oak-tx.html` | PASS | /custom-signs/white-oak-tx 301! kept |
| `/favicon-32.png` | PASS |  |
| `/favicon.ico` | PASS |  |
| `/favicon.svg` | PASS |  |
| `/furniture-repair/` | PASS |  |
| `/furniture-repair/arp-tx.html` | PASS | /furniture-repair/arp-tx 301! kept |
| `/furniture-repair/big-sandy-tx.html` | PASS | /furniture-repair/big-sandy-tx 301! kept |
| `/furniture-repair/gilmer-tx.html` | PASS | /furniture-repair/gilmer-tx 301! kept |
| `/furniture-repair/gladewater-tx.html` | PASS | /furniture-repair/gladewater-tx 301! kept |
| `/furniture-repair/hallsville-tx.html` | PASS | /furniture-repair/hallsville-tx 301! kept |
| `/furniture-repair/henderson-tx.html` | PASS | /furniture-repair/henderson-tx 301! kept |
| `/furniture-repair/kilgore-tx.html` | PASS | /furniture-repair/kilgore-tx 301! kept |
| `/furniture-repair/lindale-tx.html` | PASS | /furniture-repair/lindale-tx 301! kept |
| `/furniture-repair/longview-tx.html` | PASS | /furniture-repair/longview-tx 301! kept |
| `/furniture-repair/marshall-tx.html` | PASS | /furniture-repair/marshall-tx 301! kept |
| `/furniture-repair/new-london-tx.html` | PASS | /furniture-repair/new-london-tx 301! kept |
| `/furniture-repair/overton-tx.html` | PASS | /furniture-repair/overton-tx 301! kept |
| `/furniture-repair/troup-tx.html` | PASS | /furniture-repair/troup-tx 301! kept |
| `/furniture-repair/tyler-tx.html` | PASS | /furniture-repair/tyler-tx 301! kept |
| `/furniture-repair/white-oak-tx.html` | PASS | /furniture-repair/white-oak-tx 301! kept |
| `/gallery/` | PASS |  |
| `/icon-192.png` | PASS |  |
| `/icon-512.png` | PASS |  |
| `/robots.txt` | PASS |  |
| `/shop-upload.html` | PASS |  |
| `/site.webmanifest` | PASS |  |
| `/sitemap.xml` | PASS |  |
| `/thanks.html` | PASS |  |
| `/write.html` | PASS |  |
| `/furniture-restoration/*` | PASS | Aug 17 rename 301 to /furniture-repair/:splat |
| `/furniture-restoration/` | PASS | Aug 17 rename 301 to /furniture-repair/ |
| `/cabinets-and-built-ins/*` | PASS | Aug 17 rename 301 to /custom-cabinets/:splat |
| `/cabinets-and-built-ins/` | PASS | Aug 17 rename 301 to /custom-cabinets/ |
