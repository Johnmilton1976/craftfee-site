#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-off (idempotent), 2026-10-18: wire /etsy-tax/ into the site.
1) Footer: add "Etsy Tax" after "VAT on Fees" on every page.
2) Home hub: add the Etsy Tax card after the VAT card.
3) Home at-a-glance table: add the sales-tax row before Currency conversion.
"""
import io
import os

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

FOOT_OLD = '<a href="/etsy-vat-on-fees/">VAT on Fees</a>\n      <a href="/how-to-price/">Pricing Guide</a>'
FOOT_NEW = ('<a href="/etsy-vat-on-fees/">VAT on Fees</a>\n'
            '      <a href="/etsy-tax/">Etsy Tax</a>\n'
            '      <a href="/how-to-price/">Pricing Guide</a>')

HUB_OLD = """    <a href="/etsy-vat-on-fees/">
      <div class="k">REFERENCE</div>
      <h3>VAT on Etsy fees</h3>
      <p>Etsy taxes its own fee, not just your sale. Which countries a VAT ID switches off, which it cannot, and the rate in each.</p>
    </a>
"""
HUB_NEW = HUB_OLD + """    <a href="/etsy-tax/">
      <div class="k">REFERENCE</div>
      <h3>Etsy tax, plainly</h3>
      <p>What Etsy collects and remits for you, what it never touches, and where the 1099-K fits in.</p>
    </a>
"""

GLANCE_OLD = "      <tr><td>Currency conversion</td><td>2.5%</td><td>Your payout, when listing currency \u2260 bank currency</td></tr>"
GLANCE_NEW = ('      <tr><td>Sales tax on goods (US)</td><td>0%</td>'
              '<td>Buyer pays it; Etsy collects and remits it in most states</td></tr>\n'
              + GLANCE_OLD)

changed = 0
for dirpath, _, files in os.walk(PUBLIC):
    for fn in files:
        if not fn.endswith(".html"):
            continue
        path = os.path.join(dirpath, fn)
        src = io.open(path, encoding="utf-8").read()
        out = src
        if FOOT_OLD in out:
            out = out.replace(FOOT_OLD, FOOT_NEW, 1)
        if fn == "index.html" and HUB_OLD in out:
            out = out.replace(HUB_OLD, HUB_NEW, 1)
        if fn == "index.html" and GLANCE_OLD in out:
            out = out.replace(GLANCE_OLD, GLANCE_NEW, 1)
        if out != src:
            io.open(path, "w", encoding="utf-8", newline="\n").write(out)
            changed += 1
print("patched %d files" % changed)
