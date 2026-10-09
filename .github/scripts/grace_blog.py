#!/usr/bin/env python3
"""Grace Woodwork: twice-weekly researched blog post (Tue + Fri).

Picks the next topic from TOPICS that has no post yet, has Claude research it with
live web search and write it, then runs fail-closed guards. On ANY failure it
writes nothing and exits non-zero, so the run is skipped rather than publishing
something weak. Commits nothing itself; the workflow commits the three files.

Rules baked in (Sep 26 2026, Maurice): general, useful woodworking and furniture
advice for East Texas homeowners. Never invent jobs, customers, reviews, prices,
years in business or any fact about Grace Woodwork beyond what is listed below.
"""
import html, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(os.environ.get("GRACE_BLOG_REPO") or Path(__file__).resolve().parents[2])
BLOG = REPO / "blog"
SITEMAP = REPO / "sitemap.xml"
DOMAIN = "gracewoodworkkilgore.com"
MODEL = "claude-opus-5"
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 10}

FACTS = ("Grace Woodwork is a furniture repair, refinishing and custom woodwork shop in Kilgore, Texas. "
         "It repairs and refinishes furniture, builds custom furniture, cabinets and built-ins, and makes custom wood signs. "
         "Phone 903-445-7477. Open Monday to Friday, 9am to 5pm. Customers can send a photo through the website for a quote.")

TOPICS = [
 "How to tell solid wood from veneer before you refinish a piece",
 "Why furniture joints loosen in East Texas humidity and how they get fixed",
 "Refinishing versus restoring: what each one does to an antique's value",
 "How to clean a wood table without damaging the finish",
 "Water rings and white heat marks on wood: what causes them and what fixes them",
 "Wobbly chairs: the common causes and when a repair is worth it",
 "Painted or stained kitchen cabinets: how each holds up in a busy kitchen",
 "Refacing kitchen cabinets versus replacing them",
 "What makes a dining table last for generations",
 "Oil, wax, lacquer or polyurethane: choosing a finish for furniture",
 "How to tell if an old dresser is worth restoring",
 "Caring for wood furniture through a hot, humid Texas summer",
 "Hardwoods and softwoods: what they mean for furniture you use every day",
 "Veneer that is lifting or bubbling: why it happens and how it is repaired",
 "Custom built-ins: where they make the most sense in an older home",
 "What to look for in a solid wood bookshelf",
 "Cedar, pine, oak and walnut: how common furniture woods age",
 "Scratches, dents and gouges: which ones can be repaired invisibly",
 "Chair caning and rush seats: repair or replace",
 "Protecting outdoor wood furniture and porch swings from sun and rain",
 "Choosing wood for a custom sign that will hang outdoors",
 "Heirloom furniture: questions to ask before you change anything",
 "Why sticking drawers happen and how they are fixed",
 "Moving furniture without damaging it",
 "Mid-century modern furniture: what to know before refinishing",
 "Farmhouse tables: what makes a well-built one",
 "Termites, powderpost beetles and wood furniture in East Texas",
 "Mold and mildew on wood furniture after a wet spell",
 "Repairing a cracked tabletop",
 "Kitchen cabinet doors that won't close right: hinge fixes explained",
 "Painting furniture: when it helps and when it hurts",
 "How long a professional refinish takes, and why",
 "Wood species for cutting boards and serving trays",
 "What 'solid wood' really means on a furniture tag",
 "Bringing back a sun-faded finish",
 "Rocking chairs: the parts that wear out first",
 "Planning a custom entertainment center or TV wall",
 "Church pews and church furniture: care and repair",
 "Barn wood and reclaimed wood: what to know before you use it",
 "Gift ideas that last: custom wood pieces for weddings and anniversaries",
]

BANNED = ["one of our customers", "a customer of ours", "our client", "last week we", "recently we", "we recently",
          "years of experience", "since 19", "since 20", "award-winning", "best in", "#1", "number one", "guarantee",
          "family-owned", "family owned", "licensed", "insured", "certified", "five-star", "5-star", "reviews say",
          "our customers say", "lorem", "```", "[city]", "as an ai"]

def fail(msg):
    print("GUARD FAILED: " + msg, file=sys.stderr); sys.exit(1)

def slugify(s):
    return (re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]) or "post"

def existing_posts():
    out = []
    for p in BLOG.glob("*.html"):
        if p.name == "index.html": continue
        m = re.search(r"-(\d{10,})\.html$", p.name)
        t = re.search(r"<title>(.*?)</title>", p.read_text(errors="ignore"), re.S)
        out.append({"name": p.name, "ts": int(m.group(1)) if m else 0,
                    "title": html.unescape(re.sub(r"\s*\|\s*Grace Woodwork\s*$", "", t.group(1).strip())) if t else p.name})
    return sorted(out, key=lambda x: -x["ts"])

STOP = set("a an and are as at be by can do for from how in is it its of on or the their to what when why with you your this that".split())
def toks(s): return {w[:5] for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 2}
def similar(a, b):
    A, B = toks(a), toks(b)
    return len(A & B) / max(1, len(A | B))

def pick_topic(posts):
    for t in TOPICS:
        if all(similar(t, p["title"]) < 0.45 for p in posts): return t
    fail("every topic in TOPICS already has a post; add new topics")

SYSTEM = ("You write blog posts for Grace Woodwork, a furniture repair and custom woodwork shop in Kilgore, Texas. "
          "Readers are East Texas homeowners. Write plainly and warmly, like a craftsman explaining things across the counter. "
          "Use American spelling. Only these facts about the business are true, and you must not invent any others "
          "(no jobs, customers, reviews, prices, years in business, awards, licenses or guarantees): " + FACTS)

def prompt(topic, posts):
    prev = "\n".join("- " + p["title"] for p in posts[:12]) or "(none yet)"
    return f"""Research and write one blog post on this topic: {topic}

First use web search to check the facts you rely on (wood science, finishes, humidity, pests, care advice). Prefer sources such as university extension services, the USDA Forest Products Laboratory, finish manufacturers and museum conservation guides.

Rules:
- 550 to 850 words. Practical and specific; no filler, no hype.
- Where it helps, mention East Texas conditions (heat, humidity, pine country) but do not overdo it.
- Speak about Grace Woodwork only in the last paragraph, briefly: if a piece needs professional work, readers can send a photo through the website or call 903-445-7477. Do not describe past jobs or customers.
- Do not use em dashes or en dashes. Use American spelling.
- Plain paragraphs. You may use up to four subheadings, each on its own line starting with "## ".
- Must not repeat these recent posts:
{prev}

Return exactly this format and nothing else:
===TITLE===
(a clear title under 70 characters)
===DESCRIPTION===
(one sentence under 155 characters for search results)
===BODY===
(the post)
===SOURCES===
(one line per source you actually used: Name - https://url)
"""

def draft(topic, posts):
    import anthropic
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": prompt(topic, posts)}]
    ev = {"results": 0, "hits": 0}
    for _ in range(8):
        with client.messages.stream(model=MODEL, max_tokens=12000, system=SYSTEM, messages=messages,
                                    tools=[WEB_SEARCH_TOOL], thinking={"type": "adaptive"}) as st:
            r = st.get_final_message()
        for b in r.content:
            if getattr(b, "type", "") == "web_search_tool_result":
                ev["results"] += 1
                if isinstance(getattr(b, "content", None), list): ev["hits"] += len(b.content)
        if r.stop_reason in ("refusal", "max_tokens"): fail("stop_reason " + r.stop_reason)
        if r.stop_reason != "pause_turn": break
        messages.append({"role": "assistant", "content": r.content})
    else:
        fail("search never settled")
    if ev["results"] == 0 or ev["hits"] == 0: fail("web search did not run or returned nothing")
    text = "\n".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    parts = re.split(r"(?m)^===([A-Z]+)===\s*$", text)
    f = {k: v.strip() for k, v in zip(parts[1::2], parts[2::2])}
    for k in ("TITLE", "DESCRIPTION", "BODY", "SOURCES"):
        if not f.get(k): fail("missing field " + k)
    # tidy the gap citations leave before punctuation ("a log ." -> "a log."), and no em/en dashes
    f["BODY"] = re.sub(r"[ \t]+([.,;:!?)])", r"\1", f["BODY"])
    for k in ("TITLE", "DESCRIPTION", "BODY"):
        f[k] = undash(f[k])
    return f

def guards(f, posts):
    body = f["BODY"]; words = len(re.findall(r"\w+", body))
    if not 450 <= words <= 1000: fail(f"length {words} words")
    low = (f["TITLE"] + " " + body).lower()
    for b in BANNED:
        if b in low: fail("banned phrase: " + b)
    if re.search(r"\$\s?\d", body): fail("mentions a price")
    for p in posts:
        if similar(f["TITLE"], p["title"]) >= 0.5: fail("too similar to existing post: " + p["title"])
    srcs = re.findall(r"https?://[^\s)]+", f["SOURCES"])
    if not srcs: fail("no sources listed")
    if "903-445-7477" not in body: fail("closing call-to-action missing")
    if len(f["TITLE"]) > 90: fail("title too long")

def esc(s): return html.escape(s, quote=True)

def body_html(body):
    out = []
    for block in re.split(r"\n{2,}", body.strip()):
        block = block.strip()
        if not block: continue
        if block.startswith("## "): out.append("<h2>" + esc(block[3:].strip()) + "</h2>")
        else: out.append("<p>" + esc(block).replace("\n", "<br>") + "</p>")
    return "\n      ".join(out)

# ---- page rendering ---------------------------------------------------------------------------
# The post and index pages come from netlify/blog-templates.json, which build.py renders from the
# site's own header, footer and styles. This script only fills in the %%TOKENS%%, so a robot post
# looks exactly like the rest of the site. build.py uses these same functions to re-render old posts.
TEMPLATES = None
DEFAULT_HERO = "/images/hero-2.jpg"


def templates():
    global TEMPLATES
    if TEMPLATES is None:
        TEMPLATES = json.loads((REPO / "netlify" / "blog-templates.json").read_text())
    return TEMPLATES


def undash(s):
    """No em or en dashes in visible copy (site rule): they become commas, ranges become 'to'."""
    s = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", s)
    s = re.sub(r"\s*(?:[–—]|&mdash;|&ndash;)\s*", ", ", s)
    s = re.sub(r",\s*,", ",", s)
    return re.sub(r",\s*([.?!:;])", r"\1", s)


def hero_html(photo, alt):
    """The post's photo as the full-width hero. Local photos get their WebP sizes if build.py made them."""
    photo = photo or DEFAULT_HERO
    alt = esc(alt)
    if photo.startswith("/images/"):
        stem = Path(photo).stem
        variants = []
        for f in (REPO / "images").glob(stem + "-*.webp"):
            m = re.fullmatch(re.escape(stem) + r"-(\d+)\.webp", f.name)
            if m:
                variants.append(int(m.group(1)))
        img = f'<img src="{photo}" alt="{alt}" width="1600" height="900" fetchpriority="high" decoding="async">'
        if variants:
            srcset = ", ".join(f"/images/{stem}-{w}.webp {w}w" for w in sorted(variants))
            return f'<!--post-photo:{photo}--><picture><source type="image/webp" srcset="{srcset}" sizes="100vw">{img}</picture>', srcset
        return f"<!--post-photo:{photo}-->{img}", ""
    return (f'<!--post-photo:{esc(photo)}--><img src="{esc(photo)}" alt="{alt}" width="1600" height="900" '
            f'fetchpriority="high" decoding="async">'), ""


def preload_html(photo, srcset):
    photo = photo or DEFAULT_HERO
    extra = f' imagesrcset="{srcset}" imagesizes="100vw" type="image/webp"' if srcset else ""
    return f'<link rel="preload" as="image" href="{esc(photo)}"{extra} fetchpriority="high">'


def abs_url(photo):
    photo = photo or DEFAULT_HERO
    return photo if photo.startswith("http") else f"https://{DOMAIN}{photo}"


def ld(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def fill(tpl, values):
    for k, v in values.items():
        tpl = tpl.replace("%%" + k + "%%", v)
    return tpl


def render_post(m):
    """m: name, ts, title, description, date_str, photo, body_html, sources_html."""
    t = templates()
    url = f"https://{DOMAIN}/blog/{m['name']}"
    hero, srcset = hero_html(m.get("photo"), m["title"])
    biz = t["business"]
    published = datetime.fromtimestamp(m["ts"] / 1000, timezone.utc).strftime("%Y-%m-%d") if m.get("ts") else ""
    graph = [biz, {"@type": "BlogPosting", "@id": url + "#article", "headline": m["title"], "description": m["description"],
                   "image": abs_url(m.get("photo")), "datePublished": published, "author": {"@id": biz["@id"]},
                   "publisher": {"@id": biz["@id"]}, "mainEntityOfPage": url, "inLanguage": "en-US"},
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Home", "item": f"https://{DOMAIN}/"},
                 {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"https://{DOMAIN}/blog/"},
                 {"@type": "ListItem", "position": 3, "name": m["title"], "item": url}]}]
    sources = m.get("sources_html") or ""
    return fill(t["post"], {
        "TITLE": esc(m["title"]) + " | Grace Woodwork", "DESCRIPTION": esc(m["description"]), "CANONICAL": url,
        "OG_IMAGE": abs_url(m.get("photo")), "JSONLD": ld({"@context": "https://schema.org", "@graph": graph}),
        "HERO": hero, "PRELOAD": preload_html(m.get("photo"), srcset), "H1": esc(m["title"]), "DATE": esc(m["date_str"]),
        "BODY": m["body_html"], "SOURCES": f"<!--post-sources-->{sources}<!--/post-sources-->",
    })


def render_index(posts):
    t = templates()
    items = []
    for p in posts:
        when = datetime.fromtimestamp(p["ts"] / 1000, timezone.utc).strftime("%B %-d, %Y") if p["ts"] else ""
        items.append(f'    <li><a href="/blog/{p["name"]}">{esc(p["title"])}</a>' + (f'<span class="d">{when}</span>' if when else "") + "</li>")
    n = len(posts)
    hero, srcset = hero_html("/images/hero-6.jpg", "Pine shelf units being built in the Grace Woodwork shop")
    biz = t["business"]
    graph = [biz, {"@type": "Blog", "@id": f"https://{DOMAIN}/blog/#blog", "name": "Grace Woodwork blog",
                   "url": f"https://{DOMAIN}/blog/", "publisher": {"@id": biz["@id"]}, "inLanguage": "en-US"}]
    return fill(t["index"], {
        "TITLE": "Blog: Furniture Repair and Woodwork Notes | Grace Woodwork",
        "DESCRIPTION": "Notes from the shop: furniture repair, refinishing and custom woodwork advice from Grace Woodwork in Kilgore, Texas.",
        "JSONLD": ld({"@context": "https://schema.org", "@graph": graph}), "HERO": hero,
        "PRELOAD": preload_html("/images/hero-6.jpg", srcset), "H1": "From the shop",
        "COUNT_TEXT": f"{n} post{'' if n == 1 else 's'} on restoration, repair and custom work, written in Kilgore, Texas.",
        "ITEMS": "\n".join(items),
    })


def parse_post(raw, name):
    """Read a post written by any version of either blog robot back into its parts."""
    m = re.search(r"-(\d{10,})\.html$", name)
    ts = int(m.group(1)) if m else 0
    title = html.unescape(re.search(r"<h1>(.*?)</h1>", raw, re.S).group(1).strip())
    d = re.search(r'<meta name="description" content="([^"]*)"', raw)
    desc = html.unescape(d.group(1)) if d else title
    if "<!--post-body-->" in raw:
        body = raw.split("<!--post-body-->", 1)[1].split("<!--/post-body-->", 1)[0].strip()
        src = raw.split("<!--post-sources-->", 1)[1].split("<!--/post-sources-->", 1)[0] if "<!--post-sources-->" in raw else ""
        ph = re.search(r"<!--post-photo:(.*?)-->", raw)
        photo = html.unescape(ph.group(1)) if ph and ph.group(1) != DEFAULT_HERO else ""
        dm = re.search(r'<p class="hero__note">Posted (.*?)</p>', raw)
        date_str = html.unescape(dm.group(1)) if dm else ""
    else:
        art = re.search(r'<article class="wrap">(.*?)</article>', raw, re.S).group(1)
        dm = re.search(r'<div class="date">(.*?)</div>', art, re.S)
        date_str = html.unescape(dm.group(1).strip()) if dm else ""
        ph = re.search(r'<img class="lead" src="([^"]+)"', art)
        photo = html.unescape(ph.group(1)) if ph else ""
        start = max(dm.end() if dm else 0, art.find(">", ph.start()) + 1 if ph else 0)
        stop = min(i for i in (art.find('<div class="src">'), art.find("<footer>"), len(art)) if i >= 0)
        body = art[start:stop].strip()
        sm = re.search(r'<div class="src">.*?(<ul>.*?</ul>)</div>', art, re.S)
        src = ('<aside class="sources" aria-labelledby="sources-title"><h2 id="sources-title">Sources</h2>'
               + sm.group(1) + "</aside>") if sm else ""
    body = re.sub(r">\s+<", ">\n<", undash(body))
    if not date_str and ts:
        date_str = datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%B %-d, %Y")
    return {"name": name, "ts": ts, "title": undash(title), "description": undash(desc), "date_str": date_str,
            "photo": photo, "body_html": body, "sources_html": src}


def sources_html(sources_text):
    items = "".join(f'<li><a href="{esc(u)}" rel="nofollow noopener" target="_blank">{esc(n.strip(" -"))}</a></li>'
                    for n, u in re.findall(r"^(.*?)\s*-?\s*(https?://\S+)\s*$", sources_text, re.M))
    return f'<aside class="sources" aria-labelledby="sources-title"><h2 id="sources-title">Sources</h2><ul>{items}</ul></aside>' if items else ""


def post_page(f, name, date_str, photo, ts=0):
    return render_post({"name": name, "ts": ts, "title": f["TITLE"], "description": f["DESCRIPTION"], "date_str": date_str,
                        "photo": photo, "body_html": body_html(f["BODY"]), "sources_html": sources_html(f["SOURCES"])})


def photo_for(n):
    imgs = sorted(p.name for p in (REPO / "images").glob("work-*.jpg"))
    return ("/images/" + imgs[n % len(imgs)]) if imgs else ""


def title_from(name):
    s = re.sub(r"-\d{10,}\.html$", "", name).replace("-", " ")
    return s[:1].upper() + s[1:]


def index_page(posts):
    return render_index(posts)


def sitemap(posts):
    x = SITEMAP.read_text() if SITEMAP.exists() else '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>'
    base = f"https://{DOMAIN}/blog/"
    x = re.sub(r"\s*<url>(?:(?!</url>).)*?<loc>\s*" + re.escape(base) + r"[^<]*</loc>.*?</url>", "", x, flags=re.S)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    block = "\n".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n  </url>"
                      for u in [base] + [base + p["name"] for p in posts])
    return x.replace("</urlset>", block + "\n</urlset>")

DRY_RUN_DRAFT = {
    "TITLE": "Dry run: how to tell when a chair joint needs regluing",
    "DESCRIPTION": "A test post written by the dry run, never published: checks the robot's page matches the site design.",
    "BODY": "This post was made by a dry run of the blog robot. It checks the page template, the blog index and the sitemap.\n\n"
            "## A subheading\n\nA wobbly chair usually means a joint has let go. If a piece needs professional work, "
            "send a photo through the website or call 903-445-7477.",
    "SOURCES": "USDA Forest Products Laboratory, Wood Handbook - https://www.fpl.fs.usda.gov/documnts/fplgtr/fpl_gtr190.pdf",
}


def main():
    dry = "--dry-run" in sys.argv
    posts = existing_posts()
    topic = pick_topic(posts)
    print("topic:", topic)
    f = dict(DRY_RUN_DRAFT) if dry else draft(topic, posts)
    if not dry:
        guards(f, posts)
    ts = int(time.time() * 1000)
    name = f"{slugify(f['TITLE'])}-{ts}.html"
    date_str = datetime.now(timezone.utc).strftime("%B %-d, %Y")
    (BLOG / name).write_text(post_page(f, name, date_str, photo_for(len(posts)), ts))
    allp = [{"name": name, "ts": ts, "title": f["TITLE"]}] + posts
    (BLOG / "index.html").write_text(index_page(allp))
    SITEMAP.write_text(sitemap(allp))
    print("published:", name)


if __name__ == "__main__":
    main()
