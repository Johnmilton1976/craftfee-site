/* Embeddable mode for the Offsite Ads decision tool (?embed=1).
 *
 * The other three calculators reuse assets/embed-share.js, which measures
 * "document.querySelector('main .wrap')" - the *first* wrapper on the page.
 * That is correct there, because the tool is the first thing inside main.
 * On /offsite-ads/ it is not: main holds three wrappers (heading, tool,
 * article) and the tool is the second one, so the shared measurement would
 * report the height of the heading block and clip the entire calculator.
 *
 * So this page measures differently: every visible box inside main, take the
 * lowest bottom edge. Hidden nodes report a 0x0 rect and drop out on their
 * own, which is what makes html.embed .doc (display:none) harmless here.
 *
 * scrollHeight is still not used, for the reason written up in embed-share.js:
 * once a frame is taller than its content it reports the frame's own height,
 * so the number can only ever grow and never come back down.
 */
(function () {
  if (location.search.indexOf('embed=1') === -1) return;

  document.documentElement.className += ' embed';

  function measuredHeight() {
    var main = document.querySelector('main');
    if (!main) return document.documentElement.scrollHeight;
    var bottom = 0;
    [].slice.call(main.querySelectorAll('*')).forEach(function (el) {
      var s = getComputedStyle(el);
      if (s.display === 'none' || s.visibility === 'hidden') return;
      var r = el.getBoundingClientRect();
      if (r.width > 0 && r.height > 0 && r.bottom > bottom) bottom = r.bottom;
    });
    return Math.ceil(bottom + window.scrollY) + 8;
  }

  var timer = null;
  function report() {
    clearTimeout(timer);
    timer = setTimeout(function () {
      try { parent.postMessage({ craftfeeHeight: measuredHeight() }, '*'); } catch (e) {}
    }, 120);
  }

  window.addEventListener('load', report);
  window.addEventListener('resize', report);
  document.addEventListener('input', report);
  document.addEventListener('change', report);
  document.addEventListener('click', report);

  /* The host normally sets the frame width after load, so the first report is
     taken at the wrong width. Observe the tool wrapper itself; observing <html>
     would feed the frame's own height back in as a new measurement. */
  if (window.ResizeObserver) {
    var w = document.getElementById('oa-tool');
    if (w) { try { new ResizeObserver(report).observe(w); } catch (e) {} }
  }

  report();
  setTimeout(report, 200);
  setTimeout(report, 800);
})();
