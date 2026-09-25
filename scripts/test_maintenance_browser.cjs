// Actual application, disposable data, synthetic HA reads. Never household control.
const {chromium}=require(process.env.PILOTSUITE_PLAYWRIGHT || 'playwright');
const {spawn}=require('node:child_process');
const {createInterface}=require('node:readline');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
async function fixture(broken=false){
  const proc=spawn(process.env.PYTHON || 'python',['scripts/maintenance_browser_fixture.py',...(broken?['--broken']:[])],{
    cwd:root,env:{...process.env,PYTHONPATH:path.join(root,'pilotsuite')},stdio:['pipe','pipe','pipe']});
  let stderr='';proc.stderr.on('data',d=>{stderr=(stderr+d).slice(-8000);});
  const lines=createInterface({input:proc.stdout})[Symbol.asyncIterator]();
  async function read(){let timer;try{const row=await Promise.race([lines.next(),new Promise((_,reject)=>{
    timer=setTimeout(()=>reject(new Error('Fixture timeout '+stderr)),15000);})]);
    if(row.done)throw new Error('Fixture stopped '+stderr);return JSON.parse(row.value);
  }finally{clearTimeout(timer);}}
  return {info:await read(),command:async data=>{proc.stdin.write(JSON.stringify(data)+'\n');return read();},
    close:()=>{proc.stdin.end();proc.kill('SIGTERM');}};
}
(async()=>{
  let f,browser;
  try{
    f=await fixture();browser=await chromium.launch({headless:true,
      ...(process.env.PILOTSUITE_CHROMIUM?{executablePath:process.env.PILOTSUITE_CHROMIUM}:{})});
    const page=await browser.newPage({viewport:{width:390,height:844}});page.setDefaultTimeout(10000);
    const errors=[];page.on('pageerror',error=>errors.push(error.message));
    await page.goto(f.info.url);await page.waitForFunction(()=>!selectionBusy && contextData);
    assert.ok((await page.locator('#recent-versions').innerText()).includes(f.info.version));
    assert.equal(await page.locator('#release-install').getAttribute('href'),'/hassio/addon/0d79c5e8_pilotsuite/info');
    // A maintenance navigation must not discard an active role draft.
    await page.evaluate(()=>{contextEditing=true;});
    await page.locator('a[href="maintenance"]:visible').first().click();
    assert.equal(page.url(),f.info.url);
    await page.evaluate(()=>{contextEditing=false;});
    await page.locator('a[href="maintenance"]:visible').first().click();
    await page.waitForFunction(()=>!document.getElementById('savepoint-create').disabled);
    assert.equal(await page.locator('#release-history details').count(),3);
    assert.match(await page.locator('#native-install').innerText(),/in Home Assistant installieren/);
    assert.deepEqual((await f.command({action:'snapshot'})).helper_reads,[]);
    console.log('ok 1 - version history, native install handoff, and unsaved-edit navigation guard');

    await page.locator('#savepoint-label').fill('Rollen vor Änderung');await page.locator('#savepoint-create').click();
    await page.getByRole('button',{name:'Wiederherstellung prüfen',exact:true}).first().waitFor();
    assert.equal((await f.command({action:'snapshot'})).points,1);
    await page.getByRole('button',{name:'Wiederherstellung prüfen',exact:true}).first().click();
    await page.locator('#restore-review').waitFor({state:'visible'});
    assert.equal(await page.locator('#restore-apply').isDisabled(),true);
    await f.command({action:'change_zone'});
    await page.locator('#restore-confirm').check();await page.locator('#restore-apply').click();
    await page.waitForFunction(()=>document.getElementById('maintenance-message').textContent.includes('seit Vorschau'));
    assert.equal((await f.command({action:'snapshot'})).points,1);
    console.log('ok 2 - stale preview refuses restore with no extra savepoint or mutation');

    await page.locator('#maintenance-refresh').click();
    await page.getByRole('button',{name:'Wiederherstellung prüfen',exact:true}).first().click();
    await page.locator('#restore-review').waitFor({state:'visible'});
    await page.locator('#restore-confirm').check();await page.locator('#restore-apply').click();
    await page.waitForFunction(()=>document.getElementById('maintenance-message').textContent.includes('wiederhergestellt und pausiert'));
    const restored=await f.command({action:'snapshot'});
    assert.equal(restored.points,2);assert.equal(restored.zones[0].enabled,false);assert.equal(restored.zones[0].name,'a');
    assert.equal(restored.snapshot_reads,0);assert.equal(restored.automation_reads,0);
    console.log('ok 3 - real restore pauses zones and creates verified prior-state savepoint');

    await page.locator('#helper-inspect').click();
    await page.waitForFunction(()=>document.getElementById('helper-message').textContent.includes('1 vorhandene Helfer'));
    assert.match(await page.locator('#helper-results').innerText(),/Timer-Restore ist nicht bestätigt/);
    assert.match(await page.locator('#helper-results').innerText(),/nicht automatisch übernommen/);
    assert.deepEqual((await f.command({action:'snapshot'})).helper_reads,['timer']);
    console.log('ok 4 - renamed existing timer is inspected, not created or adopted');
    for(const width of [390,1440]){
      await page.setViewportSize({width,height:1000});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      if(process.env.PILOTSUITE_SCREENSHOTS){await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS,{recursive:true});
        await page.screenshot({path:path.join(process.env.PILOTSUITE_SCREENSHOTS,`maintenance-${width}.png`),fullPage:true});}
    }
    await page.route('**/api/v1/maintenance',route=>route.fulfill({status:503,json:{message:'synthetic failure'}}),{times:1});
    await page.locator('#maintenance-refresh').click();
    await page.waitForFunction(()=>document.getElementById('maintenance-message').textContent.includes('synthetic failure'));
    assert.equal(await page.locator('#savepoints button').count(),0);assert.equal(await page.locator('#savepoint-create').isDisabled(),true);
    assert.equal(await page.locator('#restore-review').isVisible(),false);
    console.log('ok 5 - failed refresh clears obsolete restore affordances; responsive layouts');

    f.close();f=await fixture(true);
    await page.goto(f.info.url);await page.locator('#rescue-warning').waitFor({state:'visible'});
    await page.waitForFunction(()=>document.getElementById('maintenance-message').textContent.includes('Rescue-Modus'));
    assert.equal(await page.locator('#savepoint-create').isDisabled(),true);
    assert.equal((await f.command({action:'snapshot'})).broken_unchanged,true);
    assert.deepEqual(errors,[]);
    console.log('ok 6 - broken DB serves guarded rescue UI without replacing data');
  }finally{if(browser)await browser.close();if(f)f.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
