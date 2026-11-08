import { chromium } from 'playwright';
const browser = await chromium.launch();
const ctx = await browser.newContext({ userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36', viewport:{width:1440,height:1200} });
for (const [url,out] of JSON.parse(process.argv[2])) {
  const page = await ctx.newPage();
  try{
    const r = await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForTimeout(3500);
    console.log('##### '+url+' STATUS '+r.status()+' FINAL '+page.url());
    console.log(await page.evaluate(()=>document.body.innerText));
  }catch(e){ console.log('##### '+url+' ERROR '+e.message); }
  await page.close();
}
await browser.close();
