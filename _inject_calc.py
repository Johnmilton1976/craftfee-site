#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-off: pull the calculator DOM (tabs + input/result grid + scenarios card)
from etsy-fee-calculator/index.html and drop it into the shipping page's
<!--CALC--> marker. Keeps the shipping page a genuine tool reusing the same
calculator.js, without hand-copying ~200 lines of markup.
"""
import io, os

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
SRC = os.path.join(PUBLIC, "etsy-fee-calculator", "index.html")
DST = os.path.join(PUBLIC, "etsy-shipping-calculator", "index.html")

src = io.open(SRC, encoding="utf-8").read()
dst = io.open(DST, encoding="utf-8").read()

start = src.index('<div class="tabs" role="tablist">')
end = src.index('  <div class="doc" style="margin-top:44px">')
block = src[start:end].rstrip()

if "<!--CALC-->" not in dst:
    raise SystemExit("marker not found in shipping page")
out = dst.replace("<!--CALC-->", block, 1)
io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
print("injected %d chars of calculator markup into shipping page" % len(block))
