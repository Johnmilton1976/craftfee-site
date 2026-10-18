# -*- coding: utf-8 -*-
"""第二批：首页十国对比表 + 监管费页五国表 + UK 正文残留。"""
import io, os, sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

EDITS = [
    # ---- UK 正文残留（上一批只改了前半句）----
    ('etsy-fees-uk/index.html',
     'So the £3.64 of fees above actually costs a VAT-registered seller £3.65',
     'So the £3.64 of fees above actually costs a VAT-registered seller £3.64'),

    # ---- 首页：100 单含 VAT/GST on fees 的十国表 ----
    ('index.html',
     '<tr><td>Australia</td><td>3% + A$0.25</td><td>None</td><td class="num">A$1.00</td><td class="num">A$11.03</td><td class="num">A$88.97</td><td class="num">11.0%</td></tr>',
     '<tr><td>Australia</td><td>3% + A$0.25</td><td>None</td><td class="num">A$1.00</td><td class="num">A$11.04</td><td class="num">A$88.96</td><td class="num">11.0%</td></tr>'),
    ('index.html',
     '<tr><td>Germany</td><td>4% + €0.30</td><td>None</td><td class="num">€2.09</td><td class="num">€13.07</td><td class="num">€86.93</td><td class="num">13.1%</td></tr>',
     '<tr><td>Germany</td><td>4% + €0.30</td><td>None</td><td class="num">€2.08</td><td class="num">€13.05</td><td class="num">€86.95</td><td class="num">13.1%</td></tr>'),
    ('index.html',
     '<tr><td>Netherlands</td><td>4% + €0.30</td><td>None</td><td class="num">€2.31</td><td class="num">€13.29</td><td class="num">€86.71</td><td class="num">13.3%</td></tr>',
     '<tr><td>Netherlands</td><td>4% + €0.30</td><td>None</td><td class="num">€2.30</td><td class="num">€13.27</td><td class="num">€86.73</td><td class="num">13.3%</td></tr>'),
    ('index.html',
     '<tr><td>Ireland</td><td>4% + €0.30</td><td>None</td><td class="num">€2.53</td><td class="num">€13.51</td><td class="num">€86.49</td><td class="num">13.5%</td></tr>',
     '<tr><td>Ireland</td><td>4% + €0.30</td><td>None</td><td class="num">€2.52</td><td class="num">€13.49</td><td class="num">€86.51</td><td class="num">13.5%</td></tr>'),
    ('index.html',
     '<tr><td>United Kingdom</td><td>4% + £0.20</td><td>0.48%</td><td class="num">£2.27</td><td class="num">£13.61</td><td class="num">£86.39</td><td class="num">13.6%</td></tr>',
     '<tr><td>United Kingdom</td><td>4% + £0.20</td><td>0.48%</td><td class="num">£2.27</td><td class="num">£13.60</td><td class="num">£86.40</td><td class="num">13.6%</td></tr>'),
    ('index.html',
     '<tr><td>Spain</td><td>4% + €0.30</td><td>0.88%</td><td class="num">€2.49</td><td class="num">€14.35</td><td class="num">€85.65</td><td class="num">14.3%</td></tr>',
     '<tr><td>Spain</td><td>4% + €0.30</td><td>0.88%</td><td class="num">€2.49</td><td class="num">€14.34</td><td class="num">€85.66</td><td class="num">14.3%</td></tr>'),
    ('index.html',
     '<tr><td>Italy</td><td>4% + €0.30</td><td>0.80%</td><td class="num">€2.59</td><td class="num">€14.37</td><td class="num">€85.63</td><td class="num">14.4%</td></tr>',
     '<tr><td>Italy</td><td>4% + €0.30</td><td>0.80%</td><td class="num">€2.59</td><td class="num">€14.36</td><td class="num">€85.64</td><td class="num">14.4%</td></tr>'),
    ('index.html',
     '<tr><td>France</td><td>4% + €0.30</td><td>1.14%</td><td class="num">€2.42</td><td class="num">€14.54</td><td class="num">€85.46</td><td class="num">14.5%</td></tr>',
     '<tr><td>France</td><td>4% + €0.30</td><td>1.14%</td><td class="num">€2.42</td><td class="num">€14.53</td><td class="num">€85.47</td><td class="num">14.5%</td></tr>'),

    # ---- 监管费页：100 单，不含 VAT on fees ----
    ('etsy-regulatory-operating-fee/index.html',
     '<tr><td>Germany</td><td class="num">€0.00</td><td class="num">€10.98</td><td class="num">€89.02</td><td class="num">11.0%</td></tr>',
     '<tr><td>Germany</td><td class="num">€0.00</td><td class="num">€10.97</td><td class="num">€89.03</td><td class="num">11.0%</td></tr>'),
    ('etsy-regulatory-operating-fee/index.html',
     '<tr><td>Netherlands</td><td class="num">€0.00</td><td class="num">€10.98</td><td class="num">€89.02</td><td class="num">11.0%</td></tr>',
     '<tr><td>Netherlands</td><td class="num">€0.00</td><td class="num">€10.97</td><td class="num">€89.03</td><td class="num">11.0%</td></tr>'),
    ('etsy-regulatory-operating-fee/index.html',
     '<tr><td>Italy</td><td class="num">€0.80</td><td class="num">€11.78</td><td class="num">€88.22</td><td class="num">11.8%</td></tr>',
     '<tr><td>Italy</td><td class="num">€0.80</td><td class="num">€11.77</td><td class="num">€88.23</td><td class="num">11.8%</td></tr>'),
    ('etsy-regulatory-operating-fee/index.html',
     '<tr><td>Spain</td><td class="num">€0.88</td><td class="num">€11.86</td><td class="num">€88.14</td><td class="num">11.9%</td></tr>',
     '<tr><td>Spain</td><td class="num">€0.88</td><td class="num">€11.85</td><td class="num">€88.15</td><td class="num">11.9%</td></tr>'),
    ('etsy-regulatory-operating-fee/index.html',
     '<tr><td>France</td><td class="num">€1.14</td><td class="num">€12.12</td><td class="num">€87.88</td><td class="num">12.1%</td></tr>',
     '<tr><td>France</td><td class="num">€1.14</td><td class="num">€12.11</td><td class="num">€87.89</td><td class="num">12.1%</td></tr>'),
]


def main():
    ok = fail = 0
    cache = {}
    for rel, old, new in EDITS:
        p = os.path.join(BASE, rel)
        if p not in cache:
            with io.open(p, encoding='utf-8') as f:
                cache[p] = f.read()
        n = cache[p].count(old)
        if n != 1:
            print('FAIL  %-40s 命中 %d: %s' % (rel, n, old[:70]))
            fail += 1
            continue
        cache[p] = cache[p].replace(old, new)
        ok += 1
    for p, txt in cache.items():
        with io.open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(txt)
    print('替换成功 %d，失败 %d' % (ok, fail))
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
