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

REPO = Path(__file__).resolve().parents[2]
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
    # tidy the gap citations leave before punctuation ("a log ." -> "a log.")
    f["BODY"] = re.sub(r"[ \t]+([.,;:!?)])", r"\1", f["BODY"])
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

GT = '<div id="gt-bar" style="position:fixed;top:0;left:0;right:0;height:34px;z-index:10000;background:#0b1220;border-bottom:1px solid rgba(255,255,255,.14);display:flex;align-items:center;justify-content:flex-end;padding:0 12px;box-sizing:border-box"><div id="gt-wrap" style="display:flex;align-items:center;gap:6px;color:#fff;border:1px solid rgba(255,255,255,.5);border-radius:999px;padding:3px 12px;font:600 13px/1.2 system-ui,-apple-system,Segoe UI,sans-serif;cursor:pointer"><span aria-hidden="true">&#127760;</span><span id="gt-label">Espa&ntilde;ol</span><div id="google_translate_element"></div></div></div>\n<style>#gt-wrap .goog-te-gadget-simple{background:transparent!important;border:0!important;padding:0!important;font-size:13px!important}#gt-wrap .goog-te-gadget-simple a,#gt-wrap .goog-te-gadget-simple span{color:#fff!important;border:0!important}#gt-wrap .goog-te-gadget-icon{display:none}body{top:0!important}.scripture-bar{min-height:34px;box-sizing:border-box}.skiptranslate iframe.goog-te-banner-frame{display:none!important}</style>\n<script>(function(){var H=34,b=document.body;b.style.paddingTop=((parseFloat(getComputedStyle(b).paddingTop)||0)+H)+\'px\';document.documentElement.style.scrollPaddingTop=H+\'px\';var all=b.getElementsByTagName(\'*\');for(var i=0;i<all.length;i++){var el=all[i];if(el.id===\'gt-bar\'||(el.closest&&el.closest(\'#gt-bar\')))continue;var cs=getComputedStyle(el);if((cs.position===\'fixed\'||cs.position===\'sticky\')&&cs.top!==\'auto\'&&parseFloat(cs.top)<150){el.style.setProperty(\'top\',(parseFloat(cs.top)+H)+\'px\',\'important\');}}var mb=0;for(var j=0;j<all.length;j++){var e2=all[j],c2=getComputedStyle(e2);if(c2.position===\'fixed\'&&e2.getBoundingClientRect().top<160){var bt=e2.getBoundingClientRect().bottom;if(bt<220&&bt>mb)mb=bt;}}var q=document.querySelector(\'.quote-bar\');if(q&&getComputedStyle(q).position===\'static\'){var qt=q.getBoundingClientRect().top+window.scrollY;if(qt<mb)q.style.marginTop=(mb-qt)+\'px\';}})();\nfunction googleTranslateElementInit(){new google.translate.TranslateElement({pageLanguage:\'en\',includedLanguages:\'es,pt,fr,zh-CN,vi,ko,tl\',layout:google.translate.TranslateElement.InlineLayout.SIMPLE},\'google_translate_element\');var l=document.getElementById(\'gt-label\');if(l)l.style.display=\'none\';}\n(function(){var d=false;function go(){if(d)return;d=true;var s=document.createElement(\'script\');s.src=\'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit\';s.async=true;document.body.appendChild(s);}[\'mousemove\',\'scroll\',\'touchstart\',\'keydown\'].forEach(function(e){window.addEventListener(e,go,{once:true,passive:true});});var w=document.getElementById(\'gt-wrap\');if(w)w.addEventListener(\'click\',go);setTimeout(go,3000);})();</script>'

def photo_for(n):
    imgs = sorted(p.name for p in (REPO / "images").glob("work-*.jpg"))
    return ("/images/" + imgs[n % len(imgs)]) if imgs else ""

def post_page(f, name, date_str, photo):
    srcs = "".join(f'<li><a href="{esc(u)}" rel="nofollow">{esc(n.strip(" -"))}</a></li>'
                   for n, u in re.findall(r"^(.*?)\s*-?\s*(https?://\S+)\s*$", f["SOURCES"], re.M))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(f['TITLE'])} | Grace Woodwork</title>
<meta name="description" content="{esc(f['DESCRIPTION'])}">
<link rel="canonical" href="https://{DOMAIN}/blog/{name}">
<link rel="icon" href="/favicon.ico" sizes="any">
<style>
:root{{--forest:#13261E;--ink:#0B1812;--pine:#EDF0EA;--brass:#C79045;--paper:#F5F8F3}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--pine);color:var(--forest);line-height:1.75;font-family:'Karla',system-ui,-apple-system,Arial,sans-serif;font-size:1.05rem}}
header{{background:var(--forest);padding:16px 24px}}
header a{{color:var(--brass);text-decoration:none;font-weight:700;font-size:1.1rem}}
.wrap{{max-width:74ch;margin:0 auto;padding:48px 24px 80px}}
h1{{font-family:Georgia,'Zilla Slab',serif;font-size:clamp(1.9rem,4vw,2.7rem);line-height:1.18;margin:0 0 10px}}
h2{{font-family:Georgia,serif;font-size:1.35rem;margin:34px 0 10px}}
.date{{font-family:'Roboto Mono',monospace;font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;color:#8F621E;margin-bottom:30px}}
img.lead{{width:100%;border-radius:4px;margin:0 0 30px}}
p{{margin:0 0 20px}}
.src{{font-size:.86rem;color:#4a5a50}} .src a{{color:#4a5a50}}
footer{{border-top:1px solid rgba(19,38,30,.14);margin-top:46px;padding-top:24px;font-size:.95rem}}
footer a{{color:var(--forest)}}
.cta{{display:inline-block;margin-top:14px;background:var(--brass);color:var(--ink);text-decoration:none;padding:13px 26px;border-radius:3px;font-weight:700}}
</style>
</head>
<body>
<header><a href="/">Grace Woodwork</a></header>
<article class="wrap">
  <h1>{esc(f['TITLE'])}</h1>
  <div class="date">{esc(date_str)}</div>
  {f'<img class="lead" src="{photo}" alt="A piece finished in the Grace Woodwork shop in Kilgore" loading="lazy">' if photo else ''}
      {body_html(f['BODY'])}
  <div class="src"><p><strong>Sources</strong></p><ul>{srcs}</ul></div>
  <footer>
    <p>Grace Woodwork restores and builds furniture in Kilgore, Texas.</p>
    <a class="cta" href="/#quote">Send a photo, get a quote</a><br>
    <p style="margin-top:18px"><a href="/blog/">&larr; All posts</a></p>
  </footer>
</article>
{GT}
</body>
</html>"""

def title_from(name):
    s = re.sub(r"-\d{10,}\.html$", "", name).replace("-", " ")
    return s[:1].upper() + s[1:]

def index_page(posts):
    items = []
    for p in posts:
        when = datetime.fromtimestamp(p["ts"] / 1000, timezone.utc).strftime("%B %-d, %Y") if p["ts"] else ""
        items.append(f'    <li><a href="/blog/{p["name"]}">{esc(p["title"])}</a>' + (f'<span class="d">{when}</span>' if when else "") + "</li>")
    n = len(posts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog | Grace Woodwork</title>
<meta name="description" content="Notes from the shop: furniture repair, refinishing and custom woodwork in Kilgore, Texas.">
<link rel="canonical" href="https://{DOMAIN}/blog/">
<link rel="icon" href="/favicon.ico" sizes="any">
<style>
body{{margin:0;background:#EDF0EA;color:#13261E;line-height:1.7;font-family:'Karla',system-ui,Arial,sans-serif}}
header{{background:#13261E;padding:16px 24px}}
header a{{color:#C79045;text-decoration:none;font-weight:700;font-size:1.1rem}}
.wrap{{max-width:800px;margin:0 auto;padding:46px 24px 80px}}
h1{{font-family:Georgia,serif;font-size:2rem;margin:0 0 6px}}
.sub{{color:#4a5a50;margin:0 0 28px}}
ul{{list-style:none;padding:0}}
li{{padding:16px 0;border-bottom:1px solid rgba(19,38,30,.12);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
li a{{color:#13261E;text-decoration:none;font-weight:600}}
li a:hover{{color:#8F621E}}
.d{{color:#7c8a80;font-size:.86rem;white-space:nowrap}}
</style>
</head>
<body>
<header><a href="/">Grace Woodwork</a></header>
<div class="wrap">
  <h1>From the shop</h1>
  <p class="sub">{n} post{'' if n == 1 else 's'} on restoration, repair and custom work.</p>
  <ul>
{chr(10).join(items)}
  </ul>
</div>
{GT}
</body>
</html>"""

def sitemap(posts):
    x = SITEMAP.read_text() if SITEMAP.exists() else '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>'
    base = f"https://{DOMAIN}/blog/"
    x = re.sub(r"\s*<url>(?:(?!</url>).)*?<loc>\s*" + re.escape(base) + r"[^<]*</loc>.*?</url>", "", x, flags=re.S)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    block = "\n".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n  </url>"
                      for u in [base] + [base + p["name"] for p in posts])
    return x.replace("</urlset>", block + "\n</urlset>")

def main():
    posts = existing_posts()
    topic = pick_topic(posts)
    print("topic:", topic)
    f = draft(topic, posts)
    guards(f, posts)
    ts = int(time.time() * 1000)
    name = f"{slugify(f['TITLE'])}-{ts}.html"
    date_str = datetime.now(timezone.utc).strftime("%B %-d, %Y")
    (BLOG / name).write_text(post_page(f, name, date_str, photo_for(len(posts))))
    allp = [{"name": name, "ts": ts, "title": f["TITLE"]}] + posts
    (BLOG / "index.html").write_text(index_page(allp))
    SITEMAP.write_text(sitemap(allp))
    print("published:", name)

if __name__ == "__main__":
    main()
