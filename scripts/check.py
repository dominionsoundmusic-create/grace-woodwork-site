#!/usr/bin/env python3
"""Rule and SEO checks over the built site (the repository root).

Every public HTML page except Grace's two tools (shop-upload.html, write.html) is checked for:
  copy rules   banned phrases, em/en dashes in visible text, eyebrow labels, British spellings (new pages)
  SEO          one H1, title, description, canonical = production URL, sitemap entry, Open Graph tags,
               one valid JSON-LD block, unique titles and descriptions
  content      the dwdp:handwritten 2026-10-09 marker in the first 4KB of new or rewritten pages; 3 to 6
               visible FAQs matching the FAQPage JSON-LD; a hero plus at least two in-body images
  integrity    internal links and images resolve, images have alt/width/height, in-body figures are lazy,
               the hero image is not lazy, no duplicate ids
  tools        the quote form (name, fields, honeypot, encoding, target), shop-upload.html and write.html
               still load their scripts, _redirects keeps every original rule

Usage: python3 scripts/check.py      Exit code 1 if any error is found.
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://gracewoodworkkilgore.com"
PHONE_TEL = "tel:+19034457477"
MARK = "dwdp:handwritten 2026-10-09"
TOOLS = {"shop-upload.html", "write.html"}
SKIP_DIRS = {"src", "node_modules", "docs", "scripts", "keywords", ".github", "netlify", "fonts", "assets", "images"}

BANNED = [r"\byour trusted partner\b", r"\bone-stop solution\b", r"\blook no further\b", r"\bunmatched excellence\b",
          r"\bwe'?ve got you covered\b", r"\bwe have got you covered\b", r"\bfree estimates?\b", r"\bbest prices?\b",
          r"\bcheapest\b", r"#1\b", r"\btop[- ]rated\b", r"\blicensed and insured\b", r"\bguarantee", r"\bwarrant(?:y|ies)\b",
          r"\baward[- ]winning\b", r"\byears of experience\b", r"\bfully insured\b", r"\bcertified\b", r"\b5[- ]star\b",
          r"\bfive[- ]star\b", r"\blorem\b", r"\bTODO\b"]
BRITISH = [r"\bcolour", r"\bfavour", r"\brealis(?:e|ed|es|ing|ation)\b", r"\borganis(?:e|ed|es|ing|ation)\b", r"\bcentre\b", r"\bmetres?\b", r"\bgrey\b", r"\baluminium\b",
           r"\bneighbour", r"\bstoreys?\b", r"\bwhilst\b", r"\bcatalogue\b", r"\bper cent\b", r"\bmodell", r"\btravell"]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.skip, self.h1, self.title, self._t = [], 0, 0, "", False
        self.meta, self.links, self.imgs, self.ids, self.canonical = {}, [], [], [], None
        self.jsonld, self._ld, self._in_ld = [], "", False
        self.robots = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag in ("script", "style"):
            self.skip += 1
            if a.get("type") == "application/ld+json":
                self._in_ld, self._ld = True, ""
        if tag == "title":
            self._t = True
        if tag == "h1":
            self.h1 += 1
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "a":
            self.links.append(a.get("href"))
        if tag == "img":
            self.imgs.append(a)
        if tag == "option":
            self.text.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
            if self._in_ld:
                self.jsonld.append(self._ld)
                self._in_ld = False
        if tag == "title":
            self._t = False

    def handle_data(self, data):
        if self._in_ld:
            self._ld += data
        if self._t:
            self.title += data
        if not self.skip:
            self.text.append(data)


def url_of(path):
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    return "/" + rel[:-len("index.html")] if rel.endswith("/index.html") else "/" + rel


def resolve(href):
    href = href.split("#")[0].split("?")[0]
    if not href:
        return True
    if href.startswith(ORIGIN):
        href = href[len(ORIGIN):] or "/"
    p = ROOT / href.lstrip("/")
    if href.endswith("/"):
        return (p / "index.html").exists()
    return p.exists()


def pages():
    out = []
    for f in sorted(ROOT.rglob("*.html")):
        rel = f.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or rel.parts[0].startswith(".") or f.name in TOOLS:
            continue
        out.append(f)
    return out


def check_form(errors):
    raw = (ROOT / "index.html").read_text()
    m = re.search(r"<form[^>]*name=\"quote\".*?</form>", raw, re.S)
    if not m:
        errors.append("/: quote form missing")
        return
    form = m.group(0)
    for need in ('method="POST"', 'action="/thanks.html"', 'data-netlify="true"', 'netlify-honeypot="company"',
                 'enctype="multipart/form-data"', '<input type="hidden" name="form-name" value="quote">'):
        if need not in form:
            errors.append(f"/: quote form lost {need}")
    names = re.findall(r'name="([^"]+)"', form)
    want = ["quote", "form-name", "company", "name", "phone", "email", "service", "photo", "message"]
    if sorted(set(names)) != sorted(set(want)):
        errors.append(f"/: quote form fields changed: {names}")
    old = subprocess.run(["git", "show", "6531506:index.html"], cwd=ROOT, capture_output=True, text=True).stdout
    om = re.search(r"<form[^>]*name=\"quote\".*?</form>", old, re.S).group(0)
    if re.findall(r"<(?:input|select|textarea)\b[^>]*>", om) != re.findall(r"<(?:input|select|textarea)\b[^>]*>", form):
        errors.append("/: quote form input, select or textarea tags differ from the original")


def check_tools(errors):
    for name, needs in (("shop-upload.html", ["/.netlify/functions/shop-auth", "api.cloudinary.com", "gateInit"]),
                        ("write.html", ["/.netlify/functions/shop-auth", "/.netlify/functions/blog-post", "gateInit", "publish"])):
        raw = (ROOT / name).read_text()
        for n in needs:
            if n not in raw:
                errors.append(f"/{name}: lost {n}")
        if 'name="robots" content="noindex' not in raw:
            errors.append(f"/{name}: lost noindex")


def check_redirects(errors):
    now = (ROOT / "_redirects").read_text()
    old = subprocess.run(["git", "show", "6531506:_redirects"], cwd=ROOT, capture_output=True, text=True).stdout
    rules_now = {tuple(l.split()) for l in now.splitlines() if l.strip() and not l.startswith("#")}
    for l in old.splitlines():
        if l.strip() and not l.startswith("#") and tuple(l.split()) not in rules_now:
            errors.append(f"_redirects: original rule missing: {l}")
    for l in now.splitlines():
        p = l.split()
        if not p or p[0].startswith("#"):
            continue
        if not (p[1].startswith("http") or ":splat" in p[1] or resolve(p[1])):
            errors.append(f"_redirects: target {p[1]} does not exist")
        if len(p) > 2 and p[2] == "301!" and resolve(p[0]) and not p[0].endswith("/"):
            errors.append(f"_redirects: forced rule {p[0]} would hide a real page")


def main():
    errors, warnings = [], []
    titles, descs = defaultdict(list), defaultdict(list)
    sitemap = (ROOT / "sitemap.xml").read_text()
    files = pages()
    for f in files:
        url = url_of(f)
        raw = f.read_text()
        p = PageParser()
        p.feed(raw)
        text = re.sub(r"\s+", " ", " ".join(p.text))
        noindex = 'name="robots" content="noindex' in raw
        handwritten = MARK in raw[:4096]
        town = bool(re.fullmatch(r"/[a-z-]+/[a-z-]+-tx\.html", url))

        def err(msg):
            errors.append(f"{url}: {msg}")

        visible = text + " " + p.title + " " + p.meta.get("description", "")
        for pat in BANNED:
            for mt in re.finditer(pat, visible, re.I):
                hit = f"banned /{pat}/ in: ...{visible[max(0, mt.start() - 50): mt.end() + 50]}..."
                # the Sep 1 town pages keep their words (CLAUDE.md rule 3); hits there are reviewed by hand
                # and listed in docs/decisions.md rather than reworded
                if town:
                    warnings.append(f"{url}: kept word for word: {hit}")
                else:
                    err(hit)
        for mt in re.finditer("[—–]", visible):
            err(f"em/en dash in: ...{visible[max(0, mt.start() - 40): mt.end() + 40]}...")
        if re.search(r'class="[^"]*\b(?:eyebrow|kicker|overline|tag)\b', raw):
            err("eyebrow label found")
        if handwritten:
            for pat in BRITISH:
                for mt in re.finditer(pat, visible, re.I):
                    err(f"British spelling /{pat}/ in: ...{visible[max(0, mt.start() - 40): mt.end() + 40]}...")
        if town and "dwdp:handwritten" not in raw[:600]:
            err("town page lost its dwdp:handwritten marker")
        if not town and not noindex and not url.startswith("/blog/") and url != "/gallery/" and not handwritten:
            err("new or rewritten page without the dwdp:handwritten 2026-10-09 marker in the first 4KB")
        # SEO
        if p.h1 != 1:
            err(f"expected one h1, found {p.h1}")
        if not p.title.strip():
            err("missing title")
        elif len(p.title) > 70:
            warnings.append(f"{url}: title is {len(p.title)} chars")
        d = p.meta.get("description", "")
        if not d:
            err("missing meta description")
        elif not 70 <= len(d) <= 170:
            warnings.append(f"{url}: description is {len(d)} chars")
        titles[p.title].append(url)
        descs[d].append(url)
        if p.canonical != ORIGIN + url:
            err(f"canonical {p.canonical} != {ORIGIN + url}")
        in_map = f"<loc>{ORIGIN}{url}</loc>" in sitemap
        if not noindex and not in_map:
            err("indexable page missing from sitemap.xml")
        if noindex and in_map:
            err("noindex page listed in sitemap.xml")
        for k in ("og:title", "og:description", "og:url", "og:image"):
            if not p.meta.get(k):
                err(f"missing {k}")
        if p.meta.get("og:image") and not p.meta["og:image"].startswith("https://"):
            err("og:image not absolute")
        if len(p.jsonld) != 1:
            err(f"expected one JSON-LD block, found {len(p.jsonld)}")
        faq_n = 0
        for block in p.jsonld:
            try:
                data = json.loads(block)
            except json.JSONDecodeError as e:
                err(f"invalid JSON-LD: {e}")
                continue
            types = [g.get("@type") for g in data.get("@graph", [])]
            if len(types) != len(set(types)):
                err(f"duplicate JSON-LD types {types}")
            for g in data.get("@graph", []):
                if g.get("@type") == "FAQPage":
                    faq_n = len(g["mainEntity"])
                if g.get("@type") == "LocalBusiness":
                    if g.get("telephone") != "+1-903-445-7477" or g["address"].get("addressLocality") != "Kilgore":
                        err("LocalBusiness facts changed")
                    if g["openingHoursSpecification"][0]["opens"] != "09:00" or g["openingHoursSpecification"][0]["closes"] != "17:00":
                        err("LocalBusiness hours changed")
                    if "aggregateRating" in g or "review" in g:
                        err("ratings or reviews in schema")
        visible_faq = raw.count('class="faq__item"')
        if visible_faq != faq_n:
            err(f"visible FAQs ({visible_faq}) != FAQPage entries ({faq_n})")
        if handwritten and not 3 <= visible_faq <= 6:
            err(f"needs 3 to 6 FAQs, has {visible_faq}")
        # images
        has_hero = '<section class="hero' in raw
        figs = raw.count('<figure class="fig')
        if url not in ("/thanks.html", "/404.html") and not has_hero:
            err("no hero")
        if handwritten and figs < 2:
            err(f"needs at least two in-body images, has {figs}")
        hero = re.search(r'<section class="hero.*?</section>', raw, re.S)
        if hero and 'loading="lazy"' in hero.group(0):
            err("hero image is lazy-loaded")
        for m in re.finditer(r'<figure class="fig[^"]*">(.*?)</figure>', raw, re.S):
            if 'loading="lazy"' not in m.group(1):
                err("in-body figure image without loading=lazy")
        for im in p.imgs:
            src = im.get("src", "")
            if "alt" not in im:
                err(f"img missing alt: {src}")
            if not im.get("width") or not im.get("height"):
                err(f"img missing width/height: {src}")
            real = im.get("data-src") or src
            if real.startswith("/") and not (ROOT / real.lstrip("/")).exists():
                err(f"missing image file {real}")
        for m in re.finditer(r'srcset="([^"]+)"', raw):
            for part in m.group(1).split(","):
                u = part.strip().split(" ")[0]
                if u.startswith("/") and not (ROOT / u.lstrip("/")).exists():
                    err(f"missing srcset file {u}")
        # links
        for href in p.links:
            if href is None or href.strip() in ("", "#"):
                err("empty href")
                continue
            if href.startswith("tel:") and href != PHONE_TEL:
                err(f"unexpected phone link {href}")
            if href.startswith(("tel:", "mailto:", "http://", "https://")) and not href.startswith(ORIGIN):
                continue
            if not resolve(href):
                err(f"broken internal link {href}")
        dup = {i for i in p.ids if p.ids.count(i) > 1}
        if dup:
            err(f"duplicate ids {sorted(dup)}")
    for t, urls in titles.items():
        if len(urls) > 1:
            errors.append(f"duplicate title '{t}' on {urls}")
    for d, urls in descs.items():
        if len(urls) > 1 and d:
            errors.append(f"duplicate description on {urls}")
    for u in re.findall(r"<loc>([^<]+)</loc>", sitemap):
        if not resolve(u):
            errors.append(f"sitemap.xml lists {u}, which does not exist")
    check_form(errors)
    check_tools(errors)
    check_redirects(errors)
    errors = list(dict.fromkeys(errors))
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(files)} pages checked, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
