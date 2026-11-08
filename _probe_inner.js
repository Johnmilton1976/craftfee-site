const puppeteer=require('puppeteer-core');
const B='http://127.0.0.1:8796/offsite-ads/index.html';
(async()=>{
const b=await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox','--no-proxy-server']});
const p=await b.newPage(); await p.setViewport({width:320,height:1400});
await p.goto(B+'?embed=1',{waitUntil:'load'});
await new Promise(r=>setTimeout(r,500));
console.log(await p.evaluate(()=>{
  const out=[];
  const cards=[...document.querySelectorAll('#oa-tool .card')];
  cards.forEach((c,ci)=>{
    out.push(`CARD ${ci+1} h=${Math.round(c.getBoundingClientRect().height)} pad=${getComputedStyle(c).padding}`);
    [...c.children].forEach(el=>{
      const st=getComputedStyle(el);
      if(st.display==='none') return out.push(`   ${el.tagName}.${(el.className||'').toString().split(' ')[0]} HIDDEN`);
      const q=el.getBoundingClientRect();
      out.push(`   ${el.tagName}.${(el.className||'').toString().split(' ').join('.').slice(0,26).padEnd(26)} h=${String(Math.round(q.height)).padEnd(5)} mt=${Math.round(parseFloat(st.marginTop)||0)} mb=${Math.round(parseFloat(st.marginBottom)||0)}`);
    });
  });
  const h1=document.querySelector('main h1'), lede=document.querySelector('main .lede'), eb=document.querySelector('main .eyebrow'), cr=document.querySelector('main .crumbs');
  out.push('HEAD: crumbs='+Math.round(cr.getBoundingClientRect().height)+' eyebrow='+Math.round(eb.getBoundingClientRect().height)+' h1='+Math.round(h1.getBoundingClientRect().height)+' lede='+Math.round(lede.getBoundingClientRect().height));
  const docWrap=[...document.querySelectorAll('main > .wrap.narrow')];
  out.push('docWrap h='+docWrap.map(w=>Math.round(w.getBoundingClientRect().height)).join(',')+' | doc display='+getComputedStyle(document.querySelector('.doc')).display);
  return out.join('\n');
}));
await b.close();
})();
