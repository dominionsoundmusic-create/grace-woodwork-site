#!/usr/bin/env python3
"""Build gracewoodworkkilgore.com.

Netlify publishes the repository root as it is (publish ".", no build command), so this script writes
the finished HTML straight to the same root paths the live site already uses: /index.html,
/furniture-repair/kilgore-tx.html, /custom-cabinets/cabinet-painting/index.html and so on. Run it
locally and commit the output. It never deletes anything at the root.

Sources (blocked from public view in _redirects):
  src/data/site.json        business facts, navigation, services, guides, towns
  src/pages/**.html         pages with a YAML front matter block (url, title, description, hero, faqs...)
  src/towns/<hub>/*.html    the 60 town pages: their Sep 1 2026 body text, unchanged, plus front matter
  src/templates/            Jinja layouts, partials and macros
  src/static/               site.css and site.js, copied to /assets/

Blog posts are written by two robots straight onto main (netlify/functions/blog-post.mjs from
/write.html, and .github/scripts/grace_blog.py twice a week). Both fill in the same page template,
which this build renders from the site's own header and footer and saves as
netlify/blog-templates.json (read by grace_blog.py) and netlify/blog-templates.mjs (bundled into
blog-post.mjs). The build also re-renders every existing post with that template through
grace_blog.render_post, so old and new posts look the same.

Usage:
  python3 build.py            build everything, write docs/image-list.md
  python3 build.py --check    build into a temp folder and report what would change (nothing written)
"""
import argparse
import hashlib
import html
import importlib.util
import json
import re
import shutil
import struct
import sys
import tempfile
from pathlib import Path

import yaml
from jinja2 import ChainableUndefined, Environment, FileSystemLoader, pass_context
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
IMAGES = ROOT / "images"
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
BUILD_DATE = "2026-10-09"
OG_DEFAULT = "hero-2.jpg"
HANDWRITTEN = "dwdp:handwritten 2026-10-09"


def image_size(path):
    """(width, height) of a JPEG, PNG or WebP file, or None."""
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        if data[12:16] == b"VP8X":
            return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
        if data[12:16] == b"VP8 ":
            w, h = struct.unpack("<HH", data[26:30])
            return w & 0x3FFF, h & 0x3FFF
        return None
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            marker = data[i + 1]
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + length
    return None


def strip_tags(text):
    return html.unescape(re.sub(r"<[^>]+>", "", str(text))).strip()


def out_path_for(url, out):
    if url.endswith(".html"):
        return out / url.lstrip("/")
    return out / url.strip("/") / "index.html" if url != "/" else out / "index.html"


TABLE_RE = re.compile(r"<table>(.*?)</table>", re.S)
CELL_RE = re.compile(r"<(th|td)\b([^>]*)>", re.S)


def label_table_cells(html_text):
    """Give each body cell a data-label with its column heading, so CSS can stack the rows as
    cards on phones instead of scrolling sideways."""
    def one(m):
        body = m.group(1)
        head = re.search(r"<thead>(.*?)</thead>", body, re.S)
        if not head:
            return m.group(0)
        labels = [strip_tags(h) for h in re.findall(r"<th\b[^>]*>(.*?)</th>", head.group(1), re.S)]

        def row(rm):
            i = [0]

            def cell(cm):
                n = i[0]
                i[0] += 1
                if n < len(labels) and labels[n]:
                    return f'<{cm.group(1)}{cm.group(2)} data-label="{html.escape(labels[n], quote=True)}">'
                return cm.group(0)
            return CELL_RE.sub(cell, rm.group(0))
        tbody = re.sub(r"<tr\b.*?</tr>", row, body[head.end():], flags=re.S)
        return '<table class="stack">' + body[:head.end()] + tbody + "</table>"
    return TABLE_RE.sub(one, html_text)


def load_grace_blog():
    spec = importlib.util.spec_from_file_location("grace_blog", ROOT / ".github" / "scripts" / "grace_blog.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Builder:
    WEBP_WIDTHS = (480, 800, 1200, 1600, 1920)
    WEBP_QUALITY = 74

    def __init__(self, out, write_docs=True):
        self.out = out
        self.write_docs = write_docs
        self.site = json.loads((SRC / "data" / "site.json").read_text())
        self.missing_images = {}
        self._srcset = {}
        self.written = []
        self.svc_index = {s["slug"]: s for s in self.site["services"] + self.site["guides"]}
        css = (SRC / "static" / "site.css").read_bytes()
        js = (SRC / "static" / "site.js").read_bytes()
        self.asset_version = hashlib.sha1(css + js).hexdigest()[:8]
        self.env = Environment(loader=FileSystemLoader([str(SRC / "templates"), str(SRC / "pages"), str(SRC / "towns")]),
                               undefined=ChainableUndefined, autoescape=False, trim_blocks=True, lstrip_blocks=True)
        self.env.globals.update(site=self.site, img=self.img, picture=self.picture, picture_deferred=self.picture_deferred,
                                webp_srcset=self.webp_srcset, asset_version=self.asset_version,
                                svc=lambda slug: self.svc_index[slug], image_exists=lambda f: bool(f) and (IMAGES / f).exists(),
                                img_size=lambda f: image_size(IMAGES / f) or (1200, 800))
        self.env.filters["svc_by_slug"] = lambda slug: self.svc_index[slug]
        self.env.filters["tojson_ld"] = lambda v: Markup(json.dumps(v, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))

    # ---- files -------------------------------------------------------------------------------
    def write(self, rel, text):
        dest = self.out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            dest.write_bytes(text)
        else:
            dest.write_text(text)
        self.written.append(rel)

    # ---- images --------------------------------------------------------------------------------
    def webp_srcset(self, file):
        """WebP copies of a photo at 480/800/1200/1600/1920 px (never wider than the original), saved
        next to it in /images/. Returns the srcset string, or '' for anything that is not a photo."""
        if not file or not file.lower().endswith((".jpg", ".jpeg", ".png")) or file.startswith("http"):
            return ""
        src = IMAGES / file
        if not src.exists():
            return ""
        if file in self._srcset:
            return self._srcset[file]
        from PIL import Image
        full_w = image_size(src)[0]
        widths = sorted({w for w in self.WEBP_WIDTHS if w < full_w} | {full_w})
        stem = Path(file).stem
        parts, im = [], None
        for w in widths:
            name = f"{stem}-{w}.webp"
            dest = IMAGES / name
            if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
                if im is None:
                    im = Image.open(src).convert("RGB")
                h = round(im.height * w / im.width)
                (im if w == im.width else im.resize((w, h), Image.LANCZOS)).save(dest, "WEBP", quality=self.WEBP_QUALITY, method=6)
            if self.out != ROOT:
                (self.out / "images").mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, self.out / "images" / name)
            parts.append(f"/images/{name} {w}w")
        self._srcset[file] = ", ".join(parts)
        return self._srcset[file]

    def picture(self, file, alt, width, height, sizes, extra=""):
        img = f'<img src="/images/{file}" alt="{html.escape(alt, quote=True)}" width="{width}" height="{height}"{extra}>'
        srcset = self.webp_srcset(file)
        if not srcset:
            return Markup(img)
        return Markup(f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">{img}</picture>')

    def picture_deferred(self, file, alt, width, height, sizes, extra=""):
        """A hero slide that loads after the page: site.js swaps data-src/data-srcset in."""
        srcset = self.webp_srcset(file)
        img = (f'<img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" data-src="/images/{file}" '
               f'alt="{html.escape(alt, quote=True)}" width="{width}" height="{height}"{extra}>')
        if not srcset:
            return Markup(img)
        return Markup(f'<picture><source type="image/webp" data-srcset="{srcset}" sizes="{sizes}">{img}</picture>')

    @pass_context
    def img(self, ctx, file, alt, width=1200, height=800, desc="", caption="", fallback="", fallback_alt="",
            cls="", sizes="(max-width: 900px) 100vw, 50vw"):
        """An in-body figure. A planned photo that does not exist yet is listed in docs/image-list.md,
        kept in the page as a comment, and one of Grace's own photos (`fallback`) is shown instead."""
        page = ctx.get("page", {})
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        cls_attr = f' class="fig {cls}"' if cls else ' class="fig"'
        lazy = ' loading="lazy" decoding="async"'
        if (IMAGES / file).exists():
            w, h = image_size(IMAGES / file)
            return Markup(f"<figure{cls_attr}>{self.picture(file, alt, w, h, sizes, lazy)}{cap}</figure>")
        self.note_missing(file, width, height, alt, desc, page.get("url", "?"))
        comment = (f'<!-- image pending (see docs/image-list.md): <img src="/images/{file}" '
                   f'alt="{html.escape(alt, quote=True)}" width="{width}" height="{height}" loading="lazy"> -->')
        if fallback and (IMAGES / fallback).exists():
            w, h = image_size(IMAGES / fallback)
            return Markup(f"{comment}<figure{cls_attr}>{self.picture(fallback, fallback_alt or alt, w, h, sizes, lazy)}{cap}</figure>")
        raise ValueError(f"{page.get('url')}: planned image {file} has no existing fallback photo")

    def note_missing(self, file, width, height, alt, desc, url):
        e = self.missing_images.setdefault(file, {"file": file, "size": f"{width}x{height}", "alt": alt, "desc": desc, "pages": []})
        if url not in e["pages"]:
            e["pages"].append(url)
        if desc and not e["desc"]:
            e["desc"] = desc

    # ---- pages ---------------------------------------------------------------------------------
    def load_pages(self):
        pages = []
        for base in (SRC / "pages", SRC / "towns"):
            for path in sorted(base.rglob("*.html")):
                rel = path.relative_to(base)
                if rel.name.startswith("_"):
                    continue
                text = path.read_text()
                m = FM_RE.match(text)
                if not m:
                    raise SystemExit(f"{path}: missing front matter")
                meta = yaml.safe_load(m.group(1)) or {}
                if "url" not in meta:
                    raise SystemExit(f"{path}: front matter needs url")
                meta["source"] = str(path.relative_to(ROOT))
                meta["body"] = text[m.end():]
                if base.name == "towns":
                    meta.setdefault("type", "town")
                    meta.setdefault("layout", "town")
                pages.append(meta)
        return pages

    def prepare_hero(self, page):
        hero = page.get("hero")
        if not hero:
            return
        if hero.get("slides"):
            for s in hero["slides"]:
                s["w"], s["h"] = image_size(IMAGES / s["file"])
            hero["render_image"] = hero["slides"][0]["file"]
            return
        want = hero.get("image")
        if want and not (IMAGES / want).exists():
            self.note_missing(want, 1920, 1080, hero.get("alt", ""), hero.get("desc", ""), page["url"])
            fb = hero.get("fallback")
            if not fb or not (IMAGES / fb).exists():
                raise ValueError(f"{page['url']}: planned hero {want} has no existing fallback photo")
            hero["render_image"], hero["render_alt"] = fb, hero.get("fallback_alt", hero.get("alt", ""))
        else:
            hero["render_image"], hero["render_alt"] = want, hero.get("alt", "")
        hero["w"], hero["h"] = image_size(IMAGES / hero["render_image"])

    def render(self, page, pages):
        self.prepare_hero(page)
        page.setdefault("breadcrumbs", self.breadcrumbs(page))
        img = ((page.get("hero") or {}).get("render_image")) or OG_DEFAULT
        page["og_image"] = self.site["business"]["origin"] + "/images/" + img
        if page.get("type") not in ("town",) and not page.get("marker_none"):
            page.setdefault("marker", HANDWRITTEN if page.get("handwritten", True) else "")
        page["jsonld"] = self.jsonld(page)
        layout = page.get("layout", "page")
        source = '{% extends "layouts/' + layout + '.html" %}\n{% import "macros.html" as m with context %}\n' + page["body"]
        return label_table_cells(self.env.from_string(source).render(page=page, pages=pages))

    def breadcrumbs(self, page):
        url = page["url"]
        if url == "/" or page.get("noindex"):
            return []
        crumbs = [{"label": "Home", "href": "/"}]
        hub = page.get("hub")
        if hub:
            h = next(x for x in self.site["hubs"] if x["slug"] == hub)
            crumbs.append({"label": h["name"], "href": h["url"]})
        if page.get("type") == "post":
            crumbs.append({"label": "Blog", "href": "/blog/"})
        crumbs.append({"label": page.get("crumb", page.get("h1", page["title"])), "href": url})
        return crumbs

    def business(self):
        b = self.site["business"]
        o = b["origin"]
        return {
            "@type": "LocalBusiness", "@id": o + "/#business", "name": b["name"], "url": o + "/",
            "slogan": b["tagline"], "description": b["description"],
            "logo": o + b["logo"], "image": o + b["logo_full"],
            "telephone": "+1-903-445-7477",
            "address": {"@type": "PostalAddress", "addressLocality": "Kilgore", "addressRegion": "TX", "addressCountry": "US"},
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                           "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                                           "opens": "09:00", "closes": "17:00"}],
            "areaServed": [{"@type": "City", "name": t["name"] + ", TX"} for t in self.site["towns"]],
            "sameAs": [b["facebook"]],
        }

    def jsonld(self, page):
        o = self.site["business"]["origin"]
        url = o + page["url"]
        biz = self.business()
        graph = [biz]
        if page["url"] == "/":
            graph.append({"@type": "WebSite", "@id": o + "/#website", "url": o + "/", "name": biz["name"],
                          "publisher": {"@id": biz["@id"]}, "inLanguage": "en-US"})
        if page.get("noindex"):
            return {"@context": "https://schema.org", "@graph": graph}
        image = page["og_image"]
        webpage = {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": page["title"],
                   "description": page["description"], "isPartOf": {"@id": o + "/#website"},
                   "about": {"@id": biz["@id"]}, "primaryImageOfPage": {"@type": "ImageObject", "url": image},
                   "inLanguage": "en-US"}
        if page.get("type") == "gallery":
            webpage["@type"] = "CollectionPage"
        graph.append(webpage)
        crumbs = page.get("breadcrumbs") or []
        if crumbs:
            graph.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": strip_tags(c["label"]), "item": o + c["href"]}
                for i, c in enumerate(crumbs)]})
            webpage["breadcrumb"] = {"@id": url + "#breadcrumb"}
        svc = page.get("schema_service")
        if svc:
            area = [{"@type": "City", "name": t["name"] + ", TX"} for t in self.site["towns"]]
            if page.get("type") == "town":
                area = {"@type": "City", "name": page["town_name"], "containedInPlace": {"@type": "State", "name": "Texas"}}
            graph.append({"@type": "Service", "@id": url + "#service", "name": svc["name"], "serviceType": svc["type"],
                          "provider": {"@id": biz["@id"]}, "areaServed": area, "url": url})
        if page.get("type") == "guide":
            graph.append({"@type": "Article", "@id": url + "#article", "headline": page["h1"],
                          "description": page["description"], "image": image, "datePublished": page.get("published", BUILD_DATE),
                          "dateModified": page.get("modified", BUILD_DATE), "author": {"@id": biz["@id"]},
                          "publisher": {"@id": biz["@id"]}, "mainEntityOfPage": {"@id": url + "#webpage"}, "inLanguage": "en-US"})
        faqs = page.get("faqs") or []
        if faqs:
            graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
                {"@type": "Question", "name": strip_tags(f["q"]),
                 "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", strip_tags(f["a"]))}} for f in faqs]})
        return {"@context": "https://schema.org", "@graph": graph}

    # ---- blog ----------------------------------------------------------------------------------
    BLOG_TOKENS = ("TITLE", "DESCRIPTION", "CANONICAL", "OG_IMAGE", "JSONLD", "HERO", "PRELOAD", "H1", "DATE", "BODY",
                   "SOURCES", "COUNT_TEXT", "ITEMS")

    def blog_templates(self):
        """Render the blog post and blog index pages once with placeholder tokens. The two blog
        robots fill the tokens in; this keeps their pages identical to the rest of the site."""
        tok = {k: f"%%{k}%%" for k in self.BLOG_TOKENS}
        out = {}
        for name in ("post", "index"):
            page = {"url": "/blog/" if name == "index" else "/blog/__POST__", "title": tok["TITLE"],
                    "description": tok["DESCRIPTION"], "type": "post" if name == "post" else "blog", "cta": True,
                    "tok": tok}
            src = '{% extends "layouts/blog.html" %}{% block content %}{% include "partials/blog_' + name + '.html" %}{% endblock %}'
            text = self.env.from_string(src).render(page=page, pages={})
            out[name] = text
        return out

    def build_blog(self, tpl):
        gb = load_grace_blog()
        gb.TEMPLATES = tpl
        posts = []
        for p in sorted((ROOT / "blog").glob("*.html")):
            if p.name == "index.html":
                continue
            meta = gb.parse_post(p.read_text(), p.name)
            posts.append(meta)
            self.write(f"blog/{p.name}", gb.render_post(meta))
        posts.sort(key=lambda x: -x["ts"])
        self.write("blog/index.html", gb.render_index(posts))
        return posts

    # ---- build ---------------------------------------------------------------------------------
    def build(self):
        pages = self.load_pages()
        index = {p["url"]: p for p in pages}
        if len(index) != len(pages):
            raise SystemExit("two pages share a URL")
        failed = []
        for page in pages:
            try:
                text = self.render(page, index)
            except Exception as e:  # report and keep building the other pages
                failed.append(f"{page['source']}: {type(e).__name__}: {e}")
                continue
            self.write(str(out_path_for(page["url"], Path(".")))[0:], text)
        self.write("assets/site.css", (SRC / "static" / "site.css").read_text())
        self.write("assets/site.js", (SRC / "static" / "site.js").read_text())
        # webp copies for every photo in /images (gallery and blog robots use them too)
        for f in sorted(IMAGES.glob("*.jpg")):
            if not f.name.startswith("logo"):
                self.webp_srcset(f.name)
        tpl = self.blog_templates()
        tpl["business"] = self.business()
        self.write("netlify/blog-templates.json", json.dumps(tpl, ensure_ascii=False, indent=0) + "\n")
        self.write("netlify/blog-templates.mjs",
                   "// Generated by build.py from the site's own templates. Do not edit by hand: run python3 build.py.\n"
                   "// blog-post.mjs fills in the %%TOKENS%%.\n"
                   f"export const POST = {json.dumps(tpl['post'], ensure_ascii=False)};\n"
                   f"export const INDEX = {json.dumps(tpl['index'], ensure_ascii=False)};\n"
                   f"export const BUSINESS = {json.dumps(tpl['business'], ensure_ascii=False)};\n")
        posts = self.build_blog(tpl)
        self.write_sitemap(pages, posts)
        if self.write_docs:
            self.write_image_list()
        print(f"Built {len(pages) - len(failed)} pages and {len(posts)} blog posts")
        for f in failed:
            print("FAILED", f)
        if failed:
            raise SystemExit(1)
        print(f"{len(self.missing_images)} planned images still to generate (docs/image-list.md)")

    def write_sitemap(self, pages, posts):
        """Site pages first, then the blog block in the exact shape the blog robots write, so a robot
        that strips and re-adds the blog entries leaves the rest of the file alone."""
        o = self.site["business"]["origin"]
        urls = sorted((p["url"] for p in pages if not p.get("noindex")), key=lambda u: (u != "/", u))
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        lines += [f"  <url><loc>{o}{u}</loc><lastmod>{BUILD_DATE}</lastmod></url>" for u in urls]
        for u in ["/blog/"] + [f"/blog/{p['name']}" for p in posts]:
            lines.append(f"  <url>\n    <loc>{o}{u}</loc>\n    <lastmod>{BUILD_DATE}</lastmod>\n    <changefreq>weekly</changefreq>\n  </url>")
        lines.append("</urlset>")
        self.write("sitemap.xml", "\n".join(lines) + "\n")

    def write_image_list(self):
        rows = sorted(self.missing_images.values(), key=lambda e: (e["size"] != "1920x1080", e["pages"][0], e["file"]))
        out = ["# Images still to generate (Artistly)", "",
               "Generated by build.py. Every image below already has its tag in the page source. Until the file exists",
               "in images/, the page shows one of Grace's own photos in its place (named under each entry), never a",
               "broken image or an empty box. Generate each one, save it in images/ under the exact file name and",
               "size below, run `python3 build.py`, commit, and it appears on the page with its WebP sizes.", "",
               "Style for every image: bright, clearly visible, East Texas homes and shop work, natural daylight, no",
               "text, no logos, no watermarks, no recognizable faces. Every prompt starts with: wide cinematic landscape",
               "shot, subject positioned on right third of frame, well lit.", "",
               "Heroes are 1920x1080 and go first (they show on screen straight away); in-body photos are 1200x800.", "",
               f"Total: {len(rows)} images.", ""]
        for n, e in enumerate(rows, 1):
            out += [f"## {n}. {e['file']}", "", f"- File name: {e['file']}", f"- Size: {e['size']} px",
                    f"- Page(s): {', '.join(e['pages'])}", f"- Alt text: {e['alt']}", "",
                    f"Artistly prompt: {e['desc'] or ('wide cinematic landscape shot, subject positioned on right third of frame, well lit, ' + e['alt'])}", ""]
        (ROOT / "docs" / "image-list.md").write_text("\n".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="build into a temp folder and list files that would change")
    args = ap.parse_args()
    if args.check:
        tmp = Path(tempfile.mkdtemp())
        b = Builder(tmp, write_docs=False)
        b.build()
        changed = [r for r in b.written if not (ROOT / r).exists() or (ROOT / r).read_bytes() != (tmp / r).read_bytes()]
        print(f"{len(changed)} files would change")
        for r in changed[:50]:
            print("  ", r)
        shutil.rmtree(tmp)
        return 1 if changed else 0
    Builder(ROOT).build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
