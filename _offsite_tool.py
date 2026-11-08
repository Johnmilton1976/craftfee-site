# -*- coding: utf-8 -*-
"""Insert the Offsite Ads decision tool into /offsite-ads/."""
import io, re

P = "public/offsite-ads/index.html"
s = io.open(P, encoding="utf-8", newline="").read().replace("\r\n", "\n")

TOOL = r'''
</div>

<div class="wrap" id="oa-tool" style="margin-top:6px">
  <div class="grid">
    <div class="card">
      <h2>YOUR SHOP</h2>

      <div class="row two">
        <div>
          <label for="cur" style="font-size:12px;color:#A9A7A2;display:block;margin-bottom:5px">Currency</label>
          <select id="cur">
            <option value="USD">US dollar</option>
            <option value="GBP">Pound</option>
            <option value="EUR">Euro</option>
            <option value="CAD">Canadian dollar</option>
            <option value="AUD">Australian dollar</option>
          </select>
        </div>
        <div>
          <label for="aov" style="font-size:12px;color:#A9A7A2;display:block;margin-bottom:5px">Average order</label>
          <input class="inp" id="aov" type="number" value="38" min="1" step="1" inputmode="decimal">
        </div>
      </div>

      <div class="row">
        <label for="rev" style="font-size:12px;color:#A9A7A2;display:block;margin-bottom:5px">Etsy revenue, last 12 months <em style="font-style:normal;color:#5F5E5A">item + shipping, before tax</em></label>
        <input class="inp" id="rev" type="number" value="9000" min="0" step="500" inputmode="decimal">
      </div>

      <div class="row">
        <label for="m" style="font-size:12px;color:#A9A7A2;display:block;margin-bottom:5px">Gross margin before Etsy's fees <em style="font-style:normal;color:#5F5E5A">(order less materials and packaging)</em></label>
        <input class="inp" id="m" type="number" value="55" min="1" max="95" step="1" inputmode="decimal">
        <div class="hint">A $38 order that costs $17 in materials and packaging is 55%.</div>
      </div>

      <div class="row">
        <label for="share" style="font-size:12px;color:#A9A7A2;display:block;margin-bottom:5px">Orders marked Offsite Ads <em style="font-style:normal;color:#5F5E5A">in your payment account</em></label>
        <input class="inp" id="share" type="number" value="20" min="0" max="100" step="1" inputmode="decimal">
      </div>

      <div class="toggle" id="ever">
        <div class="box"></div>
        <span>My shop has been above US$10,000 in some 365-day window
          <small>Then the rate is 12% and opting out is no longer offered &mdash; permanently.</small></span>
      </div>

      <div class="presets">
        <button type="button" data-preset="small">Small shop</button>
        <button type="button" data-preset="mid">Past $10k</button>
        <button type="button" data-preset="high">High ticket</button>
      </div>
    </div>

    <div class="card">
      <h2>WHAT IT COSTS YOU</h2>

      <div class="hero">
        <div class="lbl" id="heroLbl">Offsite Ads fees per year</div>
        <div class="big" id="feeYear">$0</div>
        <div class="note" id="feeNote"></div>
      </div>

      <div class="li"><span class="n">Orders per year</span><span class="v" id="v1">—</span></div>
      <div class="li"><span class="n">Of those, attributed to an ad</span><span class="v" id="v2">—</span></div>
      <div class="li"><span class="n">Fee on one attributed order <em id="capNote"></em></span><span class="v" id="v3">—</span></div>
      <div class="li"><span class="n">That is, of the order</span><span class="v" id="v4">—</span></div>
      <div class="li tot"><span class="n">Attributed orders that must be new</span><span class="v" id="v5">—</span></div>

      <div class="score" id="score">
        <div class="top">
          <div class="grade" id="grade">–</div>
          <div class="txt" id="gradeTxt"><b>Enter your numbers</b>The verdict appears here.</div>
        </div>
      </div>

      <div id="insights"></div>
    </div>
  </div>

  <div class="card" style="margin-top:20px">
    <h2>IF ONLY SOME OF THOSE ORDERS ARE GENUINELY NEW</h2>
    <p style="font-size:13px;color:#A9A7A2;margin:0 0 6px;line-height:1.7">An attributed order only pays for itself if it would not have happened anyway. Slide the share you believe and watch the year.</p>
    <div class="mrow" style="margin:14px 0 4px">
      <span class="mn" style="flex:0 0 150px">Would have bought anyway</span>
      <input id="p" type="range" min="0" max="100" value="50" step="5" style="flex:1;accent-color:#5DCAA5">
      <span class="mv" id="pOut" style="flex:0 0 46px">50%</span>
    </div>
    <table class="scen" style="margin-top:14px">
      <thead><tr><th>Share of ad orders that are new</th><th>Net effect per year</th><th>Per attributed order</th></tr></thead>
      <tbody id="scenBody"></tbody>
    </table>
    <div id="scenNote" class="hint" style="margin-top:12px"></div>
  </div>
  <script src="/assets/offsite.js?v=1" defer></script>
</div>

<div class="wrap narrow">
'''

anchor = '''  <p class="lede">Etsy Offsite Ads promotes your listings on Google, Facebook, Instagram, Pinterest and partner sites. You pay nothing upfront. But when a sale arrives through one of those ads, Etsy takes a further slice of the whole order \u2014 and that slice is bigger than any other fee on the invoice.</p>
'''
assert s.count(anchor) == 1, "lede anchor"
s = s.replace(anchor, anchor + TOOL)

io.open(P, "w", encoding="utf-8", newline="\r\n").write(s)
print("inserted", len(TOOL), "chars")
