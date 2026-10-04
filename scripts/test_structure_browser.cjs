// Actual app and durable stores; all HA calls use the existing disposable fixture.
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
  const page=await browser.newPage({viewport:{width:1440,height:1100},reducedMotion:'reduce'}),errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(new URL(r.url()).pathname));
  await page.addInitScript(()=>localStorage.setItem('pilotsuite.workspace.v1',JSON.stringify({view:'all',theme:'light'})));
  await page.goto(info.url);await page.waitForFunction(()=>selectionZone && !selectionBusy && structureData);
  assert.equal(await page.getByRole('link',{name:'Werkzeuge',exact:true}).count(),0);
  assert.equal(await page.locator('body').getAttribute('data-ps-foundation'),'true');
  assert.equal(await page.locator('#ps-view-title').innerText(),'Habituszonen');
  for(const old of ['all','workbench','history','automations','zone','ps-module-detail','learning-section']){
   await page.evaluate(hash=>{location.hash=hash;},'#'+(old.startsWith('ps-')||old.endsWith('section')?old:'ps-'+old));
   await page.waitForFunction(()=>location.hash==='#ps-cockpit');
   assert.equal(await page.locator('#ps-view-title').innerText(),'Habituszonen');
  }
  const before=await command({action:'snapshot'});
  await page.evaluate(async()=>{await load({background:true});await load({background:true});});
  assert.equal(requests.some(p=>/\/(suggestions|context|presence|shadow|history|organization|routines)(\/|$)/.test(p)),false,requests.join('\n'));
  const after=await command({action:'snapshot'});
  for(const key of ['helper_creates','label_creates','output_calls','metadata_calls','history_reads','automation_reads'])assert.equal(after[key],before[key],key);
  assert.deepEqual(errors,[]);
  console.log('ok - reduced routes and refresh have no deferred analysis or household writes');
  const openEditor=async()=>{
   await page.getByRole('link',{name:'Zone bearbeiten',exact:true}).click();await page.locator('#zone-edit').click();
   await page.waitForFunction(()=>!zoneLabelBusy && !document.getElementById('zone-form').hidden);
  };
  const member=eid=>page.locator('.zone-member').filter({hasText:eid});
  let releaseLabels;const heldLabels=new Promise(resolve=>releaseLabels=resolve);
  await page.route('**/api/v1/zone-labels',async route=>{await heldLabels;await route.continue();},{times:1});
  await page.getByRole('link',{name:'Zone bearbeiten',exact:true}).click();await page.locator('#zone-edit').click();
  await page.waitForFunction(()=>zoneLabelBusy);
  try{
   for(const id of ['zone-label-new','zone-candidates-import','zone-label-load'])assert.equal(await page.locator('#'+id).isDisabled(),true,id);
   assert.equal(await page.getByRole('button',{name:'Zone speichern',exact:true}).isDisabled(),true);
  }finally{releaseLabels();}
  await page.waitForFunction(()=>!zoneLabelBusy && !document.getElementById('zone-form').hidden);
  assert.equal(await page.getByText('Für Auswertung verwenden',{exact:true}).isVisible(),false);
  await page.locator('#zone-label-select').selectOption('setup_demo');await page.locator('#zone-label-import').click();
  await page.waitForFunction(()=>!zoneLabelBusy && zoneSetupRows.length===2);
  const light=member('light.demo');await light.locator('summary').click();
  assert.equal(await light.getByLabel('Habitus Bedienung',{exact:true}).isChecked(),true,'new untagged light gets an editable display default');
  assert.match(await light.innerText(),/Vorauswahl.*Leuchte/);
  const roleDirectory=process.env.PILOTSUITE_SCREENSHOTS||'/tmp/pilotsuite-structure-review';await fs.mkdir(roleDirectory,{recursive:true});
  for(const [width,theme] of [[1440,'light'],[390,'dark']]){
   await page.setViewportSize({width,height:1000});await page.getByLabel('Farbschema').selectOption(theme);
   await light.scrollIntoViewIfNeeded();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
   await page.screenshot({path:path.join(roleDirectory,`role-preselection-${width}-${theme}.png`),fullPage:true});
  }
  await page.setViewportSize({width:1440,height:1100});

  assert.equal(await member('binary_sensor.demo_presence').getByLabel('Habitus Übersicht',{exact:true}).isChecked(),true,'existing label wins over type');
  await page.locator('#zone-ha-links select[data-ha-link="light_group"]').selectOption('light.demo');
  assert.equal(await page.locator('#zone-ha-links select[data-ha-link="light_group"]').inputValue(),'light.demo');
  await light.getByLabel('Habitus Bedienung',{exact:true}).uncheck();
  await page.locator('#zone-label-import').click();await page.waitForFunction(()=>!zoneLabelBusy);
  await light.locator('summary').click();
  assert.equal(await light.getByLabel('Habitus Bedienung',{exact:true}).isChecked(),false,'intentional empty role draft survives reimport');
  await light.getByRole('button',{name:'Typbasierte Vorauswahl übernehmen',exact:true}).click();
  assert.equal(await light.getByLabel('Habitus Bedienung',{exact:true}).isChecked(),true);
  await page.locator('#zone-use-ha-roles').click();
  assert.equal(await light.getByLabel('Habitus Bedienung',{exact:true}).isChecked(),false,'HA role import can explicitly discard only type defaults');
  await light.locator('summary').click();
  await light.getByRole('button',{name:'Typbasierte Vorauswahl übernehmen',exact:true}).click();

  await member('binary_sensor.demo_presence').locator('input[type=checkbox]').first().uncheck();
  await page.locator('#zone-label-import').click();await page.waitForFunction(()=>!zoneLabelBusy);
  assert.equal(await member('binary_sensor.demo_presence').locator('input').first().isChecked(),false);
  assert.equal(await light.getByLabel('Habitus Bedienung',{exact:true}).isChecked(),true);
  await member('binary_sensor.demo_presence').locator('input').first().check();
  await page.getByRole('link',{name:'Zonendokumentation',exact:true}).click();
  assert.equal(await page.locator('#ps-view-title').innerText(),'Zone bearbeiten');
  await page.evaluate(()=>load({background:true}));
  assert.equal(await light.getByLabel('Habitus Bedienung',{exact:true}).isChecked(),true);
  await page.getByRole('button',{name:'Zone speichern',exact:true}).click();await page.waitForFunction(()=>!zoneFormOpen && !selectionBusy && !zoneSaving);
  const saved=await command({action:'snapshot'});
  assert.equal(saved.mode,before.mode);assert.equal(saved.learning,before.learning);
  assert.deepEqual(saved.roles,before.roles);assert.deepEqual(saved.selections.decisions,before.selections.decisions);
  assert.equal(saved.metadata_calls,before.metadata_calls);
  await page.getByRole('link',{name:'Zonendokumentation',exact:true}).click();await page.locator('#ps-structure-verify').click();
  await page.waitForFunction(()=>document.getElementById('ps-structure-status').textContent==='Abweichungen in der Struktur');
  await page.locator('#ps-structure-sync').click();await page.getByRole('button',{name:'Genau diese Labels abgleichen',exact:true}).waitFor();
  assert.match(await page.locator('#ps-structure-plan').innerText(),/Hinzufügen:/);
  assert.equal((await command({action:'snapshot'})).metadata_calls,before.metadata_calls);
  await page.getByRole('button',{name:'Genau diese Labels abgleichen',exact:true}).click();
  await page.getByRole('button',{name:'Rücknahme vorbereiten',exact:true}).waitFor();
  const applied=await command({action:'snapshot'});assert.equal(applied.metadata_calls,before.metadata_calls+1);
  await page.getByRole('button',{name:'Plan schließen',exact:true}).click();await page.locator('#ps-structure-verify').click();
  await page.waitForFunction(()=>document.getElementById('ps-structure-status').textContent==='Struktur stimmt mit Home Assistant überein');
  const downloadEvent=page.waitForEvent('download');await page.locator('#ps-structure-export').click();const doc=await downloadEvent;
  const exported=JSON.parse(await fs.readFile(await doc.path(),'utf8'));assert.equal(exported.verification.state,'synchronized');
  assert.equal(exported.verification.control_accepted,false);assert.equal(exported.plans[0].state,'verified');
  assert.equal(exported.structure.ha_links.light_group.entity_id,'light.demo');
  assert.equal(exported.verification.ha_links.light_group.status,'bound');
  assert.equal(exported.verification.ha_links_control_accepted,false);
  const directory=process.env.PILOTSUITE_SCREENSHOTS||'/tmp/pilotsuite-structure-review';await fs.mkdir(directory,{recursive:true});
  for(const [width,theme] of [[1440,'light'],[820,'dark'],[390,'light'],[390,'dark']]){
   await page.setViewportSize({width,height:1000});await page.getByLabel('Farbschema').selectOption(theme);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
   await page.evaluate(()=>scrollTo(0,0));
   await page.screenshot({path:path.join(directory,`foundation-documentation-${width}-${theme}.png`),fullPage:true});
  }
  await page.setViewportSize({width:1440,height:1100});await page.getByRole('link',{name:'Habituszonen',exact:true}).click();
  await page.screenshot({path:path.join(directory,'foundation-overview.png'),fullPage:true});
  await openEditor();await page.screenshot({path:path.join(directory,'foundation-editor.png'),fullPage:true});
  await page.locator('#zone-name').fill('Nicht speichern');await page.locator('#zone-cancel').click();
  assert.notEqual((await page.evaluate(()=>zoneDefinitions.find(z=>z.zone_id===selectionZone))).name,'Nicht speichern');
  await command({action:'member_identity',variant:'renamed'});
  await page.getByRole('link',{name:'Zonendokumentation',exact:true}).click();await page.locator('#ps-structure-verify').click();
  await page.waitForFunction(()=>document.getElementById('ps-structure-status').textContent==='Abweichungen in der Struktur');
  assert.match(await page.locator('#ps-structure-body').innerText(),/umbenannt/);
  await page.route('**/structure?verify=1',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({message:'HA vorübergehend nicht erreichbar'})}));
  await page.locator('#ps-structure-verify').click();await page.waitForFunction(()=>document.getElementById('ps-structure-status').textContent==='HA-Prüfung nicht bestätigt');

  await page.unroute('**/structure?verify=1');await command({action:'member_identity',variant:'normal'});
  await page.locator('#zone-new').click();await page.waitForFunction(()=>!zoneLabelBusy && zoneFormOpen);
  await page.locator('#zone-name').fill('Test Neue Zone');await page.locator('#zone-label-name').fill('Test Zonenlabel');
  await page.locator('#zone-extras').selectOption('binary_sensor.demo_motion');
  await page.locator('#zone-label-new').click();await page.locator('#zone-candidates-import').click();
  await page.waitForFunction(()=>!zoneLabelBusy && zoneSetupRows.length===1);
  await member('binary_sensor.demo_motion').locator('summary').click();
  assert.equal(await member('binary_sensor.demo_motion').getByLabel('Habitus Status',{exact:true}).isChecked(),true,'candidate import gets type default');
  assert.equal(await member('binary_sensor.demo_motion').getByLabel('Habitus Zone',{exact:true}).isChecked(),false);
  await member('binary_sensor.demo_motion').getByLabel('Habitus Status',{exact:true}).uncheck();

  await page.getByRole('button',{name:'Zone speichern',exact:true}).click();await page.waitForFunction(()=>!zoneSaving && !zoneFormOpen && !selectionBusy);
  assert.equal(await page.evaluate(()=>zoneDefinitions.find(z=>z.zone_id===selectionZone).enabled),false);
  await openEditor();await member('binary_sensor.demo_motion').locator('summary').click();
  assert.equal(await member('binary_sensor.demo_motion').getByLabel('Habitus Status',{exact:true}).isChecked(),false,'saved empty selection survives reopen');
  await page.locator('#zone-cancel').click();

  await page.getByRole('link',{name:'Zonendokumentation',exact:true}).click();await page.locator('#ps-structure-sync').click();
  await page.getByRole('button',{name:'Genau diese Labels abgleichen',exact:true}).waitFor();
  assert.match(await page.locator('#ps-structure-plan').innerText(),/Zonenlabel anlegen: Test Zonenlabel/);
  await page.route('**/ontology/*/apply',async route=>{await route.fetch();await route.abort();},{times:1});
  await page.getByRole('button',{name:'Genau diese Labels abgleichen',exact:true}).click();
  await page.waitForFunction(()=>document.getElementById('ps-structure-plan').textContent.includes('Antwort offen'));
  assert.equal(await page.getByRole('button',{name:'Genau diese Labels abgleichen',exact:true}).count(),0);
  await page.getByRole('button',{name:'Gespeicherten Planstatus lesen',exact:true}).click();
  await page.getByRole('button',{name:'Rücknahme vorbereiten',exact:true}).waitFor();
  await page.getByRole('button',{name:'Plan schließen',exact:true}).click();await page.locator('#ps-structure-verify').click();
  await page.waitForFunction(()=>document.getElementById('ps-structure-status').textContent==='Struktur stimmt mit Home Assistant überein');
  assert.match(await page.locator('#ps-structure-body').innerText(),/Test Zonenlabel/);
    await page.locator('#ps-structure-body').getByText('Gespeicherte Änderungsbelege',{exact:true}).click();
  await page.locator('#ps-structure-body details button').first().click();
  await page.getByRole('button',{name:'Rücknahme vorbereiten',exact:true}).click();
  await page.getByRole('button',{name:'Genau diese Labels abgleichen',exact:true}).waitFor();
  await page.getByRole('button',{name:'Genau diese Labels abgleichen',exact:true}).click();
  await page.getByRole('button',{name:'Rücknahme vorbereiten',exact:true}).waitFor();
  await page.getByRole('button',{name:'Plan schließen',exact:true}).click();await page.locator('#ps-structure-verify').click();
  await page.waitForFunction(()=>document.getElementById('ps-structure-status').textContent==='Abweichungen in der Struktur');
  assert.equal(await page.evaluate(()=>structureData.plans.some(p=>p.details.restores)),true);
  const final=await command({action:'snapshot'});
  assert.equal(final.label_creates,before.label_creates+1);

  for(const key of ['helper_creates','output_calls','history_reads','automation_reads'])assert.equal(final[key],before[key],key);
  assert.deepEqual(errors,[]);
  console.log('ok - import, preserved decisions/drafts, label preview/apply/readback, documentation, responsive themes and failure states');

 }finally{if(browser)await browser.close();proc.stdin.end();await new Promise(r=>proc.once('exit',r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
