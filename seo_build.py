#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
craftfee SEO helper — run after editing pages to keep discoverability tight.

What it does (all idempotent):
  1. Generate public/sitemap/index.html — one page that lists EVERY page on the
     site. This is the #1 indexing trick from 哥飞: Google trusts following links
     far more than it trusts sitemap.xml. A single human-readable sitemap page
     that links to all pages is the strongest "discover everything" signal.
  2. Inject a "All Pages" link into the footer of every page (so the sitemap
     page is itself reachable by crawling).
  3. Inject a "Related Etsy fee guides" hub into the 9 guide pages (internal
     linking — 哥飞: internal links matter as much as external ones).

Run:  python seo_build.py
Safe: never touches URLs, only adds new nodes/links.
"""

import os
import re
import json
import datetime
import hashlib
import subprocess
from html import unescape as html_unescape

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, "public")
DOMAIN = "https://craftfee.com"

# url -> (priority, changefreq) for the XML sitemap; everything else is 0.8/monthly
SITEMAP_PRIORITY = {
    "/": ("1.0", "monthly"),
    "/etsy-fee-calculator/": ("0.9", "monthly"),
    "/etsy-shipping-calculator/": ("0.9", "monthly"),
    "/etsy-profit-calculator/": ("0.9", "monthly"),
    "/etsy-pricing-calculator/": ("0.9", "monthly"),
    "/sitemap/": ("0.9", "monthly"),
    "/about/": ("0.3", "yearly"),
    "/contact/": ("0.3", "yearly"),
    "/privacy/": ("0.2", "yearly"),
}
SITEMAP_DEFAULT = ("0.8", "monthly")

# url -> (category label, short blurb)  used for the related-guides hub
GUIDES = {
    "/etsy-fees-uk/": ("Etsy fees for UK sellers",
                       "UK rate, the 0.48% regulatory fee, and the VAT trap explained."),
    "/etsy-fees-eu/": ("Etsy fees in the EU",
                       "One processing rate, six VAT rates, and three countries with a regulatory fee."),
    "/etsy-fees-by-country/": ("Etsy fees by country",
                               "Canada, Australia and Germany side by side — two-rate processing, the regulatory fee, and VAT or GST on Etsy's own fees."),
    "/etsy-fees-canada/": ("Etsy fees for Canadian sellers",
                           "Every CAD rate, the 0.50% regulatory fee, and the GST/HST decisions, worked through in real numbers."),
    "/etsy-fees-australia/": ("Etsy fees for Australian sellers",
                              "Every AUD rate and the GST decisions, worked through in real numbers — no regulatory fee down here."),
    "/etsy-fees-germany/": ("Etsy fees for German sellers",
                            "The 19% VAT on Etsy's own fees, worked line by line — the rate most calculators get wrong."),
    "/etsy-shipping-calculator/": ("Etsy shipping calculator",
                                   "Why Etsy charges fees on your shipping too, and what free shipping really costs."),
    "/etsy-vat-on-fees/": ("VAT on Etsy fees",
                           "Why Etsy taxes its own fees, which countries a VAT ID switches off, and which it does not."),
    "/etsy-tax/": ("Etsy tax — what Etsy collects for you",
                   "Sales tax Etsy remits automatically, VAT and GST abroad, the 1099-K, and the income tax Etsy never touches."),
    "/etsy-refund-fee/": ("Refund fees, line by line",
                          "Which fees come back when you refund, and which never do."),
    "/etsy-regulatory-operating-fee/": ("The regulatory operating fee",
                                        "The percentage that only exists in some countries, reset 22 June 2026."),
    "/offsite-ads/": ("Offsite Ads explained",
                      "The 15% fee, the $100 cap, and when you can and cannot opt out."),
    "/listing-fee/": ("Listing fees, per item",
                      "The $0.20 charged more often than sellers expect."),
    "/how-to-price/": ("How to price on Etsy",
                      "Price from the margin you want, with worked examples."),
    "/etsy-profit-calculator/": ("Etsy profit calculator",
                                 "Your real profit and margin after every fee, with a margin grade and break-even price."),
    "/etsy-pricing-calculator/": ("Etsy pricing calculator",
                                  "Price from the margin you want — solve the listing price that covers every fee, with category benchmarks."),
}

# ordered sections for the HTML sitemap page
SECTIONS = [
    ("Start here", ["/", "/etsy-fee-calculator/"]),
    ("Country & VAT guides", ["/etsy-fees-uk/", "/etsy-fees-eu/", "/etsy-fees-by-country/",
                              "/etsy-fees-canada/", "/etsy-fees-australia/",
                              "/etsy-fees-germany/", "/etsy-vat-on-fees/"]),
    ("Taxes", ["/etsy-tax/"]),
    ("Fee & pricing guides", ["/etsy-refund-fee/", "/etsy-regulatory-operating-fee/",
                              "/offsite-ads/", "/listing-fee/", "/how-to-price/",
                              "/etsy-shipping-calculator/", "/etsy-profit-calculator/",
                              "/etsy-pricing-calculator/"]),
    ("About", ["/about/", "/contact/", "/privacy/"]),
]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def meta(html, name):
    m = re.search(r'<meta name="%s" content="(.*?)">' % name, html, re.S)
    return m.group(1).strip() if m else ""


def title_of(html):
    """<title> 不是 meta 标签，必须单独取；取不到会让 sitemap 页 h3 全空。"""
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    return m.group(1).strip() if m else ""


def url_of(path):
    rel = os.path.relpath(path, PUBLIC).replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    # strip trailing index.html
    rel = rel[:-len("index.html")].rstrip("/")
    return "/" + rel + "/"


def build_sitemap_html(pages):
    """pages: list of (url, title, desc)"""
    info = {u: (t, d) for u, t, d in pages}
    sections_html = ""
    for label, urls in SECTIONS:
        cards = ""
        for u in urls:
            if u not in info:
                continue
            t, d = info[u]
            d = (d[:150] + "…") if len(d) > 152 else d
            cards += ('<a href="%s"><div class="k">%s</div><h3>%s</h3><p>%s</p></a>'
                      % (u, label, t, d))
        if cards:
            sections_html += (
                '  <h2 style="margin-top:36px">%s</h2>\n  <div class="hub">%s</div>\n' % (label, cards)
            )
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>All Etsy seller fee guides &amp; calculator — sitemap</title>
<meta name="description" content="Every page on this site in one place: the Etsy fee calculator, the country guides for the UK, EU, Canada and Australia, and the fee and pricing guides.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="https://craftfee.com/sitemap/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CraftFee">
<meta property="og:title" content="All Etsy seller fee guides &amp; calculator — sitemap">
<meta property="og:description" content="Every page on this site in one place: the Etsy fee calculator and all the plain-English fee and pricing guides that go with it.">
<meta property="og:url" content="https://craftfee.com/sitemap/">
<meta property="og:image" content="https://craftfee.com/assets/og-image-craftfee.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="All Etsy seller fee guides &amp; calculator — sitemap">
<meta name="twitter:description" content="Every page on this site in one place: the Etsy fee calculator and all the plain-English fee and pricing guides that go with it.">
<meta name="twitter:image" content="https://craftfee.com/assets/og-image-craftfee.png">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"WebSite","name":"CraftFee","url":"https://craftfee.com/sitemap/","description":"A complete list of every page on the site."}
</script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',wait_for_update:500});</script>
</head>
<body>

<header class="site-head">
  <div class="wrap">
    <a class="brand" href="/">Craft<i>Fee</i></a>
    <nav class="nav">
      <a href="/etsy-fee-calculator/">Fee Calculator</a>
      <a href="/etsy-fees-uk/">UK &amp; VAT</a>
      <a href="/etsy-fees-eu/">EU &amp; VAT</a>
      <a href="/etsy-fees-by-country/">By Country</a>
      <a href="/etsy-shipping-calculator/">Shipping</a>
      <a href="/etsy-profit-calculator/">Profit</a>
      <a href="/etsy-pricing-calculator/">Price</a>
      <a href="/offsite-ads/">Offsite Ads</a>
      <a href="/listing-fee/">Listing Fees</a>
      <a href="/how-to-price/">Pricing Guide</a>
    </nav>
  </div>
</header>

<main>
<div class="wrap">
  <div class="eyebrow">SITE INDEX</div>
  <h1>All guides &amp; tools on this site</h1>
  <p class="lede">One page that links to every calculator and guide. If a page exists, it is listed here.</p>
%s
</div>
</main>

<footer class="site-foot">
  <div class="wrap">
    <div class="fb">
      <a href="/">Home</a>
      <a href="/etsy-fee-calculator/">Fee Calculator</a>
      <a href="/etsy-fees-uk/">UK &amp; VAT</a>
      <a href="/etsy-fees-eu/">EU &amp; VAT</a>
      <a href="/etsy-fees-by-country/">By Country</a>
      <a href="/etsy-shipping-calculator/">Shipping</a>
      <a href="/etsy-profit-calculator/">Profit Calculator</a>
      <a href="/etsy-pricing-calculator/">Pricing Calculator</a>
      <a href="/offsite-ads/">Offsite Ads</a>
      <a href="/listing-fee/">Listing Fees</a>
      <a href="/etsy-regulatory-operating-fee/">Regulatory Fee</a>
      <a href="/etsy-refund-fee/">Refund Fees</a>
      <a href="/etsy-vat-on-fees/">VAT on Fees</a>
      <a href="/etsy-tax/">Etsy Tax</a>
      <a href="/how-to-price/">Pricing Guide</a>
      <a href="/about/">About</a>
      <a href="/contact/">Contact</a>
      <a href="/privacy/">Privacy</a>
    </div>
    <p>CraftFee is an independent site. It is not affiliated with, endorsed by, or connected to Etsy, Inc. Etsy is a trademark of Etsy, Inc., used here only to identify the marketplace these tools describe. Fee rates are published for reference and change from time to time — always confirm against Etsy's official Fees &amp; Payments Policy. Nothing here is financial or tax advice.</p>
  </div>
</footer>

<script src="/assets/cookie-consent.js" defer></script>
</body>
</html>
""" % sections_html


def strip_footer_sitemap_link(html):
    # /sitemap/ 已 noindex——页脚是全站模板，每页送一条内链会稀释；
    # 哥飞 10-28：删除页脚链接，首页正文那条单页链接保留。
    line = '      <a href="/sitemap/">All Pages</a>\n'
    if line in html:
        return html.replace(line, "", 1)
    return html


RELATED_BLOCK_RE = re.compile(
    r"\n  <!-- related-guides -->\n  <div class=\"related\"[^>]*>\n.*?\n  </div>\n", re.S
)


def inject_related(html, self_url):
    """Rebuild the related-guides hub on every guide page.

    Earlier this only ran once and skipped pages that already had a block, which
    meant a new guide never appeared in the hubs of the old ones. It now strips
    the previous block and re-renders, so adding a page to GUIDES propagates it
    site-wide on the next build.
    """
    html = RELATED_BLOCK_RE.sub("", html, count=1)
    others = [(u, t, d) for u, (t, d) in GUIDES.items() if u != self_url]
    cards = "".join(
        '<a href="%s"><div class="k">GUIDE</div><h3>%s</h3><p>%s</p></a>' % (u, t, d)
        for u, t, d in others
    )
    block = (
        '\n  <!-- related-guides -->\n'
        '  <div class="related" style="margin-top:44px">\n'
        '    <h2>Related Etsy fee guides</h2>\n'
        '    <div class="hub">%s</div>\n'
        '  </div>\n' % cards
    )
    if "</main>" not in html:
        return html
    return html.replace("</main>", block + "</main>", 1)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CRUMB_SCHEMA_MARK = "<!-- breadcrumb-schema -->"

# ---- Analytics — fill either value in and re-run to switch tracking on --------
# Cloudflare Web Analytics token: cookieless, no consent banner required, free.
#   Cloudflare dashboard -> Analytics & Logs -> Web Analytics -> Add a site
#   -> "Enable with JS snippet" -> copy the token value.
CF_BEACON_TOKEN = ""
# GA4 measurement ID, e.g. "G-XXXXXXXXXX". Every page already ships Consent Mode v2
# defaults (analytics_storage: denied), so Google only records after a visitor opts in.
GA4_ID = ""

ANALYTICS_MARK = "<!-- analytics -->"


def analytics_snippet():
    if not (CF_BEACON_TOKEN or GA4_ID):
        return ""
    out = []
    if GA4_ID:
        out.append(
            '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>\n'
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}"
            "gtag('js',new Date());gtag('config','%s');</script>" % (GA4_ID, GA4_ID)
        )
    if CF_BEACON_TOKEN:
        out.append(
            '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
            "data-cf-beacon='{\"token\": \"%s\"}'></script>" % CF_BEACON_TOKEN
        )
    return ANALYTICS_MARK + "\n" + "\n".join(out) + "\n"


def inject_analytics(html):
    """Append the tracking snippet just before </body>. No-op while both IDs are blank."""
    snip = analytics_snippet()
    if not snip:
        return html
    if ANALYTICS_MARK in html:
        return re.sub(
            re.escape(ANALYTICS_MARK) + r".*?(?=</body>)", snip, html, count=1, flags=re.S
        )
    return html.replace("</body>", snip + "</body>", 1)


def inject_breadcrumb_schema(html, url_path):
    """Add a BreadcrumbList JSON-LD node that matches the visible .crumbs trail.

    The visible breadcrumb already existed on every inner page; this gives Google
    the machine-readable version so it can render the trail in the SERP instead
    of a bare URL. Idempotent via a marker comment.
    """
    m = re.search(r'<div class="crumbs">(.*?)</div>', html, re.S)
    if not m:
        return html
    inner = m.group(1)
    items = [
        (html_unescape(label).strip(), href)
        for href, label in re.findall(r'<a href="([^"]+)">([^<]+)</a>', inner)
    ]
    tail = html_unescape(
        re.sub(r"<[^>]+>", "", inner.split("</a>")[-1])
    ).strip(" \u203a\u00a0\t›")
    if tail:
        items.append((tail, url_path))
    if len(items) < 2:
        return html
    elems = [
        {"@type": "ListItem", "position": i, "name": n, "item": DOMAIN + u}
        for i, (n, u) in enumerate(items, 1)
    ]
    schema = (
        '<script type="application/ld+json">'
        + json.dumps(
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elems},
            ensure_ascii=False,
        )
        + "</script>\n"
    )
    block = CRUMB_SCHEMA_MARK + "\n" + schema
    # Idempotent and SAFE: strip every prior breadcrumb block in <head> first.
    # The old regex could not match a BreadcrumbList payload at all (the nested
    # itemListElement braces break [^{}]*), so each build appended one more copy
    # and pages had accumulated 4-5 identical blocks each.
    html = _strip_crumb_blocks(html)
    return html.replace("</head>", block + "</head>", 1)


def _strip_crumb_blocks(html):
    """Remove every BreadcrumbList JSON-LD node sitting inside <head>."""
    head, sep, rest = html.partition("</head>")

    def repl(m):
        return "" if '"BreadcrumbList"' in m.group(1) else m.group(0)

    head = re.sub(
        r'[ \t]*<script type="application/ld\+json">(.*?)</script>[ \t]*\r?\n?',
        repl,
        head,
        flags=re.S,
    )
    head = re.sub(r"[ \t]*<!-- breadcrumb-schema -->[ \t]*\r?\n?", "", head)
    return head + sep + rest

# short titles/blurbs for pages that are not in GUIDES (used by the
# "Recently updated" block on the homepage)
EXTRA = {
    "/etsy-fee-calculator/": ("Etsy Fee Calculator",
                              "Every fee line by line, ten countries, and the price you need to hit a target margin."),
    "/about/": ("About CraftFee",
                "Who runs the site, where the rates come from, and when they were last verified."),
}


def human_date(ts):
    d = datetime.date.fromtimestamp(ts)
    return "%d %s %d" % (d.day, MONTHS[d.month - 1], d.year)


def build_recently_updated(entries, limit=5):
    """Home page 'Recently updated' block — 哥飞: list your newest content on the
    home page so crawlers keep coming back.

    Dates come from the last git commit that touched each page (mtime fallback for
    files not yet committed). File mtime cannot be used here: this build rewrites
    every page on every run, which would stamp the whole site with today's date.
    """
    rows = []
    for u, _t, desc, full in entries:
        g = GUIDES.get(u, EXTRA.get(u))
        if not g:
            continue
        rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
        ent = MANIFEST.get(rel)
        try:
            d = datetime.date.fromisoformat(ent["d"]) if ent else \
                datetime.date.fromtimestamp(os.path.getmtime(full))
        except Exception:
            d = datetime.date.fromtimestamp(os.path.getmtime(full))
        rows.append((d, os.path.getmtime(full), u, g[0], g[1]))
    rows.sort(key=lambda r: (r[0], r[1]), reverse=True)

    items = ""
    for i, (d, _mt, u, title, blurb) in enumerate(rows[:limit]):
        border = "" if i == limit - 1 else "border-bottom:1px solid #1B1F24;"
        items += (
            '<a href="%s" style="display:flex;justify-content:space-between;gap:18px;'
            'padding:16px 18px;text-decoration:none;%s">'
            '<span style="display:block">'
            '<span style="display:block;color:#E8E6E1;font-size:15px;font-weight:500;margin-bottom:4px">%s</span>'
            '<span style="display:block;color:#8A8880;font-size:12.5px;line-height:1.55">%s</span>'
            '</span>'
            '<span style="color:#5DCAA5;font-size:12px;white-space:nowrap;padding-top:3px">%s</span>'
            '</a>'
        ) % (u, border, title, blurb, "%d %s %d" % (d.day, MONTHS[d.month - 1], d.year))

    return (
        '<div style="margin-top:44px">\n'
        '  <h2 style="font-size:19px;font-weight:600;margin:0 0 6px">Recently updated</h2>\n'
        '  <p style="color:#8A8880;font-size:13px;margin:0 0 16px">Fee rates change, so every guide carries the date it was last checked against Etsy\'s published policies.</p>\n'
        '  <div style="border:1px solid #24282E;border-radius:14px;overflow:hidden">\n'
        + items +
    '  </div>\n'
    '</div>\n'
    # 哥飞 10-29：/sitemap/ 已 noindex，首页不再送它内链（内链喂给主力页）
    )


def inject_recently_updated(html, block):
    """Idempotent: replaces an existing block, otherwise inserts before the
    'at a glance' section on the home page."""
    if "<!-- recently-updated -->" in html:
        return re.sub(r"<!-- recently-updated -->.*?<!-- /recently-updated -->\n",
                      "<!-- recently-updated -->\n" + block + "<!-- /recently-updated -->\n",
                      html, flags=re.S)
    anchor = '  <div class="doc" style="margin-top:40px">'
    if anchor not in html:
        print("    !! home page anchor not found — recently-updated skipped")
        return html
    return html.replace(anchor,
                        "<!-- recently-updated -->\n" + block + "<!-- /recently-updated -->\n" + anchor, 1)


def _git_lastmod(rel_path, fallback_ts):
    """Last-commit date (YYYY-MM-DD) for a repo path — a truthful lastmod.

    Falls back to the file mtime when git is unavailable (e.g. a shallow CI
    checkout without history), so the value is never fabricated.
    """
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel_path],
                           cwd=ROOT, capture_output=True, text=True, timeout=8)
        d = r.stdout.strip()
        if d:
            return d
    except Exception:
        pass
    return datetime.date.fromtimestamp(fallback_ts).isoformat()


# ---------------------------------------------------------------------------
# Content-fingerprint lastmod (added 10-26)
#
# Why not simply "last git commit"? Because a nav/footer edit touches all 19
# files at once, so every page inherits the same date and the whole site looks
# like it changed at 00:00 on one day — 哥飞 flagged exactly that on 10-26
# (19/19 lastmod = 2026-10-25, home "Recently updated" 5/5 = 25 Oct).
# A page's <lastmod> must move when that page's own words move, nothing else.
# ---------------------------------------------------------------------------
MANIFEST_PATH = os.path.join(ROOT, ".lastmod.json")
MANIFEST = {}

# Template chrome that must not influence a page's fingerprint. The
# "recently-updated" alternative has to come FIRST: both of its markers are
# HTML comments, so a plain comment rule would eat them and leave the block.
_RE_NOISE = re.compile(
    r"<!--\s*recently-updated\s*-->.*?<!--\s*/recently-updated\s*-->"
    r"|<!--\s*related-guides\s*-->.*?</div>\s*</div>"
    r"|<!--.*?-->"
    r"|<script\b.*?</script>"
    r"|<style\b.*?</style>",
    re.S | re.I)


def content_fingerprint(html):
    """SHA1 of the page's own words, with template chrome stripped."""
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S | re.I)
    body = m.group(1) if m else html
    if not m:
        body = re.sub(r"<header\b.*?</header>", "", body, flags=re.S | re.I)
        body = re.sub(r"<footer\b.*?</footer>", "", body, flags=re.S | re.I)
        body = re.sub(r"<nav\b.*?</nav>", "", body, flags=re.S | re.I)
    body = _RE_NOISE.sub("", body)
    body = re.sub(r"\s+", " ", body).strip()
    return hashlib.sha1(body.encode("utf-8")).hexdigest()


def _load_manifest():
    global MANIFEST
    MANIFEST = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, encoding="utf-8") as f:
                MANIFEST = json.load(f)
        except Exception:
            MANIFEST = {}
    return MANIFEST


def _save_manifest():
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(MANIFEST, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def _git_commits(rel_path):
    """[(rev, 'YYYY-MM-DD'), ...] for one file, newest first."""
    try:
        r = subprocess.run(["git", "log", "--format=%H %cs", "--", rel_path],
                           cwd=ROOT, capture_output=True, text=True, timeout=25)
        rows = []
        for line in r.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) == 2:
                rows.append((parts[0], parts[1]))
        return rows
    except Exception:
        return []


def _blob_at(rel_path, rev):
    try:
        r = subprocess.run(["git", "show", "%s:%s" % (rev, rel_path)],
                           cwd=ROOT, capture_output=True, timeout=25)
        if r.returncode == 0:
            return r.stdout.decode("utf-8", "ignore")
    except Exception:
        pass
    return None


def _seed_date_from_history(rel_path, cur_fp, fallback_ts):
    """First run only: recover the real "last edited" date.

    Walks this file's commits newest -> oldest and stops at the first one whose
    <main> content differs from today's. Everything newer than that point is
    nav/footer churn, so its date is the last genuine content edit.
    """
    prev_date = None
    for rev, d in _git_commits(rel_path):
        blob = _blob_at(rel_path, rev)
        if blob is None:
            continue
        if content_fingerprint(blob) == cur_fp:
            prev_date = d
        else:
            break
    return prev_date or _git_lastmod(rel_path, fallback_ts)


def date_for(rel_path, full, html):
    """The one date that feeds both <lastmod> and 'Recently updated'."""
    fp = content_fingerprint(html)
    ent = MANIFEST.get(rel_path)
    if ent and ent.get("h") == fp:
        return ent["d"]
    if ent is None:
        d = _seed_date_from_history(rel_path, fp, os.path.getmtime(full))
    else:
        # content really changed since the last build -> the commit that did it
        d = _git_lastmod(rel_path, os.path.getmtime(full))
    MANIFEST[rel_path] = {"h": fp, "d": d}
    return d


def build_dates(targets):
    """Fingerprint every page once per build. Must run after all injections."""
    _load_manifest()
    changed = 0
    for full in targets:
        rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
        before = MANIFEST.get(rel, {}).get("h")
        date_for(rel, full, read(full))
        if MANIFEST[rel]["h"] != before:
            changed += 1
    keep = {os.path.relpath(f, ROOT).replace(os.sep, "/") for f in targets}
    for k in list(MANIFEST):
        if k not in keep:
            MANIFEST.pop(k)
    _save_manifest()
    return changed


def build_xml_sitemap(path_by_url):
    """Regenerate sitemap.xml. lastmod comes from the content fingerprint, so it
    reflects real content edits and never lies to Google."""
    # /sitemap/ is noindex,follow — listing a noindexed URL in sitemap.xml is
    # contradictory, so it is excluded here (it stays linked in the footer and
    # in the HTML sitemap page itself).
    order = [u for _, urls in SECTIONS for u in urls]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    n = 0
    for u in order:
        full = path_by_url.get(u)
        if not full or not os.path.exists(full):
            print("    !! sitemap.xml: no file for %s — skipped" % u)
            continue
        pri, freq = SITEMAP_PRIORITY.get(u, SITEMAP_DEFAULT)
        rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
        lastmod = (MANIFEST.get(rel) or {}).get("d") or _git_lastmod(rel, os.path.getmtime(full))
        out += ['  <url>',
                '    <loc>%s%s</loc>' % (DOMAIN, u),
                '    <lastmod>%s</lastmod>' % lastmod,
                '    <changefreq>%s</changefreq>' % freq,
                '    <priority>%s</priority>' % pri,
                '  </url>']
        n += 1
    out.append('</urlset>')
    return "\n".join(out) + "\n", n


def main():
    pages = []
    targets = []
    for dirpath, _, files in os.walk(PUBLIC):
        for fn in files:
            if fn != "index.html":
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, PUBLIC).replace(os.sep, "/")
            if rel.startswith("sitemap/"):
                continue
            if rel == "404.html":  # 404.html is at public/404.html -> rel "404.html"
                continue
            html = read(full)
            u = url_of(full)
            if u in ("/404.html/",):
                continue
            t = title_of(html)
            d = meta(html, "description")
            pages.append((u, t, d))
            targets.append(full)

    # 1) generate sitemap page
    write(os.path.join(PUBLIC, "sitemap", "index.html"), build_sitemap_html(pages))
    print("  sitemap/index.html  (%d pages listed)" % len(pages))

    # 2) footer link + 3) related guides + breadcrumb JSON-LD + analytics
    for full in targets:
        u = url_of(full)
        html = read(full)
        html = strip_footer_sitemap_link(html)
        html = inject_breadcrumb_schema(html, u)
        html = inject_analytics(html)
        if u in GUIDES:
            html = inject_related(html, u)
        write(full, html)
    print("  footer 'All Pages' link stripped (noindex page) + related-guides + breadcrumb schema injected (idempotent)")
    if not (CF_BEACON_TOKEN or GA4_ID):
        print("  analytics: skipped (no ID set yet)")

    # 3.5) content-fingerprint lastmod map — after all injections, before the
    #      home block and sitemap.xml read it. Only bumps a page whose own
    #      <main> content changed, so a nav edit no longer restamps the site.
    n_changed = build_dates(targets)
    print("  .lastmod.json  (%d pages tracked, %d content changes)" % (len(MANIFEST), n_changed))

    # 4) home page "Recently updated" block (哥飞: newest content on the home page)
    entries = [(u, t, d, full) for (u, t, d), full in zip(pages, targets)]
    home = os.path.join(PUBLIC, "index.html")
    html = read(home)
    html = inject_recently_updated(html, build_recently_updated(entries))
    write(home, html)
    print("  index.html  'Recently updated' block regenerated from git commit dates")

    # 4) regenerate sitemap.xml from the same page inventory (single source of truth)
    path_by_url = {u: full for (u, _t, _d), full in zip(pages, targets)}
    path_by_url["/sitemap/"] = os.path.join(PUBLIC, "sitemap", "index.html")
    xml, n = build_xml_sitemap(path_by_url)
    write(os.path.join(PUBLIC, "sitemap.xml"), xml)
    print("  sitemap.xml  (%d urls, lastmod from content fingerprint)" % n)


if __name__ == "__main__":
    main()
