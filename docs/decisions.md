# Decisions made during the Oct 9 2026 rebuild

Maurice was not available during the run, so every judgment call is written down here. Items marked
**Confirm** are things the new copy says that the current site already said but INTAKE.md does not
list; they were kept, and Maurice should confirm or strike them.

## Architecture

1. **Static build that writes to the repository root.** Netlify publishes the root (`publish = "."`, no
   build command) and that stays. `build.py` renders `src/` and writes the finished HTML to the same
   paths the site already used. The output is committed. `python3 build.py --check` proves the committed
   files match the sources (0 files would change at hand-off).
2. **Sources hidden.** `_redirects` gained forced 404s for `/src/*`, `/scripts/*`, `/docs/*`, `/keywords/*`,
   `/netlify/*`, `/.github/*`, `build.py` and the `.md` and config files. A `404.html` page was added for
   them (noindex). Every original rule in `_redirects` is untouched, above the new block.
3. **Folder URLs for new pages**, under the hub they belong to (`/custom-cabinets/cabinet-painting/`).
   Deck and porch repair have no hub, so they sit at the root. Guides sit under their hub as well, so no
   unapproved `/guides/` page was needed. List in SERVICES.md.
4. **Fonts self-hosted** (Zilla Slab 400/600/700, Karla and Roboto Mono variable, latin subset, SIL OFL)
   in `/fonts/`. The Google Fonts link is gone from every page.
5. **WebP sizes.** The build makes WebP copies at 480, 800, 1200, 1600 and 1920 px, but never wider than
   the original. Grace's photos are 1000 px (work photos) and 1680 px (hero photos), so those top out at
   1000 and 1680. Upscaling would add bytes and no detail. Artistly images at 1920x1080 will get the full set.
6. **EN/ES toggle.** The floating Google Translate bar (7 languages, fixed over the page) was replaced by
   an EN/ES switch in the evergreen header on every page. It sets the same Google Translate cookie and
   only loads Google's script when Spanish is chosen.
7. **Hours bar shown again.** It existed on every page but was hidden with `display:none`. INTAKE says
   keep it, so it is visible above the header: hours, Kilgore, the phone number.

## The 60 town pages

8. **Body text kept word for word.** `scripts/migrate_towns.py` moved each page's Sep 1 text into
   `src/towns/` from commit 6531506; `scripts/check_town_text.py` compares all 2,460 original text
   blocks with the rebuilt pages: 0 changed.
9. **What changed around the text:** header, hero (one of Grace's photos per service, full width), layout
   (heading left, text right), footer, image markup (WebP srcset, lazy), the FAQ grid became the FAQ band
   (same questions and answers, same heading), the town list became link pills, and a "More from the
   shop" row links each page to its hub's new service pages.
10. **The "Kilgore, Texas" label above each H1 was removed.** It was an eyebrow label, which the
    playbook does not allow. It is a place name, not body text.
11. **Em and en dashes became commas** (308 in the text of the 60 pages, plus their titles and descriptions).
    Punctuation only; no word was added or removed. CLAUDE.md asks for every visible dash to be fixed and
    for the town words to stay, and this satisfies both.
12. **Words kept even where they trip a rule.** Four town-page sentences use "cheapest" (custom signs,
    Lindale and White Oak: "the cheapest thing that makes a frontage look like somebody's"), one uses
    "warranty" (Hallsville furniture repair: "built by somebody who was not thinking about a warranty"),
    and some use British spellings ("remodellers", "per cent", "grey" in alt text). None is a price or
    warranty claim. The word-for-word rule wins; `scripts/check.py` reports these as warnings, not errors.
13. **Titles and descriptions:** only the dashes changed. None was clearly weak enough to rewrite.
14. **New London fixes.** Its FAQ JSON-LD listed one question that was not on the page while the page
    showed four; the JSON-LD is now built from the visible four on every town page. Its "Kilgore" town
    link pointed back at New London; the generated pills fix that. The New London pages stay plain: no
    words were added to them.

## Hubs and homepage

15. **Hub titles and descriptions were rewritten** with the hubs (they were templated):
    - `/furniture-repair/`: "Furniture Repair in East Texas | Grace Woodwork" to "Furniture Repair and
      Restoration in Kilgore, TX | Grace Woodwork"
    - `/custom-furniture/`: "Custom Furniture in East Texas" to "Custom Furniture Built in Kilgore, TX"
    - `/custom-cabinets/`: "Custom Cabinets in East Texas" to "Custom Cabinets and Built-Ins in Kilgore, TX"
    - `/custom-signs/`: "Custom Signs & Frames in East Texas" to "Custom Wood Signs and Frames in Kilgore, TX"
    - Homepage: "Grace Woodwork — Furniture Repair & Custom Woodwork | Kilgore, TX" to "Grace Woodwork |
      Furniture Repair and Custom Woodwork in Kilgore, TX" (dash removed, same words)
    - Gallery: dash removed, "Gallery: Furniture Repair and Custom Woodwork | Grace Woodwork Kilgore"
16. **"Free estimates on restoration" and "Free estimate before any work starts" were removed** from the
    homepage. INTAKE does not confirm free estimates and the phrase is banned. The list item now reads
    "A price before any work starts", which the town pages already promise.
17. **The homepage is treated as rewritten** (new service groups, FAQs, marker). Its facts, photos, video
    reels, quote form and proof strip are the same.
18. **The Cloudinary shop photos now actually appear.** The old homepage script looked for `#shots`,
    which no page had, so Grace's uploads never showed. The script now runs on `/gallery/` against a real
    `#shots` grid, newest first, with the 36 built-in photos underneath. `shop-upload.html` is unchanged.
19. **Thank-you page:** "usually within a day" was dropped (a response time INTAKE does not confirm).

## Quote form

20. Same form name, method, action, `data-netlify`, honeypot, multipart encoding and every input, select
    and textarea tag (checked against commit 6531506 by `scripts/check.py`). One option's visible text had
    an em dash ("Repair — joints, veneer, legs or hardware"); it now shows "Repair: joints, veneer, legs or
    hardware" with `value="Repair — joints, veneer, legs or hardware"`, so the submitted value is identical.

## Blog writers

21. **One template for all blog pages.** `build.py` renders the post and index pages from the site's own
    header, footer and styles with `%%TOKENS%%`, and saves them as `netlify/blog-templates.json` (read by
    `grace_blog.py`) and `netlify/blog-templates.mjs` (bundled into `blog-post.mjs` through
    `netlify/blog-render.mjs`, which sits outside `netlify/functions/` so Netlify does not treat it as a
    function). `build.py` re-renders every existing post through `grace_blog.render_post`, so old and new
    posts match. The password check in `blog-post.mjs` and `shop-auth.mjs` is untouched.
22. **Write page index titles.** `blog-post.mjs` used to rebuild the blog index with titles guessed from
    file names. It now reads the real titles from the current index (one extra GitHub request) and falls
    back to the file name.
23. **No dashes in future posts.** Both writers turn em and en dashes into commas, and the robot's prompt
    now asks for none.
24. **After this branch is merged:** if the robot posts on main before the merge, those posts use the old
    plain template until `python3 build.py` is run once and committed. It re-renders them in place.
    Expect merge conflicts only in `blog/index.html` and `sitemap.xml`; take main's posts and rebuild.

## Content

25. **Process claims kept because the current site already makes them** (**Confirm**): a price before
    work starts; pickup and delivery across East Texas; photos sent as a piece comes along; long tables
    built to come apart for old doorways; cabinets measured in person and installed.
26. **Services described as "not on our list of services"**: upholstery, leather and recliner mechanisms,
    and on-site (in-home) furniture repair. INTAKE does not list them. Rush, Danish cord and splint seats
    are described, with "send a photo and we will tell you whether we can take it on" (INTAKE lists chair
    caning only). **Confirm.**
27. **Woods offered** are described only as pine and harder woods such as oak, the two the site's
    photos show. Maple, walnut and cherry were taken out after the fact-check.
28. **Lead paint.** The cabinet painting page tells owners of pre-1978 homes that EPA rules cover paid work
    that disturbs old paint and asks them to say when the house was built. It does not claim Grace is
    EPA lead-safe certified (unknown).
29. **No privacy or terms pages** were added: none existed and none was approved.
30. **Homepage target keyword** is "woodworking shop" (18,100), which is mostly hobbyists, so the page
    leads with services and lets the service pages carry the buying keywords.
31. **Hero photos.** Every page has a full-width hero from Grace's own photos. New pages name a planned
    Artistly photo (docs/image-list.md, 30 images) and show one of Grace's photos until it arrives. A stand-in
    photo never carries the planned photo's caption.

## Research method (read with docs/fact-check.md)

32. Web pages could not be opened directly from this environment (WebFetch failed on DNS for every
    domain). Research and fact-check agents used web search restricted to each source's own domain and
    read the search excerpts. Figures that could not be confirmed that way were removed or reworded.

## Grace's tools

33. `shop-upload.html` and `write.html` keep their markup, scripts and endpoints. Only visible dashes were
    changed to commas (9 in total, two of them in the page titles), and their hidden hours bar now reads
    "Monday to Friday, 9am to 5pm". Their inline scripts were syntax-checked with Node after the edit.
