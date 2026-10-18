# -*- coding: utf-8 -*-
"""复现 calculator.js 的 compute()，用于核对页面示例数字。
费率以 Etsy 官方 2026-10-18 现值为准。
用法：python _recalc.py
"""
TXN, CONV, PLUS_M, PLUS_N = 0.065, 0.025, 10, 30

RATES = {
    'US': dict(sym='$',  proc=.030, procInt=0,    fixed=.25, list=.20, reg=0,      cap=100, feeVat=0),
    'UK': dict(sym='£',  proc=.040, procInt=0,    fixed=.20, list=.15, reg=.0048,  cap=80,  feeVat=.20),
    'CA': dict(sym='C$', proc=.030, procInt=.040, fixed=.25, list=.28, reg=.0050,  cap=140, feeVat=.05),
    'AU': dict(sym='A$', proc=.030, procInt=.040, fixed=.25, list=.29, reg=0,      cap=140, feeVat=.10),
    'DE': dict(sym='€',  proc=.040, procInt=0,    fixed=.30, list=.17, reg=0,      cap=92,  feeVat=.19),
    'FR': dict(sym='€',  proc=.040, procInt=0,    fixed=.30, list=.17, reg=.0114,  cap=92,  feeVat=.20),
    'IT': dict(sym='€',  proc=.040, procInt=0,    fixed=.30, list=.17, reg=.0080,  cap=92,  feeVat=.22),
    'ES': dict(sym='€',  proc=.040, procInt=0,    fixed=.30, list=.17, reg=.0088,  cap=92,  feeVat=.21),
    'NL': dict(sym='€',  proc=.040, procInt=0,    fixed=.30, list=.17, reg=0,      cap=92,  feeVat=.21),
    'IE': dict(sym='€',  proc=.040, procInt=0,    fixed=.30, list=.17, reg=0,      cap=92,  feeVat=.23),
}


def c2(n):
    """JS Math.round((n+1e-9)*100)/100 的等价位实现（n>=0 时一致）"""
    return int((n + 1e-9) * 100 + 0.5) / 100


def calc(key, price, ship=0.0, qty=1, wrap=0.0, tax=0.0, intl=False,
         offsite=False, offsite_rate=.15, fee_vat=False, conv=False, plus=False):
    R = RATES[key]
    pr = R['procInt'] if (intl and R['procInt']) else R['proc']
    gross = price * qty + ship + wrap
    listing = c2(R['list'] * qty)
    transaction = c2(gross * TXN)
    processing = c2((gross + tax) * pr + R['fixed'])
    regulatory = c2(gross * R['reg'])
    offsite_amt = c2(min(gross * offsite_rate, R['cap'])) if offsite else 0.0
    conversion = c2(CONV * gross) if conv else 0.0
    plus_amt = c2(PLUS_M / PLUS_N) if plus else 0.0
    fv = R['feeVat'] if fee_vat else 0
    fees_net = c2(listing + transaction + processing + regulatory + offsite_amt + conversion + plus_amt)
    fee_vat = c2(fees_net * fv)
    fees = c2(fees_net + fee_vat)
    keep = c2(c2(gross) - fees)
    return dict(listing=listing, transaction=transaction, processing=processing, regulatory=regulatory,
                offsite=offsite_amt, fees_net=fees_net, fee_vat=fee_vat, fees=fees, keep=keep,
                eff=fees / gross * 100 if gross else 0, gross=gross)


def show(label, d, sym):
    print('%-46s L%-6s T%-7s P%-7s net%-8s vat%-6s ALL%-7s keep%-8s %.1f%%'
          % (label, d['listing'], d['transaction'], d['processing'], d['fees_net'],
             d['fee_vat'], d['fees'], d['keep'], d['eff']))


if __name__ == '__main__':
    print('=== 德国 DE ===')
    show('22 item + 4.5 ship, feeVat 19%', calc('DE', 22, ship=4.5, fee_vat=True), '€')
    show('same, no feeVat (VAT ID)', calc('DE', 22, ship=4.5), '€')
    for p in (10, 25, 50, 100, 200):
        show('item %.0f only, feeVat 19%%' % p, calc('DE', p, fee_vat=True), '€')
    print()
    print('=== 澳洲 AU ===')
    show('30 domestic', calc('AU', 30), 'A$')
    show('30 international', calc('AU', 30, intl=True), 'A$')
    show('35 + 7 ship domestic', calc('AU', 35, ship=7), 'A$')
    show('35+7 domestic, GST on fees', calc('AU', 35, ship=7, fee_vat=True), 'A$')
    show('35+7 domestic, GST + offsite', calc('AU', 35, ship=7, fee_vat=True, offsite=True), 'A$')
    show('35+7 domestic, offsite only', calc('AU', 35, ship=7, offsite=True), 'A$')
    print()
    print('=== 英国 UK ===')
    show('30 incl 20% VAT, feeVat 20%', calc('UK', 25, fee_vat=True), '£')
    show('30 incl VAT -> net 25, no feeVat', calc('UK', 25), '£')
    print()
    print('=== VAT 页：100 单，无 VAT ID ===')
    for k in ('US', 'AU', 'CA', 'DE', 'NL', 'IE', 'FR', 'IT', 'ES', 'UK'):
        d = calc(k, 100, fee_vat=True)
        print('%-4s gross100  net %.2f  vat %.2f  all %.2f  (keep %.2f)'
              % (k, d['fees_net'], d['fee_vat'], d['fees'], d['keep']))
    print()
    print('=== VAT 页：DE 100 单 + 15% offsite ===')
    d = calc('DE', 100, fee_vat=True, offsite=True)
    print('  net %.2f  vat %.2f  all %.2f  keep %.2f' % (d['fees_net'], d['fee_vat'], d['fees'], d['keep']))
