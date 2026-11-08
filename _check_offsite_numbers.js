/* Read the numbers the Offsite Ads tool actually prints for real inputs.
 * Used before quoting those numbers in outreach: the page's copy must match
 * what the tool computes, not what the formula suggests it computes.
 *
 * Usage: MSYS_NO_PATHCONV=1 node _check_offsite_numbers.js
 */
const puppeteer = require('puppeteer-core');
// argv[2] optional: override the base, e.g. http://127.0.0.1:8791/offsite-ads/
const BASE = process.argv[2] || 'https://craftfee.com/offsite-ads/';

const cases = [
  // label,                query
  ['15% / 55% margin',    'cur=USD&rev=24000&aov=38&m=55&share=30&p=30&ever=0'],
  ['12% / 55% margin',    'cur=USD&rev=24000&aov=38&m=55&share=30&p=30&ever=1'],
  ['15% / 30% margin',    'cur=USD&rev=24000&aov=38&m=30&share=30&p=30&ever=0'],
  ['15% / 12% margin',    'cur=USD&rev=24000&aov=38&m=12&share=30&p=30&ever=0'],
  ['15% / 20% margin',    'cur=USD&rev=24000&aov=38&m=20&share=30&p=30&ever=0'],
  ['12% / 20% margin',    'cur=USD&rev=24000&aov=38&m=20&share=30&p=30&ever=1'],
  ['12% / high ticket',   'cur=USD&rev=30000&aov=320&m=65&share=25&p=30&ever=1'],
];

(async () => {
  const local = BASE.includes('127.0.0.1');
  const b = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', local ? '--no-proxy-server' : '--proxy-server=http://127.0.0.1:7890',
           '--ignore-certificate-errors'],
  });
  for (const [label, q] of cases) {
    const p = await b.newPage();
    await p.setViewport({ width: 1200, height: 900 });
    try {
      await p.goto(BASE + '?' + q, { waitUntil: 'load', timeout: 60000 });
      await new Promise(r => setTimeout(r, 1200));
      const out = await p.evaluate(() => {
        const g = s => (document.getElementById(s) || {}).textContent || '';
        return { v2: g('v2'), v3: g('v3'), v4: g('v4'), v5: g('v5'), grade: g('grade'),
                 verdict: g('gradeTxt').replace(/\s+/g, ' ').slice(0, 150) };
      });
      console.log(`\n[${label}]`);
      console.log('  attributed/yr :', out.v2);
      console.log('  fee per order :', out.v3);
      console.log('  share of order:', out.v4);
      console.log('  must be new   :', out.v5, '  grade', out.grade);
      console.log('  verdict       :', out.verdict);
    } catch (e) {
      console.log(`\n[${label}] FAILED ${e.message}`);
    }
    await p.close();
  }
  await b.close();
})();
