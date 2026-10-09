CLIENT WEBSITE QUESTIONNAIRE: GRACE WOODWORK (gracewoodworkkilgore.com)

Filled in Oct 9 2026 from what Maurice Johnson has stated. This is the factual source of truth for
the Playbook 2.0 rebuild. Anything marked UNKNOWN stays off the site. Never fill a gap by guessing.

1. BUSINESS BASICS
OFFICIAL BUSINESS NAME: Grace Woodwork
TAGLINE: "Giving old wood new life"
PRIMARY CITY: Kilgore
STATE: Texas
FULL BUSINESS ADDRESS: UNKNOWN. Do not display a street address.
PHONE: 903-445-7477 / tel:+19034457477. Facebook Messenger is the other contact route
  (m.me/100057624850623). Facebook page: https://www.facebook.com/profile.php?id=100057624850623
PUBLIC EMAIL: do not display. The quote form already emails the owner.
OWNER: Mr. McCarty. "Grace" is the business name only; never call the owner Grace. Do not name the
  owner on the site unless the current site already does.
HOURS: Monday to Friday, 9am to 5pm.
TEAM: three or four people work there. NOT a one-man shop. Do not invent names.
REACH: has driven as far as Lufkin (about two hours) for a job.
REVIEWS: 13 Facebook recommendations, 100% recommend. Mention only as "100% recommend on Facebook
  from 13 reviews" with a link to the Facebook page. No Google reviews exist. Invent nothing.
SIGNS: signs are also sold under the name "Stella Grace" (the current site says so; keep it as is).

WHAT THE BUSINESS ACTUALLY IS:
A real East Texas woodworking shop that does the work itself (unlike Maurice's referral-line
sites, "we" language is correct here). Services Maurice confirmed on Oct 9 2026:
- Furniture repair, furniture refinishing, antique furniture restoration, table refinishing
- Chair repair and chair caning
- Custom furniture, custom dining tables
- Custom cabinets and kitchen cabinetry, cabinet painting, cabinet refacing, built-in shelves and
  bookshelves
- Custom wood signs and custom frames
- Porch repair and deck repair
Do NOT invent licenses, insurance, warranties, guarantees, prices, years in business, job counts,
awards or certifications. Prices in cost guides must be published, sourced ranges and say real
quotes vary and Grace Woodwork quotes each job after seeing it.

2. SERVICE AREA (keep exactly these 15 towns; do not add more town pages)
Kilgore, Longview, White Oak, Gladewater, Overton, Troup, Henderson, Tyler, Marshall, Lindale,
Big Sandy, Gilmer, Arp, New London, Hallsville.
NEW LONDON: those town pages are deliberately plain. Never use the 1937 school explosion as a
marketing hook. Leave those pages' words as they are.

3. BRANDING (KEEP EVERYTHING THE SAME)
COLORS: keep the current palette exactly: evergreen header #13261E with the brass accent #C79045
  and the related tones already in the site's CSS (#0B1812, #213d2f, #1c3529, #d9a457, #8F621E,
  #4a5a50). Do not introduce new brand colors. Body sections stay WHITE with occasional bold color
  bands in these colors. No pale off-white tints for whole sections.
FONTS: keep Zilla Slab, Karla and Roboto Mono (self-host them as woff2 for speed).
LOGO: keep the existing logo images and favicons exactly.
SIGNATURE DEVICE: the carpenter's-rule tick marks; keep them.
STYLE: full-width hero edge to edge with a dark fade behind the headline; body text, photos and
  cards run full width (same left and right edge as the header and color bands), never a narrow
  center strip. No white on white. No em dashes or en dashes in visible copy. American spelling.
TOP BAR: keep the existing slim hours bar (Mon to Fri 9am to 5pm, Kilgore, the phone number).
  This is a client site: do NOT add the John 3:16 / Jesse Duplantis line used on Dominion pages.
LANGUAGE: EN / ES toggle in the header on every page (the site already has one; keep it working).
FOOTER: keep the current footer content and the "Designed by Dominion Web Design Pro" credit if
  present.

4. CALLS TO ACTION
MAIN: call 903-445-7477. SECOND: the existing quote form (name, phone, email, service, photo upload,
message) on Netlify Forms, posting to thanks.html. Keep the form exactly working: same form name
"quote", same fields, same honeypot, same multipart encoding.

5. GRACE'S OWN TOOLS (MUST KEEP WORKING, DO NOT BREAK)
- /shop-upload.html: password-protected photo upload to Cloudinary (netlify/functions/shop-auth.mjs)
- /write.html: password-protected blog writing; netlify/functions/blog-post.mjs commits the post to
  blog/<slug>-<timestamp>.html plus a rebuilt blog/index.html and sitemap.xml in ONE commit on main
- .github/workflows/grace-blog.yml + .github/scripts/grace_blog.py: automatic posts twice a week
  (Tue and Fri), writing to blog/ and sitemap.xml on main
- The gallery prepends Cloudinary photos (tag grace-shop) to the hard-coded repo photos
These three writers commit straight to main at the repo root paths above. Netlify publishes the
repo root (publish ".", no build command) and Maurice will NOT change Netlify settings.

6. WEBSITE
DOMAIN: https://gracewoodworkkilgore.com (live on Netlify project grace-woodwork, production
  branch main). Search Console verified. It already ranks: "wooden furniture repair near me" around
  position 2.5, /custom-signs/hallsville-tx.html around position 2.3.
URL FORM: every page lives at its .html address; _redirects holds forced 301! rules from the
  extensionless forms (Netlify Pretty URLs is on). Keep that system exactly.
PHOTOS: 36+ of Grace's own work photos in images/ (work-01 to work-36 and others). Reuse them
  first. Any new photo needed goes in docs/image-list.md with an Artistly prompt.
