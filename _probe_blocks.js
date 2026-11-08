/* Where the embedded height actually goes.
 *
 * 2840px at a 320px column is tall enough that a host site has to think twice,
 * and a 2840px frame on a narrow blog column is mostly the frame, not the tool.
 * This lists every visible block inside main with its own height, so the
 * decision of what to keep in embed mode is made on numbers.
 *
 * Usage: MSYS_NO_PATHCONV=1 node _probe_blocks.js
 */
const puppeteer = require('puppeteer-core');
const BASE = 'http://127.0.0.1:8796/offsite-ads/index.html';
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';

(async () => {
  const b = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--no-sandbox', '--no-proxy-server'],
  });
  const p = await b.newPage();

  for (const mode of ['normal', 'embed']) {
    for (const w of [320, 720]) {
      await p.setViewport({ width: w, height: 1200 });
      await p.goto(BASE + (mode === 'embed' ? '?embed=1' : ''), { waitUntil: 'load' });
      await new Promise(r => setTimeout(r, 400));
      const r = await p.evaluate(() => {
        const main = document.querySelector('main');
        const out = [];
        [...main.children].forEach(el => {
          const st = getComputedStyle(el);
          if (st.display === 'none') { out.push({ tag: el.tagName, cls: cl(el), hidden: true }); return; }
          const q = el.getBoundingClientRect();
          out.push({
            tag: el.tagName, cls: cl(el),
            top: Math.round(q.top + scrollY), h: Math.round(q.height),
            mt: Math.round(parseFloat(st.marginTop) || 0), mb: Math.round(parseFloat(st.marginBottom) || 0),
          });
        });
        // and, inside the tool, each of the three cards
        const tool = document.getElementById('oa-tool');
        const inner = [];
        if (tool) [...tool.querySelectorAll('.calc-card, .card')].forEach(c => {
          const q = c.getBoundingClientRect();
          inner.push({ cls: cl(c), h: Math.round(q.height) });
        });
        function cl(e) { return (typeof e.className === 'string' ? e.className : '').split(' ').filter(Boolean).join('.') || '(none)'; }
        const de = document.documentElement;
        return { blocks: out, inner, sw: de.scrollWidth, cw: de.clientWidth };
      });
      console.log(`\n=== ${mode} @ ${w}px  (scrollW ${r.sw} / clientW ${r.cw}) ===`);
      r.blocks.forEach(x => {
        if (x.hidden) return console.log(`  ${x.tag}.${x.cls}  HIDDEN`);
        console.log(`  ${(x.tag + '.' + x.cls).padEnd(46)} top=${String(x.top).padEnd(5)} h=${String(x.h).padEnd(5)} m=${x.mt}/${x.mb}`);
      });
      if (mode === 'embed' && r.inner.length) {
        console.log('  -- inside the tool --');
        r.inner.forEach(x => console.log(`     .${x.cls.padEnd(24)} h=${x.h}`));
      }
    }
  }
  await b.close();
})();
