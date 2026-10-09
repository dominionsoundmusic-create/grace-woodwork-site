# Playbook 2.0, Prompts 1 to 3: fact brief, architecture, baseline

Run Oct 9 2026 on branch `build` from commit 6531506. Source of truth: INTAKE.md.

## Prompt 1: client fact brief

| Item | Value | Status |
|---|---|---|
| Business name | Grace Woodwork | Confirmed |
| Tagline | "Giving old wood new life" | Confirmed |
| Category | Woodworking shop: furniture repair and refinishing, custom furniture, cabinets, signs, porch and deck repair | Confirmed |
| Services | Furniture repair, furniture refinishing, antique furniture restoration, table refinishing, chair repair and caning, custom furniture, custom dining tables, custom cabinets and kitchen cabinetry, cabinet painting, cabinet refacing, built-in shelves and bookshelves, custom wood signs and frames (also sold as Stella Grace), porch repair, deck repair | Confirmed Oct 9 2026 |
| Service area | Kilgore, Longview, White Oak, Gladewater, Overton, Troup, Henderson, Tyler, Marshall, Lindale, Big Sandy, Gilmer, Arp, New London, Hallsville. Has driven as far as Lufkin | Confirmed; no new towns |
| Address | Not displayed (city only: Kilgore, TX) | Confirmed: do not display |
| Phone | 903-445-7477, tel:+19034457477 | Confirmed |
| Other contact | Facebook Messenger m.me/100057624850623; Facebook page profile.php?id=100057624850623 | Confirmed |
| Email | Not displayed | Confirmed: do not display |
| Hours | Monday to Friday, 9am to 5pm | Confirmed |
| Owner | Mr. McCarty; not named on site (current site does not name him) | Confirmed: do not name |
| Team | Three or four people; no names | Confirmed: no names |
| Reviews | "100% recommend on Facebook from 13 reviews", linked to the Facebook page | Confirmed; no Google reviews |
| Primary CTA | Call 903-445-7477 | Confirmed |
| Secondary CTA | Quote form (name, phone, email, service, photo, message), Netlify form "quote" to /thanks.html | Confirmed, must not change |
| Colors | #13261E evergreen, #C79045 brass, #0B1812, #213d2f, #1c3529, #d9a457, #8F621E, #4a5a50 | Confirmed |
| Fonts | Zilla Slab, Karla, Roboto Mono (now self-hosted woff2) | Confirmed |
| Logo | images/logo.jpg, images/logo-full.jpg, favicons | Confirmed, unchanged |
| Signature device | Carpenter's-rule tick marks | Confirmed, kept |
| Domain | https://gracewoodworkkilgore.com, canonical form `.html` for flat pages | Confirmed |
| Search Console | Verified per INTAKE; no verification file or meta tag exists in the repo (likely DNS), so nothing to keep | Confirmed by search |
| Photos | 36 work photos, 7 hero photos, shop photo, logo files in images/ | Confirmed |
| Analytics | None found in the current site | Missing but deferrable |
| Licenses, insurance, warranties, prices, years in business, awards | UNKNOWN | Must stay off the site |
| Privacy policy, terms | Not on the current site, not approved | Deferred |

Contradictions found and how they were handled (details in docs/decisions.md):

- The current homepage says "Free estimates on restoration" and "Free estimate before any work starts". INTAKE
  does not confirm free estimates and CLAUDE.md bans the phrase, so both were removed.
- The hours bar exists on every page but is hidden with `display:none`. INTAKE says keep it, so it is shown again.
- The homepage's Cloudinary script looks for `#shots`, which no page has, so new shop photos never appeared.
  The script now runs on the gallery page against a real `#shots` grid.
- The New London furniture repair page's FAQPage JSON-LD lists one question that is not on the page, while the
  page shows four. The JSON-LD now matches the visible four. Its "Kilgore" town link pointed at itself; fixed.

Launch blockers: none. Missing but deferrable: about 30 photos of work Grace has not photographed yet (decks,
porches, caning, painted kitchens), listed in docs/image-list.md with Artistly prompts.

## Prompt 2: architecture

This is not the GHL AI Studio SSR template the playbook was written for. It is a static site published by
Netlify from the repository root (`publish = "."`, no build command), with Netlify Pretty URLs on, two Netlify
functions (`shop-auth.mjs`, `blog-post.mjs`) and one GitHub Actions workflow (`grace-blog.yml`). There is no
framework, router or hydration: every page is complete HTML, so "raw server HTML" is simply the file.

The playbook's SSR steps were applied as their static-site equivalents: every title, description, canonical,
Open Graph tag, JSON-LD block, H1 and body copy is in the committed HTML; the quote form is plain HTML that
renders on first load; nothing important depends on JavaScript.

Build system added (copied in shape from phoenix-pool-cleaning-pro `build`): `build.py` renders Jinja templates
in `src/` and writes finished HTML to the same root paths the site already uses, so Netlify settings do not
change. `scripts/check.py`, `scripts/similarity.py`, `scripts/check_urls.py` and `scripts/check_town_text.py`
verify the output. Source folders are blocked from public view in `_redirects`.

## Prompt 3: baseline

- URL inventory: 85 public URLs (file tree plus sitemap.xml's 73 entries), saved in docs/url-inventory.txt.
- Pre-existing problems recorded before any change: hidden hours bar; banned "free estimate" copy; Cloudinary
  gallery script pointing at a missing element; em and en dashes across the site, including inside the 60 town
  pages; New London FAQ JSON-LD mismatch and self-link; no Open Graph image on any page; Google Fonts loaded from
  Google; no hero image on hubs or town pages.
- Route matrix and plan: SERVICES.md lists every route, its type and its nav and sitemap status. All indexable
  routes go in sitemap.xml; thanks.html, shop-upload.html, write.html and 404.html are noindex and left out.
