// Actual HTTP application and canonical temporary stores, never the live HA host.
const {chromium} = require(process.env.PILOTSUITE_PLAYWRIGHT || 'playwright');
const {spawn} = require('node:child_process');
const {createInterface} = require('node:readline');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');

function bounded(promise, label, ms=15000) {
  let timer;
  return Promise.race([promise, new Promise((_,reject) => {
    timer=setTimeout(() => reject(new Error(`${label} timed out`)),ms);
  })]).finally(() => clearTimeout(timer));
}

(async () => {
  const root=path.resolve(__dirname,'..');
  const fixture=spawn(process.env.PYTHON || 'python',['scripts/daily_brief_browser_fixture.py'], {
    cwd:root,env:{...process.env,PYTHONPATH:path.join(root,'pilotsuite')},stdio:['pipe','pipe','pipe']});
  let stderr=''; fixture.stderr.on('data', chunk=>{stderr=(stderr+chunk).slice(-12000);});
  const lines=createInterface({input:fixture.stdout})[Symbol.asyncIterator]();
  const read=async () => {
    const item=await bounded(lines.next(),'Fixture response');
    if(item.done) throw new Error('Fixture stopped: '+stderr);
    return JSON.parse(item.value);
  };
  const command=async fields => {fixture.stdin.write(JSON.stringify(fields)+'\n'); return read();};
  let browser;
  let steps=0;
  const checked=label=>{steps++;console.log(`ok ${steps} - ${label}`);};
  try {
    const info=await read();
    browser=await chromium.launch({headless:true,
      ...(process.env.PILOTSUITE_CHROMIUM ? {executablePath:process.env.PILOTSUITE_CHROMIUM} : {})});
    const page=await browser.newPage({viewport:{width:390,height:844}});
    page.setDefaultTimeout(10000);
    const errors=[],writes=[];
    page.on('pageerror', error=>errors.push(error.message));
    page.on('request', request=>{if(!['GET','HEAD'].includes(request.method()))writes.push(request.url());});
    await page.goto(info.url);
    await page.waitForFunction(()=>contextData?.daily_brief?.candidate && !selectionBusy);
    const brief=page.locator('#daily-brief');
    const link=brief.locator('a[data-pattern-id]');
    assert.equal(await link.count(),1);
    assert.equal(await link.getAttribute('data-pattern-id'),info.pattern_id);
    assert.match(await brief.textContent(),/12 Aktivierungen an 6 Tagen/);
    checked('actual owner-backed candidate is rendered in the real app shell');
    const initial=await command({action:'snapshot'});
    assert.deepEqual([initial.related_reads,initial.config_reads,initial.snapshot_reads],[0,0,0]);

    // One keyboard navigation, no draft creation, feedback or HA API call.
    await link.focus(); await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(()=>document.activeElement.id),'pattern-workbench');
    assert.deepEqual(initial,await command({action:'snapshot'}));
    assert.deepEqual(writes,[]);
    checked('keyboard navigation uses the existing workbench without writes');

    await brief.locator('details summary').click();
    await brief.locator('details summary').focus();
    await page.evaluate(async()=>{await loadContext();});
    assert.equal(await brief.locator('details').getAttribute('open'),'');
    assert.equal(await page.evaluate(()=>document.activeElement.textContent),'Grundlage und Grenzen');
    checked('equal full HTTP reload retains expanded explanation and keyboard focus');

    // Pause a real HTTP response after fetching it; no fabricated response shape.
    let release,arrived;
    const arrival=new Promise(resolve=>{arrived=resolve;});
    const gate=new Promise(resolve=>{release=resolve;});
    await page.route('**/api/v1/zones/a/context',async route=>{
      const response=await route.fetch(); arrived(); await gate; await route.fulfill({response});
    },{times:1});
    await page.evaluate(()=>{window.briefReload=loadContext();});
    await bounded(arrival,'Held reload');
    assert.equal(await link.count(),0);
    checked('pending same-zone HTTP reload removes the old candidate immediately');
    release();await page.evaluate(()=>window.briefReload);
    assert.equal(await link.count(),1);

    // A latest request error invalidates just the brief; no stale candidate resurrection.
    await page.route('**/api/v1/zones/a/context',route=>route.fulfill({status:503,json:{message:'Synthetic temporary failure'}}),{times:1});
    await page.evaluate(async()=>{try{await loadContext();}catch{}renderDailyBrief();});
    assert.equal(await link.count(),0);
    await page.evaluate(async()=>{await loadContext();});
    assert.equal(await link.count(),1);
    checked('failed reload stays invalid through rerender and recovers only on fresh read');

    // Local unsaved choice must be retained, never applied by a brief read.
    await page.evaluate(()=>{selectionDraft.set('light.synthetic','ignored');selectionChanged();});
    assert.equal(await link.count(),0);
    assert.equal(await page.evaluate(()=>selectionDraft.dirty),true);
    assert.deepEqual(initial,await command({action:'snapshot'}));
    await page.evaluate(async()=>{selectionDraft.set('light.synthetic','relevant');await loadSelection(selectionZone);});
    assert.equal(await link.count(),1);
    checked('unsaved entity choices prevent navigation without saving or clearing them');

    // Mutation is only in the disposable fixture over stdin; browser still reads only.
    await command({action:'feedback',decision:'rejected'});
    await page.evaluate(async()=>{await loadContext();});
    assert.equal(await link.count(),0);
    assert.match(await brief.textContent(),/1 abgelehnt/);
    await command({action:'feedback',decision:'later'});
    await page.evaluate(async()=>{await loadContext();});
    assert.match(await brief.textContent(),/1 vertagt/);
    await command({action:'feedback',decision:'accepted'});
    await page.evaluate(async()=>{await loadContext();});
    assert.equal(await link.count(),1);
    checked('existing preference owner excludes rejected and deferred patterns');

    await command({action:'connection',ready:false});
    await page.evaluate(async()=>{await loadContext();});
    assert.equal(await link.count(),0);
    assert.match(await brief.textContent(),/Verbindung/);
    await command({action:'connection',ready:true});
    await page.evaluate(async()=>{await loadSelection(selectionZone);});
    assert.equal(await link.count(),1);
    checked('disconnect and recovery are reflected without changing consent');

    for(const width of [390,1440]) {
      await page.setViewportSize({width,height:width===390?844:1000});
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'horizontal overflow');
      if(process.env.PILOTSUITE_SCREENSHOTS) {
        await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS,{recursive:true});
        await brief.screenshot({path:path.join(process.env.PILOTSUITE_SCREENSHOTS,`daily-brief-full-app-${width}.png`)});
      }
    }
    checked('mobile and desktop layouts fit the viewport');

    await page.evaluate(async()=>{document.activeElement?.blur();await loadSelection('b');});
    assert.equal(await link.count(),0);
    assert.equal(await page.evaluate(()=>contextData.daily_brief.zone_id),'b');
    assert.ok(!(await brief.textContent()).includes('12 Aktivierungen'));
    await page.evaluate(async()=>{await loadSelection('a');});
    assert.equal(await link.count(),1);
    checked('zone switch never leaks the other zone candidate');

    const end=await command({action:'snapshot'});
    assert.deepEqual([end.related_reads,end.config_reads,end.snapshot_reads],[0,0,0]);
    assert.deepEqual(writes,[]);assert.deepEqual(errors,[]);
    checked('full browser flow emitted no mutation requests or JavaScript errors');
    console.log(`Daily brief full-app browser: ${steps} checks passed (synthetic only)`);
  } finally {
    if(browser)await browser.close();
    fixture.stdin.end();
    try {
      const code=await bounded(new Promise(resolve=>{
        if(fixture.exitCode!==null)return resolve(fixture.exitCode);
        fixture.once('exit',resolve);
      }),'Fixture cleanup',5000);
      if(code!==0)throw new Error('Fixture cleanup failed: '+stderr);
    } catch(error) {fixture.kill('SIGTERM');throw error;}
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
