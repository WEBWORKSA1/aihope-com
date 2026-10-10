#!/usr/bin/env python3
"""AiHope.com static site builder.

How it works
------------
* Every top-level page (index.html, learn.html, ...) is its own source. The editable part
  sits between <!--BODY--> and <!--/BODY-->, and the page settings live in a
  <!--PAGE {json}--> comment just after <!--BODY-->. Edit the body in place, then run
  this script: it re-wraps every page with the shared header, partner bar, footer,
  SEO tags, AdSense code and JSON-LD.
* Blocks written as <!--@name args--> ... <!--@/name--> are regenerated from the JSON
  files in _source/data on every build (job grids, tools, videos, courses, prompts...).
* Occupation pages in /jobs/ are generated entirely from _source/data/jobs.json.
* sitemap.xml, robots.txt, ads.txt, site.webmanifest and assets/js/data.js are written too.

Usage:  python3 _source/build.py
"""
import datetime
import html
import json
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
SITE = json.loads((SRC / "site.json").read_text(encoding="utf-8"))


def load(name):
    return json.loads((SRC / "data" / f"{name}.json").read_text(encoding="utf-8"))


JOBS, TOOLS, VIDEOS, COURSES, PROMPTS = (load(n) for n in ("jobs", "tools", "videos", "courses", "prompts"))
TOOL_BY_NAME = {t["name"]: t for t in TOOLS}
JOB_BY_SLUG = {j["slug"]: j for j in JOBS}
TODAY = datetime.date.today().isoformat()
BASE = (f"https://{SITE['custom_domain']}" if SITE.get("custom_domain") else SITE["site_url"]).rstrip("/")
esc = html.escape


def r(x):
    return int(x + 0.5)


# ----------------------------------------------------------------- job maths
def job_stats(j):
    total = sum(t[1] for t in j["tasks"])
    assert total == 100, f"{j['slug']}: task shares add up to {total}, not 100"
    exp = sum(t[1] * t[2] for t in j["tasks"]) / 100
    auto = sum(t[1] * t[2] for t in j["tasks"] if t[3] == "M") / 100
    return r(exp), (r(100 * auto / exp) if exp else 0)


for _j in JOBS:
    _j["score"], _j["auto"] = job_stats(_j)
    for _a in _j["adjacent"]:
        assert _a in JOB_BY_SLUG, f"{_j['slug']}: unknown adjacent job {_a}"
    for _t in _j["tools"]:
        assert _t in TOOL_BY_NAME, f"{_j['slug']}: unknown tool {_t}"


PLURAL = {"content-writer": "content writers and copywriters", "translator": "translators and interpreters",
          "hr-specialist": "HR specialists and recruiters", "teacher": "secondary school teachers",
          "psychologist": "psychologists and therapists", "caregiver": "personal care aides and caregivers",
          "delivery-driver": "truck and delivery drivers", "chef": "chefs and cooks"}


def plural(j):
    if j["slug"] in PLURAL:
        return PLURAL[j["slug"]]
    return " ".join(w if (w.isupper() and len(w) > 1) else w.lower() for w in j["title"].split()) + "s"


def cap(phrase):
    return " ".join(w if (w.isupper() or w == "and") else w[0].upper() + w[1:] for w in phrase.split())


def band(s):
    if s < 25:
        return "low", "Low exposure"
    if s < 45:
        return "moderate", "Moderate exposure"
    if s < 60:
        return "high", "High exposure"
    return "very-high", "Very high exposure"


OUTLOOK = {
    "growing": ("Growing", "Demand for this work is expected to grow."),
    "stable": ("Stable", "Demand looks broadly stable, while the tasks inside the job change."),
    "shifting": ("Shifting", "The job is being reshaped: some work disappears, new work appears."),
    "declining": ("Declining", "Fewer of these roles are expected, so plan your next move early."),
}

NAV = [
    ("ai-job-checker.html", "Job Checker", "checker"),
    ("jobs.html", "Jobs A–Z", "jobs"),
    ("learn.html", "Learn", "learn"),
    ("tools.html", "AI Tools", "tools"),
    ("prompts.html", "Prompts", "prompts"),
    ("guides.html", "Guides", "guides"),
    ("stories.html", "Hope Stories", "stories"),
    ("contests.html", "Challenge", "contests"),
]

FOOTER = [
    ("Explore", [("ai-job-checker.html", "AI Job Exposure Checker"), ("jobs.html", "Jobs A–Z"), ("tools.html", "AI Tools Directory"), ("prompts.html", "Prompt Library"), ("videos.html", "Video Library")]),
    ("Learn", [("learn.html", "Learning Paths"), ("guides.html", "Guides"), ("stories.html", "Hope Stories"), ("methodology.html", "Methodology")]),
    ("Get involved", [("career-plan.html", "Free AI Career Plan"), ("support.html", "Support the Hope Fund"), ("contests.html", "AI Hope Challenge"), ("careers.html", "Careers & Volunteering"), ("advertise.html", "Advertise & Partner")]),
    ("About", [("about.html", "About AI Hope"), ("editorial-policy.html", "Editorial Policy"), ("contact.html", "Contact"), ("privacy.html", "Privacy Policy"), ("terms.html", "Terms of Use"), ("disclaimer.html", "Disclaimer & Trademark")]),
]

LOGO = '<img class="logo" src="{p}assets/img/logo.svg" alt="" width="36" height="36">'

ADSENSE = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + SITE["adsense_client"] + '"\n'
           '     crossorigin="anonymous"></script>')


# ----------------------------------------------------------------- chrome
def head(meta, path, prefix):
    base_tag = ""
    if meta.get("abs"):
        from urllib.parse import urlparse
        base_tag = '<base href="' + (urlparse(BASE).path.rstrip("/") + "/") + '">\n'

    title = meta["title"]
    full_title = title if "AI Hope" in title else f"{title} | AI Hope"
    canon = BASE + "/" + ("" if path == "index.html" else path)
    desc = esc(meta["description"])
    ld = [] if path != "index.html" else [
        {"@context": "https://schema.org", "@type": "Organization", "name": "AI Hope", "url": BASE + "/",
         "logo": BASE + "/assets/img/logo.svg", "description": SITE["description"]},
        {"@context": "https://schema.org", "@type": "WebSite", "name": "AI Hope", "url": BASE + "/",
         "potentialAction": {"@type": "SearchAction", "target": BASE + "/jobs.html?q={search_term_string}",
                             "query-input": "required name=search_term_string"}},
    ]
    crumbs = meta.get("crumbs")
    if crumbs:
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"}]
        for i, (name, href) in enumerate(crumbs, start=2):
            items.append({"@type": "ListItem", "position": i, "name": name, "item": BASE + "/" + href})
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": meta.get("h1", title)})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    if meta.get("type") == "article":
        ld.append({"@context": "https://schema.org", "@type": "Article", "headline": meta.get("h1", title),
                   "description": meta["description"], "datePublished": meta.get("date", TODAY),
                   "dateModified": meta.get("updated", meta.get("date", TODAY)),
                   "author": {"@type": "Organization", "name": "AI Hope Editorial Team", "url": BASE + "/about.html"},
                   "publisher": {"@type": "Organization", "name": "AI Hope", "logo": {"@type": "ImageObject", "url": BASE + "/assets/img/logo.svg"}},
                   "mainEntityOfPage": canon})
    if meta.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in meta["faq"]]})
    if meta.get("ld"):
        ld.extend(meta["ld"])
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = '<meta name="robots" content="noindex,follow">' if meta.get("noindex") else '<meta name="robots" content="index,follow,max-image-preview:large">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{base_tag}<title>{esc(full_title)}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canon}">
<meta name="google-adsense-account" content="{SITE['adsense_client']}">
{ADSENSE}
<meta property="og:type" content="{'article' if meta.get('type') == 'article' else 'website'}">
<meta property="og:site_name" content="AI Hope">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#141938">
<link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{prefix}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
<script>try{{var t=localStorage.getItem('aih-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
{ld_html}
<script src="{prefix}assets/js/config.js" defer></script>
<script src="{prefix}assets/js/data.js" defer></script>
<script src="{prefix}assets/js/app.js" defer></script>
</head>"""


def header(nav, prefix):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{prefix}{href}"{cur if key == nav else ""}>{label}</a>' for href, label, key in NAV)
    return f"""<body data-prefix="{prefix}">
<a class="skip" href="#main">Skip to content</a>
<div class="partner-bar"><div class="wrap"><a href="{SITE['partner_link']}" target="_blank" rel="noopener">{esc(SITE['partner_text'])} <span aria-hidden="true">→</span></a></div></div>
<header class="site-header">
  <div class="wrap header-in">
    <a class="brand" href="{prefix}index.html" aria-label="AI Hope home">{LOGO.format(p=prefix)}<span>AI<b>Hope</b></span></a>
    <nav class="nav" id="nav" aria-label="Main">{links}<a class="nav-support" href="{prefix}support.html">Support</a></nav>
    <div class="header-actions">
      <button class="icon-btn" type="button" data-theme-toggle aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
      <a class="btn btn-sun btn-sm hide-sm" href="{prefix}career-plan.html">Free AI career plan</a>
      <button class="icon-btn menu-btn" type="button" aria-controls="nav" aria-expanded="false" aria-label="Open menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
  </div>
</header>
<main id="main">"""


def footer(prefix, meta):
    cols = "".join(
        f'<div><h3>{t}</h3><ul>' + "".join(f'<li><a href="{prefix}{h}">{l}</a></li>' for h, l in links) + "</ul></div>"
        for t, links in FOOTER)
    cta = "" if meta.get("nocta") else (
        f'<a class="sticky-cta" href="{prefix}career-plan.html" data-sticky-cta>Get my free AI career plan <span aria-hidden="true">→</span></a>')
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <a class="brand" href="{prefix}index.html">{LOGO.format(p=prefix)}<span>AI<b>Hope</b></span></a>
        <p>{esc(SITE['tagline'])}. Free tools, honest guidance and practical skills for people whose work is changing because of AI.</p>
        <form class="news-form" data-form="newsletter" data-subject="New newsletter subscriber" novalidate>
          <label for="nf-email-{meta['_id']}">Get the weekly AI Hope brief: one skill, one tool, one hopeful story.</label>
          <div class="inline-field"><input id="nf-email-{meta['_id']}" type="email" name="email" placeholder="you@example.com" required autocomplete="email"><button class="btn btn-sun" type="submit">Subscribe</button></div>
          <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
          <input type="hidden" name="source" value="footer newsletter">
          <p class="form-note">Free. Unsubscribe anytime. We never sell your email.</p>
          <p class="form-status" role="status" aria-live="polite"></p>
        </form>
      </div>
      <div class="footer-cols">{cols}</div>
    </div>
    <div class="footer-bottom">
      <p>AI Hope is an independent educational publication about AI and work. “AI Hope” is used as a descriptive name; we are not affiliated with, endorsed by or sponsored by any company, product, charity or organization with a similar name, or by any AI company or tool we mention. All trademarks belong to their owners. See our <a href="{prefix}disclaimer.html">Disclaimer &amp; Trademark notice</a>.</p>
      <p>Content is general information, not career, legal, financial or medical advice. Ads are served by Google AdSense; some links may be affiliate links. © <span data-year>{datetime.date.today().year}</span> AiHope.com. Interested in this website, the domain, sponsorship, advertising or partnership? <a href="{SITE['partner_link']}" target="_blank" rel="noopener">Contact us</a>.</p>
    </div>
  </div>
</footer>
{cta}
<div class="cookie" data-cookie hidden><p>We use cookies to serve ads (Google AdSense) and understand how the site is used. See our <a href="{prefix}privacy.html">Privacy Policy</a>.</p><button class="btn btn-ink btn-sm" type="button" data-cookie-ok>OK</button></div>
</body>
</html>
"""


# ----------------------------------------------------------------- blocks
def job_card(j, prefix=""):
    cls, label = band(j["score"])
    return (f'<a class="job-card" href="{prefix}jobs/{j["slug"]}.html" data-item data-tags="{esc(j["cat"])}" data-text="{esc(j["title"].lower())}">'
            f'<span class="job-card-top"><span class="pill pill-{cls}">{label}</span><span class="out out-{j["outlook"]}">{OUTLOOK[j["outlook"]][0]}</span></span>'
            f'<strong>{esc(j["title"])}</strong>'
            f'<span class="meter" aria-hidden="true"><span style="width:{j["score"]}%" class="m-{cls}"></span></span>'
            f'<span class="job-card-score"><b>{j["score"]}</b>/100 exposure · {j["auto"]}% automation</span></a>')


def block_jobs_grid(args, prefix):
    cats = sorted({j["cat"] for j in JOBS})
    chips = '<button class="chip" type="button" data-chip="" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" type="button" data-chip="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats)
    cards = "".join(job_card(j, prefix) for j in sorted(JOBS, key=lambda x: x["title"]))
    return (f'<div class="filter" data-filter><div class="filter-bar"><input type="search" placeholder="Search {len(JOBS)} jobs, e.g. nurse, analyst…" aria-label="Search jobs" data-filter-q>'
            f'<div class="chips" role="group" aria-label="Filter by field">{chips}</div></div>'
            f'<div class="job-grid">{cards}</div><p class="empty" data-empty hidden>No jobs match. Try the <a href="ai-job-checker.html#custom">custom checker</a> for any role.</p></div>')


def block_jobs_popular(args, prefix):
    picks = ["software-developer", "registered-nurse", "content-writer", "accountant", "teacher", "graphic-designer",
             "customer-service-rep", "electrician"]
    return '<div class="job-grid">' + "".join(job_card(JOB_BY_SLUG[s], prefix) for s in picks) + "</div>"


def block_jobs_extremes(args, prefix):
    hi = sorted(JOBS, key=lambda j: -j["score"])[:6]
    lo = sorted(JOBS, key=lambda j: j["score"])[:6]

    def lst(items):
        return "<ol class='rank'>" + "".join(
            f'<li><a href="{prefix}jobs/{j["slug"]}.html">{esc(j["title"])}</a><b>{j["score"]}</b></li>' for j in items) + "</ol>"
    return (f'<div class="grid-2"><div class="card"><h3>Most exposed to AI</h3>{lst(hi)}</div>'
            f'<div class="card"><h3>Least exposed to AI</h3>{lst(lo)}</div></div>')


def block_tools_grid(args, prefix):
    cats = sorted({t["cat"] for t in TOOLS})
    chips = '<button class="chip" type="button" data-chip="" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" type="button" data-chip="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats)
    cards = "".join(
        f'<article class="tool" data-item data-tags="{esc(t["cat"])}" data-text="{esc((t["name"] + " " + t["desc"] + " " + t["best"]).lower())}">'
        f'<div class="tool-top"><span class="tool-ico" aria-hidden="true">{esc(t["name"][0])}</span><div><h3>{esc(t["name"])}</h3><span class="tag">{esc(t["cat"])}</span> <span class="tag tag-soft">{esc(t["price"])}</span></div></div>'
        f'<p>{esc(t["desc"])}</p><p class="best"><b>Best for:</b> {esc(t["best"])}</p>'
        f'<a class="link-arrow" href="{t["url"]}" target="_blank" rel="noopener nofollow">Visit {esc(t["name"])} <span aria-hidden="true">↗</span></a></article>'
        for t in TOOLS)
    return (f'<div class="filter" data-filter><div class="filter-bar"><input type="search" placeholder="Search {len(TOOLS)} tools, e.g. meetings, resume…" aria-label="Search tools" data-filter-q>'
            f'<div class="chips" role="group" aria-label="Filter by category">{chips}</div></div>'
            f'<div class="tool-grid">{cards}</div><p class="empty" data-empty hidden>No tools match that search.</p></div>')


def video_card(v):
    return (f'<figure class="video" data-item data-tags="{esc(v["cat"])}" data-text="{esc((v["title"] + " " + v["channel"]).lower())}">'
            f'<button class="yt" type="button" data-yt="{v["id"]}" aria-label="Play video: {esc(v["title"])}">'
            f'<img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360"><span class="yt-play" aria-hidden="true"></span></button>'
            f'<figcaption><strong>{esc(v["title"])}</strong><span>{esc(v["channel"])} · {esc(v["level"])}</span></figcaption></figure>')


def block_videos(args, prefix):
    a = args.split()
    limit = int(a[0]) if a and a[0].isdigit() else None
    vids = VIDEOS[:limit] if limit else VIDEOS
    if limit:
        return '<div class="video-grid">' + "".join(video_card(v) for v in vids) + "</div>"
    cats = []
    for v in VIDEOS:
        if v["cat"] not in cats:
            cats.append(v["cat"])
    chips = '<button class="chip" type="button" data-chip="" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" type="button" data-chip="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats)
    return (f'<div class="filter" data-filter><div class="filter-bar"><input type="search" placeholder="Search {len(VIDEOS)} videos…" aria-label="Search videos" data-filter-q>'
            f'<div class="chips" role="group" aria-label="Filter by topic">{chips}</div></div>'
            f'<div class="video-grid">' + "".join(video_card(v) for v in vids) + '</div><p class="empty" data-empty hidden>No videos match.</p></div>')


def block_courses(args, prefix):
    path = args.strip()
    rows = [c for c in COURSES if not path or c["path"] == path]
    return ('<div class="table-wrap"><table class="table"><thead><tr><th>Course</th><th>Provider</th><th>Level</th><th>Cost</th></tr></thead><tbody>'
            + "".join(f'<tr><td><a href="{c["url"]}" target="_blank" rel="noopener">{esc(c["name"])}</a><small>{esc(c["note"])}</small></td>'
                      f'<td>{esc(c["by"])}</td><td>{esc(c["level"])}</td><td><span class="tag {"tag-free" if c["price"].startswith("Free") else ""}">{esc(c["price"])}</span></td></tr>' for c in rows)
            + "</tbody></table></div>")


def block_prompts(args, prefix):
    a = args.split()
    limit = int(a[0]) if a and a[0].isdigit() else None
    items = PROMPTS[:limit] if limit else PROMPTS
    cats = []
    for p in PROMPTS:
        if p["cat"] not in cats:
            cats.append(p["cat"])
    cards = "".join(
        f'<article class="prompt" data-item data-tags="{esc(p["cat"])}" data-text="{esc((p["title"] + " " + p["prompt"]).lower())}">'
        f'<div class="prompt-top"><span class="tag">{esc(p["cat"])}</span><button class="copy-btn" type="button" data-copy>Copy</button></div>'
        f'<h3>{esc(p["title"])}</h3><p class="prompt-text">{esc(p["prompt"])}</p></article>' for p in items)
    if limit:
        return f'<div class="prompt-grid">{cards}</div>'
    chips = '<button class="chip" type="button" data-chip="" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" type="button" data-chip="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats)
    return (f'<div class="filter" data-filter><div class="filter-bar"><input type="search" placeholder="Search {len(PROMPTS)} prompts…" aria-label="Search prompts" data-filter-q>'
            f'<div class="chips" role="group" aria-label="Filter by category">{chips}</div></div>'
            f'<div class="prompt-grid">{cards}</div><p class="empty" data-empty hidden>No prompts match.</p></div>')


def block_stats(args, prefix):
    stats = [
        ("170M", "new jobs expected worldwide by 2030, against 92M displaced", "World Economic Forum, Future of Jobs Report 2025"),
        ("~40%", "of global jobs are exposed to AI, about 60% in advanced economies", "IMF, Gen-AI and the Future of Work, 2024"),
        ("1 in 4", "workers globally hold a job with some generative-AI exposure", "International Labour Organization, 2025"),
        ("56%", "wage premium for jobs that require AI skills", "PwC, 2025 Global AI Jobs Barometer"),
    ]
    return '<div class="stats">' + "".join(
        f'<div class="stat"><b>{n}</b><span>{t}</span><small>{s}</small></div>' for n, t, s in stats) + "</div>"


def block_lead_band(args, prefix):
    return (f'<aside class="lead-band"><div><span class="eyebrow">Free · 3 minutes · no account</span>'
            f'<h2>Get your personal AI career plan</h2><p>Answer five quick questions and get a plan built around your job: what AI will change, the skills to learn first, free courses and a 90-day roadmap.</p></div>'
            f'<a class="btn btn-sun btn-lg" href="{prefix}career-plan.html">Build my free plan <span aria-hidden="true">→</span></a></aside>')


def block_contest(args, prefix):
    c = SITE["contest"]
    return (f'<div class="contest-facts"><div><b>{c["prize_pool"]}</b><span>prize pool</span></div><div><b>{c["opens"]}</b><span>entries open</span></div>'
            f'<div><b>{c["closes"]}</b><span>entries close</span></div><div><b>{c["winners"]}</b><span>winners announced</span></div></div>')


BLOCKS = {
    "jobs-grid": block_jobs_grid, "jobs-popular": block_jobs_popular, "jobs-extremes": block_jobs_extremes,
    "tools-grid": block_tools_grid, "videos": block_videos, "courses": block_courses, "prompts": block_prompts,
    "stats": block_stats, "lead-band": block_lead_band, "contest": block_contest,
}
BLOCK_RE = re.compile(r"<!--@([\w-]+)([^>]*?)-->(.*?)<!--@/\1-->", re.S)


def render_blocks(body, prefix):
    def one(m):
        out = BLOCKS[m.group(1)](m.group(2), prefix)
        # keep lines short so files stay easy to diff and edit
        out = re.sub(r'(</article>|</figure>|</tr>|</li>|</div>(?=<div)|</a>(?=<a )|</button>(?=<button))', "\\1\n", out)
        return f"<!--@{m.group(1)}{m.group(2)}-->{out}<!--@/{m.group(1)}-->"
    return BLOCK_RE.sub(one, body)


def faq_from(body):
    out = []
    for m in re.finditer(r'<details class="faq"[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>', body, re.S):
        q = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        a = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        out.append((html.unescape(q), html.unescape(a)))
    return out


# ----------------------------------------------------------------- occupation pages
def job_page(j):
    cls, label = band(j["score"])
    olabel, otext = OUTLOOK[j["outlook"]]
    tasks = sorted(j["tasks"], key=lambda t: -t[2])
    top, safe = tasks[:2], sorted(j["tasks"], key=lambda t: t[2])[:2]
    t = j["title"]
    pl = plural(j)
    band_text = {
        "low": f"For {pl}, most of the working week is hands-on, relational or physical work that today's AI cannot do. AI is a helper here, not a replacement.",
        "moderate": f"AI can take over or speed up a meaningful slice of the week for {pl}, but the core of the job still depends on human judgment, relationships or physical work.",
        "high": f"A large share of the tasks done by {pl} can already be done or accelerated by AI. The job is unlikely to vanish, but people who do not adapt will feel the pressure first.",
        "very-high": f"Most of the tasks that fill the week for {pl} can already be automated or heavily assisted by AI. This is the moment to reshape the role around the parts AI cannot do, or to plan a move.",
    }[cls]
    rows = "".join(
        f'<tr><td>{esc(n)}</td><td>{s}%</td><td><span class="meter meter-sm"><span style="width:{a}%" class="m-{band(a)[0]}"></span></span> {a}</td>'
        f'<td><span class="tag {"tag-warn" if m == "M" else "tag-soft"}">{"Can automate" if m == "M" else "Assists"}</span></td></tr>' for n, s, a, m in j["tasks"])
    skills = "".join(f"<li>{esc(s)}</li>" for s in j["skills"])
    tools = "".join(
        f'<a class="mini-tool" href="{TOOL_BY_NAME[n]["url"]}" target="_blank" rel="noopener nofollow"><b>{esc(n)}</b><span>{esc(TOOL_BY_NAME[n]["desc"])}</span></a>' for n in j["tools"])
    adj = "".join(job_card(JOB_BY_SLUG[a], "../") for a in j["adjacent"])
    path_key = "build" if j["cat"] == "Tech & Data" else "start"
    courses = [c for c in COURSES if c["path"] == path_key][:2] + [c for c in COURSES if c["path"] == "work"][:1]
    clist = "".join(f'<li><a href="{c["url"]}" target="_blank" rel="noopener">{esc(c["name"])}</a> ({esc(c["by"])}, {esc(c["price"].lower())})</li>' for c in courses)
    faq = [
        (f"Will AI replace {pl}?",
         f"Not entirely. On AI Hope's task-based estimate, this job scores {j['score']}/100 for AI exposure ({label.lower()}). "
         f"{otext} The biggest changes are in {top[0][0].lower()} and {top[1][0].lower()}."),
        (f"Which tasks can AI already do for {pl}?",
         f"AI is strongest at {top[0][0].lower()} (exposure {top[0][2]}/100) and {top[1][0].lower()} (exposure {top[1][2]}/100). "
         f"It has the least impact on {safe[0][0].lower()} and {safe[1][0].lower()}."),
        (f"What should {pl} learn to stay ahead of AI?",
         "Focus on " + ", ".join(s[0].lower() + s[1:] for s in j["skills"][:3]) + f" and {j['skills'][3][0].lower() + j['skills'][3][1:]}."),
    ]
    faq_html = "".join(f'<details class="faq"><summary>{esc(q)}</summary><div><p>{esc(a)}</p></div></details>' for q, a in faq)
    h1 = f"Will AI replace {pl}?"
    meta = {"title": "", "description": f"{t}: AI exposure score {j['score']}/100 ({label.lower()}). See which tasks AI can do, the skills to learn, AI tools to use and safer adjacent careers.",
            "nav": "jobs", "crumbs": [["Jobs A–Z", "jobs.html"]], "h1": h1, "faq": faq, "type": "article", "date": "2026-10-10", "_id": j["slug"]}
    meta["title"] = f"Will AI Replace {cap(pl)}? Exposure Score {j['score']}/100, Skills & Safer Paths"
    body = f"""
<article class="job-page">
  <section class="page-hero page-hero-job">
    <div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a> / <a href="../jobs.html">Jobs A–Z</a> / <span>{esc(t)}</span></nav>
      <div class="job-hero">
        <div>
          <span class="eyebrow">{esc(j['cat'])} · updated {meta['date']}</span>
          <h1>{esc(h1)}</h1>
          <p class="lede">{esc(j['summary'])}</p>
          <div class="share" data-share><button class="btn btn-ghost btn-sm" type="button" data-share-btn>Share this result</button></div>
        </div>
        <div class="score-card">
          <div class="dial dial-{cls}" style="--v:{j['score']}"><b>{j['score']}</b><span>/100</span></div>
          <p class="score-label pill pill-{cls}">{label}</p>
          <dl><div><dt>Automation share</dt><dd>{j['auto']}%</dd></div><div><dt>Augmentation share</dt><dd>{100 - j['auto']}%</dd></div><div><dt>Outlook</dt><dd><span class="out out-{j['outlook']}">{olabel}</span></dd></div></dl>
          <a class="btn btn-sun btn-block" href="../career-plan.html?job={j['slug']}">Get my plan for this job</a>
        </div>
      </div>
    </div>
  </section>
  <div class="wrap content-grid">
    <div class="prose">
      <h2>The short answer</h2>
      <p>{esc(band_text)} The score is an estimate of how much of the typical working week involves tasks that current AI tools can perform or speed up. It is <strong>not</strong> a probability that the job disappears. Read <a href="../methodology.html">how we calculate it</a>.</p>
      <h2>Task by task: where AI fits in the work of {esc(pl)}</h2>
      <div class="table-wrap"><table class="table"><thead><tr><th>Task</th><th>Share of time</th><th>AI exposure</th><th>Effect</th></tr></thead><tbody>{rows}</tbody></table></div>
      <p>“Can automate” means AI can increasingly do the task with light human review. “Assists” means AI makes a person faster or better, but a human still does the work and owns the result.</p>
      <div class="ad-slot" data-ad="in-article"></div>
      <h2>What this means for you</h2>
      <p>AI is most likely to take over <strong>{esc(top[0][0].lower())}</strong> and <strong>{esc(top[1][0].lower())}</strong>. If those tasks fill most of your days, start handing them to AI tools now, on your terms, and use the time you save to grow the parts of the job that stay human.</p>
      <p>Your most durable work is <strong>{esc(safe[0][0].lower())}</strong> and <strong>{esc(safe[1][0].lower())}</strong>. These depend on trust, physical presence, context or accountability, which is why employers keep paying for them even as tools improve.</p>
      <h2>Skills to learn next</h2>
      <ul class="check">{skills}</ul>
      <h3>Free and low-cost courses to start</h3>
      <ul>{clist}</ul>
      <p>See all <a href="../learn.html">learning paths</a> and the <a href="../videos.html">video library</a>.</p>
      <h2>Job outlook</h2>
      <p><span class="out out-{j['outlook']}">{olabel}</span> {esc(otext)} {esc(j['note'])}</p>
      <h2>Frequently asked questions</h2>
      {faq_html}
      <p class="small muted">Sources and assumptions: task mix and exposure ratings are AI Hope editorial estimates informed by research from the ILO (2025), the IMF (2024), the World Economic Forum (Future of Jobs Report 2025) and published academic exposure studies. Your own job may differ. Try the <a href="../ai-job-checker.html#custom">custom checker</a> to score your actual week.</p>
    </div>
    <aside class="side">
      <div class="card"><h3>AI tools for {esc(pl)}</h3><div class="mini-tools">{tools}</div><a class="link-arrow" href="../tools.html">All AI tools →</a></div>
      <div class="ad-slot" data-ad="sidebar"></div>
      <div class="card card-sun"><h3>Want a personal plan?</h3><p>Get a free roadmap for your exact situation: skills, courses and a 90-day plan.</p><a class="btn btn-ink btn-block" href="../career-plan.html?job={j['slug']}">Start free →</a></div>
    </aside>
  </div>
  <section class="section section-soft"><div class="wrap"><h2>Safer adjacent careers</h2><p class="muted">Roles that reuse much of your experience. Scores are on the same scale.</p><div class="job-grid">{adj}</div></div></section>
  <div class="wrap">{block_lead_band('', '../')}</div>
</article>"""
    return meta, body


# ----------------------------------------------------------------- assemble
PAGE_RE = re.compile(r"<!--BODY-->\s*<!--PAGE (\{.*?\})-->(.*)<!--/BODY-->", re.S)


def wrap(meta, body, path, prefix):
    return head(meta, path, prefix) + "\n" + header(meta.get("nav", ""), prefix) + "\n<!--BODY-->\n<!--PAGE " + \
        json.dumps({k: v for k, v in meta.items() if not k.startswith("_") and k != "faq"}, ensure_ascii=False) + "-->" + body + "<!--/BODY-->\n" + footer(prefix, meta)


def main():
    pages = []
    for f in sorted(ROOT.glob("*.html")):
        txt = f.read_text(encoding="utf-8")
        m = PAGE_RE.search(txt)
        if not m:
            print("skip (no BODY markers):", f.name)
            continue
        meta = json.loads(m.group(1))
        meta["_id"] = f.stem
        body = render_blocks(m.group(2), "")
        meta["faq"] = faq_from(body)
        f.write_text(wrap(meta, body, f.name, ""), encoding="utf-8")
        pages.append((f.name, meta))
    jobs_dir = ROOT / "jobs"
    jobs_dir.mkdir(exist_ok=True)
    for j in JOBS:
        meta, body = job_page(j)
        path = f"jobs/{j['slug']}.html"
        body = re.sub(r'(</tr>|</li>|</a>(?=<a ))', "\\1\n", body)
        (ROOT / path).write_text(wrap(meta, body, path, "../"), encoding="utf-8")
        pages.append((path, meta))
    # data for the interactive checker and plan builder
    data = {"jobs": [{"s": j["slug"], "t": j["title"], "c": j["cat"], "score": j["score"], "auto": j["auto"], "tasks": j["tasks"],
                      "skills": j["skills"], "adj": j["adjacent"], "out": j["outlook"], "tools": j["tools"]} for j in sorted(JOBS, key=lambda x: x["title"])],
            "courses": COURSES}
    (ROOT / "assets/js/data.js").write_text("/* generated by _source/build.py: do not edit */\nwindow.AIH_DATA=" + "{\"jobs\":[\n" + ",\n".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in data["jobs"]) + "],\n\"courses\":[\n" + ",\n".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in data["courses"]) + "]};\n", encoding="utf-8")
    # sitemap
    urls = []
    for path, meta in pages:
        if meta.get("noindex"):
            continue
        loc = BASE + "/" + ("" if path == "index.html" else path)
        pri = "1.0" if path == "index.html" else ("0.7" if path.startswith("jobs/") else "0.8")
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><priority>{pri}</priority></url>")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /_source/\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    pub = SITE["adsense_client"].replace("ca-", "")
    (ROOT / "ads.txt").write_text(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(json.dumps({"name": "AI Hope", "short_name": "AI Hope", "start_url": "./index.html", "display": "standalone",
                                                       "background_color": "#FFFBF5", "theme_color": "#141938",
                                                       "icons": [{"src": "assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, indent=2), encoding="utf-8")
    if SITE.get("custom_domain"):
        (ROOT / "CNAME").write_text(SITE["custom_domain"] + "\n", encoding="utf-8")
    print(f"Built {len(pages)} pages ({len(JOBS)} occupation pages). Base URL: {BASE}")


if __name__ == "__main__":
    main()
