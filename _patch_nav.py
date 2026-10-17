#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-off (idempotent): add the Germany and VAT-on-fees pages to the nav and
footer of every existing page, so the two new URLs are one hop from anywhere.
Run once; re-running is a no-op because the anchor disappears after the insert.
"""
import io
import os
import sys

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

NAV_OLD = '<a href="/etsy-fees-eu/">EU &amp; VAT</a>\n      <a href="/etsy-fees-canada/">Canada</a>'
NAV_NEW = ('<a href="/etsy-fees-eu/">EU &amp; VAT</a>\n'
           '      <a href="/etsy-fees-germany/">Germany</a>\n'
           '      <a href="/etsy-fees-canada/">Canada</a>')

FOOT_OLD = ('<a href="/etsy-refund-fee/">Refund Fees</a>\n'
            '      <a href="/how-to-price/">Pricing Guide</a>')
FOOT_NEW = ('<a href="/etsy-refund-fee/">Refund Fees</a>\n'
            '      <a href="/etsy-vat-on-fees/">VAT on Fees</a>\n'
            '      <a href="/how-to-price/">Pricing Guide</a>')

changed = 0
for dirpath, _, files in os.walk(PUBLIC):
    for fn in files:
        if not fn.endswith(".html"):
            continue
        path = os.path.join(dirpath, fn)
        src = io.open(path, encoding="utf-8").read()
        out = src
        n = 0
        if NAV_OLD in out:
            out = out.replace(NAV_OLD, NAV_NEW, 1)
            n += 1
        if FOOT_OLD in out:
            out = out.replace(FOOT_OLD, FOOT_NEW, 1)
            n += 1
        if out != src:
            io.open(path, "w", encoding="utf-8", newline="\n").write(out)
            changed += 1
            print("  patched %s (%d inserts)" % (os.path.relpath(path, PUBLIC), n))

print("files changed:", changed)
sys.exit(0)
