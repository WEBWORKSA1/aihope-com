#!/usr/bin/env python3
"""Quality checks for the built AI Hope site. Run after build.py:  python3 _source/tests/qa.py"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
problems = []
pages = sorted(ROOT.glob("*.html")) + sorted((ROOT / "jobs").glob("*.html"))
ids_cache = {}


def ids(path):
    if path not in ids_cache:
        ids_cache[path] = set(re.findall(r'\sid="([^"]+)"', path.read_text(encoding="utf-8")))
    return ids_cache[path]


# 1. The inbox must never appear anywhere in the published files.
needle = ("webworksa1" + "@", "gmail" + ".com", "mail" + "to:")
for f in ROOT.rglob("*"):
    if f.is_file() and ".git" not in f.parts and f.suffix in {".html", ".js", ".css", ".xml", ".txt", ".json", ".md", ".py", ".webmanifest", ".svg"}:
        t = f.read_text(encoding="utf-8", errors="ignore").lower()
        for n in needle:
            if n in t:
                problems.append(f"{f.relative_to(ROOT)}: exposes '{n}'")

for p in pages:
    html = p.read_text(encoding="utf-8")
    rel = p.relative_to(ROOT)
    # 2. Required on every page
    if 'href="https://web.works/contact"' not in html or "partner-bar" not in html:
        problems.append(f"{rel}: missing partner bar")
    if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6620975821265271" not in html:
        problems.append(f"{rel}: missing AdSense code")
    if '<meta name="google-adsense-account"' not in html:
        problems.append(f"{rel}: missing AdSense meta")
    if html.count("<h1") != 1:
        problems.append(f"{rel}: has {html.count('<h1')} h1 elements")
    if not re.search(r'<meta name="description" content="[^"]{50,}"', html):
        problems.append(f"{rel}: weak or missing meta description")
    # 3. JSON-LD parses
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block)
        except Exception as e:
            problems.append(f"{rel}: bad JSON-LD ({e})")
    # 4. Duplicate ids (the inline logo gradient is shared on purpose)
    seen = {}
    for i in re.findall(r'\sid="([^"]+)"', html):
        seen[i] = seen.get(i, 0) + 1
    for i, n in seen.items():
        if n > 1 and i != "lg":
            problems.append(f"{rel}: duplicate id '{i}'")
    # 5. Internal links and anchors
    base_dir = p.parent
    if "<base href=" in html:
        continue
    for href in re.findall(r'href="([^"]+)"', html):
        if href.startswith(("http://", "https://", "mail" + "to:", "tel:", "javascript:", "data:")):
            continue
        u = urlparse(href)
        if not u.path:
            if u.fragment and u.fragment not in ids(p):
                problems.append(f"{rel}: missing anchor #{u.fragment}")
            continue
        target = (base_dir / u.path).resolve()
        if not target.exists():
            problems.append(f"{rel}: broken link {href}")
        elif u.fragment and target.suffix == ".html" and u.fragment not in ids(target):
            problems.append(f"{rel}: missing anchor {href}")

for req in ["ads.txt", "robots.txt", "sitemap.xml", "site.webmanifest", "assets/js/data.js"]:
    if not (ROOT / req).exists():
        problems.append(f"missing {req}")
if "pub-6620975821265271, DIRECT, f08c47fec0942fa0" not in (ROOT / "ads.txt").read_text():
    problems.append("ads.txt has the wrong publisher line")

print(f"Checked {len(pages)} pages.")
if problems:
    print("\n".join(problems))
    sys.exit(1)
print("No problems found.")
