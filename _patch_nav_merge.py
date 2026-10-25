#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild nav + footer across every page for the country-page merge.

Steps (idempotent, re-run is a no-op):
  1. Replace the <nav class="nav"> block with the canonical link list, marking
     the current page "on".
  2. Replace the <div class="fb"> footer link list the same way (no "on").
  3. Rewrite any remaining inline references to the three merged country pages
     (/etsy-fees-canada/, /etsy-fees-australia/, /etsy-fees-germany/) to the new
     consolidated /etsy-fees-by-country/ page.
Run:  python _patch_nav_merge.py
"""
import io, os, re

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

NAV_LINKS = [
    ("/etsy-fee-calculator/", "Fee Calculator"),
    ("/etsy-fees-uk/", "UK &amp; VAT"),
    ("/etsy-fees-eu/", "EU &amp; VAT"),
    ("/etsy-fees-by-country/", "By Country"),
    ("/etsy-shipping-calculator/", "Shipping"),
    ("/offsite-ads/", "Offsite Ads"),
    ("/listing-fee/", "Listing Fees"),
    ("/how-to-price/", "Pricing Guide"),
]
FOOTER_LINKS = [
    ("/", "Home"),
    ("/etsy-fee-calculator/", "Fee Calculator"),
    ("/etsy-fees-uk/", "UK &amp; VAT"),
    ("/etsy-fees-eu/", "EU &amp; VAT"),
    ("/etsy-fees-by-country/", "By Country"),
    ("/etsy-shipping-calculator/", "Shipping"),
    ("/offsite-ads/", "Offsite Ads"),
    ("/listing-fee/", "Listing Fees"),
    ("/etsy-regulatory-operating-fee/", "Regulatory Fee"),
    ("/etsy-refund-fee/", "Refund Fees"),
    ("/etsy-vat-on-fees/", "VAT on Fees"),
    ("/etsy-tax/", "Etsy Tax"),
    ("/how-to-price/", "Pricing Guide"),
    ("/about/", "About"),
    ("/contact/", "Contact"),
    ("/privacy/", "Privacy"),
    ("/sitemap/", "All Pages"),
]
MERGED = ["/etsy-fees-canada/", "/etsy-fees-australia/", "/etsy-fees-germany/"]


def url_of(path):
    rel = os.path.relpath(path, PUBLIC).replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    rel = rel[:-len("index.html")].rstrip("/")
    return "/" + rel + "/"


def build_nav(own):
    links = "".join(
        '      <a%s href="%s">%s</a>\n' % (' class="on"' if u == own else "", u, t)
        for u, t in NAV_LINKS
    )
    return '  <nav class="nav">\n' + links + '    </nav>'


def build_footer():
    links = "".join(
        '      <a href="%s">%s</a>\n' % (u, t) for u, t in FOOTER_LINKS
    )
    return '    <div class="fb">\n' + links + '    </div>'


def patch(html, own):
    new_nav = build_nav(own)
    new_fb = build_footer()
    html, n_nav = re.subn(r'  <nav class="nav">.*?</nav>',
                          new_nav, html, flags=re.S)
    html, n_fb = re.subn(r'    <div class="fb">.*?</div>',
                         new_fb, html, flags=re.S)
    n_urls = 0
    for old in MERGED:
        html, c = re.subn(re.escape(old), "/etsy-fees-by-country/", html)
        n_urls += c
    return html, (n_nav, n_fb, n_urls)


changed = 0
for dirpath, _, files in os.walk(PUBLIC):
    for fn in files:
        if not fn.endswith(".html"):
            continue
        path = os.path.join(dirpath, fn)
        src = io.open(path, encoding="utf-8").read()
        out, counts = patch(src, url_of(path))
        if out != src:
            io.open(path, "w", encoding="utf-8", newline="\n").write(out)
            changed += 1
            print("  patched %-44s nav=%d fb=%d urls=%d" %
                  (os.path.relpath(path, PUBLIC), counts[0], counts[1], counts[2]))
print("files changed:", changed)
