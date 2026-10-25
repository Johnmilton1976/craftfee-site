#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-off helper: pull the calculator DOM (tabs + input/result grid + scenarios
card) from etsy-fee-calculator/index.html and drop it into every page that
carries a <!--CALC--> marker (shipping, profit, pricing). Reusing the same
calculator.js keeps the three tool pages accurate without hand-copying markup.
"""
import io, os

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
SRC = os.path.join(PUBLIC, "etsy-fee-calculator", "index.html")
DSTS = [
    os.path.join(PUBLIC, "etsy-shipping-calculator", "index.html"),
    os.path.join(PUBLIC, "etsy-profit-calculator", "index.html"),
    os.path.join(PUBLIC, "etsy-pricing-calculator", "index.html"),
]

src = io.open(SRC, encoding="utf-8").read()
start = src.index('<div class="tabs" role="tablist">')
end = src.index('  <div class="doc" style="margin-top:44px">')
block = src[start:end].rstrip()

for dst in DSTS:
    html = io.open(dst, encoding="utf-8").read()
    if "<!--CALC-->" not in html:
        print("  skip (no marker): %s" % os.path.relpath(dst, PUBLIC))
        continue
    out = html.replace("<!--CALC-->", block, 1)
    io.open(dst, "w", encoding="utf-8", newline="\n").write(out)
    print("  injected %d chars -> %s" % (len(block), os.path.relpath(dst, PUBLIC)))
