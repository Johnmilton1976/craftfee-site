# -*- coding: utf-8 -*-
"""按 Etsy 官方 2026-10-18 现值修正 listing fee 及相关示例数字。
每处替换要求命中次数 == 1，否则中止，避免误伤。
"""
import io, sys, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

# (相对路径, 旧串, 新串)
EDITS = [
    # ---------- calculator.js 费率源 ----------
    ('assets/calculator.js',
     "UK: { sym:'£',  proc:0.040, procInt:0,     fixed:0.20, list:0.16,",
     "UK: { sym:'£',  proc:0.040, procInt:0,     fixed:0.20, list:0.15,"),
    ('assets/calculator.js',
     "AU: { sym:'A$', proc:0.030, procInt:0.040, fixed:0.25, list:0.28,",
     "AU: { sym:'A$', proc:0.030, procInt:0.040, fixed:0.25, list:0.29,"),
    ('assets/calculator.js',
     "DE: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.18,",
     "DE: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17,"),
    ('assets/calculator.js',
     "FR: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.18,",
     "FR: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17,"),
    ('assets/calculator.js',
     "IT: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.18,",
     "IT: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17,"),
    ('assets/calculator.js',
     "ES: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.18,",
     "ES: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17,"),
    ('assets/calculator.js',
     "NL: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.18,",
     "NL: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17,"),
    ('assets/calculator.js',
     "IE: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.18,",
     "IE: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17,"),

    # ---------- 计算器页引用版本（/assets 是 immutable） ----------
    ('etsy-fee-calculator/index.html',
     '/assets/calculator.js?v=3', '/assets/calculator.js?v=4'),

    # ---------- UK ----------
    ('etsy-fees-uk/index.html',
     '<tr><td>Listing fee</td><td>£0.16</td>',
     '<tr><td>Listing fee</td><td>£0.15</td>'),
    ('etsy-fees-uk/index.html',
     '<tr><td>Total Etsy fees</td><td class="num">− £3.65</td></tr>',
     '<tr><td>Total Etsy fees</td><td class="num">− £3.64</td></tr>'),
    ('etsy-fees-uk/index.html',
     '<tr><td><strong>You keep</strong></td><td class="num"><strong>£21.35</strong></td></tr>',
     '<tr><td><strong>You keep</strong></td><td class="num"><strong>£21.36</strong></td></tr>'),
    ('etsy-fees-uk/index.html',
     '<tr><td>Not VAT-registered, no ads</td><td class="num">£30.00</td><td class="num">£3.65</td><td class="num">£26.35</td><td class="num">12.2%</td></tr>',
     '<tr><td>Not VAT-registered, no ads</td><td class="num">£30.00</td><td class="num">£3.64</td><td class="num">£26.36</td><td class="num">12.1%</td></tr>'),
    ('etsy-fees-uk/index.html',
     '<tr><td>VAT-registered, no ads</td><td class="num">£25.00</td><td class="num">£3.65</td><td class="num">£21.35</td><td class="num">12.2%</td></tr>',
     '<tr><td>VAT-registered, no ads</td><td class="num">£25.00</td><td class="num">£3.64</td><td class="num">£21.36</td><td class="num">12.1%</td></tr>'),
    ('etsy-fees-uk/index.html',
     '<tr><td>VAT-registered, Offsite Ads order</td><td class="num">£25.00</td><td class="num">£8.15</td><td class="num">£16.85</td><td class="num">27.2%</td></tr>',
     '<tr><td>VAT-registered, Offsite Ads order</td><td class="num">£25.00</td><td class="num">£8.14</td><td class="num">£16.86</td><td class="num">27.1%</td></tr>'),
    ('etsy-fees-uk/index.html',
     'So the £3.65 of fees above actually costs',
     'So the £3.64 of fees above actually costs'),

    # ---------- Australia ----------
    ('etsy-fees-australia/index.html',
     'A listing fee of about 0.28 AUD per item',
     'A listing fee of about 0.29 AUD per item'),
    ('etsy-fees-australia/index.html',
     '<tr><td>Listing fee</td><td>US$0.20 (about A$0.28)</td>',
     '<tr><td>Listing fee</td><td>US$0.20 (about A$0.29)</td>'),
    ('etsy-fees-australia/index.html',
     '<tr><td>Buyer in Australia</td><td class="num">A$0.28</td><td class="num">A$1.95</td><td class="num">A$1.15</td><td class="num">A$3.38</td><td class="num">A$26.62</td></tr>',
     '<tr><td>Buyer in Australia</td><td class="num">A$0.29</td><td class="num">A$1.95</td><td class="num">A$1.15</td><td class="num">A$3.39</td><td class="num">A$26.61</td></tr>'),
    ('etsy-fees-australia/index.html',
     '<tr><td>Buyer anywhere else</td><td class="num">A$0.28</td><td class="num">A$1.95</td><td class="num">A$1.45</td><td class="num">A$3.68</td><td class="num">A$26.32</td></tr>',
     '<tr><td>Buyer anywhere else</td><td class="num">A$0.29</td><td class="num">A$1.95</td><td class="num">A$1.45</td><td class="num">A$3.69</td><td class="num">A$26.31</td></tr>'),
    ('etsy-fees-australia/index.html',
     '<tr><td>Listing fee</td><td class="num">− A$0.28</td></tr>',
     '<tr><td>Listing fee</td><td class="num">− A$0.29</td></tr>'),
    ('etsy-fees-australia/index.html',
     '<tr><td><strong>Total Etsy fees</strong></td><td class="num"><strong>− A$4.52</strong></td></tr>',
     '<tr><td><strong>Total Etsy fees</strong></td><td class="num"><strong>− A$4.53</strong></td></tr>'),
    ('etsy-fees-australia/index.html',
     '<tr><td><strong>You keep</strong></td><td class="num"><strong>A$37.48</strong></td></tr>',
     '<tr><td><strong>You keep</strong></td><td class="num"><strong>A$37.47</strong></td></tr>'),
    ('etsy-fees-australia/index.html',
     'about <strong>A$0.45</strong>, bringing the total to roughly <strong>A$4.97</strong>',
     'about <strong>A$0.45</strong>, bringing the total to roughly <strong>A$4.98</strong>'),
    ('etsy-fees-australia/index.html',
     'Total fees jump to <strong>A$10.82</strong> and you keep <strong>A$31.18</strong>',
     'Total fees jump to <strong>A$10.83</strong> and you keep <strong>A$31.17</strong>'),
    ('etsy-fees-australia/index.html',
     'about A$0.84 rather than A$0.28',
     'about A$0.87 rather than A$0.29'),

    # ---------- EU ----------
    ('etsy-fees-eu/index.html',
     'converted (about €0.18)',
     'converted (about €0.17)'),

    # ---------- Germany ----------
    ('etsy-fees-germany/index.html',
     'About 13.07 euros, or 13.1% of the order: 0.18 listing fee, 6.50 transaction fee, 4.30 payment processing and 2.09 VAT',
     'About 13.05 euros, or 13.1% of the order: 0.17 listing fee, 6.50 transaction fee, 4.30 payment processing and 2.08 VAT'),
    ('etsy-fees-germany/index.html',
     '<tr><td>Listing fee</td><td>€0.18</td>',
     '<tr><td>Listing fee</td><td>€0.17</td>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>Listing fee</td><td class="num">− €0.18</td><td class="num">0.7%</td></tr>',
     '<tr><td>Listing fee</td><td class="num">− €0.17</td><td class="num">0.6%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td><strong>Total Etsy fees</strong></td><td class="num"><strong>− €3.88</strong></td><td class="num"><strong>14.6%</strong></td></tr>',
     '<tr><td><strong>Total Etsy fees</strong></td><td class="num"><strong>− €3.87</strong></td><td class="num"><strong>14.6%</strong></td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td><strong>You keep</strong></td><td class="num"><strong>€22.62</strong></td><td class="num">85.4%</td></tr>',
     '<tr><td><strong>You keep</strong></td><td class="num"><strong>€22.63</strong></td><td class="num">85.4%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>No VAT ID (e.g. Kleinunternehmer)</td><td class="num">€3.88</td><td class="num">€22.62</td><td class="num">14.6%</td></tr>',
     '<tr><td>No VAT ID (e.g. Kleinunternehmer)</td><td class="num">€3.87</td><td class="num">€22.63</td><td class="num">14.6%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>VAT ID submitted</td><td class="num">€3.26</td><td class="num">€23.24</td><td class="num">12.3%</td></tr>',
     '<tr><td>VAT ID submitted</td><td class="num">€3.25</td><td class="num">€23.25</td><td class="num">12.3%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>VAT ID, and your price includes 19% VAT on the sale</td><td class="num">€3.26</td><td class="num">€19.01</td><td class="num">12.3%</td></tr>',
     '<tr><td>VAT ID, and your price includes 19% VAT on the sale</td><td class="num">€3.25</td><td class="num">€19.02</td><td class="num">12.3%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>VAT ID, price includes VAT, Offsite Ads order</td><td class="num">€7.24</td><td class="num">€15.03</td><td class="num">27.3%</td></tr>',
     '<tr><td>VAT ID, price includes VAT, Offsite Ads order</td><td class="num">€7.23</td><td class="num">€15.04</td><td class="num">27.3%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '€0.18 plus €0.30 is €0.48 before a single percentage is applied',
     '€0.17 plus €0.30 is €0.47 before a single percentage is applied'),
    ('etsy-fees-germany/index.html',
     '<tr><td>€10</td><td class="num">€1.82</td><td class="num">€8.18</td><td class="num">18.2%</td></tr>',
     '<tr><td>€10</td><td class="num">€1.81</td><td class="num">€8.19</td><td class="num">18.1%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>€25</td><td class="num">€3.70</td><td class="num">€21.30</td><td class="num">14.8%</td></tr>',
     '<tr><td>€25</td><td class="num">€3.69</td><td class="num">€21.31</td><td class="num">14.8%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>€50</td><td class="num">€6.82</td><td class="num">€43.18</td><td class="num">13.6%</td></tr>',
     '<tr><td>€50</td><td class="num">€6.81</td><td class="num">€43.19</td><td class="num">13.6%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>€100</td><td class="num">€13.07</td><td class="num">€86.93</td><td class="num">13.1%</td></tr>',
     '<tr><td>€100</td><td class="num">€13.05</td><td class="num">€86.95</td><td class="num">13.1%</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>Germany</td><td class="num">0%</td><td class="num">€13.07</td><td class="num">€86.93</td></tr>',
     '<tr><td>Germany</td><td class="num">0%</td><td class="num">€13.05</td><td class="num">€86.95</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>Netherlands</td><td class="num">0%</td><td class="num">€13.29</td><td class="num">€86.71</td></tr>',
     '<tr><td>Netherlands</td><td class="num">0%</td><td class="num">€13.27</td><td class="num">€86.73</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>France</td><td class="num">1.14%</td><td class="num">€14.54</td><td class="num">€85.46</td></tr>',
     '<tr><td>France</td><td class="num">1.14%</td><td class="num">€14.53</td><td class="num">€85.47</td></tr>'),
    ('etsy-fees-germany/index.html',
     '<tr><td>Italy</td><td class="num">0.80%</td><td class="num">€14.37</td><td class="num">€85.63</td></tr>',
     '<tr><td>Italy</td><td class="num">0.80%</td><td class="num">€14.36</td><td class="num">€85.64</td></tr>'),
    ('etsy-fees-germany/index.html',
     'The gap between Germany and France is €1.47 on the same order',
     'The gap between Germany and France is €1.48 on the same order'),

    # ---------- VAT on fees ----------
    ('etsy-vat-on-fees/index.html',
     '<tr><td>Listing fee</td><td class="num">€0.18</td></tr>',
     '<tr><td>Listing fee</td><td class="num">€0.17</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>Subtotal — Etsy\'s cut</td><td class="num">€10.98</td></tr>',
     '<tr><td>Subtotal — Etsy\'s cut</td><td class="num">€10.97</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>VAT at 19% on that subtotal</td><td class="num">€2.09</td></tr>',
     '<tr><td>VAT at 19% on that subtotal</td><td class="num">€2.08</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td><strong>Total taken by Etsy</strong></td><td class="num"><strong>€13.07</strong></td></tr>',
     '<tr><td><strong>Total taken by Etsy</strong></td><td class="num"><strong>€13.05</strong></td></tr>'),
    ('etsy-vat-on-fees/index.html',
     'It is charged on €10.98 — the fee',
     'It is charged on €10.97 — the fee'),
    ('etsy-vat-on-fees/index.html',
     'the fee subtotal rises from €10.98 to €25.98 and the VAT from €2.09 to €4.94',
     'the fee subtotal rises from €10.97 to €25.97 and the VAT from €2.08 to €4.93'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>Australia</td><td class="num">10% GST</td><td class="num">A$10.03</td><td class="num">A$1.00</td><td class="num">A$11.03</td></tr>',
     '<tr><td>Australia</td><td class="num">10% GST</td><td class="num">A$10.04</td><td class="num">A$1.00</td><td class="num">A$11.04</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>Germany</td><td class="num">19%</td><td class="num">€10.98</td><td class="num">€2.09</td><td class="num">€13.07</td></tr>',
     '<tr><td>Germany</td><td class="num">19%</td><td class="num">€10.97</td><td class="num">€2.08</td><td class="num">€13.05</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>Netherlands</td><td class="num">21%</td><td class="num">€10.98</td><td class="num">€2.31</td><td class="num">€13.29</td></tr>',
     '<tr><td>Netherlands</td><td class="num">21%</td><td class="num">€10.97</td><td class="num">€2.30</td><td class="num">€13.27</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>Ireland</td><td class="num">23%</td><td class="num">€10.98</td><td class="num">€2.53</td><td class="num">€13.51</td></tr>',
     '<tr><td>Ireland</td><td class="num">23%</td><td class="num">€10.97</td><td class="num">€2.52</td><td class="num">€13.49</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>United Kingdom</td><td class="num">20%</td><td class="num">£11.34</td><td class="num">£2.27</td><td class="num">£13.61</td></tr>',
     '<tr><td>United Kingdom</td><td class="num">20%</td><td class="num">£11.33</td><td class="num">£2.27</td><td class="num">£13.60</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>Spain</td><td class="num">21%</td><td class="num">€11.86</td><td class="num">€2.49</td><td class="num">€14.35</td></tr>',
     '<tr><td>Spain</td><td class="num">21%</td><td class="num">€11.85</td><td class="num">€2.49</td><td class="num">€14.34</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>Italy</td><td class="num">22%</td><td class="num">€11.78</td><td class="num">€2.59</td><td class="num">€14.37</td></tr>',
     '<tr><td>Italy</td><td class="num">22%</td><td class="num">€11.77</td><td class="num">€2.59</td><td class="num">€14.36</td></tr>'),
    ('etsy-vat-on-fees/index.html',
     '<tr><td>France</td><td class="num">20%</td><td class="num">€12.12</td><td class="num">€2.42</td><td class="num">€14.54</td></tr>',
     '<tr><td>France</td><td class="num">20%</td><td class="num">€12.11</td><td class="num">€2.42</td><td class="num">€14.53</td></tr>'),

    # ---------- listing-fee ----------
    ('listing-fee/index.html',
     'so a UK shop pays roughly £0.16 and a euro shop roughly €0.18',
     'so a UK shop pays roughly £0.15 and a euro shop roughly €0.17'),
]


def main():
    ok = fail = 0
    cache = {}
    for rel, old, new in EDITS:
        p = os.path.join(BASE, rel)
        if p not in cache:
            with io.open(p, encoding='utf-8') as f:
                cache[p] = f.read()
        txt = cache[p]
        n = txt.count(old)
        if n != 1:
            print('FAIL  %-34s 命中 %d 次: %s' % (rel, n, old[:60].replace('\n', ' ')))
            fail += 1
            continue
        cache[p] = txt.replace(old, new)
        ok += 1
    for p, txt in cache.items():
        with io.open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(txt)
    print('\n替换成功 %d 处，失败 %d 处，改写文件 %d 个' % (ok, fail, len(cache)))
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
