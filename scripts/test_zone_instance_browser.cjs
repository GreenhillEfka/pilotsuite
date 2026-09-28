// Actual HTTP/store/application; fake HA only. No household credentials or writes.
const {chromium}=require(process.env.PILOTSUITE_PLAYWRIGHT||'playwright');
const {spawn}=require('node:child_process'),{createInterface}=require('node:readline');
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path');
(async()=>{
 const root=path.resolve(__dirname,'..'),proc=spawn(process.env.PYTHON||'python',['scripts/zone_instance_browser_fixture.py'],{cwd:root,env:{...process.env,PYTHONPATH:path.join(root,'pilotsuite')},stdio:['pipe','pipe','pipe']});
 let stderr='',browser;proc.stderr.on('data',d=>stderr=(stderr+d).slice(-5000));const lines=createInterface({input:proc.stdout})[Symbol.asyncIterator]();
 async function read(){let timer;try{const r=await Promise.race([lines.next(),new Promise((_,reject)=>timer=setTimeout(()=>reject(Error(stderr||'fixture timeout')),15000))]);if(r.done)throw Error(stderr);return JSON.parse(r.value);}finally{clearTimeout(timer);}}
 const command=async c=>{proc.stdin.write(JSON.stringify(c)+'\n');return read();};
 try{
  const info=await read();browser=await chromium.launch({headless:true,...(process.env.PILOTSUITE_CHROMIUM?{executablePath:process.env.PILOTSUITE_CHROMIUM}:{})});
  const page=await browser.newPage({viewport:{width:1440,height:1100}});page.setDefaultTimeout(10000);const errors=[],network=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());page.on('request',r=>{if(r.method()!=='GET')network.push({method:r.method(),url:r.url()});});
  await page.clock.setFixedTime(new Date(info.now*1000));await page.goto(info.url);
  await page.waitForFunction(()=>contextData&&!selectionBusy);
  await page.locator('#ps-zone-configure:not([disabled])').waitFor();
  assert.equal(await page.locator('.ps-nav > a').count(),3);
  assert.equal(await page.locator('#ps-zone-diagnostics').evaluate(e=>e.open),false);
  assert.equal(await page.locator('#ps-module-grid').isVisible(),false);
  assert.equal(await page.locator('#ps-presence-state strong').textContent(),'Belegt');
  assert.equal(await page.locator('#ps-presence-publication strong').textContent(),'Nicht eingerichtet');
  await page.locator('#ps-zone-diagnostics > summary').click();
  await page.locator('[data-ps-module="climate"]').click();
  assert.equal(await page.locator('#ps-zone-presence').isVisible(),true,'presence is independent of diagnostic module');
  await page.locator('#ps-zone-diagnostics > summary').click();
  assert.deepEqual(errors,[]);const baseline=await command({action:'snapshot'});assert.equal(baseline.learning,false);assert.equal(baseline.view.current.state,'occupied');
  assert.equal(baseline.helper_creates,0);assert.equal(baseline.output_calls,0);
  const out=process.env.PILOTSUITE_SCREENSHOTS;if(out){await fs.mkdir(out,{recursive:true});await page.screenshot({path:path.join(out,'zone-presence-first-desktop.png'),fullPage:true});}
  assert.equal(baseline.zones.length,4);
  for(const [zone,expected] of [['z_empty','Unklar'],['z_paused','Pausiert'],['z_other','Unklar'],['room','Belegt']]){
   await page.locator('.ps-nav [data-ps-nav="cockpit"]').click();
   assert.equal(await page.locator('#ps-zone-grid>article').count(),4);
   await page.locator(`[data-ps-zone="${zone}"]`).click();
   await page.waitForFunction(value=>document.querySelector('#ps-presence-state strong')?.textContent===value,expected);
   assert.equal(await page.locator('#ps-view-title').evaluate(e=>e===document.activeElement),true);
  }
  assert.deepEqual((await command({action:'snapshot'})).zones,baseline.zones);
  assert.equal(network.length,0,'zone navigation performs no POST, PUT or HA write');
  await page.locator('[data-ps-live="sources"] summary').click();
  const passive=await page.evaluate(async()=>{
    window.scrollTo(0,450);
    const before=document.scrollingElement.scrollTop,button=document.getElementById('ps-zone-configure'),context=contextData;
    await load({background:true});await load({background:true});
    return {before,after:document.scrollingElement.scrollTop,buttonRetained:button===document.getElementById('ps-zone-configure'),contextRetained:context===contextData,sourcesOpen:document.querySelector('[data-ps-live="sources"]').open};
  });
  assert.equal(passive.after,passive.before);assert.equal(passive.buttonRetained,true);
  assert.equal(passive.contextRetained,true);assert.equal(passive.sourcesOpen,true);
  console.log('ok 0 - passive refresh retains reading position, controls, context and open sources');
  const refreshPresence=()=>page.locator('#ps-zone-presence').getByRole('button',{name:'Aktualisieren',exact:true}).click();
  await command({action:'tick',values:{'binary_sensor.demo_presence':'unavailable','binary_sensor.demo_motion':'unavailable'}});await refreshPresence();
  await page.waitForFunction(()=>document.querySelector('#ps-presence-state strong')?.textContent==='Unklar');
  assert.match(await page.locator('#ps-zone-presence').innerText(),/erforderliche Quelle\(n\) derzeit nicht nutzbar/);
  await command({action:'tick',values:{'binary_sensor.demo_presence':'on','binary_sensor.demo_motion':'off'}});await refreshPresence();
  await page.waitForFunction(()=>document.querySelector('#ps-presence-state strong')?.textContent==='Belegt');
  await page.route('**/api/v1/zones/room/presence',route=>route.fulfill({status:503,json:{message:'Synthetic connection failure'}}),{times:1});
  await refreshPresence();await page.locator('#ps-zone-configure[disabled]').waitFor();
  assert.match(await page.locator('#ps-zone-presence').innerText(),/Unklar bedeutet nicht frei/);
  assert.equal(await page.locator('#ps-presence-state').count(),0,'failed read removes the old decision');
  await refreshPresence();await page.locator('#ps-zone-configure:not([disabled])').waitFor();
  await page.evaluate(()=>{location.hash='#ps-module-detail';});
  await page.waitForFunction(()=>document.getElementById('ps-zone-diagnostics').open);
  await page.locator('#ps-zone-diagnostics > summary').focus();await page.keyboard.press('Enter');
  assert.equal(await page.locator('#ps-zone-diagnostics').evaluate(e=>e.open),false);
  console.log('ok 0b - required source gaps, failed reads and keyboard/direct-link recovery stay explicit');
  await page.locator('#ps-zone-configure').click();await page.locator('#ps-zone-form').waitFor();
  await page.locator('.ps-nav [data-ps-nav="cockpit"]').click();assert.equal(await page.locator('#ps-zone-form').isVisible(),true);
  await page.getByRole('button',{name:'Konfiguration speichern',exact:true}).click();
  await page.locator('#ps-zone-form').waitFor({state:'hidden'});await page.locator('#ps-zone-configure:not([disabled])').waitFor();
  assert.equal((await command({action:'snapshot'})).mode,'compare');console.log('ok 1 - relevance-based presence, typed configuration, no extra grant, dirty guard');
  await page.getByRole('button',{name:'Sensordaten & Verläufe',exact:true}).click();
  try{await page.locator('.ps-zone-chart:visible').first().waitFor();}catch(e){throw Error('Historienansicht blieb leer: '+await page.locator('#ps-zone-presence .ps-notice').first().textContent()+' / '+e.message);}assert.equal(await page.locator('.ps-zone-chart:visible').count()>0,true);
  assert.equal((await command({action:'snapshot'})).history_reads,1);
  if(out)await page.screenshot({path:path.join(out,'zone-data-desktop.png'),fullPage:true});
  await page.getByRole('button',{name:'Ansicht schließen',exact:true}).click();
  console.log('ok 2 - real data endpoint, recorded history charts and tables without consent step');
  await page.getByRole('button',{name:'Eigenen Anwesenheitssensor vorbereiten',exact:true}).click();
  await page.getByRole('button',{name:'Genau diesen Plan anwenden',exact:true}).waitFor();
  assert.equal((await command({action:'snapshot'})).helper_creates,0);
  await page.getByRole('button',{name:'Genau diesen Plan anwenden',exact:true}).click();
  await page.getByText('Planstatus: verified',{exact:true}).waitFor();
  const created=await command({action:'snapshot'});assert.equal(created.helper_creates,5);assert.equal(created.output_calls,0);assert.equal(created.metadata_calls,1);
  await page.getByRole('button',{name:'Schließen',exact:true}).last().click();
  await page.locator('#refresh').click();await page.locator('#ps-zone-configure[disabled]').waitFor();await page.getByRole('button',{name:'Jetzt abgleichen',exact:true}).waitFor();await page.locator('#ps-zone-configure:not([disabled])').waitFor();
  console.log('ok 3 - reviewed owned output package creates only on explicit click, publishing remains off');
  await page.getByRole('button',{name:'Entitäten → Ontologie',exact:true}).click();
  await page.getByLabel('Anzeigename',{exact:true}).fill('Demo · Präsenz');await page.getByLabel('Logische Zonenmitgliedschaft',{exact:true}).selectOption('zone');await page.getByLabel('Habitus Übersicht',{exact:true}).check();
  await page.getByRole('button',{name:'Änderungsplan prüfen',exact:true}).click();await page.getByRole('button',{name:'Genau diesen Plan anwenden',exact:true}).click();
  await page.getByText('Planstatus: verified',{exact:true}).waitFor();assert.equal((await command({action:'snapshot'})).metadata_calls,created.metadata_calls+1);
  await page.getByRole('button',{name:'Rücknahme prüfen',exact:true}).click();await page.getByRole('button',{name:'Genau diesen Plan anwenden',exact:true}).click();
  await page.getByText('Planstatus: verified',{exact:true}).waitFor();assert.equal((await command({action:'snapshot'})).metadata_calls,created.metadata_calls+2);
  await page.getByRole('button',{name:'Schließen',exact:true}).last().click();
  await page.waitForFunction(()=>!selectionBusy&&!window.PilotSuiteZonePresence.dirty());
  console.log('ok 4 - name/ontology preview, exact apply and explicit rollback');
  await page.locator('#ps-zone-configure').click();await page.locator('#ps-zone-form').waitFor();
  await page.getByLabel('Betriebsmodus',{exact:true}).selectOption('publish');
  await page.getByRole('button',{name:'Konfiguration speichern',exact:true}).click();
  await page.locator('#ps-zone-form').waitFor({state:'hidden'});await page.locator('#ps-zone-configure:not([disabled])').waitFor();
  await command({action:'tick',seconds:1,values:{'binary_sensor.demo_presence':'on'}});
  const published=await command({action:'publish'});assert.equal(published.view.publication,'verified');
  const checkedAt=published.view.publication_checked_at;assert.equal(typeof checkedAt,'number');
  await refreshPresence();await page.getByText('Zuletzt bestätigt',{exact:true}).waitFor();
  const proofHint=await page.locator('#ps-presence-publication small').textContent();assert.match(proofHint,/Rückleseprüfung:/);
  for(let i=0;i<3;i++){
   await command({action:'tick',seconds:5});const unchanged=await command({action:'publish'});
   assert.equal(unchanged.output_calls,published.output_calls,'unchanged ticks cause no extra output write');
   assert.equal(unchanged.view.publication_checked_at,checkedAt,'passive checks never re-date evidence');
   await refreshPresence();assert.equal(await page.locator('#ps-presence-publication strong').textContent(),'Zuletzt bestätigt');
   assert.equal(await page.locator('#ps-presence-publication small').textContent(),proofHint);
  }
  if(out)await page.screenshot({path:path.join(out,'zone-publication-proof-desktop.png'),fullPage:true});
  console.log('ok 4b - dated publication proof survives unchanged ticks without extra mocked HA writes');
  for(const width of [390,768,1440]){await page.setViewportSize({width,height:1100});for(const theme of ['dark','light']){
   await page.locator('.ps-nav [data-ps-nav="system"]').click();await page.locator('#ps-theme').selectOption(theme);await page.locator('.ps-nav [data-ps-nav="cockpit"]').click();await page.locator('[data-ps-nav="zone"]').click();
   await page.locator('#ps-zone-configure:not([disabled])').waitFor();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'overflow '+width);
   if(out){
    await page.screenshot({path:path.join(out,`zone-instance-${theme}-${width}.png`),fullPage:true});
    if(width===390){await page.locator('#ps-presence-publication').evaluate(e=>e.scrollIntoView({block:'center',behavior:'instant'}));
     await page.locator('#ps-presence-publication').screenshot({path:path.join(out,`zone-publication-proof-mobile-${theme}.png`)});}
   }
  }}
  const final=await command({action:'snapshot'});assert.equal(final.learning,false);assert.deepEqual(final.roles,baseline.roles);assert.deepEqual(final.zones,baseline.zones);assert.deepEqual(errors,[]);
  assert.equal(network.some(r=>/presence-runtime|transactions\/.+\/apply|history\/import/.test(r.url)),false);
  await page.evaluate(()=>window.PilotSuiteZonePresence.invalidate());assert.equal(await page.locator('#ps-zone-configure').isDisabled(),true);
  console.log('ok 5 - themes, three widths, conservative invalidation, no legacy grants and no household calls');
 }finally{if(browser)await browser.close();proc.stdin.end();proc.kill('SIGTERM');}
})().catch(e=>{console.error(e);process.exitCode=1;});
