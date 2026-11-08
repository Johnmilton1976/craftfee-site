/* 静态宿主模拟：宿主只贴 <iframe height=声明值>，不装 postMessage 监听。
 * 这是最坏也最常见的场景（很多人只复制 iframe 那一行），
 * 用来回答一个问题：声明高度够不够，会不会裁掉内容。
 *
 * Usage: MSYS_NO_PATHCONV=1 NODE_PATH=../pet-care-site/node_modules \
 *        node _static_host_check.js <base> <path> <declaredHeight> [width...]
 */
const puppeteer = require('puppeteer-core');
const http = require('http');
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE = process.argv[2];
const P = process.argv[3];
const D = parseInt(process.argv[4], 10);
const cols = process.argv.slice(5).map(Number);

const host = () => `<!doctype html><meta charset="utf-8">
<style>body{margin:0;font-family:sans-serif}iframe{border:0;width:100%;display:block}</style>
<iframe id="f" src="${BASE}${P}?embed=1" width="100%" height="${D}" title="widget"></iframe>`;

(async () => {
  const b = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--no-sandbox', '--proxy-server=http://127.0.0.1:7890', '--ignore-certificate-errors'],
  });
  let ok = 0, bad = 0;
  for (const w of cols) {
    const srv = http.createServer((q, r) => { r.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }); r.end(host()); });
    await new Promise((res) => srv.listen(0, '127.0.0.1', res));
    const p = await b.newPage();
    await p.setViewport({ width: w, height: 1000 });
    await p.goto('http://127.0.0.1:' + srv.address().port + '/', { waitUntil: 'load', timeout: 60000 });
    await new Promise((r) => setTimeout(r, 2000));
    const fr = p.frames().find((f) => f.url().includes('embed=1'));
    if (!fr) { console.log(`${w} FRAME FAILED`); bad++; await p.close(); srv.close(); continue; }
    const inner = await fr.evaluate(() => {
      const de = document.documentElement;
      let bottom = 0;
      document.querySelectorAll('main *').forEach((el) => {
        const s = getComputedStyle(el);
        if (s.display === 'none' || s.visibility === 'hidden') return;
        const q = el.getBoundingClientRect();
        if (q.width > 0 && q.height > 0) bottom = Math.max(bottom, q.bottom + window.scrollY);
      });
      return { docH: de.scrollHeight, contentBottom: Math.ceil(bottom), sw: de.scrollWidth, cw: de.clientWidth };
    });
    const clipped = Math.max(0, inner.contentBottom - D);
    const over = inner.sw > inner.cw + 1;
    const verdict = clipped > 0 ? 'CLIPPED' : 'FITS';
    console.log(`w=${String(w).padEnd(4)} declared=${String(D).padEnd(5)} contentBottom=${String(inner.contentBottom).padEnd(5)} clipped=${String(clipped).padEnd(4)} overflow=${over} ${verdict}`);
    clipped > 0 ? bad++ : ok++;
    await p.close(); srv.close();
  }
  console.log(`\n${ok} fit, ${bad} clipped`);
  await b.close();
})();
