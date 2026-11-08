/* Measure the Offsite Ads page in both modes, at real widths, against a real
 * static server. A file:// run reports overflow that is only missing styles.
 *
 * Usage: MSYS_NO_PATHCONV=1 node _probe_offsite.js
 */
const puppeteer = require('puppeteer-core');
const BASE = 'http://127.0.0.1:8796/offsite-ads/index.html';
const WIDTHS = [320, 360, 390, 414, 720, 1100];

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';

(async () => {
  const b = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--no-proxy-server'],
  });
  const p = await b.newPage();
  p.on('pageerror', e => console.log('PAGEERROR:', e.message));
  p.on('console', m => { if (m.type() === 'error') console.log('CONSOLE ERROR:', m.text().slice(0, 200)); });

  console.log('== full page: horizontal overflow ==');
  console.log('width  scrollW  clientW  over  widest element');
  for (const w of WIDTHS) {
    await p.setViewport({ width: w, height: 1000 });
    await p.goto(BASE, { waitUntil: 'load' });
    const r = await p.evaluate(() => {
      const de = document.documentElement;
      let worst = '', max = 0;
      document.querySelectorAll('body *').forEach(el => {
        const q = el.getBoundingClientRect();
        if (q.right > max) { max = q.right; worst = el.tagName + (el.id ? '#' + el.id : '') + '.' + (el.className || ''); }
      });
      return { sw: de.scrollWidth, cw: de.clientWidth, worst, right: Math.round(max) };
    });
    console.log(String(w).padEnd(6) + String(r.sw).padEnd(9) + String(r.cw).padEnd(9)
      + String(r.sw - r.cw).padEnd(6) + r.worst.slice(0, 46) + ' right=' + r.right);
  }

  console.log('\n== calculator still works (real input events) ==');
  await p.setViewport({ width: 1100, height: 1000 });
  await p.goto(BASE, { waitUntil: 'load' });
  const before = await p.$eval('#oa-out, #res, main', el => el.textContent.replace(/\s+/g, ' ').trim().slice(0, 160));
  await p.evaluate(() => {
    const set = (id, v) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    };
    set('rev', '9000'); set('aov', '38'); set('m', '55'); set('share', '20');
  });
  await new Promise(r => setTimeout(r, 200));
  const after = await p.$eval('main', el => el.textContent.replace(/\s+/g, ' ').trim());
  const money = after.match(/(?:US\$|C\$|£|€|A\$)\s?[\d,]+(?:\.\d+)?/g) || [];
  console.log('numbers on page after 9000/38/55%/20%:', money.slice(0, 8).join(' | '));
  console.log('url now:', await p.url());

  console.log('\n== embed mode: height + overflow + what stays visible ==');
  for (const w of WIDTHS) {
    await p.setViewport({ width: w, height: 1000 });
    await p.goto(BASE + '?embed=1', { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 400));
    const r = await p.evaluate(() => {
      const de = document.documentElement;
      const main = document.querySelector('main');
      let bottom = 0;
      const visible = [];
      main.querySelectorAll('*').forEach(el => {
        const s = getComputedStyle(el);
        if (s.display === 'none' || s.visibility === 'hidden') return;
        const q = el.getBoundingClientRect();
        if (q.width > 0 && q.height > 0) {
          if (q.bottom > bottom) bottom = q.bottom;
          if (el === el.parentElement.firstElementChild && el.textContent.trim() && el.children.length === 0) visible.push(el.tagName);
        }
      });
      const credit = document.querySelector('.embed-credit');
      const creditVis = credit ? getComputedStyle(credit).display !== 'none' : false;
      const creditLink = credit ? credit.querySelector('a') : null;
      const linkVis = creditLink ? creditLink.getBoundingClientRect().width > 0 : false;
      return {
        need: Math.ceil(bottom + 8), sw: de.scrollWidth, cw: de.clientWidth,
        embedClass: de.className.includes('embed'),
        docHidden: getComputedStyle(document.querySelector('.doc')).display === 'none',
        sourcesHidden: getComputedStyle(document.querySelector('.callout.embed-hide')).display === 'none',
        ctaHidden: getComputedStyle(document.querySelector('.embed-cta')).display === 'none',
        relatedHidden: getComputedStyle(document.querySelector('.related')).display === 'none',
        h1: (document.querySelector('h1') || {}).textContent,
        toolVisible: document.getElementById('oa-tool').getBoundingClientRect().height > 100,
        creditVis, linkVis, creditHref: creditLink ? creditLink.href : null,
      };
    });
    console.log(`w=${String(w).padEnd(5)} need=${String(r.need).padEnd(5)} overflow=${r.sw > r.cw + 1 ? 'YES ' + (r.sw - r.cw) : 'no'}`
      + ` embed=${r.embedClass} docHidden=${r.docHidden} sourcesHidden=${r.sourcesHidden} ctaHidden=${r.ctaHidden}`
      + ` relatedHidden=${r.relatedHidden} tool=${r.toolVisible} credit=${r.creditVis}/${r.linkVis}`);
    if (w === 320 || w === 720) console.log('   h1:', r.h1, '| credit ->', r.creditHref);
  }

  await b.close();
})();
