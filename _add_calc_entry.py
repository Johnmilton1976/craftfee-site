#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-off: put an 'answer-first' block with the /etsy-fee-calculator/ link
inside the first 300 words of the five pages that already rank 8-14.

锚文本统一为 "Etsy fee calculator"（哥飞 11-12：主计算器页要收这个词的权重）。
Idempotent via the <!-- calc-entry --> marker.
"""

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, "public")

MARK = "  <!-- calc-entry -->\n"

BLOCKS = {
    "etsy-vat-on-fees": """  <!-- calc-entry -->
  <div class="callout good"><b>The number this page turns on: a rate between nothing and 23%.</b> A US shop pays no VAT on Etsy's fees at all; a German shop pays 19% on the fee subtotal, French and UK sellers 20%, Irish sellers 23% &mdash; and in Ireland no VAT ID removes it. The rate is applied to Etsy's own charges, never to your sale, which is why it is invisible in every headline fee percentage. The <a href="/etsy-fee-calculator/">Etsy fee calculator</a> puts that line on your own order and shows what a VAT ID would actually save.</div>

""",
    "etsy-fees-eu": """  <!-- calc-entry -->
  <div class="callout good"><b>Four rates, six countries, one number that decides your margin.</b> Every eurozone shop pays the same <b>4% + &euro;0.30</b> processing and <b>6.5%</b> transaction fee; what differs is the regulatory fee (France 1.14%, Spain 0.88%, Italy 0.80%, none in Germany, Netherlands and Ireland) and the VAT added to Etsy's own fees (19% Germany, 21% Netherlands and Spain, 20% France, 22% Italy, 23% Ireland). The <a href="/etsy-fee-calculator/">Etsy fee calculator</a> applies all four to an order and returns what you keep in euros, before materials.</div>

""",
    "etsy-fees-australia": """  <!-- calc-entry -->
  <div class="callout good"><b>The Australian stack, in one line each.</b> US$0.20 listing (about A$0.29), 6.5% transaction on item plus shipping, <b>3% + A$0.25</b> processing on domestic orders against <b>4% + A$0.25</b> on anything shipped overseas, no regulatory operating fee at all, and 10% GST added to Etsy's own fees unless Etsy holds your ABN. The <a href="/etsy-fee-calculator/">Etsy fee calculator</a> switches between the two processing rates and prices the whole thing in AUD.</div>

""",
    "etsy-fees-by-country": """  <!-- calc-entry -->
  <div class="callout good"><b>Two things change at the border: the processing rate and the tax on Etsy's own fees &mdash; plus, in nine markets, a third line.</b> Canada and Australia charge one processing rate domestically and a higher one on foreign orders; outside the US, VAT or GST is added to Etsy's fee invoice; and the regulatory operating fee runs from 0.05% in India to 1.97% in Hungary. The <a href="/etsy-fee-calculator/">Etsy fee calculator</a> has all ten markets built in &mdash; pick the country your bank account sits in and the fee stack rebuilds.</div>

""",
    "etsy-refund-fee": """  <!-- calc-entry -->
  <div class="callout good"><b>What a refund actually gives back, at 2026 rates.</b> The <b>6.5%</b> transaction fee and the payment processing fee (3% + $0.25 in the US, 4% + &pound;0.20 in the UK, 4% + &euro;0.30 in the eurozone) reverse automatically; the <b>$0.20</b> listing fee reverses only if you also cancel the order; the Offsite Ads fee never does. The <a href="/etsy-fee-calculator/">Etsy fee calculator</a> shows the full fee stack those reversals are calculated from, line by line.</div>

""",
}

# 补充：退款页缺一张「按国家看处理费」的小表——退款反还的就是这一行，
# 而它恰好是五个页面里唯一没有国家费率表的一页。
PROC_TABLE = """
    <h2>The processing line, by shop country</h2>
    <p>Processing is the fee a refund reverses most completely, and it is also the line that differs most between countries. These are the rates the reversal is calculated on:</p>
    <table>
      <tr><th>Shop bank account in</th><th>Processing rate</th><th>On a $100-equivalent order</th></tr>
      <tr><td>United States</td><td>3% + $0.25</td><td>$3.25</td></tr>
      <tr><td>United Kingdom</td><td>4% + &pound;0.20</td><td>4% of the order</td></tr>
      <tr><td>Germany, Netherlands, Ireland, France, Spain, Italy</td><td>4% + &euro;0.30</td><td>4% of the order</td></tr>
      <tr><td>Canada</td><td>3% + C$0.25 domestic and US, 4% + C$0.25 elsewhere</td><td>3% or 4%, by buyer location</td></tr>
      <tr><td>Australia</td><td>3% + A$0.25 domestic, 4% + A$0.25 elsewhere</td><td>3% or 4%, by buyer location</td></tr>
    </table>
    <p>Two details decide how much comes back. The fixed charge is per transaction, not per unit, so a multi-item order returns one fixed fee and not several. And Canada and Australia charge the higher rate whenever the buyer is abroad &mdash; which means the amount reversed depends on where the buyer was, not on where you are. If the order also carried a regulatory operating fee, whether <em>that</em> reverses is the one line Etsy does not document; your payment account after the first such refund is the only reliable answer.</p>

"""


def main():
    for slug, block in BLOCKS.items():
        path = os.path.join(PUBLIC, slug, "index.html")
        with open(path, encoding="utf-8") as f:
            html = f.read()
        if MARK in html:
            html = re.sub(re.escape(MARK) + r".*?\n\n(?=  <div class=\"doc\")", block, html, count=1, flags=re.S)
            print("refreshed", slug)
        else:
            # insert straight after the lede paragraph, before <div class="doc">
            m = re.search(r'(<p class="lede">.*?</p>\n)', html, re.S)
            if not m:
                print("NO LEDE", slug)
                continue
            html = html[:m.end()] + "\n" + block + html[m.end():]
            print("inserted", slug)

        # refund page: add the per-country processing table once
        if slug == "etsy-refund-fee" and "The processing line, by shop country" not in html:
            anchor = '    <h2>A myth worth retiring'
            if anchor in html:
                html = html.replace(anchor, PROC_TABLE.strip("\n") + "\n" + anchor, 1)
                print("  + processing table")

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)


if __name__ == "__main__":
    main()
