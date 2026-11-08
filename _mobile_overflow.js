/* Narrow-screen overflow check for a page, per element rather than per document.
 * A page can report scrollWidth == clientWidth while a table is silently cut
 * inside an overflow-x:auto block, so tables and figures are measured on their
 * own. Usage:
 *   MSYS_NO_PATHCONV=1 node _mobile_overflow.js <url> [widths...]
 */
const puppeteer = require('puppeteer-core');
const URL_ = process.argv[2];
const widths = process.argv.slice(3).map(Number);
const cols = widths.length ? widths : [360, 378, 390];

(async () => {
  const b = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--no-proxy-server', '--ignore-certificate-errors'],
  });
  let bad = 0;
  for (const w of cols) {
    const p = await b.newPage();
    await p.setViewport({ width: w, height: 900, isMobile: true, hasTouch: true });
    await p.goto(URL_, { waitUntil: 'load', timeout: 60000 });
    await new Promise(r => setTimeout(r, 800));
    const r = await p.evaluate(() => {
      const de = document.documentElement;
      const out = { doc: [de.scrollWidth, de.clientWidth], tables: [], figs: [] };
      document.querySelectorAll('.doc table').forEach((t, i) => {
        const ox = getComputedStyle(t).overflowX;
        out.tables.push({ i, sw: t.scrollWidth, cw: t.clientWidth,
                          ox, reachable: ox === 'auto' || ox === 'scroll' });
      });
      document.querySelectorAll('.doc figure, .doc img').forEach((f, i) => {
        out.figs.push([i, f.scrollWidth, f.clientWidth]);
      });
      return out;
    });
    const docOver = r.doc[0] > r.doc[1] + 1;
    // 站点 CSS 在窄屏把表格做成 overflow-x:auto 的滚动块 —— 内容滑得到，不算裁。
    const tOver = r.tables.filter(t => t.sw > t.cw + 1 && !t.reachable);
    const tScroll = r.tables.filter(t => t.sw > t.cw + 1 && t.reachable);
    const fOver = r.figs.filter(t => t[1] > t[2] + 1);
    console.log(`\n[${w}px] document ${r.doc[0]}/${r.doc[1]} ${docOver ? '<== 溢出' : 'ok'}`);
    console.log(`  tables ${r.tables.length} 张：横向可滚 ${tScroll.length} 张（设计如此），内容被藏死 ${tOver.length} 张`);
    tOver.forEach(t => console.log(`    #${t.i} scroll ${t.sw} > client ${t.cw}  overflowX=${t.ox}`));
    if (fOver.length) fOver.forEach(f => console.log(`    figure #${f[0]} scroll ${f[1]} > client ${f[2]}`));
    if (docOver || tOver.length || fOver.length) bad++;
    await p.close();
  }
  await b.close();
  console.log(bad ? `\n失败 ${bad} 档` : '\n全部通过');
  process.exit(bad ? 1 : 0);
})();
