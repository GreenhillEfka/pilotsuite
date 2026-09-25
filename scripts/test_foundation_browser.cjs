// Actual disposable application. No access to the household or write-capable API.
const {chromium}=require(process.env.PILOTSUITE_PLAYWRIGHT || 'playwright');
const {spawn}=require('node:child_process');
const {createInterface}=require('node:readline');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');

(async()=>{
  const root=path.resolve(__dirname,'..');
  const fixture=spawn(process.env.PYTHON || 'python',['scripts/daily_brief_browser_fixture.py'],{
    cwd:root,env:{...process.env,PYTHONPATH:path.join(root,'pilotsuite')},stdio:['pipe','pipe','pipe']});
  let stderr='';fixture.stderr.on('data',d=>{stderr=(stderr+d).slice(-12000);});
  const lines=createInterface({input:fixture.stdout})[Symbol.asyncIterator]();
  let browser;
  async function read(){
    let timer;
    try{
      const item=await Promise.race([lines.next(),new Promise((_,reject)=>{
        timer=setTimeout(()=>reject(new Error('fixture timed out: '+stderr)),15000);})]);
      if(item.done)throw new Error('fixture stopped: '+stderr);
      return JSON.parse(item.value);
    }finally{clearTimeout(timer);}
  }
  async function command(data){fixture.stdin.write(JSON.stringify(data)+'\n');return read();}
  try{
    const info=await read();
    browser=await chromium.launch({headless:true,
      ...(process.env.PILOTSUITE_CHROMIUM?{executablePath:process.env.PILOTSUITE_CHROMIUM}:{})});
    const page=await browser.newPage({viewport:{width:390,height:844}});
    page.setDefaultTimeout(10000);
    const errors=[],writes=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('request',r=>{if(!['GET','HEAD'].includes(r.method()))writes.push(r.url());});
    await page.goto(info.url);
    await page.waitForFunction(()=>contextData?.foundation && !selectionBusy);
    const journey=page.locator('#foundation-journey');
    assert.equal(await journey.locator('article').count(),5);
    assert.match(await journey.innerText(),/Quellen & Rollen/);
    assert.match(await journey.innerText(),/Gesperrt/);
    assert.doesNotMatch(await journey.innerText(),/ready|unverified|locked/);
    const before=await command({action:'snapshot'});
    assert.deepEqual([before.related_reads,before.config_reads,before.snapshot_reads],[0,0,0]);
    console.log('ok 1 - actual-app foundation is German, planning-only and read-only');

    await page.route('**/api/v1/zones/a/context',route=>route.fulfill({status:503,json:{message:'synthetic'}}),{times:1});
    await page.evaluate(async()=>{try{await loadContext();}catch{}renderLearning();});
    assert.equal(await journey.locator('article').count(),0);
    assert.match(await journey.innerText(),/nicht bestätigt/);
    await page.evaluate(async()=>{await loadContext();});
    assert.equal(await journey.locator('article').count(),5);
    console.log('ok 2 - failed reads cannot revive the old foundation through rerender');

    await page.evaluate(()=>{selectionDraft.set('light.synthetic','ignored');selectionChanged();});
    assert.equal(await journey.locator('article').count(),0);
    assert.equal(await page.evaluate(()=>selectionDraft.dirty),true);
    assert.deepEqual(before,await command({action:'snapshot'}));
    await page.evaluate(async()=>{selectionDraft.set('light.synthetic','relevant');await loadSelection(selectionZone);});
    console.log('ok 3 - unsaved source decisions invalidate preparation without saving');

    await page.evaluate(async()=>{await loadSelection('b');});
    assert.equal(await page.evaluate(()=>contextData.foundation.zone_id),'b');
    assert.equal(await journey.locator('article').count(),5);
    await page.evaluate(async()=>{await loadSelection('a');});
    assert.equal(await page.evaluate(()=>contextData.foundation.zone_id),'a');
    console.log('ok 4 - actual zone changes do not carry foundation identity across zones');

    for(const width of [390,1440]){
      await page.setViewportSize({width,height:1000});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      if(process.env.PILOTSUITE_SCREENSHOTS){
        await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS,{recursive:true});
        await journey.locator('..').screenshot({path:path.join(process.env.PILOTSUITE_SCREENSHOTS,`foundation-${width}.png`)});
      }
    }
    assert.deepEqual(errors,[]);assert.deepEqual(writes,[]);
    assert.deepEqual(before,await command({action:'snapshot'}));
    console.log('ok 5 - mobile/desktop layout and stores remain unchanged');
  }finally{
    if(browser)await browser.close();
    fixture.stdin.end();fixture.kill('SIGTERM');
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
