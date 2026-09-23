// Synthetic note-editor contract. The full selection suite separately loads the real app shell.
const {chromium} = require(process.env.PILOTSUITE_PLAYWRIGHT || 'playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({headless:true,
    ...(process.env.PILOTSUITE_CHROMIUM ? {executablePath:process.env.PILOTSUITE_CHROMIUM} : {})});
  try {
    const page = await browser.newPage({viewport:{width:390,height:844}});
    const errors=[]; page.on('pageerror',error=>errors.push(error.message));
    page.on('dialog',dialog=>dialog.accept());
    let fail=false, conflict=false, fingerprint='a'.repeat(64);
    let saved={revision:0,items:[],limit:20,execution:{allowed:false,actions:[]}};
    const draft=()=>({id:'d',zone_id:'z',revision:2,source_status:'current',unavailable_targets:[],
      fields:{target_ids:['light.synthetic']},current_pattern:{sources:['binary_sensor.synthetic']},review_notes:saved});
    const comparison=()=>({draft_id:'d',zone_id:'z',draft_revision:2,zone_revision:3,
      checked_at:'2026-09-23T12:00:00Z',inspection:{entity_id:'automation.synthetic',config_fingerprint:fingerprint}});
    const harness=`
      let selectionZone='z',contextData=null,routineComparison=null,selectionBusy=false,
        contextEditing=false,zoneFormOpen=false,selectionDraft=null,contextGeneration=0;
      const byId=id=>document.getElementById(id);
      const text=(id,value)=>byId(id).textContent=value;
      const endpoint=value=>new URL(value,location.href).href;
      async function json(url,options={}) {
        const response=await fetch(endpoint(url),{...options,headers:{'Content-Type':'application/json'}});
        const data=await response.json();if(!response.ok)throw new Error(data.message);return data;
      }
      function comparisonFor(draft) {
        const r=routineComparison;
        return r && r.zone_id===selectionZone && r.draft_id===draft.id &&
          r.draft_revision===draft.revision && r.zone_revision===contextData.revision ? r : null;
      }
      function renderSelection() {}
      function renderLearning() {
        byId('cards').replaceChildren();
        for(const draft of contextData?.drafts || []) {
          const card=document.createElement('article');
          if(typeof appendReviewNotes==='function')appendReviewNotes(card,draft);
          byId('cards').append(card);
        }
      }
      async function loadContext() {
        contextData=await json('api/v1/zones/'+selectionZone+'/context');renderLearning();return true;
      }
    `;
    await page.route('http://pilotsuite.test/**',async route=>{
      const suffix=new URL(route.request().url()).pathname.replace('/ingress/test/','');
      if (!suffix) return route.fulfill({contentType:'text/html',body:`<!doctype html><html lang="de"><head><meta name="viewport" content="width=device-width"></head><body><main><div id="cards"></div><form id="routine-form" hidden></form><p id="routine-message" role="status"></p></main><script>${harness}</script></body></html>`});
      if(suffix.startsWith('assets/')) {
        const name=suffix.slice(7);
        return route.fulfill({body:await fs.readFile(path.join(__dirname,'../pilotsuite/pilotsuite/web',name)),contentType:name.endsWith('.js')?'text/javascript':'text/css'});
      }
      if(suffix.endsWith('/context')) return route.fulfill({json:{revision:3,drafts:suffix.includes('/z/')?[draft()]:[]}});
      if(suffix.endsWith('/automation-inspection')) {
        if(fail)return route.fulfill({status:503,json:{message:'synthetic offline'}});
        return route.fulfill({json:comparison()});
      }
      assert.ok(suffix.endsWith('/review-notes'),'Unexpected route '+suffix);
      const payload=route.request().postDataJSON();
      if(fail)return route.fulfill({status:503,json:{message:'synthetic offline'}});
      if(conflict || payload.review_revision!==saved.revision || (route.request().method()==='PUT' && payload.config_fingerprint!==fingerprint))
        return route.fulfill({status:409,json:{message:'synthetic changed basis'}});
      if(route.request().method()==='DELETE') {
        saved={...saved,revision:saved.revision+1,items:[]};return route.fulfill({json:saved});
      }
      assert.equal(payload.revision,2);assert.equal(payload.zone_revision,3);
      assert.deepEqual(Object.keys(payload).sort(),['automation_id','config_fingerprint','disposition','review_revision','revision','text','zone_revision']);
      saved={...saved,revision:saved.revision+1,items:[{
        automation_id:payload.automation_id,draft_revision:2,zone_revision:3,config_fingerprint:fingerprint,
        disposition:payload.disposition,text:payload.text,checked_at:comparison().checked_at,
        stale:false,stale_reasons:[],config_status:'not_rechecked'}]};
      return route.fulfill({json:{review_notes:saved,automation_review:comparison()}});
    });
    await page.goto('http://pilotsuite.test/ingress/test/');
    await page.evaluate(async()=>{await loadContext();});
    await page.addScriptTag({url:'http://pilotsuite.test/ingress/test/assets/review_notes.js'});
    await page.evaluate(report=>{routineComparison=report;renderLearning();},comparison());
    await page.getByRole('button',{name:'Bewertung festhalten',exact:true}).click();
    const unsafe='<img src=x onerror="window.canary=true">';
    await page.locator('#review-note-text').fill(unsafe);
    await page.locator('#review-note-disposition').selectOption('reviewed');
    await page.getByRole('button',{name:'Bewertung für diesen Prüfstand speichern',exact:true}).click();
    await page.waitForFunction(()=>byId('review-note-form').hidden);
    assert.equal(await page.locator('.review-note-text').textContent(),unsafe);
    assert.equal(await page.locator('.review-note img').count(),0);
    assert.equal(await page.evaluate(()=>window.canary),undefined);
    assert.match(await page.locator('.review-note').textContent(),/Passt zum zuletzt gelesenen/);
    await page.evaluate(async()=>{routineComparison=null;await loadContext();});
    assert.match(await page.locator('.review-note').textContent(),/noch nicht erneut geprüft/);
    await page.evaluate(report=>{routineComparison=report;renderLearning();},comparison());
    await page.getByRole('button',{name:'Bewertung festhalten',exact:true}).click();
    await page.locator('#review-note-text').fill('Mein unverlorener Entwurf');
    conflict=true;
    await page.getByRole('button',{name:'Bewertung für diesen Prüfstand speichern',exact:true}).click();
    await page.waitForFunction(()=>byId('review-note-message').textContent.includes('Speichern nicht bestätigt'));
    assert.equal(await page.locator('#review-note-text').inputValue(),'Mein unverlorener Entwurf');
    assert.equal(await page.locator('#review-note-form').isVisible(),true);
    assert.match(await page.locator('.review-note').textContent(),/noch nicht erneut geprüft/);
    conflict=false;fingerprint='b'.repeat(64);
    await page.locator('#review-note-reload').click();
    await page.waitForFunction(()=>byId('review-note-message').textContent.startsWith('Prüfstand neu geladen'));
    assert.equal(await page.locator('#review-note-text').inputValue(),'Mein unverlorener Entwurf');
    assert.match(await page.locator('.review-note').textContent(),/Automation geändert/);
    fail=true;
    await page.getByRole('button',{name:'Bewertung für diesen Prüfstand speichern',exact:true}).click();
    await page.waitForFunction(()=>byId('review-note-message').textContent.includes('synthetic offline'));
    assert.equal(await page.locator('#review-note-text').inputValue(),'Mein unverlorener Entwurf');
    assert.equal(saved.items[0].text,unsafe);
    fail=false;
    await page.locator('#review-note-reload').click();
    await page.waitForFunction(()=>byId('review-note-message').textContent.startsWith('Prüfstand neu geladen'));
    for(const width of [390,1280]) {
      await page.setViewportSize({width,height:900});
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'horizontal overflow '+width);
      if(process.env.PILOTSUITE_SCREENSHOTS) {
        await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS,{recursive:true});
        await page.screenshot({path:path.join(process.env.PILOTSUITE_SCREENSHOTS,`review-notes-${width}.png`),fullPage:true});
      }
    }
    await page.getByRole('button',{name:'Bewertung für diesen Prüfstand speichern',exact:true}).click();
    await page.waitForFunction(()=>byId('review-note-form').hidden);
    assert.equal(saved.items[0].text,'Mein unverlorener Entwurf');
    const exported=await page.evaluate(()=>projectReviewNotes(contextData.drafts[0]));
    assert.equal(exported.items[0].view_status,'matches_last_read');assert.equal(exported.execution.allowed,false);
    await page.getByRole('button',{name:'Bewertung löschen: automation.synthetic',exact:true}).click();
    await page.waitForFunction(()=>byId('cards').textContent.includes('Noch keine eigene Bewertung'));
    assert.equal(saved.items.length,0);assert.equal(saved.revision,3);
    await page.evaluate(async()=>{selectionZone='other';routineComparison=null;await loadContext();});
    assert.equal(await page.locator('.review-note').count(),0);
    assert.deepEqual(errors,[]);
    console.log('Review-note browser: save, reload, conflicts, failures, text preservation, XSS, export, delete, zone isolation and mobile/desktop passed.');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
