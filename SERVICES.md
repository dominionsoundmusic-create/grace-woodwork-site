# Grace Woodwork: pages, URLs and target keywords

Written Oct 9 2026 before any page copy, from docs/keyword-plan.md. Volumes are Ubersuggest United States
monthly searches (Oct 9 2026); SD is Ubersuggest SEO difficulty. National volume shows what people search for,
not East Texas demand (see the keyword plan).

URL rules: every existing URL stays exactly where it is. New service and guide pages sit in a folder under the
hub they belong to (`/custom-cabinets/cabinet-painting/`), so the breadcrumb, the hub and the URL all tell the
same story. Deck and porch repair have no hub, so they sit at the root. Folder URLs end in a slash and are served
from `index.html`; no `_redirects` rule is needed for them.

## Hubs (rewritten by hand, same URLs)

| Page | URL | Target keyword | Volume | SD |
|---|---|---|---:|---:|
| Furniture repair | `/furniture-repair/` | furniture repair (also "furniture repair near me" 18,100) | 9,900 | 27 |
| Custom furniture | `/custom-furniture/` | custom furniture | 12,100 | 32 |
| Custom cabinets | `/custom-cabinets/` | custom cabinets | 22,200 | 38 |
| Custom signs | `/custom-signs/` | custom wood signs | 5,400 | 32 |

## New service pages (10)

| Page | URL | Target keyword | Volume | SD | Hub |
|---|---|---|---:|---:|---|
| Cabinet painting | `/custom-cabinets/cabinet-painting/` | cabinet painting | 40,500 | 20 | Custom cabinets |
| Cabinet refacing | `/custom-cabinets/cabinet-refacing/` | cabinet refacing | 18,100 | 13 | Custom cabinets |
| Built-in shelves and bookshelves | `/custom-cabinets/built-in-shelves/` | built in shelves (also "built in bookshelves" 12,100, SD 47) | 4,400 | 28 | Custom cabinets |
| Furniture refinishing | `/furniture-repair/furniture-refinishing/` | furniture refinishing | 6,600 | 31 | Furniture repair |
| Antique furniture restoration | `/furniture-repair/antique-furniture-restoration/` | antique furniture restoration | 1,300 | 23 | Furniture repair |
| Chair caning and chair repair | `/furniture-repair/chair-caning-and-repair/` | chair caning (also "cane chair repair near me" 1,600, SD 11) | 2,400 | 31 | Furniture repair |
| Table refinishing | `/furniture-repair/table-refinishing/` | table refinishing | 880 | 32 | Furniture repair |
| Custom dining tables | `/custom-furniture/custom-dining-tables/` | custom dining table | 2,900 | 31 | Custom furniture |
| Deck repair | `/deck-repair/` | deck repair (also "deck repair contractors" 2,900, SD 10) | 9,900 | 36 | none (root) |
| Porch repair | `/porch-repair/` | porch repair | 880 | 17 | none (root) |

## New guide pages (6)

| Page | URL | Target keyword | Volume | SD | Hub |
|---|---|---|---:|---:|---|
| What cabinet painting costs | `/custom-cabinets/cabinet-painting-cost/` | cabinet painting prices (also "how much paint cabinets" 720) | 1,600 | 30 | Custom cabinets |
| What cabinet refacing is | `/custom-cabinets/what-is-cabinet-refacing/` | what is cabinet resurfacing | 880 | 19 | Custom cabinets |
| What furniture refinishing costs | `/furniture-repair/furniture-refinishing-cost/` | furniture refinishing cost | 880 | 25 | Furniture repair |
| Fixing furniture veneer | `/furniture-repair/furniture-veneer-repair/` | how to repair furniture veneer | 260 | 15 | Furniture repair |
| How chair caning is repaired | `/furniture-repair/how-chair-caning-is-repaired/` | how to repair chair caning | 210 | 17 | Furniture repair |
| What size dining table seats 8 | `/custom-furniture/dining-table-size-for-8/` | what size dining table seats 8 | 210 | 22 | Custom furniture |

## Pages kept (same URL, new design around them)

| Page | URL | Notes |
|---|---|---|
| Homepage | `/` | Rebuilt around the same facts and quote form; target "woodworking shop" (18,100, SD 27), which is mostly hobby searchers, so the page leads with the services instead |
| 60 town pages | `/<hub>/<town>-tx.html` | Sep 1 2026 body text kept word for word |
| Gallery | `/gallery/` | Same 36 photos plus the Cloudinary shop photos |
| Blog index and posts | `/blog/`, `/blog/*.html` | Same URLs; new design; written by write.html and the twice-weekly robot |
| Thank-you page | `/thanks.html` | Quote form target, noindex |
| Shop upload | `/shop-upload.html` | Grace's photo tool, unchanged |
| Blog writer | `/write.html` | Grace's blog tool, unchanged |

There are no privacy or terms pages on the current site, and none were approved, so none are added.

## Where each new page is linked from

- Its hub page (service cards and guide links), the homepage service groups, the header menu (services only),
  the footer, related links on sibling pages, and sitemap.xml.
- Deck and porch repair: homepage, header menu ("Porch & deck"), footer, each other, and the custom cabinets hub
  is not used for them.
