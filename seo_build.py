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
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, "public")
DOMAIN = "https://craftfee.com"

# url -> (priority, changefreq) for the XML sitemap; everything else is 0.8/monthly
SITEMAP_PRIORITY = {
    "/": ("1.0", "monthly"),
    "/etsy-fee-calculator/": ("0.9", "monthly"),
    "/sitemap/": ("0.9", "monthly"),
    "/about/": ("0.3", "yearly"),
    "/privacy/": ("0.2", "yearly"),
}
SITEMAP_DEFAULT = ("0.8", "monthly")

# url -> (category label, short blurb)  used for the related-guides hub
GUIDES = {
    "/etsy-fees-uk/": ("Etsy fees for UK sellers",
                       "UK rate, the 0.48% regulatory fee, and the VAT trap explained."),
    "/etsy-fees-eu/": ("Etsy fees in the EU",
                       "One processing rate, six VAT rates, and three countries with a regulatory fee."),
    "/etsy-fees-canada/": ("Etsy fees for Canadian sellers",
                           "Two processing rates, GST/HST, and the 0.5% regulatory fee."),
    "/etsy-fees-australia/": ("Etsy fees for Australian sellers",
                              "Two processing rates and GST arriving twice — on orders and on fees."),
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
}

# ordered sections for the HTML sitemap page
SECTIONS = [
    ("Start here", ["/", "/etsy-fee-calculator/"]),
    ("Country & VAT guides", ["/etsy-fees-uk/", "/etsy-fees-eu/", "/etsy-fees-canada/", "/etsy-fees-australia/"]),
    ("Fee & pricing guides", ["/etsy-refund-fee/", "/etsy-regulatory-operating-fee/",
                              "/offsite-ads/", "/listing-fee/", "/how-to-price/"]),
    ("About", ["/about/", "/privacy/"]),
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
<meta name="description" content="Every page on this site in one place: the Etsy fee calculator, country guides for the UK, EU, Canada and Australia, and plain-English guides to the regulatory fee, Offsite Ads, listing fees and pricing.">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://craftfee.com/sitemap/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CraftFee">
<meta property="og:title" content="All Etsy seller fee guides &amp; calculator — sitemap">
<meta property="og:description" content="Every page on this site in one place: the fee calculator and all plain-English guides.">
<meta property="og:url" content="https://craftfee.com/sitemap/">
<meta property="og:image" content="https://craftfee.com/assets/og-image-craftfee.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="All Etsy seller fee guides &amp; calculator — sitemap">
<meta name="twitter:description" content="Every page on this site in one place: the fee calculator and all plain-English guides.">
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
      <a href="/etsy-fees-canada/">Canada</a>
      <a href="/etsy-fees-australia/">Australia</a>
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
      <a href="/etsy-fees-canada/">Canada</a>
      <a href="/etsy-fees-australia/">Australia</a>
      <a href="/offsite-ads/">Offsite Ads</a>
      <a href="/listing-fee/">Listing Fees</a>
      <a href="/etsy-regulatory-operating-fee/">Regulatory Fee</a>
      <a href="/etsy-refund-fee/">Refund Fees</a>
      <a href="/how-to-price/">Pricing Guide</a>
      <a href="/about/">About</a>
      <a href="/privacy/">Privacy</a>
    </div>
    <p>CraftFee is an independent site. It is not affiliated with, endorsed by, or connected to Etsy, Inc. Etsy is a trademark of Etsy, Inc., used here only to identify the marketplace these tools describe. Fee rates are published for reference and change from time to time — always confirm against Etsy's official Fees &amp; Payments Policy. Nothing here is financial or tax advice.</p>
  </div>
</footer>

<script src="/assets/cookie-consent.js" defer></script>
</body>
</html>
""" % sections_html


def inject_footer_link(html):
    if "/sitemap/" in html:
        return html
    anchor = '      <a href="/privacy/">Privacy</a>\n    </div>'
    repl = '      <a href="/privacy/">Privacy</a>\n      <a href="/sitemap/">All Pages</a>\n    </div>'
    if anchor in html:
        return html.replace(anchor, repl, 1)
    return html


def inject_related(html, self_url):
    if "<!-- related-guides -->" in html:
        return html
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
    return html.replace("</main>", block + "</main>", 1)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

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
    home page so crawlers keep coming back. Dates come from real file mtimes,
    so it can never drift out of date."""
    rows = []
    for u, _t, desc, full in entries:
        g = GUIDES.get(u, EXTRA.get(u))
        if not g:
            continue
        blurb = g[1]
        rows.append((os.path.getmtime(full), u, g[0], blurb))
    rows.sort(reverse=True)

    items = ""
    for i, (mtime, u, title, blurb) in enumerate(rows[:limit]):
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
        ) % (u, border, title, blurb, human_date(mtime))

    return (
        '<div style="margin-top:44px">\n'
        '  <h2 style="font-size:19px;font-weight:600;margin:0 0 6px">Recently updated</h2>\n'
        '  <p style="color:#8A8880;font-size:13px;margin:0 0 16px">Fee rates change, so every guide carries the date it was last checked against Etsy\'s published policies.</p>\n'
        '  <div style="border:1px solid #24282E;border-radius:14px;overflow:hidden">\n'
        + items +
        '  </div>\n'
        '  <p style="margin:14px 0 0;font-size:13px;color:#8A8880">See every page on the site: '
        '<a href="/sitemap/">all pages &rarr;</a></p>\n'
        '</div>\n'
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


def build_xml_sitemap(path_by_url):
    """Regenerate sitemap.xml. lastmod comes from each file's real mtime, so it
    never goes stale and never lies to Google."""
    order = [u for _, urls in SECTIONS for u in urls] + ["/sitemap/"]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    n = 0
    for u in order:
        full = path_by_url.get(u)
        if not full or not os.path.exists(full):
            print("    !! sitemap.xml: no file for %s — skipped" % u)
            continue
        pri, freq = SITEMAP_PRIORITY.get(u, SITEMAP_DEFAULT)
        lastmod = datetime.date.fromtimestamp(os.path.getmtime(full)).isoformat()
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
            t = meta(html, "title")
            d = meta(html, "description")
            pages.append((u, t, d))
            targets.append(full)

    # 1) generate sitemap page
    write(os.path.join(PUBLIC, "sitemap", "index.html"), build_sitemap_html(pages))
    print("  sitemap/index.html  (%d pages listed)" % len(pages))

    # 2) footer link + 3) related guides
    for full in targets:
        u = url_of(full)
        html = read(full)
        html = inject_footer_link(html)
        if u in GUIDES:
            html = inject_related(html, u)
        write(full, html)
    print("  footer 'All Pages' link + related-guides blocks injected (idempotent)")

    # 4) home page "Recently updated" block (哥飞: newest content on the home page)
    entries = [(u, t, d, full) for (u, t, d), full in zip(pages, targets)]
    home = os.path.join(PUBLIC, "index.html")
    html = read(home)
    html = inject_recently_updated(html, build_recently_updated(entries))
    write(home, html)
    print("  index.html  'Recently updated' block regenerated from file mtimes")

    # 4) regenerate sitemap.xml from the same page inventory (single source of truth)
    path_by_url = {u: full for (u, _t, _d), full in zip(pages, targets)}
    path_by_url["/sitemap/"] = os.path.join(PUBLIC, "sitemap", "index.html")
    xml, n = build_xml_sitemap(path_by_url)
    write(os.path.join(PUBLIC, "sitemap.xml"), xml)
    print("  sitemap.xml  (%d urls, lastmod from file mtime)" % n)


if __name__ == "__main__":
    main()
