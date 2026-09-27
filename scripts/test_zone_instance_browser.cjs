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
  await page.clock.install({time:new Date(info.now*1000)});await page.goto(info.url);
  await page.evaluate(async()=>{await load();});
  await page.locator('[data-ps-module="presence"]').click();await page.locator('.ps-nav [data-ps-nav="zone"]').click();await page.locator('#ps-zone-configure:not([disabled])').waitFor();
  assert.deepEqual(errors,[]);const baseline=await command({action:'snapshot'});assert.equal(baseline.learning,false);assert.equal(baseline.view.current.state,'occupied');
  assert.equal(baseline.helper_creates,0);assert.equal(baseline.output_calls,0);
  await page.locator('#ps-zone-configure').click();await page.locator('#ps-zone-form').waitFor();
  await page.locator('.ps-nav [data-ps-nav="cockpit"]').click();assert.equal(await page.locator('#ps-zone-form').isVisible(),true);
  await page.getByRole('button',{name:'Konfiguration speichern',exact:true}).click();
  await page.locator('#ps-zone-form').waitFor({state:'hidden'});await page.locator('#ps-zone-configure:not([disabled])').waitFor();
  assert.equal((await command({action:'snapshot'})).mode,'compare');console.log('ok 1 - relevance-based presence, typed configuration, no extra grant, dirty guard');
  await page.getByRole('button',{name:'Sensordaten & Verläufe',exact:true}).click();
  try{await page.locator('.ps-zone-chart').first().waitFor();}catch(e){throw Error('Historienansicht blieb leer: '+await page.locator('#ps-zone-presence .ps-notice').first().textContent()+' / '+e.message);}assert.equal(await page.locator('.ps-zone-chart').count()>0,true);
  assert.equal((await command({action:'snapshot'})).history_reads,1);
  const out=process.env.PILOTSUITE_SCREENSHOTS;if(out)await fs.mkdir(out,{recursive:true});
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
  await page.locator('#refresh').click();await page.locator('#ps-zone-configure:not([disabled])').waitFor();
  console.log('ok 3 - reviewed owned output package creates only on explicit click, publishing remains off');
  await page.getByRole('button',{name:'Entitäten → Ontologie',exact:true}).click();
  await page.getByLabel('Anzeigename',{exact:true}).fill('Demo · Präsenz');await page.getByLabel('Logische Zonenmitgliedschaft',{exact:true}).selectOption('zone');await page.getByLabel('Habitus Übersicht',{exact:true}).check();
  await page.getByRole('button',{name:'Änderungsplan prüfen',exact:true}).click();await page.getByRole('button',{name:'Genau diesen Plan anwenden',exact:true}).click();
  await page.getByText('Planstatus: verified',{exact:true}).waitFor();assert.equal((await command({action:'snapshot'})).metadata_calls,created.metadata_calls+1);
  await page.getByRole('button',{name:'Rücknahme prüfen',exact:true}).click();await page.getByRole('button',{name:'Genau diesen Plan anwenden',exact:true}).click();
  await page.getByText('Planstatus: verified',{exact:true}).waitFor();assert.equal((await command({action:'snapshot'})).metadata_calls,created.metadata_calls+2);
  await page.getByRole('button',{name:'Schließen',exact:true}).last().click();
  console.log('ok 4 - name/ontology preview, exact apply and explicit rollback');
  for(const width of [390,768,1440]){await page.setViewportSize({width,height:1100});for(const theme of ['dark','light']){
   await page.locator('.ps-nav [data-ps-nav="system"]').click();await page.locator('#ps-theme').selectOption(theme);await page.locator('.ps-nav [data-ps-nav="zone"]').click();
   await page.locator('#ps-zone-configure:not([disabled])').waitFor();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'overflow '+width);
   if(out)await page.screenshot({path:path.join(out,`zone-instance-${theme}-${width}.png`),fullPage:true});
  }}
  const final=await command({action:'snapshot'});assert.equal(final.learning,false);assert.deepEqual(final.roles,baseline.roles);assert.deepEqual(errors,[]);
  assert.equal(network.some(r=>/presence-runtime|transactions\/.+\/apply|history\/import/.test(r.url)),false);
  console.log('ok 5 - themes, three widths, no legacy grants and no household calls');
 }finally{if(browser)await browser.close();proc.stdin.end();proc.kill('SIGTERM');}
})().catch(e=>{console.error(e);process.exitCode=1;});
