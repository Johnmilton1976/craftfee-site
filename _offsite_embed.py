# -*- coding: utf-8 -*-
"""Make /offsite-ads/ embeddable (one-off, idempotent).

The decision tool on that page already sits outside <div class="doc">, so
hiding the article is enough to leave the tool alone in the frame. What is
missing is the credit line, the height script, and the snippet that invites
other sites to use it. The Sources callout lives *outside* .doc too, so it
needs embed-hide or it would trail the widget in every embed.
"""
import io

HTML = "public/offsite-ads/index.html"
JS = "public/assets/offsite.js"

CREDIT = ('<p class="embed-credit">Tool by <a href="https://craftfee.com/offsite-ads/">CraftFee</a>'
          ' &mdash; Etsy Offsite Ads 15% vs 12%, the $100 cap, and whether to opt out.</p>\n')

CTA = '''<div class="embed-cta">
    <h2 id="embed">Put this decision tool on your own site</h2>
    <p>If you write about Etsy fees, ads or pricing, this is the one part of the page worth quoting rather than summarising: it works out what Offsite Ads actually costs a shop, and how many of the ad-attributed orders would have to be new customers before the fee pays for itself. The credit line is the only thing we ask for.</p>
    <div class="callout"><code style="font-size:12px;word-break:break-all">&lt;iframe id="cf-oa" src="https://craftfee.com/offsite-ads/?embed=1" width="100%" height="__H__" style="border:1px solid #24282E;border-radius:14px" title="Etsy Offsite Ads cost calculator"&gt;&lt;/iframe&gt;
&lt;script&gt;addEventListener("message",function(e){if(e.data&amp;&amp;e.data.craftfeeHeight){var f=document.getElementById("cf-oa");if(f)f.height=e.data.craftfeeHeight+2}});&lt;/script&gt;
&lt;p&gt;Tool by &lt;a href="https://craftfee.com/offsite-ads/"&gt;CraftFee&lt;/a&gt; &amp;mdash; Etsy Offsite Ads 15% vs 12%, the $100 cap, and whether to opt out.&lt;/p&gt;</code></div>
    <p>The <code>?embed=1</code> parameter strips the navigation, footer and article, so the frame holds the tool and nothing else. No script from us runs on your page and no cookie is set. The height script fits the frame to your column; the number in the snippet is the tall end of the range, for sites that block inline script.</p>
    </div>

'''

s = io.open(HTML, encoding="utf-8", newline=None).read()
changed = []

# 1. Sources callout must not survive into the frame.
old_src = '  <div class="callout">\n    <b>Where these numbers come from.</b>'
if old_src in s:
    s = s.replace(old_src, '  <div class="callout embed-hide">\n    <b>Where these numbers come from.</b>', 1)
    changed.append("sources callout -> embed-hide")

# 2. The invitation block, inside .doc, before the grey verification line.
if 'class="embed-cta"' not in s:
    anchor = '<p style="margin-top:24px;color:#5F5E5A;font-size:12.5px">Rates and rules last verified October 2026.'
    assert anchor in s, "verification line not found"
    s = s.replace(anchor, CTA.replace("__H__", "2840") + anchor, 1)
    changed.append("embed-cta inserted")

# 3. Credit line, outside .doc, last thing before </main>.
if 'class="embed-credit"' not in s:
    assert "\n</main>" in s
    s = s.replace("\n</main>", "\n" + CREDIT + "</main>", 1)
    changed.append("credit added")

# 4. Height script.
if "offsite-embed.js" not in s:
    old = '<script src="/assets/cookie-consent.js" defer></script>'
    assert old in s
    s = s.replace(old, old + '\n<script src="/assets/offsite-embed.js?v=1" defer></script>', 1)
    changed.append("height script")

io.open(HTML, "w", encoding="utf-8", newline="\r\n").write(s)

# 5. url() would strip ?embed=1 and keep rewriting the frame's address.
j = io.open(JS, encoding="utf-8", newline=None).read()
if "indexOf('embed=1')" not in j:
    old = "  function url() {\n    var q = "
    assert old in j, "url() not found"
    j = j.replace(old, "  function url() {\n    /* Inside a frame the address is the host's business, not ours, and\n"
                       "       rewriting it would drop the ?embed=1 that keeps this mode on. */\n"
                       "    if (location.search.indexOf('embed=1') > -1) return;\n    var q = ", 1)
    io.open(JS, "w", encoding="utf-8", newline="\r\n").write(j)
    changed.append("offsite.js url() guard")

print("changed:", changed or "nothing (already applied)")
