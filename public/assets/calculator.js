/* Etsy Fee Calculator — calculation engine
   Rates verified against Etsy's own Help pages, October 2026. Every rate is
   applied to the correct base:
   - Transaction fee 6.5%  -> item + shipping + gift wrap (EXCLUDES sales tax)
   - Payment processing    -> item + shipping + gift wrap + sales tax
   - Regulatory fee        -> item + shipping + gift wrap
   - Offsite Ads 15%/12%   -> the whole order total, capped at USD 100 per order
   Payment processing is set by the country of your BANK ACCOUNT, and in Canada
   and Australia it is higher on orders from abroad — hence proc vs procInt.
*/
var RATES = {
  US: { sym:'$',  proc:0.030, procInt:0,     fixed:0.25, list:0.20, reg:0,      cap:100, vat:0,  feeVat:0    },
  UK: { sym:'£',  proc:0.040, procInt:0,     fixed:0.20, list:0.15, reg:0.0048, cap:80,  vat:20, feeVat:0.20 },
  CA: { sym:'C$', proc:0.030, procInt:0.040, fixed:0.25, list:0.28, reg:0.0050, cap:140, vat:0,  feeVat:0.05 },
  AU: { sym:'A$', proc:0.030, procInt:0.040, fixed:0.25, list:0.29, reg:0,      cap:140, vat:0,  feeVat:0.10 },
  DE: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17, reg:0,      cap:92,  vat:19, feeVat:0.19 },
  FR: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17, reg:0.0114, cap:92,  vat:20, feeVat:0.20 },
  IT: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17, reg:0.0080, cap:92,  vat:22, feeVat:0.22 },
  ES: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17, reg:0.0088, cap:92,  vat:21, feeVat:0.21 },
  NL: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17, reg:0,      cap:92,  vat:21, feeVat:0.21 },
  IE: { sym:'€',  proc:0.040, procInt:0,     fixed:0.30, list:0.17, reg:0,      cap:92,  vat:23, feeVat:0.23 }
};
var TXN = 0.065;              /* transaction fee, same in every country */
var CONV = 0.025;             /* currency conversion, only if payout currency differs */
var PLUS_MONTHLY = 10;        /* Etsy Plus subscription */
var PLUS_ORDERS = 30;         /* orders used to amortise it */

var state = { offsite:false, offsiteRate:0.15, plus:false, conv:false, intl:false, feeVat:false, mode:'forward' };

function rv(){ return RATES[document.getElementById('country').value]; }
function rvKey(){ return document.getElementById('country').value; }
/* Etsy charges VAT/GST on its own fees outside the US. The rate follows the
   seller's country, not the VAT rate on the sale — Canada is the clearest case,
   where the sale carries no VAT line but Etsy's fees still carry GST/HST. */
function feeVatNote(key, R){
  var pct = (R.feeVat * 100).toFixed(0) + '%';
  if (key === 'CA') return 'Etsy adds ' + pct + ' GST to its own fees for sellers here — or 13–15% HST in those provinces.';
  if (key === 'AU') return 'Etsy adds ' + pct + ' GST to its own fees for sellers here, unless Etsy has your GST ID or ABN.';
  return 'Etsy adds ' + pct + ' VAT to its own fees for sellers here.';
}
function sym(){ return rv().sym; }
/* processing rate actually applied: international where the country has two rates */
function procRate(){ var R = rv(); return (R.procInt && state.intl) ? R.procInt : R.proc; }
function num(id){
  var v = parseFloat(document.getElementById(id).value);
  return isNaN(v) || v < 0 ? 0 : v;
}
function money(n){
  var s = sym();
  if (!isFinite(n)) return s + '0.00';
  return (n < 0 ? '-' + s : s) + Math.abs(n).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});
}
function vatFrac(){ return num('vat') / 100 / (1 + num('vat') / 100); }
/* round to cents the way an invoice does, so the numbers on screen always add up */
function c2(n){ return Math.round((n + 1e-9) * 100) / 100; }

function compute(price){
  var R = rv();
  var ship = num('ship'), wrap = num('wrap'), cost = num('cost'), tax = num('tax');
  var qty = Math.max(1, Math.floor(num('qty')) || 1);
  var cpct = state.conv ? CONV : 0;
  var pr = procRate();

  var gross = price * qty + ship + wrap;
  var vf = vatFrac();
  var vatAmt = gross * vf;
  var netRev = gross - vatAmt;

  var listing = c2(R.list * qty);
  var transaction = c2(gross * TXN);
  var processing = c2((gross + tax) * pr + R.fixed);
  var regulatory = c2(gross * R.reg);
  var offsiteRaw = state.offsite ? gross * state.offsiteRate : 0;
  var offsite = c2(Math.min(offsiteRaw, R.cap));
  var conversion = c2(cpct * netRev);
  var plus = c2(state.plus ? PLUS_MONTHLY / PLUS_ORDERS : 0);

  /* Etsy charges VAT/GST on its own fees in most countries outside the US.
     Registered sellers reclaim it; unregistered sellers absorb it. */
  var fv = state.feeVat ? R.feeVat : 0;
  var feesNet = c2(listing + transaction + processing + regulatory + offsite + conversion + plus);
  var feeVatAmt = c2(feesNet * fv);
  var fees = c2(feesNet + feeVatAmt);
  var keep = c2(c2(netRev) - fees);
  var profit = c2(keep - cost);
  var effRate = gross > 0 ? fees / gross * 100 : 0;
  var margin = netRev > 0 ? profit / netRev * 100 : 0;
  var markup = cost > 0 ? profit / cost * 100 : 0;

  var v = TXN + pr + R.reg + (state.offsite ? state.offsiteRate : 0);
  var denom = (1 - vf) * (1 - cpct) - v * (1 + fv);
  var F = (R.list * qty + R.fixed + (state.plus ? PLUS_MONTHLY / PLUS_ORDERS : 0)) * (1 + fv);
  var beGross = denom > 0.01 ? (cost + F) / denom : 0;
  var be = Math.max(0, (beGross - ship - wrap) / qty);

  return {
    gross:gross, vatAmt:vatAmt, netRev:netRev, fees:fees, feesNet:feesNet, keep:keep, profit:profit,
    effRate:effRate, margin:margin, markup:markup, cost:cost, qty:qty, be:be, denom:denom, F:F,
    pr:pr, fv:fv,
    lines:{ listing:listing, transaction:transaction, processing:processing,
            regulatory:regulatory, offsite:offsite, conversion:conversion, plus:plus, feeVat:feeVatAmt },
    R:R
  };
}

function solvePrice(target){
  var R = rv();
  var qty = Math.max(1, Math.floor(num('qty')) || 1);
  var cpct = state.conv ? CONV : 0;
  var vf = vatFrac();
  var fv = state.feeVat ? R.feeVat : 0;
  var v = TXN + procRate() + R.reg + (state.offsite ? state.offsiteRate : 0);
  var denom = (1 - vf) * (1 - cpct) - v * (1 + fv);
  if (denom <= 0.01) return NaN;
  var F = (R.list * qty + R.fixed + (state.plus ? PLUS_MONTHLY / PLUS_ORDERS : 0)) * (1 + fv);
  var gross = (target + F) / denom;
  return (gross - num('ship') - num('wrap')) / qty;
}

/* the international-buyer toggle only exists where the country has two rates */
function syncIntl(){
  var R = rv();
  var row = document.getElementById('intlRow');
  if (R.procInt) {
    row.style.display = 'block';
    document.getElementById('intlHint').textContent =
      'Etsy charges ' + (R.procInt * 100).toFixed(1).replace('.0','') + '% + ' + money(R.fixed) +
      ' on orders from outside your country, against ' + (R.proc * 100).toFixed(1).replace('.0','') +
      '% + ' + money(R.fixed) + ' on domestic orders.';
  } else {
    row.style.display = 'none';
    if (state.intl) {
      state.intl = false;
      document.getElementById('intl').classList.remove('on');
    }
  }
}

function calc(){
  var isFwd = state.mode === 'forward';
  var price;

  if (isFwd) {
    price = num('price');
  } else {
    price = solvePrice(num('target'));
    if (!isFinite(price) || price < 0) price = 0;
    document.getElementById('price').value = price.toFixed(2);
  }

  var x = compute(price);
  var R = x.R;

  /* the per-order cap is a rounded local-currency figure, not always "$100" */
  document.getElementById('oaHint').textContent =
    'Charged on the whole order total, capped at ' + money(R.cap) + ' per order';

  document.getElementById('heroLbl').textContent = isFwd ? 'You keep' : 'You should charge';
  document.getElementById('resultTitle').textContent = isFwd ? 'YOUR PAYOUT' : 'YOUR PRICE';
  document.getElementById('keep').textContent = isFwd ? money(x.keep) : money(price);
  document.getElementById('effrate').textContent = x.gross > 0
    ? 'Buyer pays ' + money(x.gross) + ' · Effective Etsy rate ' + x.effRate.toFixed(1) + '%'
    : 'Enter a price to begin';

  document.getElementById('o1').textContent = money(price * x.qty);
  document.getElementById('o2').textContent = money(num('ship'));
  document.getElementById('o3').textContent = money(num('wrap'));
  document.getElementById('o4').textContent = '-' + money(x.vatAmt);
  document.getElementById('o5').textContent = money(num('tax'));
  document.getElementById('oWrapRow').style.display = num('wrap') > 0 ? 'flex' : 'none';
  document.getElementById('oVatRow').style.display = x.vatAmt > 0 ? 'flex' : 'none';
  document.getElementById('oTaxRow').style.display = num('tax') > 0 ? 'flex' : 'none';
  document.getElementById('oRev').textContent = money(x.netRev);

  document.getElementById('l1base').textContent = money(R.list) + ' × ' + x.qty;
  document.getElementById('l2base').textContent = '6.5% of ' + money(x.gross) + ', excl. tax';
  document.getElementById('l3base').textContent = (x.pr * 100).toFixed(1).replace('.0','') + '% + ' + money(R.fixed) +
    (state.intl && R.procInt ? ' · international' : '') + ', incl. tax';
  document.getElementById('l4base').textContent = R.reg > 0 ? (R.reg * 100).toFixed(2) + '% of order' : 'not charged in your country';
  document.getElementById('l5base').textContent = (state.offsiteRate * 100) + '% of order, cap ' + money(R.cap);
  document.getElementById('l6base').textContent = '2.5%, payout currency differs';
  document.getElementById('l7base').textContent = money(PLUS_MONTHLY) + '/mo over ' + PLUS_ORDERS + ' orders';
  document.getElementById('l8base').textContent = (R.feeVat * 100).toFixed(0) + '% on Etsy\'s fees';

  document.getElementById('f1').textContent = money(x.lines.listing);
  document.getElementById('f2').textContent = money(x.lines.transaction);
  document.getElementById('f3').textContent = money(x.lines.processing);
  document.getElementById('f4').textContent = money(x.lines.regulatory);
  document.getElementById('f5').textContent = money(x.lines.offsite);
  document.getElementById('f6').textContent = money(x.lines.conversion);
  document.getElementById('f7').textContent = money(x.lines.plus);
  document.getElementById('f8').textContent = money(x.lines.feeVat);
  document.getElementById('ftot').textContent = money(x.fees);
  document.getElementById('oaRow').style.display = state.offsite ? 'flex' : 'none';
  document.getElementById('cvRow').style.display = state.conv ? 'flex' : 'none';
  document.getElementById('plusRow').style.display = state.plus ? 'flex' : 'none';
  document.getElementById('regRow').style.display = R.reg > 0 ? 'flex' : 'none';
  document.getElementById('fvRow').style.display = (state.feeVat && R.feeVat > 0) ? 'flex' : 'none';

  var fvRow = document.getElementById('feeVatRow');
  if (R.feeVat > 0) {
    fvRow.style.display = 'block';
    document.getElementById('feeVatHint').textContent = feeVatNote(rvKey(), R) +
      ' Registered sellers reclaim it as input tax; if you are not registered, it is a real cost.';
  } else {
    fvRow.style.display = 'none';
    if (state.feeVat) {
      state.feeVat = false;
      document.getElementById('feevat').classList.remove('on');
    }
  }

  var total = Math.max(x.gross, 0.01);
  document.getElementById('barKeep').style.width = Math.max(0, x.keep / total * 100) + '%';
  document.getElementById('barFee').style.width = Math.min(100, x.fees / total * 100) + '%';
  var costW = Math.max(0, Math.min(100, x.cost / total * 100));
  document.getElementById('barCost').style.width = costW + '%';
  document.getElementById('barCost').style.display = x.cost > 0 ? 'block' : 'none';

  document.getElementById('profit').textContent = money(x.profit);
  document.getElementById('margin').textContent = x.netRev > 0 ? x.margin.toFixed(1) + '%' : '–';
  document.getElementById('markup').textContent = (x.cost > 0 && x.netRev > 0) ? x.markup.toFixed(0) + '%' : '–';
  document.getElementById('be').textContent = money(x.be);

  var g = document.getElementById('grade'), gt = document.getElementById('gradeTxt');
  var m = x.margin;
  if (x.netRev <= 0) { g.textContent='–'; g.style.background='#1D1F24'; g.style.color='#5F5E5A';
    gt.innerHTML='<b>Enter a price</b>The margin rating appears here.'; }
  else if (m >= 45) { g.textContent='A'; g.style.background='#085041'; g.style.color='#9FE1CB';
    gt.innerHTML='<b>Excellent margin — ' + m.toFixed(0) + '%</b>Room to absorb a return, a discount or a shipping upgrade without going negative.'; }
  else if (m >= 30) { g.textContent='B'; g.style.background='#085041'; g.style.color='#9FE1CB';
    gt.innerHTML='<b>Healthy margin — ' + m.toFixed(0) + '%</b>This is the target zone. Fees and materials are covered with room to spare.'; }
  else if (m >= 15) { g.textContent='C'; g.style.background='#633806'; g.style.color='#FAC775';
    gt.innerHTML='<b>Thin margin — ' + m.toFixed(0) + '%</b>One refund, or one Offsite Ad order, wipes out the profit on this sale.'; }
  else if (m >= 0) { g.textContent='D'; g.style.background='#633806'; g.style.color='#FAC775';
    gt.innerHTML='<b>At risk — ' + m.toFixed(0) + '%</b>Barely above water. A discount or a promoted click puts you underwater.'; }
  else { g.textContent='F'; g.style.background='#791F1F'; g.style.color='#F09595';
    gt.innerHTML='<b>Selling at a loss — ' + m.toFixed(0) + '%</b>Fees plus cost exceed what you receive. You need at least ' + money(x.be) + ', or a lower cost.'; }

  var ins = [];
  if (state.offsite && state.offsiteRate * x.gross > R.cap)
    ins.push({c:'warn', h:'The Offsite Ads cap just saved you money',
      t:'A ' + (state.offsiteRate*100) + '% fee on this order would be ' + money(state.offsiteRate*x.gross) + ', but Etsy caps it at ' + money(R.cap) + ' per order. Large orders through Offsite Ads are effectively cheaper than the headline rate suggests.'});
  if (x.gross > 0 && price * x.qty > 0 && price * x.qty < 20)
    ins.push({c:'warn', h:'Fixed fees punish cheap items',
      t:'The flat listing fee plus the fixed processing charge alone take ' + (((R.list + R.fixed) / x.gross) * 100).toFixed(1) + '% of what the buyer pays. The same order at 50 would cut your effective rate by more than a point.'});
  if (x.cost > 0 && x.keep > 0 && x.cost > x.keep * 0.6)
    ins.push({c:'warn', h:'Materials dominate your payout',
      t:'Your cost is ' + ((x.cost / x.keep) * 100).toFixed(0) + '% of what you take home. A small price rise flows almost entirely to profit, because percentage fees only take a fraction of it.'});
  if (x.vatAmt > 0)
    ins.push({c:'', h:'VAT is not your money',
      t:'Of the ' + money(x.gross) + ' the buyer pays, ' + money(x.vatAmt) + ' is VAT owed to the tax authority. Your real revenue is ' + money(x.netRev) + '. Pricing profit off the tax-inclusive number overstates it.'});
  if (state.intl && R.procInt)
    ins.push({c:'warn', h:'International orders cost you one extra point',
      t:'Processing on orders from outside your country is ' + (R.procInt*100).toFixed(1).replace('.0','') + '% + ' + money(R.fixed) + ' instead of ' + (R.proc*100).toFixed(1).replace('.0','') + '% + ' + money(R.fixed) + '. On this order that is ' + money((x.pr - R.proc) * x.gross) + ' more in fees.'});
  if (R.reg === 0 && !state.offsite)
    ins.push({c:'', h:'Why this country has no regulatory fee',
      t:'Etsy only charges a regulatory operating fee in countries with a digital services tax. The US, Germany, Australia and the Netherlands are not on that list — the UK, France, Italy, Spain and Canada are.'});
  if (state.offsite)
    ins.push({c:'warn', h:'Offsite Ads is the single biggest fee',
      t:'Your effective rate is ' + x.effRate.toFixed(1) + '%. Below 10,000 USD in trailing sales you can opt out; above it, participation is required for the life of the shop at the 12% rate.'});
  if (!state.offsite && x.gross > 0)
    ins.push({c:'', h:'Try the Offsite Ads toggle',
      t:'If a sale arrives through an Etsy ad on Google, Facebook or Pinterest, Etsy takes 15% of the whole order. That is where the feeling that Etsy takes a third comes from.'});
  if (state.conv)
    ins.push({c:'', h:'Currency conversion only applies if the currencies differ',
      t:'The 2.5% conversion fee applies to the converted amount when your listing currency differs from your payout bank currency. If both are the same, switch this off.'});
  if (state.feeVat && R.feeVat > 0)
    ins.push({c:'warn', h:'Etsy charges tax on its own fees too',
      t:'On this order that is ' + money(x.lines.feeVat) + ' on top of ' + money(x.feesNet) + ' of fees — ' + (R.feeVat*100).toFixed(0) + '% of the fee stack, owed whether or not you are registered. Registered sellers reclaim it; unregistered sellers absorb it, which is part of why the real cost feels higher than the headline rates.'});
  if (ins.length === 0)
    ins.push({c:'', h:'How to read this',
      t:'The 6.5% transaction fee does not include sales tax, but payment processing does. Most calculators get one of those two bases wrong.'});

  document.getElementById('insights').innerHTML = ins.slice(0,3).map(function(i){
    return '<div class="insight ' + i.c + '"><b>' + i.h + '.</b> ' + i.t + '</div>';
  }).join('');

  document.getElementById('cmp1').textContent = x.effRate.toFixed(1) + '%';
  document.getElementById('cmp1bar').style.width = Math.max(2, Math.min(100, x.effRate / 30 * 100)) + '%';
  document.getElementById('cmp2').textContent = (x.effRate + (state.offsite ? 0 : 12)).toFixed(1) + '%';
  buildScenarios(R);
}

function buildScenarios(R){
  var prices = [10, 15, 25, 38, 50, 75, 100];
  var pr = procRate();
  var rows = prices.map(function(p){
    var fees = c2(c2(R.list) + c2(p * TXN) + c2(p * pr + R.fixed) + c2(p * R.reg));
    var keep = c2(p - fees);
    var eff = fees / p * 100;
    var hl = Math.abs(p - 38) < 0.01 ? ' class="hl"' : '';
    return '<tr' + hl + '><td>' + money(p) + '</td><td>' + money(fees) + '</td><td>' + money(keep) + '</td><td>' + eff.toFixed(1) + '%</td></tr>';
  });
  document.getElementById('scenBody').innerHTML = rows.join('');
}

function switchMode(m){
  state.mode = m;
  document.querySelectorAll('.tabs button').forEach(function(b){
    b.classList.toggle('on', b.dataset.mode === m);
  });
  document.getElementById('priceRow').style.display = m === 'forward' ? 'block' : 'none';
  document.getElementById('targetRow').style.display = m === 'reverse' ? 'block' : 'none';
  calc();
}

document.querySelectorAll('.tabs button').forEach(function(b){
  b.addEventListener('click', function(){ switchMode(this.dataset.mode); });
});
document.getElementById('offsite').addEventListener('click', function(){
  state.offsite = !state.offsite;
  this.classList.toggle('on', state.offsite);
  document.getElementById('offsiteRateWrap').style.display = state.offsite ? 'block' : 'none';
  calc();
});
document.querySelectorAll('#offsiteRateWrap button').forEach(function(b){
  b.addEventListener('click', function(){
    state.offsiteRate = parseFloat(this.dataset.r);
    document.querySelectorAll('#offsiteRateWrap button').forEach(function(o){ o.classList.toggle('on', o === this); }, this);
    calc();
  });
});
document.getElementById('plus').addEventListener('click', function(){
  state.plus = !state.plus;
  this.classList.toggle('on', state.plus);
  calc();
});
document.getElementById('conv').addEventListener('click', function(){
  state.conv = !state.conv;
  this.classList.toggle('on', state.conv);
  calc();
});
document.getElementById('intl').addEventListener('click', function(){
  state.intl = !state.intl;
  this.classList.toggle('on', state.intl);
  calc();
});
document.getElementById('feevat').addEventListener('click', function(){
  state.feeVat = !state.feeVat;
  this.classList.toggle('on', state.feeVat);
  calc();
});
/* Only the price shortcuts carry data-p. The Offsite Ads rate buttons sit in
   their own .presets block but carry data-r, so they must not be caught here —
   doing so used to blank the price field and kick the user out of reverse mode. */
document.querySelectorAll('.presets button[data-p]').forEach(function(b){
  b.addEventListener('click', function(){
    document.getElementById('price').value = this.dataset.p;
    if (state.mode === 'reverse') switchMode('forward');
    calc();
  });
});
document.getElementById('country').addEventListener('change', function(){
  var R = rv();
  document.getElementById('vatHint').textContent = R.vat > 0
    ? 'This country\'s standard VAT rate is about ' + R.vat + '%. Only enter it if you are VAT-registered.'
    : 'No VAT is added to Etsy prices in this country for domestic sellers.';
  syncIntl();
  calc();
});
['price','ship','wrap','cost','tax','vat','qty','target'].forEach(function(id){
  var el = document.getElementById(id);
  el.addEventListener('input', calc);
  el.addEventListener('change', calc);
});
syncIntl();
calc();
