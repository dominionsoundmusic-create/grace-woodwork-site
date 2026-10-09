#!/usr/bin/env python3
"""Duplicate-content check: Jaccard similarity on 5-word shingles.

Compares every pair of new or rewritten pages (those carrying the dwdp:handwritten 2026-10-09 marker),
and each of them against each of the 60 town pages. Only a page's own copy is compared: the hero,
body and FAQs inside <main>. Parts that are the same on every page by design are removed first (the
call band, service and guide cards whose text comes from site.json, link pills, related links,
sources lists, figures, scripts).

Usage: python3 scripts/similarity.py [--limit 0.15] [--report docs/similarity.md]
Exit code 1 if any pair is above the limit.
"""
import argparse
import html
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK = "dwdp:handwritten 2026-10-09"
DROP = [r"<script.*?</script>", r"<style.*?</style>", r"<!--.*?-->", r"<figure.*?</figure>",
        r'<section class="band band--ink" aria-labelledby="cta-title">.*?</section>',
        r'<section class="sec related">.*?</section>', r'<aside class="sources".*?</aside>',
        r'<ul class="pills">.*?</ul>', r'<div class="cards">.*?</div>\s*</article>\s*</div>',
        r'<nav class="crumbs".*?</nav>', r'<div class="btn-row">.*?</div>']


def words(raw):
    m = re.search(r"<main id=\"main\">(.*)</main>", raw, re.S)
    body = m.group(1) if m else raw
    for pat in DROP:
        body = re.sub(pat, " ", body, flags=re.S)
    body = re.sub(r'<div class="cards">.*?(?=</section>)', " ", body, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", body)).lower()
    txt = re.sub(r"903-445-7477", " phone ", txt)
    return re.findall(r"[a-z0-9']+", txt)


def shingles(w, n=5):
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def jac(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def url_of(p):
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    return "/" + rel[:-len("index.html")] if rel.endswith("/index.html") else "/" + rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=float, default=0.15)
    ap.add_argument("--report", default="")
    a = ap.parse_args()
    new, towns = {}, {}
    for f in sorted(ROOT.rglob("*.html")):
        rel = f.relative_to(ROOT)
        if rel.parts[0] in ("src", "docs", "scripts", "netlify", "node_modules") or rel.parts[0].startswith("."):
            continue
        raw = f.read_text()
        if MARK in raw[:4096]:
            new[url_of(f)] = shingles(words(raw))
        elif re.fullmatch(r"[a-z-]+/[a-z-]+-tx\.html", rel.as_posix()):
            towns[url_of(f)] = shingles(words(raw))
    nn = sorted(((jac(new[x], new[y]), x, y) for x, y in itertools.combinations(new, 2)), reverse=True)
    nt = sorted(((jac(new[x], towns[t]), x, t) for x in new for t in towns), reverse=True)
    fails = [r for r in nn + nt if r[0] > a.limit]
    def stats(rows):
        js = [r[0] for r in rows]
        return max(js), sum(js) / len(js), min(js)
    lines = [f"New or rewritten pages: {len(new)}; town pages: {len(towns)}", ""]
    for name, rows in (("new vs new", nn), ("new vs town", nt)):
        mx, mean, mn = stats(rows)
        lines.append(f"{name:12s} pairs={len(rows):5d}  max={mx:.1%}  mean={mean:.1%}  min={mn:.1%}")
    lines += ["", "Highest new vs new:"] + [f"  {j:.1%}  {x}  {y}" for j, x, y in nn[:8]]
    lines += ["", "Highest new vs town:"] + [f"  {j:.1%}  {x}  {y}" for j, x, y in nt[:8]]
    print("\n".join(lines))
    for f in fails:
        print(f"FAIL above {a.limit:.0%}: {f[1]} vs {f[2]} = {f[0]:.1%}")
    if a.report:
        out = ["| Comparison | Pairs | Max | Mean | Min |", "|---|---:|---:|---:|---:|"]
        for name, rows in (("New vs new", nn), ("New vs town pages", nt)):
            mx, mean, mn = stats(rows)
            out.append(f"| {name} | {len(rows)} | {mx:.1%} | {mean:.1%} | {mn:.1%} |")
        out += ["", "Highest pairs:", "", "| Jaccard | Page | Page |", "|---:|---|---|"]
        out += [f"| {j:.1%} | {x} | {y} |" for j, x, y in sorted(nn[:8] + nt[:4], reverse=True)]
        Path(a.report).write_text("\n".join(out) + "\n")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
