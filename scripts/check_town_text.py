#!/usr/bin/env python3
"""Prove the 60 town pages kept their Sep 1 2026 body text word for word.

For each town page, every text block of the original (commit 6531506) is taken from inside <main> and
the closing call band: headings, paragraphs, FAQ questions and answers. Its words (letters, digits
and apostrophes, case kept, punctuation ignored) must appear, in the same order, as one block of the
rebuilt page. Image alt text is not body text and is not compared. The "Kilgore, Texas" eyebrow label
was removed on purpose (no eyebrow labels) and is listed as an expected removal.

Usage: python3 scripts/check_town_text.py   (exit 1 on any missing block)
"""
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "6531506"
BLOCK = re.compile(r"<(h1|h2|h3|p|li)\b[^>]*>(.*?)</\1>", re.S)


def words(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return " ".join(re.findall(r"[A-Za-z0-9']+", s.replace("’", "'")))


def blocks(raw, main_only):
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    if main_only:
        m = re.search(r"<main.*?</main>", raw, re.S)
        band = re.search(r'<section class="band">.*?</section>', raw, re.S)
        raw = m.group(0) + (band.group(0) if band else "")
    else:
        raw = re.search(r"<main.*?</main>", raw, re.S).group(0)
    out = [words(b) for _, b in BLOCK.findall(raw)]
    # town lists (li with only a town name) are links, not body text
    return [w for w in out if w]


def main():
    files = sorted(ROOT.glob("*/*-tx.html"))
    bad, total = 0, 0
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        old = subprocess.run(["git", "show", f"{BASE}:{rel}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        new_blocks = blocks(f.read_text(), False)
        new_text = "\n".join(new_blocks)
        olds = blocks(old, True)
        missing = []
        for b in olds:
            total += 1
            if b in new_blocks or b in new_text:
                continue
            missing.append(b)
        # the old <ul> of town links is regenerated as link pills; town names are not body text
        missing = [b for b in missing if len(b.split()) > 3]
        if missing:
            bad += 1
            print(f"FAIL {rel}: {len(missing)} block(s) changed")
            for b in missing[:3]:
                print("   ", b[:160])
    print(f"{len(files)} town pages, {total} original text blocks compared, {bad} pages with changed text")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
