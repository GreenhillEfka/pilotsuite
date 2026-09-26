// Actual application plus synthetic native registry. No household access.
const {chromium}=require(process.env.PILOTSUITE_PLAYWRIGHT||'playwright');
const {spawn}=require('node:child_process');
const {createInterface}=require('node:readline');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs/promises');
(async()=>{
 const root=path.resolve(__dirname,'..');
 const proc=spawn(process.env.PYTHON||'python',['scripts/organization_browser_fixture.py'],{cwd:root,
  env:{...process.env,PYTHONPATH:path.join(root,'pilotsuite')},stdio:['pipe','pipe','pipe']});
 let stderr='',browser;proc.stderr.on('data',d=>stderr=(stderr+d).slice(-12000));
 const lines=createInterface({input:proc.stdout})[Symbol.asyncIterator]();
 async function read(){let timer;try{const r=await Promise.race([lines.next(),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Fixture timeout: '+stderr)),15000);})]);if(r.done)throw Error(stderr);return JSON.parse(r.value);}finally{clearTimeout(timer);}}
 const command=async obj=>{proc.stdin.write(JSON.stringify(obj)+'\n');return read();};
 try{
  const info=await read();browser=await chromium.launch({headless:true,...(process.env.PILOTSUITE_CHROMIUM?{executablePath:process.env.PILOTSUITE_CHROMIUM}:{})});
  const page=await browser.newPage({viewport:{width:1440,height:1000}});page.setDefaultTimeout(10000);
  const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());page.on('request',r=>{if(!['GET','HEAD'].includes(r.method()))requests.push(r.url());});
  await page.goto(info.url);await page.waitForFunction(()=>contextData&&!selectionBusy&&document.body.classList.contains('ps-workspace-ready'));
  await page.locator('.ps-nav [data-ps-nav=config]').click();await page.locator('#org-load').click();
  await page.locator('#org-timing').waitFor();
  let snapshot=await command({action:'snapshot'});assert.equal(snapshot.automation_reads,0);assert.equal(snapshot.name_writes,0);
  const before=structuredClone(snapshot.config);
  const choose=async(role,eid)=>{const details=page.locator(`[data-org-group="${role}"]`);if(!await details.evaluate(e=>e.open))await details.locator('summary').click();await details.locator(`[data-org-role="${role}"][data-org-candidate="${eid}"]`).click();};
  await choose('presence_automations','automation.legacy_presence');
  await page.locator('#org-analyze').click();
  await page.waitForFunction(()=>document.querySelector('#org-reports [data-org-finding="input_number.room_timeout_old"]'));
  assert.match(await page.locator('#org-reports').innerText(),/Bestehender for:/);
  assert.match(await page.locator('#org-reports').innerText(),/Referenz fehlt/);
  assert.doesNotMatch(await page.locator('#org-reports').innerText(),/PRIVATE_ALIAS/);
  await page.locator('[data-org-replacement="input_number.room_timeout_old"]').selectOption('input_number.room_timeout_new');
  await page.getByRole('button',{name:'Gewählte Reparaturstellen prüfen',exact:true}).click();
  await page.waitForFunction(()=>document.getElementById('org-plan').textContent.includes('Reparaturvorschau gespeichert'));
  assert.equal(await page.locator('#org-apply-names').count(),0);
  assert.equal((await command({action:'snapshot'})).name_writes,0);
  console.log('ok 1 - automation-first inspection finds event/template helpers; repair is not silently executed');
  await choose('presence_sources','binary_sensor.room_motion');
  await choose('presence_status','input_boolean.legacy_presence');
  await choose('presence_timer','timer.legacy_wait');
  await choose('presence_duration','input_number.room_timeout_new');
  await page.locator('#org-timing').selectOption('timer');
  const group=page.locator('[data-org-group=presence_timer]');
  await group.locator('input[type=search]').fill('no-match');
  assert.match(await group.innerText(),/timer.legacy_wait/);assert.match(await group.innerText(),/1 gewählt/);
  await page.locator('.ps-nav [data-ps-nav=cockpit]').click();
  assert.equal(await page.locator('#org-timing').isVisible(),true);
  await page.locator('#zone-new').click();assert.equal(await page.evaluate(()=>zoneFormOpen),false);
  snapshot=await command({action:'snapshot'});assert.deepEqual(snapshot.config,before);
  console.log('ok 2 - global manual assignments include area-less helpers and block navigation without losing filtered selections');
  await page.locator('#org-save').click();
  await page.waitForFunction(()=>document.getElementById('org-message').textContent.includes('Funktionszuordnung gespeichert')&&!window.PilotSuiteOrganization.dirty()).catch(async error=>{console.error('save diagnostic',await page.locator('#org-message').innerText(),errors);throw error;});
  await page.locator('#org-timing').waitFor();snapshot=await command({action:'snapshot'});
  assert.equal(snapshot.config.organization.timing,'timer');assert.deepEqual(snapshot.config.roles,before.roles);assert.equal(snapshot.config.learning,before.learning);
  assert.equal(snapshot.name_writes,0);assert.equal(snapshot.helper_calls,0);
  const readsBeforeGlobal=snapshot.automation_reads;
  await page.locator('#org-scan').click();
  await page.waitForFunction(()=>document.getElementById('org-message').textContent.includes('1 von 1 katalogisierten Automationen')&&!window.PilotSuiteOrganization.dirty());
  assert.equal((await command({action:'snapshot'})).automation_reads,readsBeforeGlobal+1);
  assert.equal(await page.locator('#org-scan').isDisabled(),true);
  await page.locator('#org-naming>summary').click();
  await page.locator('[data-org-name-role=presence_status]').check();
  await page.locator('[data-org-name-role=presence_timer]').check();
  await page.locator('#org-name-preview').click();await page.locator('#org-confirm-names').waitFor();
  assert.equal((await command({action:'snapshot'})).name_writes,0);
  assert.equal(await page.locator('#org-apply-names').isDisabled(),true);
  await page.locator('#org-confirm-names').check();await page.locator('#org-apply-names').click();
  await page.waitForFunction(()=>document.getElementById('org-plan').textContent.includes('Änderung zurückgelesen'));
  snapshot=await command({action:'snapshot'});assert.equal(snapshot.name_writes,2);
  assert.equal(snapshot.names['timer.legacy_wait'],'room · Nachlauftimer');assert.equal(snapshot.control_calls,0);
  console.log('ok 3 - persistent mapping and explicit confirmed metadata-only name cleanup with independent read-back');
  await page.getByRole('button',{name:'Gespeicherten Planstatus laden',exact:true}).click();
  await page.waitForFunction(()=>!window.PilotSuiteOrganization.dirty());assert.equal((await command({action:'snapshot'})).name_writes,2);
  await page.getByRole('button',{name:'Rücknahme prüfen',exact:true}).click();await page.locator('#org-confirm-names').waitFor();
  assert.equal((await command({action:'snapshot'})).name_writes,2);
  await page.locator('#org-confirm-names').check();await page.locator('#org-apply-names').click();
  await page.waitForFunction(()=>document.getElementById('org-plan').textContent.includes('Änderung zurückgelesen'));
  snapshot=await command({action:'snapshot'});assert.equal(snapshot.names['timer.legacy_wait'],'Legacy wait');assert.equal(snapshot.name_writes,4);
  console.log('ok 4 - status reload does not replay writes; rollback is a separately confirmed new plan');
  await page.reload();await page.waitForFunction(()=>contextData&&!selectionBusy&&document.body.classList.contains('ps-workspace-ready'));
  await page.locator('#org-load').click();await page.locator('#org-timing').waitFor();assert.equal(await page.locator('#org-timing').inputValue(),'timer');
  assert.match(await page.locator('[data-org-group=presence_status]').innerText(),/input_boolean.legacy_presence/);
  const prefs=await page.evaluate(()=>JSON.stringify(localStorage));assert.doesNotMatch(prefs,/legacy_presence|presence-stable/);
  for(const width of [390,768,1440]){
   await page.setViewportSize({width,height:1000});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`organization overflow ${width}`);
   if(process.env.PILOTSUITE_SCREENSHOTS){await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS,{recursive:true});await page.screenshot({path:path.join(process.env.PILOTSUITE_SCREENSHOTS,`organization-${width}.png`),fullPage:true});}
  }
  await choose('manual_override','input_boolean.room_override');
  await command({action:'touch_revision'});
  await page.locator('#org-save').click();
  await page.waitForFunction(()=>document.getElementById('org-message').textContent.includes('geändert'));
  assert.match(await page.locator('[data-org-group=manual_override]').innerText(),/input_boolean.room_override/);
  assert.equal((await command({action:'snapshot'})).name_writes,4);
  assert.equal(requests.some(u=>u.includes('presence-runtime')||u.includes('helpers/provision')),false);assert.deepEqual(errors,[]);
  console.log('ok 5 - reload persistence, local-cache privacy, responsive UI, stale revision preserves draft and no control activation');
 }finally{if(browser)await browser.close();proc.stdin.end();proc.kill('SIGTERM');}
})().catch(error=>{console.error(error);process.exitCode=1;});
