# grace-woodwork-site

Grace Woodwork, Kilgore TX: furniture repair and refinishing, custom furniture, cabinets, signs, porch
and deck repair. Live at https://gracewoodworkkilgore.com (Netlify publishes this folder as it is).

## Editing the site

The HTML at the root is built from `src/` and committed. Netlify does not run a build.

    pip install jinja2 pyyaml pillow openpyxl
    python3 build.py                 # rebuild every page, WebP sizes, sitemap, blog templates
    python3 scripts/check.py         # copy, SEO, links, images, form and tools checks
    python3 scripts/check_urls.py    # every pre-rebuild URL still works
    python3 scripts/check_town_text.py   # the 60 town pages kept their Sep 1 2026 words
    python3 scripts/similarity.py    # duplicate-content check (15% limit)
    python3 scripts/test_blog_writers.py # dry run of both blog writers

- Business facts, navigation, services and towns: `src/data/site.json`
- Pages: `src/pages/` (new and rewritten pages) and `src/towns/` (the 60 town pages)
- Layout and shared parts: `src/templates/`; styles and scripts: `src/static/`
- New photos: save them in `images/` under the names in `docs/image-list.md`, then run `build.py`

Blog posts are written straight onto main by `/write.html` (netlify/functions/blog-post.mjs) and the
twice-weekly robot (.github/scripts/grace_blog.py). Both use the page template build.py saves in
`netlify/blog-templates.*`, so rebuild after changing the header, footer or styles.

Notes from the Oct 9 2026 rebuild: SERVICES.md, docs/decisions.md, docs/qa.md, docs/fact-check.md,
docs/keyword-plan.md.
