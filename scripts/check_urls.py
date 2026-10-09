#!/usr/bin/env python3
"""Every URL the site had before the rebuild must still work at the same address.

Reads docs/url-inventory.txt (the file tree and sitemap.xml at commit 6531506) and checks each URL
resolves to a file in the repository root, the way Netlify will serve it (folder URLs from
index.html). Also checks that every extensionless town address still has its forced 301! rule to the
.html page, that the Aug 17 folder-rename 301s are still in _redirects, and that every pre-rebuild
blog post is still listed in blog/index.html and sitemap.xml.

Usage: python3 scripts/check_urls.py [--report docs/url-check.md]   (exit 1 on any failure)
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def served(url):
    p = ROOT / url.lstrip("/")
    if url.endswith("/"):
        return (p / "index.html").is_file()
    return p.is_file()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="")
    a = ap.parse_args()
    urls = [u for u in (ROOT / "docs" / "url-inventory.txt").read_text().split() if u]
    red = (ROOT / "_redirects").read_text()
    rules = {tuple(l.split()[:3]) for l in red.splitlines() if l.strip() and not l.startswith("#")}
    sitemap = (ROOT / "sitemap.xml").read_text()
    index = (ROOT / "blog" / "index.html").read_text()
    rows, fails = [], 0
    for u in urls:
        ok = served(u)
        notes = []
        m = re.fullmatch(r"(/[a-z-]+/[a-z-]+-tx)\.html", u)
        if m:
            if (m.group(1), u, "301!") not in rules:
                ok = False
                notes.append("forced 301! from the extensionless address missing")
            else:
                notes.append(f"{m.group(1)} 301! kept")
        if u.startswith("/blog/") and u.endswith(".html"):
            if f'href="{u}"' not in index:
                ok = False
                notes.append("not in blog index")
            if f"https://gracewoodworkkilgore.com{u}<" not in sitemap:
                ok = False
                notes.append("not in sitemap")
        fails += not ok
        rows.append((u, "PASS" if ok else "FAIL", "; ".join(notes)))
    for src, dst in (("/furniture-restoration/*", "/furniture-repair/:splat"), ("/furniture-restoration/", "/furniture-repair/"),
                     ("/cabinets-and-built-ins/*", "/custom-cabinets/:splat"), ("/cabinets-and-built-ins/", "/custom-cabinets/")):
        ok = (src, dst, "301") in rules
        fails += not ok
        rows.append((src, "PASS" if ok else "FAIL", f"Aug 17 rename 301 to {dst}"))
    for r in rows:
        if r[1] == "FAIL":
            print("FAIL", *r)
    print(f"{len(rows)} old URLs and redirect rules checked, {fails} failures")
    if a.report:
        out = ["| Old URL or rule | Result | Note |", "|---|---|---|"] + [f"| `{u}` | {s} | {n} |" for u, s, n in rows]
        Path(a.report).write_text("\n".join(out) + "\n")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
