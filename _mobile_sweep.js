/* Site-wide narrow-screen sweep: one browser, every page, only real defects.
 *
 * _mobile_overflow.js measures a single page and prints everything. This walks
 * the whole site so a single bad page cannot hide among 22. Judgement rules are
 * the same as that tool: a table inside an overflow-x:auto/scrooll block is
 * reachable by finger, not clipped; only a box whose content is wider than it
 * and *cannot* be scrolled counts.
 *
 * Usage:
 *   MSYS_NO_PATHCONV=1 node _mobile_sweep.js <baseUrl> <publicDir> [width]
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const BASE = (process.argv[2] || 'http://127.0.0.1:8793').replace(/\/$/, '');
const ROOT = process.argv[3] || 'public';
const W = Number(process.argv[4] || 320);

function pages(dir, prefix = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory()) {
      if (e.name === 'assets' || e.name.startsWith('.')) continue;
      const rel = prefix + '/' + e.name;
      if (fs.existsSync(path.join(dir, e.name, 'index.html'))) out.push(rel + '/');
      out.push(...pages(path.join(dir, e.name), rel));
    }
  }
  return out;
}

(async () => {
  const list = pages(ROOT).sort();
  const b = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--no-proxy-server', '--ignore-certificate-errors'],
  });
  let bad = 0;
  for (const u of list) {
    const p = await b.newPage();
    await p.setViewport({ width: W, height: 900, isMobile: true, hasTouch: true });
    try {
      await p.goto(BASE + u, { waitUntil: 'load', timeout: 60000 });
      await new Promise(r => setTimeout(r, 500));
      const r = await p.evaluate(() => {
        const de = document.documentElement;
        const docOver = de.scrollWidth - de.clientWidth;
        const clipped = [];
        const push = (kind, el, sw, cw) => {
          const t = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
          clipped.push({ kind, sw, cw, t });
        };
        document.querySelectorAll('.doc table').forEach(t => {
          const ox = getComputedStyle(t).overflowX;
          const reachable = ox === 'auto' || ox === 'scroll';
          if (t.scrollWidth > t.clientWidth + 1 && !reachable) push('table', t, t.scrollWidth, t.clientWidth);
        });
        document.querySelectorAll('.doc figure, .doc img, .doc pre').forEach(f => {
          const ox = getComputedStyle(f.parentElement || f).overflowX;
          const reachable = ox === 'auto' || ox === 'scroll';
          if (f.scrollWidth > f.clientWidth + 1 && !reachable) push(f.tagName.toLowerCase(), f, f.scrollWidth, f.clientWidth);
        });
        // A box that sticks out of the viewport *and cannot be reached*.
        // Every td inside an overflow-x:auto table sticks out geometrically while
        // the reader can still swipe to it — that is not a defect, so any element
        // with a horizontally scrollable ancestor is skipped.
        const scrollableAncestor = el => {
          for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
            const cs = getComputedStyle(a);
            if ((cs.overflowX === 'auto' || cs.overflowX === 'scroll') && a.scrollWidth > a.clientWidth + 1) return true;
          }
          return false;
        };
        let widest = 0, widestEl = '';
        document.querySelectorAll('.doc *').forEach(el => {
          if (el.closest('.t-scroll, .embed-hide, [class*=scroll]')) return;
          const r = el.getBoundingClientRect();
          if (r.width > 0 && r.right > de.clientWidth + 1 && !scrollableAncestor(el)) {
            const over = r.right - de.clientWidth;
            if (over > widest) { widest = over; widestEl = el.tagName.toLowerCase() + '.' + (el.className || '').toString().split(' ')[0]; }
          }
        });
        return { docOver, clipped, widest, widestEl };
      });
      const issues = [];
      if (r.docOver > 1) issues.push(`doc +${r.docOver}px`);
      r.clipped.forEach(c => issues.push(`${c.kind} ${c.sw}>${c.cw} "${c.t}"`));
      if (r.widest > 4) issues.push(`${r.widestEl} 超出视口 ${r.widest}px`);
      if (issues.length) {
        bad++;
        console.log(`\n✗ ${u}`);
        issues.forEach(i => console.log('    ' + i));
      } else {
        console.log(`✓ ${u}`);
      }
    } catch (e) {
      bad++;
      console.log(`\n! ${u}  加载失败: ${e.message.slice(0, 80)}`);
    }
    await p.close();
  }
  await b.close();
  console.log(`\n${W}px：${list.length} 页，${bad} 页有问题`);
  process.exit(bad ? 1 : 0);
})();
