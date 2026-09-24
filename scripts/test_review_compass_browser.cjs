// Actual application + temporary canonical stores + mocked HA reads, never a live house.
const {chromium}=require(process.env.PILOTSUITE_PLAYWRIGHT || 'playwright');
const {spawn}=require('node:child_process');
const {createInterface}=require('node:readline');
const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');

(async()=>{
  const root=path.resolve(__dirname,'..');
  const fixture=spawn(process.env.PYTHON || 'python',['scripts/compass_browser_fixture.py'],{
    cwd:root,env:{...process.env,PYTHONPATH:path.join(root,'pilotsuite')},stdio:['pipe','pipe','pipe']});
  let stderr='';fixture.stderr.on('data',data=>{stderr+=data;});
  const lines=createInterface({input:fixture.stdout})[Symbol.asyncIterator]();
  async function read() {
    const item=await lines.next();if(item.done)throw new Error('Fixture stopped: '+stderr);
    return JSON.parse(item.value);
  }
  const command=async action=>{fixture.stdin.write(JSON.stringify(action)+'\n');return read();};
  let browser;
  try {
    const info=await read();
    browser=await chromium.launch({headless:true,...(process.env.PILOTSUITE_CHROMIUM ? {executablePath:process.env.PILOTSUITE_CHROMIUM}:{})});
    const page=await browser.newPage({viewport:{width:390,height:844}});
    page.setDefaultTimeout(10000);
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    page.on('dialog',dialog=>dialog.accept());
    await page.goto(info.url);
    await page.waitForFunction(()=>typeof PilotSuiteReviewCompass==='object' && contextData?.drafts?.length===2 && !selectionBusy);
    const card=id=>page.locator(`#routine-list > article[data-draft-id="${id}"]`);
    const initial=await command({action:'snapshot'});
    assert.equal(initial.related_reads,0);assert.equal(initial.config_reads,0);
    assert.equal(await page.locator('#routine-list > article').count(),2);
    assert.match(await card(info.draft_ids[0]).locator('.review-compass-next').textContent(),/Entwurfsangaben prüfen/);
    assert.match(await card(info.draft_ids[1]).locator('.review-compass-next').textContent(),/Bestehende Automationen prüfen/);

    await page.locator('#review-compass-filter').selectOption('intent');
    assert.equal(await page.locator('#routine-list > article').count(),1);
    await page.locator('#review-compass-filter').selectOption('automation');
    assert.equal(await page.locator('#routine-list > article').count(),1);
    await page.locator('#review-compass-sort').selectOption('title');
    assert.equal((await command({action:'snapshot'})).related_reads,0);
    await page.locator('#review-compass-filter').selectOption('all');
    await card(info.draft_ids[0]).locator('.review-compass-action').click();
    await page.waitForFunction(()=>!byId('routine-form').hidden);
    const unsafe='<img src=x onerror="window.compassCanary=true">';
    await page.locator('#routine-goal').fill(unsafe);
    await command({action:'touch_draft',id:info.draft_ids[0]});
    await page.locator('#routine-form button[type="submit"]').click();
    await page.waitForFunction(()=>!selectionBusy);
    assert.equal(await page.locator('#routine-goal').inputValue(),unsafe);
    assert.equal(await page.locator('#routine-form').isVisible(),true);
    assert.match(await page.locator('#routine-message').textContent(),/nicht bestätigt/);
    await page.locator('#routine-cancel').click();
    await page.evaluate(async()=>{await loadContext();});
    assert.equal(await page.evaluate(()=>window.compassCanary),undefined);

    // Only the explicit compass button performs the bounded comparison.
    await card(info.draft_ids[1]).locator('.review-compass-action').click();
    await page.waitForFunction(()=>!selectionBusy && !!routineComparison);
    assert.equal((await command({action:'snapshot'})).related_reads,1);
    assert.match(await card(info.draft_ids[1]).locator('.review-compass-next').textContent(),/Treffer/);
    await card(info.draft_ids[1]).locator('.review-compass-action').click();
    assert.equal((await command({action:'snapshot'})).config_reads,0);
    await card(info.draft_ids[1]).getByRole('button',{name:'Details prüfen: automation.synthetic',exact:true}).click();
    await page.waitForFunction(()=>!selectionBusy && !!routineComparison?.inspection);
    assert.equal((await command({action:'snapshot'})).config_reads,1);
    assert.match(await card(info.draft_ids[1]).locator('.review-compass-next').textContent(),/Eigene Bewertung/);
    await card(info.draft_ids[1]).locator('.review-compass-action').click();
    await page.locator('#review-note-text').fill(unsafe);
    await page.locator('#review-note-disposition').selectOption('reviewed');
    await page.getByRole('button',{name:'Bewertung für diesen Prüfstand speichern',exact:true}).click();
    await page.waitForFunction(()=>!selectionBusy && byId('review-note-form').hidden);
    const saved=await command({action:'snapshot'});
    assert.equal(saved.config_reads,2);assert.equal(saved.learning,initial.learning);
    assert.equal(Object.values(saved.notes[0])[0].text,unsafe);
    assert.equal(await card(info.draft_ids[1]).locator('img').count(),0);
    assert.equal(await page.evaluate(()=>window.compassCanary),undefined);
    assert.match(await card(info.draft_ids[1]).locator('.review-compass-next').textContent(),/fachliche Grenzen/);
    assert.match(await card(info.draft_ids[1]).locator('.review-compass').textContent(),/keine Ausführungsfreigabe/);
    assert.ok(!(await page.locator('body').textContent()).includes('PRIVATE_CONFIG_CANARY'));

    // Background reread keeps the last inspected scope but updates current evidence.
    await page.evaluate(async()=>{document.activeElement?.blur();await loadContext();});
    assert.equal((await command({action:'snapshot'})).config_reads,2);
    await command({action:'config_change'});
    await card(info.draft_ids[1]).getByRole('button',{name:'Erneut prüfen: automation.synthetic',exact:true}).click();
    await page.waitForFunction(()=>!selectionBusy && routineComparison?.inspection?.change_status==='changed');
    assert.match(await card(info.draft_ids[1]).locator('.review-compass-next').textContent(),/Eigene Bewertung/);
    const changed=await command({action:'snapshot'});
    assert.equal(Object.values(changed.notes[0])[0].text,unsafe);
    assert.equal(Object.values(changed.notes[0])[0].disposition,'reviewed');

    // Time expiry and foreign responses never turn the compass into an approval.
    await page.evaluate(()=>{
      routineComparison.checked_at='2000-01-01T00:00:00Z';
      routineComparison.review_compass.comparison_checked_at=routineComparison.checked_at;
      document.activeElement?.blur();renderRoutineDrafts();
    });
    assert.doesNotMatch(await card(info.draft_ids[1]).locator('.review-compass-next').textContent(),/fachliche Grenzen/);
    await command({action:'source_unavailable'});
    await page.evaluate(async()=>{document.activeElement?.blur();await loadContext();});
    assert.match(await card(info.draft_ids[1]).locator('.review-compass-next').textContent(),/Quellenübersicht/);
    const detail=card(info.draft_ids[1]).locator('.review-compass-details');await detail.locator('summary').click();
    assert.match(await detail.textContent(),/nicht auswertbar/);
    await page.locator('#review-compass-filter').selectOption('sources');
    assert.equal(await page.locator('#routine-list > article').count(),2);

    // Keyboard focus survives a pure projection refresh; forms were not reset.
    await card(info.draft_ids[1]).locator('.review-compass-details summary').focus();
    const beforeFocus=await page.evaluate(()=>document.activeElement.textContent);
    await page.evaluate(async()=>{await loadContext();});
    assert.equal(await page.evaluate(()=>document.activeElement.textContent),beforeFocus);
    assert.equal((await command({action:'snapshot'})).config_reads,changed.config_reads);

    const screenshotDir=process.env.PILOTSUITE_SCREENSHOTS;
    if(screenshotDir){await fs.mkdir(screenshotDir,{recursive:true});await page.screenshot({path:path.join(screenshotDir,'review-compass-mobile.png'),fullPage:true});}
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'mobile overflow');
    await page.setViewportSize({width:1440,height:1000});
    if(screenshotDir)await page.screenshot({path:path.join(screenshotDir,'review-compass-desktop.png'),fullPage:true});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'desktop overflow');
    await page.evaluate(async()=>{document.activeElement?.blur();await loadSelection('b');});
    await page.waitForFunction(()=>selectionZone==='b' && !selectionBusy);
    assert.equal(await page.locator('#routine-list > article').count(),0);
    assert.equal(await page.locator('#review-compass-workspace').isVisible(),false);
    assert.equal(await page.locator('#routine-list').textContent(),'Noch keine gespeicherten Entwürfe in dieser Zone.');
    assert.deepEqual(errors,[]);
    console.log('Review-compass full-app browser contracts: OK (synthetic only)');
  } finally {
    if(browser)await browser.close();
    fixture.stdin.end();
    const exit=await new Promise(resolve=>{if(fixture.exitCode!==null)return resolve(fixture.exitCode);fixture.once('exit',resolve);});
    if(exit!==0)throw new Error('Fixture cleanup failed: '+stderr);
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
