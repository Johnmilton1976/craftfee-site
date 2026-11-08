/* Host-side check for the Offsite Ads embed: a real page, a real iframe, the
 * real snippet copied out of the page. This is the only test that catches what
 * a host actually gets — measuring the page on its own says nothing about
 * whether the frame clips its own last line, or whether ?embed=1 ever fires
 * inside a frame.
 *
 * Usage: MSYS_NO_PATHCONV=1 node _host_check_offsite.js [baseUrl] [declaredHeight]
 */
const puppeteer = require('puppeteer-core');
const http = require('http');

const BASE = process.argv[2] || 'http://127.0.0.1:8796';
const DECLARED = parseInt(process.argv[3] || '2840', 10);
const WIDTHS = [320, 388, 720, 1100];

const HOST = `<!doctype html><meta charset="utf-8">
<title>host</title>
<style>body{margin:0;font-family:sans-serif}iframe{border:0;width:100%;display:block}</style>
<h1 style="font:600 18px sans-serif;padding:12px">A host site's article</h1>
<iframe id="cf-oa" src="${BASE}/offsite-ads/?embed=1" width="100%" height="${DECLARED}"
        style="border:1px solid #24282E;border-radius:14px" title="Etsy Offsite Ads cost calculator"></iframe>
<script>addEventListener("message",function(e){if(e.data&&e.data.craftfeeHeight){var f=document.getElementById("cf-oa");if(f)f.height=e.data.craftfeeHeight+2}});</script>
<footer style="padding:12px">Footer of the host page</footer>`;

(async () => {
  const b = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--no-proxy-server'],
  });

  let pass = 0, fail = 0;
  for (const w of WIDTHS) {
    const srv = http.createServer((q, r) => {
      r.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      r.end(HOST);
    });
    await new Promise(res => srv.listen(0, '127.0.0.1', res));
    const port = srv.address().port;

    const p = await b.newPage();
    await p.setViewport({ width: w, height: 1400 });
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    await p.goto('http://127.0.0.1:' + port + '/', { waitUntil: 'load', timeout: 30000 });
    await new Promise(r => setTimeout(r, 1600));

    const frame = p.frames().find(f => f.url().includes('offsite-ads'));
    let out = { w, loaded: !!frame && !frame.url().startsWith('chrome-error'), url: frame ? frame.url() : null };

    if (!out.loaded) {
      console.log(`w=${w} FRAME FAILED url=${out.url}`);
      fail++;
    } else {
      try {
        out.inner = await frame.evaluate(() => {
          const de = document.documentElement;
          const main = document.querySelector('main');
          let bottom = 0, last = '';
          main.querySelectorAll('*').forEach(el => {
            const s = getComputedStyle(el);
            if (s.display === 'none' || s.visibility === 'hidden') return;
            const q = el.getBoundingClientRect();
            if (q.width > 0 && q.height > 0 && q.bottom > bottom) {
              bottom = q.bottom;
              last = el.tagName + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '');
            }
          });
          const credit = document.querySelector('.embed-credit a');
          const cr = credit ? credit.getBoundingClientRect() : null;
          return {
            need: Math.ceil(bottom + 8), lastEl: last,
            sw: de.scrollWidth, cw: de.clientWidth,
            embed: de.className.includes('embed'),
            docHidden: getComputedStyle(document.querySelector('.doc')).display === 'none',
            toolH: Math.round(document.getElementById('oa-tool').getBoundingClientRect().height),
            creditVisible: !!(cr && cr.width > 0 && cr.height > 0),
            creditText: credit ? credit.closest('p').textContent.trim().slice(0, 40) : null,
            // a frame that is shorter than its content still reports the content
            // height here, which is exactly how a clip is detected
            contentBottom: Math.ceil(bottom),
          };
        });
        out.frameH = await p.$eval('iframe', f => f.height);
        out.clipped = out.frameH < out.inner.contentBottom;
        out.overflow = out.inner.sw > out.inner.cw + 1;

        const ok = !out.clipped && !out.overflow && out.inner.creditVisible && out.inner.embed && out.inner.docHidden;
        console.log(`w=${String(w).padEnd(5)} frameH=${String(out.frameH).padEnd(5)} need=${String(out.inner.need).padEnd(5)}`
          + ` contentBottom=${String(out.inner.contentBottom).padEnd(5)} clipped=${out.clipped} overflow=${out.overflow}`
          + ` embed=${out.inner.embed} docHidden=${out.inner.docHidden} credit=${out.inner.creditVisible} toolH=${out.inner.toolH}`
          + ` last=${out.inner.lastEl} ${ok ? 'OK' : 'FAIL'}`);
        if (out.inner.creditText) console.log(`        credit: "${out.inner.creditText}..."`);
        if (errs.length) console.log('        pageerrors:', errs.join(' | ').slice(0, 160));
        ok ? pass++ : fail++;
      } catch (e) {
        console.log(`w=${w} EVAL FAILED ${e.message}`);
        fail++;
      }
    }
    await p.close();
    srv.close();
  }
  console.log(`\n${pass} passed, ${fail} failed`);
  await b.close();
})();
