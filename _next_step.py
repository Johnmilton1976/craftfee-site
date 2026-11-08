# -*- coding: utf-8 -*-
"""Append the calculator step to the four country/refund guides.

The affiliate half is deliberately data-driven: AFFILIATES is empty until a
programme actually exists, and an empty list renders nothing at all. When a
link is added it must carry the tracking URL, so the disclosure line appears
at the same time as the thing it discloses.
"""
import io, os

# name, url, one-line reason it is here. url must already contain the tag.
AFFILIATES = [
    # {"name": "ShipStation", "url": "https://www.shipstation.com/?ref=...",
    #  "blurb": "Prints the labels this page assumes you are already paying for."},
]

PAGES = {
    "/etsy-refund-fee/": (
        "",
        "Price the refund before you promise it",
        "The calculator shows what Etsy kept from the original order \u2014 which is exactly the part a refund does not give back.",
    ),
    "/etsy-fees-eu/": (
        "DE",
        "Run a German, French or Dutch order through it",
        "Six VAT rates, three countries with a regulatory fee, and one processing rate. Put a real order in and see the split.",
    ),
    "/etsy-fees-canada/": (
        "CA",
        "Run a Canadian order through it",
        "It knows about the 0.50% regulatory fee and the four HST rates \u2014 the two things every other calculator gets wrong.",
    ),
    "/etsy-fees-germany/": (
        "DE",
        "Run a German order through it",
        "19% VAT on Etsy's own fees is a line most estimators leave out. Here it is charged, line by line.",
    ),
}

MARK = "<!-- next-step -->"


def block(country, headline, blurb):
    tools = ""
    if AFFILIATES:
        items = "".join(
            '<li><a href="%s" target="_blank" rel="sponsored nofollow noopener">%s</a> &mdash; %s</li>'
            % (a["url"], a["name"], a["blurb"])
            for a in AFFILIATES
        )
        tools = (
            '<div class="ns-tools"><p class="ns-h">Tools we use for this</p><ul>%s</ul>'
            '<p class="ns-note">These are affiliate links: we earn a commission if you sign up, '
            "at no extra cost to you. It does not change what the fee pages say.</p></div>" % items
        )
    return (
        MARK + "\n"
        '<div class="wrap narrow">\n  <div class="next-step">\n'
        '    <a class="ns-cta" href="/etsy-fee-calculator/%s">\n'
        '      <span class="txt"><span class="ns-k">CALCULATOR</span>'
        "<strong>%s</strong>"
        '<span class="ns-d">%s</span></span>\n'
        '      <span class="ns-arrow">&rarr;</span>\n'
        "    </a>\n%s\n  </div>\n</div>\n" % (country, headline, blurb, tools)
    )


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
    for url, (country, headline, blurb) in PAGES.items():
        path = os.path.join(root, url.strip("/"), "index.html")
        s = io.open(path, encoding="utf-8", newline="").read()
        if MARK in s:
            print("skip (already there)", url)
            continue
        s = s.replace("\r\n", "\n")
        anchor = '  <div class="related"'
        if s.count(anchor) != 1:
            raise SystemExit("%s: related anchor count %d" % (url, s.count(anchor)))
        s = s.replace(anchor, block(country, headline, blurb) + "\n" + anchor)
        io.open(path, "w", encoding="utf-8", newline="\r\n").write(s)
        print("inserted", url)


if __name__ == "__main__":
    main()
