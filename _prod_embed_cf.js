/* Production embed check for craftfee.com, through the local proxy.
 * The localhost harness runs Chrome with --no-proxy-server and cannot reach
 * production from this machine, so it fails on a null contentDocument - on
 * pages that are fine. This one goes through 127.0.0.1:7890.
 *
 * Usage: MSYS_NO_PATHCONV=1 node _prod_embed_cf.js <path> <declaredHeight> [width...]
 */
const puppeteer=require('puppeteer-core');const http=require('http');
const BASE='https://craftfee.com', P=process.argv[2]||'/offsite-ads/', D=parseInt(process.argv[3]||'3050',10);
const cols=process.argv.slice(4).map(Number);
const host=()=>`<!doctype html><meta charset="utf-8"><style>body{margin:0}iframe{border:0;width:100%;display:block}</style>
<iframe id="cf-oa" src="${BASE}${P}?embed=1" width="100%" height="${D}" style="border:1px solid #24282E;border-radius:14px" title="Etsy Offsite Ads cost calculator"></iframe>
<script>addEventListener("message",function(e){if(e.data&&e.data.craftfeeHeight){var f=document.getElementById("cf-oa");if(f)f.height=e.data.craftfeeHeight+2}});</script>`;
(async()=>{
const b=await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',
  args:['--no-sandbox','--proxy-server=http://127.0.0.1:7890','--ignore-certificate-errors']});
let pass=0,fail=0;
for(const w of cols){
  const srv=http.createServer((q,r)=>{r.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});r.end(host())});
  await new Promise(res=>srv.listen(0,'127.0.0.1',res));
  const port=srv.address().port;
  const p=await b.newPage(); await p.setViewport({width:w,height:1000});
  try{ await p.goto('http://127.0.0.1:'+port+'/',{waitUntil:'load',timeout:60000}); }catch(e){ console.log(w,'host nav fail',e.message); }
  await new Promise(r=>setTimeout(r,2000));
  const frame=p.frames().find(f=>f.url().includes('craftfee.com'));
  const out={w,loaded:!!frame&&!frame.url().startsWith('chrome-error'),url:frame?frame.url().slice(0,70):null};
  if(!out.loaded){ console.log(`${w} FRAME FAILED ${out.url}`); fail++; await p.close(); srv.close(); continue; }
  try{
    out.inner=await frame.evaluate(()=>{
      const de=document.documentElement, main=document.querySelector('main');
      let bottom=0,last='';
      main.querySelectorAll('*').forEach(el=>{
        const s=getComputedStyle(el);
        if(s.display==='none'||s.visibility==='hidden')return;
        const q=el.getBoundingClientRect();
        if(q.width>0&&q.height>0&&q.bottom>bottom){bottom=q.bottom;last=el.tagName+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ')[0]:'');}
      });
      const credit=document.querySelector('.embed-credit a');
      const cr=credit?credit.getBoundingClientRect():null;
      // 工具根节点各页 id 不同（#oa-tool / #calc / .calc），别写死：写死会让
      // 非 offsite 页在这里取到 null 直接抛错，看起来像「站坏了」。
      const toolEl=document.querySelector('#oa-tool, #calc, #calculator, .calc, form.calc');
      const docEl=document.querySelector('.doc');
      return {need:Math.ceil(bottom+8),contentBottom:Math.ceil(bottom),lastEl:last,
              sw:de.scrollWidth,cw:de.clientWidth,embed:de.className.includes('embed'),
              docHidden:docEl?getComputedStyle(docEl).display==='none':null,
              toolH:toolEl?Math.round(toolEl.getBoundingClientRect().height):null,
              creditVisible:!!(cr&&cr.width>0&&cr.height>0)};
    });
    out.frameH=await p.$eval('iframe',f=>f.height);
    const clipped=out.frameH<out.inner.contentBottom, over=out.inner.sw>out.inner.cw+1;
    const ok=!clipped&&!over&&out.inner.creditVisible&&out.inner.embed&&out.inner.docHidden;
    console.log(`w=${String(w).padEnd(5)} frameH=${String(out.frameH).padEnd(5)} need=${String(out.inner.need).padEnd(5)}`
      +` contentBottom=${String(out.inner.contentBottom).padEnd(5)} clipped=${clipped} overflow=${over}`
      +` embed=${out.inner.embed} docHidden=${out.inner.docHidden} credit=${out.inner.creditVisible} toolH=${out.inner.toolH} last=${out.inner.lastEl} ${ok?'OK':'FAIL'}`);
    ok?pass++:fail++;
  }catch(e){ console.log(w,'EVAL FAILED',e.message); fail++; }
  await p.close(); srv.close();
}
console.log(`\n${pass} passed, ${fail} failed`);
await b.close();
})();
