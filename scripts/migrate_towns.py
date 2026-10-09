#!/usr/bin/env python3
"""One-time move of the 60 hand-written town pages (Sep 1 2026) into src/towns/ for build.py.

Reads each page as it was at commit 6531506 (before the rebuild) and keeps every word of its body
text: the H1, the lead sentence, every section, every FAQ question and answer, the "towns" note and
the closing call band. Only markup changes:
  - the page is split into heading-left / text-right blocks, the FAQ grid becomes the FAQ band
  - <div class="shots"> photo rows become figures with WebP srcset (same files, same alt text)
  - the "Kilgore, Texas" eyebrow label is dropped (eyebrow labels are not allowed)
  - em and en dashes in visible text become commas (punctuation only; no word changes)
  - the FAQPage JSON-LD is rebuilt from the visible questions (New London's did not match)

Run once: python3 scripts/migrate_towns.py   (scripts/check_town_text.py proves the words survived)
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BASE = "6531506"
HUBS = {"furniture-repair": "Furniture Repair", "custom-furniture": "Custom Furniture",
        "custom-cabinets": "Custom Cabinets", "custom-signs": "Custom Signs"}
TOWNS = json.loads((ROOT / "src" / "data" / "site.json").read_text())["towns"]
HEROES = {
    "furniture-repair": [("hero-2.jpg", "An oval oak dining table with its leaves in, refinished in the Grace Woodwork shop")],
    "custom-furniture": [("hero-1.jpg", "A dark stained console table with matching storage boxes, built in the shop"),
                         ("hero-5.jpg", "A pine desk with built-in shelving under construction in the shop"),
                         ("hero-4.jpg", "Three stained wooden storage boxes finished in the shop")],
    "custom-cabinets": [("hero-3.jpg", "A dark stained corner bar cabinet with a built-in ice bucket, built in the shop"),
                        ("hero-7.jpg", "A plywood corner cabinet carcass being assembled in the shop"),
                        ("hero-6.jpg", "Two pine shelf units under construction in the shop")],
    "custom-signs": [("work-06.jpg", "Four framed wooden laundry room signs reading wash, dry, fold and repeat"),
                     ("work-28.jpg", "Handmade Stella Grace wooden signs with heart designs on a display shelf")],
}


def git_show(path):
    return subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def undash(s):
    """Em/en dashes in visible text become commas; the words are untouched."""
    s = re.sub(r"\s*(?:&mdash;|—)\s*", ", ", s)
    s = re.sub(r"(\d)\s*(?:&ndash;|–)\s*(\d)", r"\1 to \2", s)
    s = re.sub(r"\s*(?:&ndash;|–)\s*", ", ", s)
    s = re.sub(r",\s*,", ",", s)
    s = re.sub(r",\s*([.?!])", r"\1", s)
    return s


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def shots(m):
    out = []
    for im in re.finditer(r"<img ([^>]*)>", m.group(0)):
        a = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', im.group(1)))
        f = a["src"].split("/images/")[-1]
        out.append("{{ img(%s, %s) }}" % (json.dumps(f), json.dumps(html.unescape(a.get("alt", "")))))
    return '<div class="shots">' + "".join(out) + "</div>"


def migrate(hub, town_slug, idx):
    path = f"{hub}/{town_slug}-tx.html"
    raw = git_show(path)
    marker = re.search(r"<!--\s*(dwdp:handwritten.*?)\s*-->", raw).group(1)
    title = html.unescape(re.search(r"<title>(.*?)</title>", raw, re.S).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', raw).group(1))
    main = re.search(r'<main class="wrap">(.*?)</main>', raw, re.S).group(1)
    h1 = text(re.search(r"<h1>(.*?)</h1>", main, re.S).group(1))
    lede = re.search(r'<p class="lede">(.*?)</p>', main, re.S).group(1).strip()
    acts = re.search(r'<div class="actions">.*?</div>', main, re.S)
    body = main[acts.end():]
    towns = re.search(r'<div class="towns">\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>', body, re.S)
    body = body[:body.index('<div class="towns">')]
    # FAQ grid -> faqs
    faq_m = re.search(r"<h2>([^<]*)</h2>\s*<div class=\"grid\">(.*?)</div>", body, re.S)
    faqs = [{"q": undash(text(q)), "a": undash(a.strip())}
            for q, a in re.findall(r"<article><h3>(.*?)</h3><p>(.*?)</p></article>", faq_m.group(2), re.S)]
    faq_title = undash(text(faq_m.group(1)))
    body = body[:faq_m.start()] + body[faq_m.end():]
    # markup only
    body = body.replace('<p class="lede" style="margin-top:14px">', "<p>")
    body = re.sub(r'<div class="shots">.*?</div>', shots, body, flags=re.S)
    body = undash(body)
    parts = re.split(r"(<h2>.*?</h2>)", body)
    lead_in, blocks = parts[0].strip(), []
    for i in range(1, len(parts), 2):
        blocks.append(f'<div class="blk">\n<div class="blk__head">{parts[i]}</div>\n<div class="blk__body">\n{parts[i + 1].strip()}\n</div>\n</div>')
    if lead_in:
        blocks.insert(0, lead_in)
    band = re.search(r'<section class="band">\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>\s*<a [^>]*>(.*?)</a>', raw, re.S)
    stype = re.search(r'"serviceType":"([^"]+)"', raw).group(1)
    town_name = next(t["name"] for t in TOWNS if t["slug"] == town_slug)
    heroes = HEROES[hub]
    hero_file, hero_alt = heroes[idx % len(heroes)]
    fm = {
        "url": "/" + path, "title": undash(title), "description": undash(desc), "h1": h1, "crumb": town_name,
        "hub": hub, "hub_name": HUBS[hub], "town": town_slug, "town_name": town_name, "marker": marker,
        "hero": {"image": hero_file, "alt": hero_alt, "lead": undash(lede),
                 "secondary_label": "Send a photo, get a quote", "secondary_href": "/#quote"},
        "faq_title": faq_title, "faqs": faqs,
        "towns_h2": undash(text(towns.group(1))), "towns_p": undash(text(towns.group(2))),
        "cta_title": undash(text(band.group(1))), "cta_text": undash(text(band.group(2))), "cta_button": text(band.group(3)),
        "schema_service": {"name": f"{stype} in {town_name}, Texas", "type": stype},
        "related": [s for s in ("furniture-refinishing", "table-refinishing", "antique-furniture-restoration", "chair-caning-and-repair")] if hub == "furniture-repair"
        else ["custom-dining-tables", "built-in-shelves"] if hub == "custom-furniture"
        else ["cabinet-painting", "cabinet-refacing", "built-in-shelves"] if hub == "custom-cabinets" else [],
    }
    src = ("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000) + "---\n"
           "{% block content %}\n<section class=\"sec\">\n" + "\n".join(blocks) + "\n</section>\n{% endblock %}\n")
    dest = ROOT / "src" / "towns" / hub / f"{town_slug}-tx.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src)


def main():
    n = 0
    for hub in HUBS:
        for i, t in enumerate(TOWNS):
            migrate(hub, t["slug"], i)
            n += 1
    print("migrated", n)


if __name__ == "__main__":
    sys.exit(main())
