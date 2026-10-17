#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P5 权威性改造（2026-10-17，幂等）
1) 全站移除 <div class="adzone">ADVERTISEMENT</div> 空广告占位框（AdSense 未上线前不占版面）
2) 首页 H1 加回核心词 "Etsy fee calculator"（保留原句式）
3) 十国对比表后补一句「金额为各国本币，请对比百分比」
4) 四个费率页各加一条 Etsy 官方文档出处链接（E-E-A-T + 用户核对路径）

跑法：python etsy-fee-site/_p5_authority.py
"""
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

H1_OLD = "<h1>What Etsy actually takes — and what you actually keep</h1>"
H1_NEW = "<h1>The Etsy fee calculator that shows what you actually keep</h1>"

CURRENCY_HINT_TAIL = (
    "Verify your own rate in Etsy's Fees &amp; Payments Policy before pricing anything."
)
CURRENCY_HINT_NEW = (
    CURRENCY_HINT_TAIL
    + " All amounts below are in each seller's own local currency, so compare the "
      "percentages, not the absolute figures."
)

SOURCES_BLOCK = """  <div class="callout">
    <b>Where these numbers come from.</b> Etsy publishes its rates across two places, and both are worth checking before you price anything: the <a href="https://www.etsy.com/legal/fees/" target="_blank" rel="noopener">Fees &amp; Payments Policy</a> sets out the fee types and who pays them, and <a href="https://help.etsy.com/hc/en-us/articles/115014483627-What-are-the-Fees-and-Taxes-for-Selling-on-Etsy" target="_blank" rel="noopener">What are the fees and taxes for selling on Etsy?</a> lists the current figures by fee type. Every rate on this page was checked against both on 17 October 2026.
  </div>

"""

SOURCE_PAGES = [
    "etsy-regulatory-operating-fee",
    "etsy-vat-on-fees",
    "offsite-ads",
    "listing-fee",
]

ADZONE_RE = re.compile(r'\n?[ \t]*<div class="adzone">ADVERTISEMENT</div>\n?')

ANCHOR = "  <!-- related-guides -->"


def patch(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    orig = html

    # 1) 拆掉空广告框
    html = ADZONE_RE.sub("\n", html)

    # 2) 首页 H1
    html = html.replace(H1_OLD, H1_NEW)

    # 3) 十国表货币说明
    html = html.replace(CURRENCY_HINT_TAIL, CURRENCY_HINT_NEW)

    # 4) 官方出处（仅四个费率页，且不重复插入）
    rel = os.path.relpath(os.path.dirname(path), ROOT).replace("\\", "/")
    if rel in SOURCE_PAGES and "Fees &amp; Payments Policy</a> sets out" not in html:
        if ANCHOR in html:
            html = html.replace(ANCHOR, SOURCES_BLOCK + ANCHOR, 1)

    if html != orig:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(html)
        return True
    return False


def main():
    changed = []
    for dirpath, _dirnames, filenames in os.walk(ROOT):
        for fn in filenames:
            if fn.endswith(".html"):
                p = os.path.join(dirpath, fn)
                if patch(p):
                    changed.append(os.path.relpath(p, ROOT).replace("\\", "/"))
    print("patched %d files:" % len(changed))
    for c in sorted(changed):
        print("  " + c)


if __name__ == "__main__":
    main()
