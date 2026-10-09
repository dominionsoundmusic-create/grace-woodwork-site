#!/usr/bin/env python3
"""Dry run of both blog writers, in a throwaway copy of the site (nothing in the repo changes).

1. The twice-weekly robot: .github/scripts/grace_blog.py --dry-run writes a canned post (no API call),
   rebuilds blog/index.html and sitemap.xml.
2. Grace's /write.html publisher: the same rendering code blog-post.mjs uses (netlify/blog-render.mjs)
   publishes a second post, exactly as the function would commit it.

Then checks that both posts use the site design (header, hero, footer, stylesheet), that both are
listed in the blog index and the sitemap, that every non-blog URL survived in the sitemap, that there
are no leftover %%TOKENS%%, and that blog-post.mjs still parses and still checks the password.

Usage: python3 scripts/test_blog_writers.py   (exit 1 on failure)
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NODE = r"""
import { postHtml, buildIndex, buildSitemap, titlesFromIndex } from '%(render)s';
import fs from 'node:fs';
const dir = %(dir)s;
const stamp = Date.now() + 5;
const title = 'Write page dry run — a test post from Grace';
const name = 'write-page-dry-run-a-test-post-from-grace-' + stamp + '.html';
const body = 'This is a dry run of the write page.\n\nIt checks the post matches the site.';
const html = postHtml({ title, body, photo: '', dateStr: 'October 9, 2026', name, stamp });
fs.writeFileSync(dir + '/blog/' + name, html);
const files = fs.readdirSync(dir + '/blog').filter(f => f.endsWith('.html') && f !== 'index.html')
  .sort((a, z) => parseInt((z.match(/-(\d{10,})\.html$/) || [0, 0])[1], 10) - parseInt((a.match(/-(\d{10,})\.html$/) || [0, 0])[1], 10));
const titles = titlesFromIndex(fs.readFileSync(dir + '/blog/index.html', 'utf8'));
titles[name] = 'Write page dry run, a test post from Grace';
fs.writeFileSync(dir + '/blog/index.html', buildIndex(files, titles));
fs.writeFileSync(dir + '/sitemap.xml', buildSitemap(fs.readFileSync(dir + '/sitemap.xml', 'utf8'), files));
console.log(name);
"""


def main():
    tmp = Path(tempfile.mkdtemp())
    errors = []
    try:
        for d in ("blog", "netlify", "images", ".github"):
            shutil.copytree(ROOT / d, tmp / d)
        shutil.copy2(ROOT / "sitemap.xml", tmp / "sitemap.xml")
        before = set(re.findall(r"<loc>(.*?)</loc>", (tmp / "sitemap.xml").read_text()))
        env = dict(os.environ, GRACE_BLOG_REPO=str(tmp))
        r = subprocess.run([sys.executable, str(tmp / ".github/scripts/grace_blog.py"), "--dry-run"], env=env,
                           capture_output=True, text=True)
        print(r.stdout.strip(), r.stderr.strip())
        robot = re.search(r"published: (\S+)", r.stdout)
        if not robot:
            errors.append("robot dry run did not publish")
        js = tmp / "publish.mjs"
        js.write_text(NODE % {"render": (tmp / "netlify" / "blog-render.mjs").as_posix(), "dir": repr(str(tmp))})
        r2 = subprocess.run(["node", str(js)], capture_output=True, text=True)
        if r2.returncode:
            errors.append("write-page dry run failed: " + r2.stderr[-400:])
        write = r2.stdout.strip()
        print("write page published:", write)
        index = (tmp / "blog" / "index.html").read_text()
        sitemap = (tmp / "sitemap.xml").read_text()
        after = set(re.findall(r"<loc>(.*?)</loc>", sitemap))
        lost = before - after
        if lost:
            errors.append(f"sitemap lost {len(lost)} URLs: {sorted(lost)[:3]}")
        for name in filter(None, [robot.group(1) if robot else "", write]):
            page = (tmp / "blog" / name).read_text()
            for need in ('<header class="site-header">', '<section class="hero', '<footer class="site-footer">',
                         '/assets/site.css', '<h1>', 'rel="canonical" href="https://gracewoodworkkilgore.com/blog/' + name,
                         '"@type":"BlogPosting"', 'class="topbar"', 'data-lang="es"'):
                if need not in page:
                    errors.append(f"{name}: missing {need}")
            if "%%" in page:
                errors.append(f"{name}: unfilled token")
            if "—" in re.sub(r"<script.*?</script>", "", page, flags=re.S) or "–" in page:
                errors.append(f"{name}: em or en dash in the page")
            if f'href="/blog/{name}"' not in index:
                errors.append(f"{name}: not in blog/index.html")
            if f"https://gracewoodworkkilgore.com/blog/{name}" not in sitemap:
                errors.append(f"{name}: not in sitemap.xml")
        if "%%" in index:
            errors.append("blog index: unfilled token")
        n_posts = len([p for p in (tmp / "blog").glob("*.html") if p.name != "index.html"])
        listed = len(re.findall(r'<li><a href="/blog/[^"]+\.html">', index))
        if listed != n_posts:
            errors.append(f"blog index lists {listed} posts, folder has {n_posts}")
        out = Path(os.environ.get("DRYRUN_OUT", "")) if os.environ.get("DRYRUN_OUT") else None
        if out:
            out.mkdir(parents=True, exist_ok=True)
            for name in filter(None, [robot.group(1) if robot else "", write, "index.html"]):
                shutil.copy2(tmp / "blog" / name, out / name)
        # the function itself: parses, imports the renderer, still checks the password before publishing
        fn = (ROOT / "netlify" / "functions" / "blog-post.mjs").read_text()
        r3 = subprocess.run(["node", "--check", str(ROOT / "netlify" / "functions" / "blog-post.mjs")], capture_output=True, text=True)
        if r3.returncode:
            errors.append("blog-post.mjs does not parse: " + r3.stderr[-300:])
        if fn.find("same(hash(") < 0 or fn.find("same(hash(") > fn.find("postHtml("):
            errors.append("blog-post.mjs: password check missing or after publishing")
    finally:
        shutil.rmtree(tmp)
    for e in errors:
        print("ERROR", e)
    print("blog writers dry run:", "PASS" if not errors else f"{len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
