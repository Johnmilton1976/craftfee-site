/* Shareable calculator state, and height reporting for embeds (2026-11-07).
 *
 * Two problems this solves, both of which decide whether anyone ever links to
 * these calculators rather than quoting them from memory:
 *
 * 1. A forum answer that reads "on a $38 print Etsy keeps $4.06" is worth
 *    nothing to the next reader, because they sell something else. A link that
 *    arrives with the numbers already in it is worth something. So every input
 *    is mirrored into the query string, and the page reads them back on load.
 *
 * 2. An embedding site should not have to guess a pixel height. The result
 *    column grows and shrinks with the answer, so the frame is told the real
 *    height whenever it changes; the snippet on each page listens for it.
 *
 * Loaded after each calculator's own script (defer), so the listeners that
 * recompute the results are already attached when values are restored.
 */
(function () {
  var isEmbed = location.search.indexOf('embed=1') > -1;
  var inputs = [].slice.call(document.querySelectorAll('input.inp[id], select[id]'));
  var toggles = [].slice.call(document.querySelectorAll('div.toggle[id]'));
  var params;
  try { params = new URLSearchParams(location.search); } catch (e) { params = null; }

  function isOn(el) {
    return el.classList.contains('on') || el.getAttribute('aria-pressed') === 'true';
  }

  /* Write the current state into the address bar. replaceState, not pushState:
     typing 38 then deleting the 8 should not leave two history entries. */
  function syncUrl() {
    if (isEmbed || !params) return;
    try {
      var u = new URL(location.href);
      inputs.forEach(function (el) {
        var v = el.value;
        if (v === '' || v === null) { u.searchParams.delete(el.id); return; }
        u.searchParams.set(el.id, v);
      });
      toggles.forEach(function (el) {
        if (isOn(el)) { u.searchParams.set('t_' + el.id, '1'); }
        else { u.searchParams.delete('t_' + el.id); }
      });
      history.replaceState(null, '', u.toString());
    } catch (e) { /* old browser: the button still copies the plain URL */ }
  }

  /* Restore a shared link before the first paint of the results. Toggles are
     clicked rather than class-flipped, because the page's own click handler is
     what applies the rate change and repaints. */
  function restore() {
    if (!params) return;
    var changed = [];
    inputs.forEach(function (el) {
      var v = params.get(el.id);
      if (v === null || v === '') return;
      if (el.tagName === 'SELECT') {
        var hit = [].slice.call(el.options).some(function (o) { return o.value === v; });
        if (!hit) return;
      } else if (el.type === 'number' && isNaN(parseFloat(v))) {
        return;
      }
      el.value = v;
      changed.push(el);
    });
    toggles.forEach(function (el) {
      if (params.get('t_' + el.id) === '1' && !isOn(el)) { el.click(); }
      if (params.get('t_' + el.id) !== '1' && isOn(el)) { el.click(); }
    });
    /* Recompute. Both events are fired on every restored field: the page binds
       calc to 'input' on the number boxes but to 'change' on the country
       select, and firing only one of the two left a restored $100 order
       showing the $38 result. */
    changed.forEach(function (el) {
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
  }

  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(function () { return legacy(text); });
    }
    return legacy(text);
  }

  function legacy(text) {
    try {
      var t = document.createElement('textarea');
      t.value = text;
      t.setAttribute('readonly', '');
      t.style.position = 'fixed';
      t.style.top = '-1000px';
      document.body.appendChild(t);
      t.select();
      document.execCommand('copy');
      t.remove();
    } catch (e) { /* nothing else to try */ }
  }

  function addCopyButton() {
    if (isEmbed) return;
    var hero = document.querySelector('.hero');
    if (!hero) return;
    var b = document.createElement('button');
    b.type = 'button';
    b.id = 'cf-copy-link';
    b.textContent = 'Copy a link to this result';
    b.style.cssText = 'margin-top:14px;width:100%;background:#1D1F24;border:1px solid rgba(255,255,255,.12);' +
      'color:#9FE1CB;border-radius:10px;padding:10px 14px;font:inherit;font-size:13px;cursor:pointer';
    b.addEventListener('click', function () {
      syncUrl();
      var url = location.href;
      copy(url);
      b.textContent = 'Link copied \u2713';
      setTimeout(function () { b.textContent = 'Copy a link to this result'; }, 1800);
    });
    hero.parentNode.insertBefore(b, hero.nextSibling);
  }

  /* scrollHeight cannot be used to shrink a frame: once the iframe is taller
     than its content, scrollHeight reports the iframe's own height, so the
     number can only ever grow and never comes back down. Measure the bottom of
     the last visible block inside the calculator wrapper instead — that value
     depends on the width, not on how tall the host made the frame. */
  function measuredHeight() {
    var wrap = document.querySelector('main .wrap') || document.querySelector('.wrap');
    var bottom = 0;
    if (wrap) {
      [].slice.call(wrap.children).forEach(function (e) {
        var s = getComputedStyle(e);
        if (s.display === 'none' || s.visibility === 'hidden') return;
        var r = e.getBoundingClientRect();
        if (r.width > 0 && r.height > 0) bottom = Math.max(bottom, r.bottom + window.scrollY);
      });
    }
    return Math.ceil(bottom || document.documentElement.scrollHeight) + 8;
  }

  var reportTimer = null;
  function reportHeight() {
    clearTimeout(reportTimer);
    reportTimer = setTimeout(function () {
      try { parent.postMessage({ craftfeeHeight: measuredHeight() }, '*'); } catch (e) {}
    }, 120);
  }

  if (params) restore();
  syncUrl();
  inputs.forEach(function (el) {
    el.addEventListener('input', syncUrl);
    el.addEventListener('change', syncUrl);
  });
  toggles.forEach(function (el) { el.addEventListener('click', syncUrl); });
  addCopyButton();

  if (isEmbed) {
    window.addEventListener('load', reportHeight);
    document.addEventListener('input', reportHeight);
    document.addEventListener('change', reportHeight);
    document.addEventListener('click', reportHeight);
    window.addEventListener('resize', reportHeight);
    /* The host usually sets the frame width after load, so the first report is
       measured at the wrong width. Watch the wrapper itself, not <html>: its
       height follows the content, which would otherwise feed the frame's own
       height back in as a new measurement. */
    if (window.ResizeObserver) {
      try {
        var w0 = document.querySelector('main .wrap') || document.querySelector('.wrap');
        if (w0) new ResizeObserver(reportHeight).observe(w0);
      } catch (e) { /* older browser: the load and resize listeners still fire */ }
    }
    setTimeout(reportHeight, 200);
    setTimeout(reportHeight, 800);
  }
})();
