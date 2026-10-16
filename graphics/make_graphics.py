#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
craftfee info-graphics generator.

Writes SVG sources to graphics/svg/*.svg and (via render.js + sharp) PNGs to
public/assets/img/*.png.

ALL FIGURES MUST MATCH public/assets/calculator.js — same rates, same bases:
  gross      = item*qty + shipping + gift wrap        (sales tax EXCLUDED)
  transaction= gross * 6.5%
  processing = (gross + tax) * procRate + fixed       (only fee whose base has tax)
  regulatory = gross * reg
  listing    = per country
  offsite    = min(gross * 15%|12%, cap)

Run:  python graphics/make_graphics.py   then   node graphics/render.js
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SVG_DIR = os.path.join(HERE, "svg")
IMG_DIR = os.path.join(ROOT, "public", "assets", "img")

BG, PANEL, BORDER = "#0F1114", "#14181C", "#24282E"
INK, MUT, DIM = "#E8E6E1", "#9A9891", "#6E6C66"
ACC, ACC_D, ACC_F = "#5DCAA5", "#2F6B58", "#16211D"
WARN, WARN_D = "#E8B84B", "#6B5A2A"
NEG, NEG_F = "#D9736C", "#241A1A"
FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"


def t(x, y, s, size=24, fill=INK, weight="normal", anchor="start", ls=0):
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
            'fill="%s" text-anchor="%s" letter-spacing="%s">%s</text>'
            % (x, y, FONT, size, weight, fill, anchor, ls, s))


def rect(x, y, w, h, fill, stroke=None, rx=0, sw=2, o=1):
    s = '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" opacity="%s"' % (
        x, y, w, h, rx, fill, o)
    if stroke:
        s += ' stroke="%s" stroke-width="%s"' % (stroke, sw)
    return s + "/>"


def line(x1, y1, x2, y2, stroke=BORDER, sw=1):
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>' % (
        x1, y1, x2, y2, stroke, sw)


def frame(w, h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d">%s' % (w, h, w, h, rect(0, 0, w, h, BG)))


# ---------------------------------------------------------------- figure 1
def fig_flow():
    W, H = 1600, 900
    s = frame(W, H)
    s += t(80, 86, "Where your Etsy money goes", 44, INK, "bold")
    s += t(80, 130, "One order, three different bases. Applying the right rate to the wrong amount is the most common Etsy fee-calculator error.", 22, MUT)

    # order bar -------------------------------------------------------------
    y, bh = 176, 88
    segs = [(80, 720, "Item price", INK, ACC_F, ACC),
            (800, 200, "Shipping", INK, PANEL, BORDER),
            (1000, 160, "Gift wrap", INK, PANEL, BORDER),
            (1160, 360, "Sales tax", NEG, NEG_F, "#5A3A36")]
    for x, w, label, fg, fill, stroke in segs:
        s += rect(x, y, w, bh, fill, stroke, rx=6)
        s += t(x + w / 2, y + bh / 2 + 9, label, 23, fg, "normal", "middle")
    s += t(1160 + 180, y + bh + 30, "not your revenue", 20, NEG, "normal", "middle")

    # scale bar -> strip coordinates
    def sx(x):
        return 760 + (x - 80) * (760.0 / 1440.0)

    it = [(sx(80), sx(800)), (sx(800), sx(1000)), (sx(1000), sx(1160)), (sx(1160), sx(1520))]

    rows = [
        ("Transaction fee", "6.5%", [True, True, True, False], ACC_D,
         "item + shipping + gift wrap  (sales tax excluded)"),
        ("Payment processing", "3% – 4% + fixed", [True, True, True, True], ACC_D,
         "item + shipping + gift wrap + sales tax  (the only base that includes tax)"),
        ("Regulatory operating fee", "0% – 1.14%", [True, True, True, False], ACC_D,
         "same base as the transaction fee — excluded in most countries"),
        ("Offsite Ads", "15% / 12%", [True, True, True, True], WARN_D,
         "the whole order total, then capped per order"),
    ]
    ry = 330
    for name, rate, on, fillc, base in rows:
        s += t(80, ry + 8, name, 26, INK, "bold")
        s += t(80, ry + 38, rate, 22, ACC)
        for i, (x1, x2) in enumerate(it):
            f = fillc if on[i] else None
            s += rect(x1 + 1, ry - 12, x2 - x1 - 2, 34, f if f else "none",
                      BORDER if not f else None, rx=4)
        s += t(760, ry + 46, base, 19, MUT)
        ry += 116

    s += t(80, 856, "Rates as published by Etsy in 2026. Every figure on this site is derived from the bases shown above.", 19, DIM)
    return s + "</svg>"


# ---------------------------------------------------------------- figure 2
def fig_regulatory():
    W, H = 1600, 880
    s = frame(W, H)
    s += t(80, 86, "Etsy's regulatory operating fee, by country", 44, INK, "bold")
    s += t(80, 130, "Charged on the same base as the transaction fee: order total excluding sales tax. Five of the ten markets we cover charge it.", 22, MUT)
    data = [("France", 1.14), ("Spain", 0.88), ("Italy", 0.80),
            ("Canada", 0.50), ("United Kingdom", 0.48)]
    y, mx = 236, 1.14
    for name, v in data:
        w = v / mx * 880.0
        s += t(380, y + 27, name, 27, INK, "bold", "end")
        s += rect(410, y, w, 38, ACC_F, ACC, rx=5)
        s += t(410 + w + 18, y + 28, "%.2f%%" % v, 26, ACC, "bold")
        y += 82
    s += rect(80, 664, 1440, 104, PANEL, BORDER, rx=12)
    s += t(116, 706, "No regulatory operating fee:", 24, INK, "bold")
    s += t(116, 746, "United States · Germany · Australia · Netherlands · Ireland", 24, MUT)
    s += t(80, 826, "Etsy reset these rates on 22 June 2026 \u2014 anything published before that date is out of date. Source: Etsy's Fees &amp; Payments Policy.", 19, DIM)
    return s + "</svg>"


# ---------------------------------------------------------------- figure 3
def fig_processing():
    W, H = 1600, 920
    s = frame(W, H)
    s += t(80, 86, "Etsy payment processing rates, by seller country", 44, INK, "bold")
    s += t(80, 130, "Two of the ten markets we cover charge a higher rate on international orders \u2014 a full extra point on every foreign sale.", 22, MUT)
    cols = (80, 700, 1120)
    s += t(cols[0], 208, "COUNTRY", 20, DIM, "bold", "start", 2)
    s += t(cols[1], 208, "DOMESTIC", 20, DIM, "bold", "start", 2)
    s += t(cols[2], 208, "INTERNATIONAL", 20, DIM, "bold", "start", 2)
    s += line(80, 228, 1520, 228)
    rows = [
        ("United States", "3.0% + $0.25", "same rate", False),
        ("United Kingdom", "4.0% + £0.20", "same rate", False),
        ("EU \u2014 DE \u00b7 FR \u00b7 IT \u00b7 ES \u00b7 NL \u00b7 IE", "4.0% + €0.30", "same rate", False),
        ("Canada", "3.0% + C$0.25", "4.0% + C$0.25", True),
        ("Australia", "3.0% + A$0.25", "4.0% + A$0.25", True),
    ]
    y = 250
    for name, dom, intl, hot in rows:
        if hot:
            s += rect(60, y - 4, 1480, 104, "#141F1B", rx=10)
            s += rect(60, y - 4, 6, 104, ACC, rx=3)
        s += t(cols[0] + 20, y + 58, name, 26, INK, "bold" if hot else "normal")
        s += t(cols[1], y + 58, dom, 26, ACC if hot else INK, "bold" if hot else "normal")
        s += t(cols[2], y + 58, intl, 26, ACC if hot else MUT, "bold" if hot else "normal")
        y += 118
    s += t(80, 866, "Charged on item + shipping + gift wrap + sales tax \u2014 the only Etsy fee whose base includes the tax the buyer pays.", 19, DIM)
    return s + "</svg>"


# ---------------------------------------------------------------- figure 4
def fig_refund():
    W, H = 1600, 880
    s = frame(W, H)
    s += t(80, 86, "Refunding an Etsy order: which fees come back", 44, INK, "bold")
    s += t(80, 130, "Miss the second step and you donate fees on a sale that no longer exists.", 22, MUT)
    c = (80, 860, 1220)
    s += t(c[0], 208, "FEE", 20, DIM, "bold", "start", 2)
    s += t(c[1], 208, "REFUND ONLY", 20, DIM, "bold", "start", 2)
    s += t(c[2], 208, "REFUND + CANCEL ORDER", 20, DIM, "bold", "start", 2)
    s += line(80, 228, 1520, 228)
    rows = [
        ("Transaction fee \u2014 6.5%", True, True),
        ("Payment processing \u2014 3\u20134% + fixed", True, True),
        ("Listing fee \u2014 US$0.20", False, True),
        ("Offsite Ads \u2014 15% / 12%", False, False),
    ]
    y = 250
    for name, a, b in rows:
        s += t(c[0], y + 44, name, 26, INK)
        s += t(c[1], y + 44, ("Comes back" if a else "Does not come back"), 25,
               ACC if a else NEG, "bold" if not a else "normal")
        s += t(c[2], y + 44, ("Comes back" if b else "Never comes back"), 25,
               ACC if b else NEG, "bold" if not b else "normal")
        s += line(80, y + 80, 1520, y + 80, "#1B1F24")
        y += 104
    s += rect(80, 676, 1440, 130, PANEL, BORDER, rx=12)
    s += t(116, 720, "Etsy's help centre, \u201cHow to Cancel a Sale\u201d:", 22, MUT)
    s += t(116, 758, '"Your Etsy transaction and processing fees for the refunded transactions', 22, INK)
    s += t(116, 790, 'are automatically refunded to your Payment account."', 22, INK)
    s += t(80, 852, "Automatic, for the refunded amount. No form, no request, and no 48-hour window \u2014 that claim comes from misreading Etsy's case system.", 19, DIM)
    return s + "</svg>"


# ---------------------------------------------------------------- figure 5
def fig_offsite():
    W, H = 1600, 920
    s = frame(W, H)
    s += t(80, 86, "Etsy Offsite Ads: 15% or 12%, and the per-order cap", 44, INK, "bold")
    s += t(80, 130, "Charged on the whole order total \u2014 before shipping, tax and every other fee are taken out.", 22, MUT)
    s += rect(80, 184, 700, 232, PANEL, BORDER, rx=12)
    s += t(116, 242, "Under US$10,000", 32, INK, "bold")
    s += t(116, 280, "in any consecutive 365-day period", 21, MUT)
    s += t(116, 366, "15%", 54, ACC, "bold")
    s += t(320, 366, "You can opt out.", 24, INK)
    s += rect(820, 184, 700, 232, PANEL, ACC, rx=12)
    s += t(856, 242, "US$10,000 or more", 32, INK, "bold")
    s += t(856, 280, "reached at any point in the shop's life", 21, MUT)
    s += t(856, 366, "12%", 54, ACC, "bold")
    s += t(1030, 366, "Mandatory for the shop's life.", 22, INK)
    s += rect(80, 454, 1440, 96, PANEL, BORDER, rx=12)
    s += t(116, 512, "Per-order cap", 26, INK, "bold")
    s += t(420, 514, "US$100  \u00b7  \u00a380  \u00b7  C$140  \u00b7  A$140  \u00b7  \u20ac92", 28, ACC, "bold")
    s += rect(80, 588, 1440, 152, PANEL, BORDER, rx=12)
    s += t(116, 636, "A $38 order \u00d7 15% = $5.70 \u2014 the cap never binds. The cap only starts to matter", 24, INK)
    s += t(116, 674, "above roughly $667 at 15%, or $833 at 12%.", 24, INK)
    s += t(116, 718, "Only orders Etsy attributes to an ad are charged; the rest cost you nothing.", 20, MUT)
    s += t(80, 830, "Source: Etsy's Advertising &amp; Marketing Policy, 2026. Opt-out eligibility is based on lifetime sales in any 365-day window.", 19, DIM)
    return s + "</svg>"


FIGURES = {
    "etsy-fee-flow-three-bases": fig_flow,
    "etsy-regulatory-operating-fee-by-country": fig_regulatory,
    "etsy-payment-processing-rates-by-country": fig_processing,
    "etsy-refund-fees-what-comes-back": fig_refund,
    "etsy-offsite-ads-fee-15-vs-12-percent": fig_offsite,
}


def main():
    os.makedirs(SVG_DIR, exist_ok=True)
    for name, fn in FIGURES.items():
        p = os.path.join(SVG_DIR, name + ".svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(fn())
        print("svg  ->", os.path.relpath(p, ROOT))
    print("\nNow run:  node graphics/render.js")


if __name__ == "__main__":
    main()
