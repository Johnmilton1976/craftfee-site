/* Offsite Ads decision tool.
   The article already says the fee is only worth paying on orders that would
   not have happened otherwise. This turns that sentence into a number:
   the share of attributed orders that has to be genuinely new, which is
   simply the fee divided by the contribution the order would have made. */
(function () {
  var CAPS = { USD: [100, '$'], GBP: [80, '\u00a3'], EUR: [92, '\u20ac'], CAD: [140, 'C$'], AUD: [140, 'A$'] };
  var $ = function (id) { return document.getElementById(id); };
  var S = { cur: 'USD', rev: 9000, aov: 38, m: 55, share: 20, p: 50, ever: false };

  function num(v, d) {
    d = (d == null ? 2 : d);
    var neg = v < 0; v = Math.abs(v);
    var parts = v.toFixed(d).split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return (neg ? '-' : '') + parts.join('.');
  }
  function money(v, d) { return (v < 0 ? '-' : '') + CAPS[S.cur][1] + num(Math.abs(v), d); }
  function pc(v, d) { return num(v * 100, d == null ? 1 : d) + '%'; }

  function calc() {
    var cap = CAPS[S.cur][0];
    var rate = S.ever ? 0.12 : 0.15;
    var m = S.m / 100, A = S.aov, share = S.share / 100;
    var orders = A > 0 ? S.rev / A : 0;
    var adOrders = orders * share;
    var raw = A * rate;
    var feePer = Math.min(raw, cap);
    var feeYear = adOrders * feePer;
    var feeYear12 = adOrders * Math.min(A * 0.12, cap);
    var contrib = m * A;
    var eff = A > 0 ? feePer / A : 0;
    var pStar = contrib > 0 ? feePer / contrib : 2;
    return { cap: cap, rate: rate, orders: orders, adOrders: adOrders, feePer: feePer, feeYear: feeYear,
      feeYear12: feeYear12, contrib: contrib, eff: eff, pStar: pStar, capped: raw > cap };
  }

  function grade(pStar) {
    if (pStar <= 0.20) return ['A', '#5DCAA5', '#141F1B'];
    if (pStar <= 0.33) return ['B', '#9FE1CB', '#141F1B'];
    if (pStar <= 0.50) return ['C', '#EF9F27', '#1F1B14'];
    if (pStar <= 0.75) return ['D', '#F0997B', '#1F1714'];
    return ['F', '#D85A30', '#1F1714'];
  }

  function verdict(pStar, hard) {
    if (hard) {
      return '<b>The fee is bigger than the margin</b>At this order size and margin, no amount of new customers makes an attributed order worth having. Either the price goes up or the low-priced listings go.';
    }
    var band = grade(pStar)[0];
    var n = Math.max(2, Math.round(1 / pStar));
    var words = { A: 'a comfortable margin for error', B: 'still a reasonable bet', C: 'a coin flip, honestly', D: 'a stretch most shops do not clear', F: 'unlikely for most shops' }[band];
    if (pStar > 0.5) {
      return '<b>' + pc(pStar, 0) + ' must be new</b>That is the share of your attributed orders that has to come from buyers you would not otherwise have reached. At that level it is ' + words + '.';
    }
    return '<b>At least 1 in ' + n + ' must be new</b>' + pc(pStar, 0) +
      ' of your attributed orders have to come from buyers you would not otherwise have reached, or the programme costs more than it brings. That is ' + words + '.';
  }

  function render() {
    var c = calc();
    $('feeYear').textContent = money(c.feeYear, 0);
    if (!S.ever) {
      $('feeNote').innerHTML = 'If you cross US$10,000 it becomes <b>' + money(c.feeYear12, 0) + '</b> at 12% &mdash; and opting out stops being an option.';
    } else {
      $('feeNote').innerHTML = 'That is <b>' + pc(S.rev > 0 ? c.feeYear / S.rev : 0) + '</b> of the revenue you took, and it is not optional.';
    }

    $('v1').textContent = num(c.orders, 0);
    $('v2').textContent = num(c.adOrders, 0) + '  (' + pc(S.share / 100, 0) + ')';
    $('v3').textContent = money(c.feePer);
    $('capNote').textContent = c.capped ? 'capped' : 'at ' + pc(c.rate, 0);
    $('v4').textContent = pc(c.eff);
    $('v5').textContent = c.pStar > 1.005 ? 'all of them, and it still loses'
      : (c.pStar > 0.95 ? 'all of them'
      : (c.pStar > 0.5 ? pc(c.pStar, 0) : '1 in ' + Math.max(2, Math.round(1 / c.pStar))));

    var g = grade(c.pStar);
    var hard = c.pStar > 1.005;
    $('grade').textContent = g[0];
    $('grade').style.background = g[2];
    $('grade').style.color = g[1];
    $('gradeTxt').innerHTML = verdict(c.pStar, hard);

    var bits = [];
    if (c.capped) {
      bits.push({ c: 'good', h: 'The cap is doing the work', t: 'At ' + pc(c.rate, 0) + ' your ' + money(S.aov) + ' order would carry ' + money(S.aov * c.rate) + ', but the fee stops at ' + money(c.cap) + '. Past ' + money(c.cap / c.rate, 0) + ' the effective rate falls as the order grows, which is the one place a big-ticket shop wins.' });
    } else {
      bits.push({ c: '', h: 'The cap never binds at your order size', t: 'It starts at ' + money(c.cap / c.rate, 0) + ' per order at ' + pc(c.rate, 0) + '. Below that you pay the full percentage on the whole order, shipping included.' });
    }
    if (!S.ever) {
      bits.push({ c: '', h: 'You can still leave', t: 'Below US$10,000 in every 365-day window, Shop Manager &rarr; Settings &rarr; Offsite Ads offers an opt-out. The catch is that crossing US$10,000 once makes the 12% rate and the mandatory status permanent, so this is a decision you get to make only while you are small.' });
    } else {
      bits.push({ c: 'warn', h: 'You cannot leave', t: 'Having been above US$10,000, the setting is gone for the life of the shop. The live question is not stay-or-go; it is whether to carry the fee or lift prices to cover it &mdash; and lifting prices costs sales too.' });
    }
    var rise = S.m / 100 > c.eff ? (S.m / 100) / (S.m / 100 - c.eff) - 1 : null;
    if (rise !== null && S.share > 0) {
      bits.push({ c: '', h: 'What absorbing it in the price would take', t: 'To keep the same cash from an attributed order you would have to charge ' + pc(rise, 1) + ' more on it &mdash; ' + money(S.aov * (1 + rise), 0) + ' instead of ' + money(S.aov, 0) + '. On every order, not just the advertised ones, that is a different shop.' });
    }
    if (S.share >= 45) {
      bits.push({ c: 'warn', h: 'Check that number before you trust the total', t: pc(S.share / 100, 0) + ' of orders arriving through ads is far above what most shops report. Open Payment account &rarr; find the month, and add up the Offsite Ads lines rather than estimating.' });
    }
    $('insights').innerHTML = bits.map(function (b) {
      return '<div class="insight ' + b.c + '"><b>' + b.h + '</b> ' + b.t + '</div>';
    }).join('');

    var rows = '', hi = -1, best = 99;
    [0, 25, 50, 75, 100].forEach(function (p, i) {
      var net = c.adOrders * ((p / 100) * c.contrib - c.feePer);
      var per = (p / 100) * c.contrib - c.feePer;
      var d = Math.abs(p - S.p); if (d < best) { best = d; hi = i; }
      rows += '<tr' + (d === best ? ' class="hl"' : '') + '><td>' + p + '%</td><td>' + money(net, 0) + '</td><td>' + money(per) + '</td></tr>';
    });
    $('scenBody').innerHTML = rows;
    $('pOut').textContent = S.p + '%';
    $('scenNote').innerHTML = c.pStar > 1.005
      ? 'Every row is negative. The fee per attributed order (' + money(c.feePer) + ') is larger than the margin the order carries (' + money(c.contrib) + '), so no mix of new and repeat buyers rescues it.'
      : 'Break-even is ' + pc(c.pStar, 0) + '. Below that the year is a loss, above it a gain &mdash; and the highlighted row is where your slider sits.';
  }

  function sync() {
    S.cur = $('cur').value;
    S.rev = Math.max(0, parseFloat($('rev').value) || 0);
    S.aov = Math.max(1, parseFloat($('aov').value) || 1);
    S.m = Math.min(95, Math.max(1, parseFloat($('m').value) || 1));
    S.share = Math.min(100, Math.max(0, parseFloat($('share').value) || 0));
    S.p = parseInt($('p').value, 10);
  }

  function url() {
    /* Inside a frame the address belongs to the host, not to us, and
       rewriting it would drop the ?embed=1 that keeps this mode on. */
    if (location.search.indexOf('embed=1') > -1) return;
    var q = 'cur=' + S.cur + '&rev=' + Math.round(S.rev) + '&aov=' + S.aov + '&m=' + S.m + '&share=' + S.share + '&p=' + S.p + (S.ever ? '&ever=1' : '');
    try { history.replaceState(null, '', location.pathname + '?' + q); } catch (e) {}
  }

  function load() {
    var q = new URLSearchParams(location.search);
    if (q.get('cur') && CAPS[q.get('cur')]) $('cur').value = q.get('cur');
    if (q.get('rev')) $('rev').value = q.get('rev');
    if (q.get('aov')) $('aov').value = q.get('aov');
    if (q.get('m')) $('m').value = q.get('m');
    if (q.get('share')) $('share').value = q.get('share');
    if (q.get('p')) $('p').value = q.get('p');
    if (q.get('ever') === '1') S.ever = true;
    sync();
  }

  function setToggle() { $('ever').classList.toggle('on', S.ever); }

  ['rev', 'aov', 'm', 'share'].forEach(function (id) {
    $(id).addEventListener('input', function () {
      sync();
      if (id === 'rev') { S.ever = S.rev >= 10000; setToggle(); }
      render(); url();
    });
    $(id).addEventListener('change', function () { sync(); render(); url(); });
  });
  $('cur').addEventListener('change', function () { sync(); render(); url(); });
  $('p').addEventListener('input', function () { sync(); render(); });
  $('p').addEventListener('change', function () { sync(); render(); url(); });
  $('ever').addEventListener('click', function () { S.ever = !S.ever; setToggle(); render(); url(); });

  var presets = {
    small: { cur: 'USD', rev: 6000, aov: 30, m: 60, share: 15, p: 50, ever: false },
    mid: { cur: 'USD', rev: 24000, aov: 45, m: 50, share: 30, p: 50, ever: true },
    high: { cur: 'USD', rev: 30000, aov: 320, m: 65, share: 25, p: 50, ever: true }
  };
  [].slice.call(document.querySelectorAll('.presets button')).forEach(function (b) {
    b.addEventListener('click', function () {
      var p = presets[b.getAttribute('data-preset')];
      $('cur').value = p.cur; $('rev').value = p.rev; $('aov').value = p.aov;
      $('m').value = p.m; $('share').value = p.share; $('p').value = p.p;
      S.ever = p.ever; setToggle(); sync(); render(); url();
    });
  });

  load(); setToggle(); render();
})();
