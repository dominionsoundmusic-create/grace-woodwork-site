# Grace Woodwork (gracewoodworkkilgore.com): PLAYBOOK 2.0 REBUILD. INSTRUCTIONS FOR CLAUDE CODE

You are rebuilding a LIVE website for Grace Woodwork, an East Texas woodworking shop, for Maurice
Johnson by running Dominic & Dalton's Website Builder Prompt Playbook 2.0 (PLAYBOOK.md), Prompts 1
to 20, in full. The site ALREADY RANKS on Google, so the rebuild must not lose a single URL, and the
pages that rank must keep their words. Maurice: "This is a site the Lord told me to do." Build it to
the standard of the best paying client.

## RUN STRAIGHT THROUGH. DO NOT STOP.
Maurice is not watching this session and cannot approve anything. Do NOT pause at the end of each
playbook phase, do NOT ask "continue?", do NOT wait for input. Make reasonable decisions yourself,
write them down in docs/decisions.md, and keep going until Prompt 20 is finished and every check
below passes. The only reason to stop early is if something would require paying money, deploying,
changing Netlify settings, or changing a repository other than this one.

## Source files (read all of them first)
- INTAKE.md: the facts. It wins over anything else. UNKNOWN means leave it off the site.
- PLAYBOOK.md: the playbook (Operating Rules, then Prompts 1 to 20). It was written for GHL AI
  Studio; apply its rules and its 20 steps to this static site.
- keywords/Grace-Woodwork-Keywords.xlsx: Ubersuggest, United States, pulled Oct 9 2026. 6,039
  unique keywords, an ALL tab, a "FIT FOR GRACE 10+" tab, and a tab per seed. Column H "Fit for
  Grace" is a rough first sort (East Texas, Service, Question, DIY or product, Other place,
  Off-topic); correct it where it is wrong. Every keyword with 10+ searches that fits Grace must be
  assigned to a page as a target or supporting keyword, or listed in docs/keyword-plan.md as
  deliberately unused with a one-line reason. National volume (no town in the keyword) shows what
  people search for, not East Texas demand; say so in the plan.
- The current site in this repo (main branch). Read every page before writing.

## WHAT MUST NOT CHANGE (rankings and Grace's tools)
1. Every URL that exists now keeps working at the SAME address: index.html, the 4 hubs
   (/furniture-repair/, /custom-furniture/, /custom-cabinets/, /custom-signs/), all 60 town pages
   (/<service>/<town>-tx.html), /gallery/, /blog/ and every post in blog/, thanks.html,
   shop-upload.html, write.html, privacy or terms pages if present. List every current URL (file
   tree + sitemap.xml) before you start and check every one at the end with a script; record the
   result in docs/qa.md.
2. Keep _redirects exactly as it works now (the forced 301! rules from extensionless addresses to
   .html, and the four Aug 17 folder-rename 301s). Add rules only for new pages if needed.
3. The 60 town pages were hand-written on Sep 1 2026 and keep their BODY TEXT word for word. Change
   only the design around them (header, hero, layout, footer, image markup, internal links). Their
   titles and meta descriptions also stay, except you may improve a title or description where it
   is clearly weak; record each change in docs/decisions.md. The four New London pages stay plain.
4. Keep the canonical form (.html), the LocalBusiness schema facts, the hours, the phone, and the
   Search Console verification file or tag if one exists.
5. Grace's tools must keep working: /shop-upload.html and netlify/functions/shop-auth.mjs, /write.html
   and netlify/functions/blog-post.mjs, .github/workflows/grace-blog.yml and
   .github/scripts/grace_blog.py, and the Cloudinary gallery. Netlify publishes the REPO ROOT
   (publish ".", no build command) and that will NOT change. So the finished HTML must be committed
   at the same root paths it lives at now. If you add a build script (copy the build system from
   dominionsoundmusic-create/phoenix-pool-cleaning-pro branch `build`: build.py, scripts/check.py,
   scripts/similarity.py, templates, site.css, macros, WebP srcset, self-hosted fonts), make it
   write its output to the repo root, keep source files out of public view (or block them in
   _redirects), and make sure new blog posts written by the two blog writers still look right and
   appear in blog/index.html and sitemap.xml. If the blog writers' HTML template needs updating to
   match the new design, update blog-post.mjs and grace_blog.py carefully and test them locally
   with a dry run. Never break the password check.
6. The quote form keeps the same form name "quote", fields, honeypot, photo upload and thanks.html.

## Design (keep the colors, apply Maurice's standing rules)
- KEEP ALL COLORS, FONTS AND THE LOGO EXACTLY AS THEY ARE (see INTAKE.md).
- Header in the evergreen brand color with the EN/ES toggle on every page.
- Hero stretches edge to edge on every page: full-strength photo of Grace's own work, dark
  left-to-right fade behind the headline, call button visible above the fold (max-height about
  700px).
- Body text, photos and cards run FULL WIDTH: the same left and right edge as the header and color
  bands. Never a narrow center strip.
- Mostly WHITE sections with occasional bold bands in the brand colors. Never every section tinted.
- No white text or boxes on white. Every card, box and button has clear contrast.
- Speed: WebP 480/800/1200/1600/1920 srcset, preloaded hero with fetchpriority high, self-hosted
  woff2 fonts, lazy-loaded below-the-fold images.

## Pages to build: 16 NEW pages (Maurice approved this list on Oct 9 2026)
New service pages (10): cabinet painting (40,500/mo, SD 20); cabinet refacing (18,100, SD 13);
furniture refinishing (6,600, SD 31); antique furniture restoration (1,300, SD 23); chair caning and
chair repair (2,400, SD 31; "cane chair repair near me" 1,600, SD 11); custom dining tables (2,900,
SD 31); built-in shelves and bookshelves (4,400, SD 28); deck repair (9,900, SD 36; "deck repair
contractors" 2,900, SD 10); porch repair (880, SD 17); table refinishing (880, SD 32).
New guide pages (6): what cabinet painting costs (cabinet painting prices 1,600; how much paint
cabinets 720); what cabinet refacing or resurfacing is (880, SD 19); what furniture refinishing
costs (880, SD 25); fixing furniture veneer and when to call a pro (260, SD 15); how chair caning
is repaired (210, SD 17); what size dining table seats 8 (210, SD 22).
Pick clean folder URLs that fit the existing structure (record them in SERVICES.md). Link every
new page from the right hub, the homepage service groups, the nav where sensible, and the sitemap.
Also REWRITE BY HAND the 4 hub pages (/furniture-repair/, /custom-furniture/, /custom-cabinets/,
/custom-signs/), which are still templated, keeping their URLs. Write SERVICES.md (every page, URL,
target keyword, volume, SEO difficulty) and docs/keyword-plan.md BEFORE writing pages.

## Hard rules for every new or rewritten page
1. Written for its own keyword, for Kilgore and the surrounding East Texas towns, by a real shop
   that does the work. Researched on the web; cite sources on guide pages. If a fact cannot be
   verified, leave it out.
2. Never invent prices, warranties, guarantees, licenses, insurance, years in business, job counts,
   reviews, awards or team names. Cost guides use published, sourced ranges and say Grace Woodwork
   quotes each job after seeing it.
3. 3 to 6 FAQs per page written the way people ask (use the Question rows), shown on the page AND
   as FAQPage JSON-LD.
4. A full-width hero plus at least two in-body images, each with filename, alt, width, height and
   loading="lazy" (hero eager). Use Grace's own photos from images/ first. Any photo still needed
   goes in docs/image-list.md (File name, Size, Artistly prompt: bright, clearly visible, East Texas
   homes and shop work, no text, no logos, no recognizable faces, "wide cinematic landscape shot,
   subject positioned on right third of frame, well lit"; heroes 1920x1080, in-body 1200x800) and
   shows one of Grace's existing photos until it arrives. Never a broken image.
5. Safety: no instructions involving power tools, chemical strippers, or structural deck or porch
   repairs beyond safe homeowner checks; tell readers when to call.
6. No em dashes or en dashes in visible copy. No eyebrow labels. American spelling. Banned phrases:
   "your trusted partner", "one-stop solution", "look no further", "unmatched excellence",
   "we've got you covered", "free estimate", "best price", "cheapest", "#1", "top-rated",
   "licensed and insured", "guarantee".
7. Measure duplication: Jaccard similarity on 5-word shingles between every pair of new or
   rewritten pages, and each against the 60 town pages. Any pair above 15% gets rewritten. Record
   the numbers in docs/qa.md.
8. Mark every new or rewritten page with the HTML comment `dwdp:handwritten 2026-10-09` in the first
   4KB. The 60 town pages keep their existing marker.

## Before you finish (all must pass)
- Build (if you added a build script) and scripts/check.py: 0 errors.
- Every old URL resolves (script, result in docs/qa.md). The forced 301! redirects still fire.
- The quote form markup is unchanged in name, fields and encoding. shop-upload.html and write.html
  still load their scripts. A dry run of the blog writers produces a post that matches the new
  design and lands in blog/index.html and sitemap.xml.
- Grep the site for em/en dashes in visible text and the banned phrases. Fix every hit.
- No horizontal overflow at 1440, 1024, 768 and 390 px wide.
- Independent fact-check: start separate sub-agents that did not write the pages, have them check
  every factual claim and source on every new or rewritten page, and fix what they find. Record it
  in docs/fact-check.md. Never say "fact-checked" unless this was actually run.

## Git
- Work on the branch `build`. Commit as you go with clear messages.
- Before finishing, merge the latest origin/main into `build` (the blog robot adds posts to main
  twice a week) and make sure those posts come through in the new design.
- Push to origin `build` ONCE, at the very end.
- Do NOT merge to main, do NOT deploy, do NOT touch Netlify settings, do NOT pay for anything.

## Final report (Maurice reads on his phone, 5 lines max)
Pages (kept / new / rewritten), checks passed, duplication range, fact-check result, and how many
images still need Artistly.
