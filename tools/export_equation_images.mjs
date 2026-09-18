/**
 * Export the article's actual MathJax displays; no second typesetting source.
 * Supply a Playwright chromium instance to exportEquationImages().
 * With playwright installed, CLI: node tools/export_equation_images.mjs
 */
const { mkdir } = await import('node:fs/promises');
const { resolve } = await import('node:path');
const { pathToFileURL } = await import('node:url');

export async function exportEquationImages(chromium, {
  url = 'https://datarichinsightpoor.github.io/organoid-hook-model/article.html',
  output = resolve('publication/equations'),
} = {}) {
  const browser = await chromium.launch({headless:true});
  try {
    const context = await browser.newContext({
      viewport:{width:1440,height:1000}, deviceScaleFactor:3,
    });
    const page = await context.newPage();
    await page.goto(url, {waitUntil:'networkidle'});
    await page.evaluate(()=>MathJax.startup.promise);
    const displays = page.locator('mjx-container[display=true]');
    if (await displays.count() !== 5 || await page.locator('mjx-merror').count()) {
      throw new Error('The five expected equations did not render correctly.');
    }
    const names = ['01-assembly','02-high-dose-limit','05-secondary-excess','03-payload-balance','04-fluorescence-history'];
    for (const theme of ['light','dark']) {
      await mkdir(resolve(output,theme), {recursive:true});
      await page.evaluate(theme=>{
        document.documentElement.dataset.theme=theme;
        const ink=theme==='light'?'#171717':'#f1f1ef';
        const paper=theme==='light'?'#ffffff':'#10141c';
        for(const el of document.querySelectorAll('mjx-container[display=true]')){
          Object.assign(el.style,{
            display:'block',width:'max-content',maxWidth:'none',margin:'0',
            padding:'24px 32px',overflow:'visible',color:ink,background:paper,
          });
        }
      },theme);
      for (let i=0;i<names.length;i++){
        await displays.nth(i).screenshot({path:resolve(output,theme,`${names[i]}.png`)});
      }
    }
    return {equations:5,variants:2,output};
  } finally {
    await browser.close();
  }
}
if(typeof process !== 'undefined' && process.argv[1] && import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
  const {chromium}=await import('playwright');
  console.log(await exportEquationImages(chromium));
}
