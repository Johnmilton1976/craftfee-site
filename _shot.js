const puppeteer=require('puppeteer-core');
(async()=>{
 const b=await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox','--no-proxy-server']});
 const p=await b.newPage(); await p.setViewport({width:1100,height:900,deviceScaleFactor:1});
 await p.goto(process.argv[2],{waitUntil:'load',timeout:60000});
 await new Promise(r=>setTimeout(r,900));
 const h=await p.evaluate(()=>{const el=[...document.querySelectorAll('h2')].find(x=>x.textContent.includes('narrower question'));return el?el.getBoundingClientRect().top+scrollY:0;});
 await p.evaluate(y=>window.scrollTo(0,y-40),h);
 await new Promise(r=>setTimeout(r,400));
 await p.screenshot({path:process.argv[3]});
 await b.close();
})();
