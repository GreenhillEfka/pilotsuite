// Real application with disposable synthetic data. No household credentials or control.
const {chromium}=require(process.env.PILOTSUITE_PLAYWRIGHT||'playwright');
const {spawn}=require('node:child_process'),{createInterface}=require('node:readline');
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path');
(async()=>{
 const root=path.resolve(__dirname,'..'),proc=spawn(process.env.PYTHON||'python',['scripts/shadow_browser_fixture.py'],{cwd:root,env:{...process.env,PYTHONPATH:path.join(root,'pilotsuite')},stdio:['pipe','pipe','pipe']});
 let stderr='',browser;proc.stderr.on('data',d=>stderr=(stderr+d).slice(-8000));const lines=createInterface({input:proc.stdout})[Symbol.asyncIterator]();
 async function read(){let timer;try{const r=await Promise.race([lines.next(),new Promise((_,reject)=>timer=setTimeout(()=>reject(Error(stderr||'Fixture timeout')),15000))]);if(r.done)throw Error(stderr);return JSON.parse(r.value);}finally{clearTimeout(timer);}}
 const command=async c=>{proc.stdin.write(JSON.stringify(c)+'\n');return read();};
 try{
  const info=await read();browser=await chromium.launch({headless:true,...(process.env.PILOTSUITE_CHROMIUM?{executablePath:process.env.PILOTSUITE_CHROMIUM}:{})});
  const page=await browser.newPage({viewport:{width:1440,height:1100}});page.setDefaultTimeout(12000);const errors=[],posts=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());page.on('request',r=>{if(r.method()==='POST')posts.push(r.url());});
  await page.goto(info.url);await page.waitForFunction(()=>document.body.classList.contains('ps-workspace-ready')&&contextData&&!selectionBusy);
  await page.locator('#ps-zone-diagnostics > summary').click();
  await page.locator('#ps-shadow-configure:not([disabled])').waitFor();const baseline=await command({action:'snapshot'});
  assert.equal(baseline.view.state,'disabled');assert.equal(posts.length,0);
  await page.locator('#ps-shadow-configure').click();await page.locator('#ps-shadow-grace').fill('30');
  await page.locator('#ps-shadow-lux').selectOption('sensor.demo_lux');await page.locator('#ps-shadow-outdoor').check();
  await page.locator('.ps-nav [data-ps-nav="cockpit"]').click();assert.equal(await page.locator('#ps-shadow-form').isVisible(),true);
  assert.match(await page.locator('#ps-notice').innerText(),/speichern oder abbrechen/);
  await page.locator('#ps-shadow-start').click();
  await page.waitForFunction(()=>document.getElementById('ps-shadow-form').hidden&&!selectionBusy&&!window.PilotSuiteShadow.dirty());
  await page.locator('#ps-shadow-refresh').click();await page.waitForFunction(()=>document.getElementById('ps-shadow-message').textContent.includes('aktiv'));
  assert.equal((await command({action:'snapshot'})).view.state,'running');console.log('ok 1 - explicit configuration starts a persistent no-actuation shadow session; dirty guard works');
  const refresh=async()=>{await page.locator('#ps-shadow-refresh').click();};
  await command({action:'tick',values:{'binary_sensor.demo_presence':'on'}});await refresh();
  await page.waitForFunction(()=>document.getElementById('ps-shadow-result').textContent.includes('Abweichung prüfen'));
  await command({action:'tick',seconds:31});await refresh();
  await page.waitForFunction(()=>document.getElementById('ps-shadow-result').textContent.includes('15 %'));
  const out=process.env.PILOTSUITE_SCREENSHOTS;if(out)await fs.mkdir(out,{recursive:true});
  for(const width of [390,1440]){await page.setViewportSize({width,height:1100});for(const theme of ['light','dark']){
   await page.locator('.ps-nav [data-ps-nav="system"]').click();await page.locator('#ps-theme').selectOption(theme);await page.locator('.ps-nav [data-ps-nav="cockpit"]').click();await page.locator('[data-ps-nav="zone"]').click();
   await page.locator('#ps-shadow-panel').scrollIntoViewIfNeeded();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   if(out)await page.screenshot({path:path.join(out,`presence-shadow-${theme}-${width}.png`),fullPage:true});
  }}
  console.log('ok 2 - real observations produce explicit status disagreement and bounded light proposals in both themes');
  const grace=await command({action:'tick',values:{'binary_sensor.demo_presence':'off'}});const deadline=grace.view.current.computed.deadline;
  await page.reload();await page.locator('#ps-zone-diagnostics > summary').click();await page.locator('#ps-shadow-configure:not([disabled])').waitFor();
  assert.equal((await command({action:'snapshot'})).view.current.computed.deadline,deadline);
  await command({action:'tick',seconds:31});await refresh();
  await page.waitForFunction(()=>document.getElementById('ps-shadow-result').textContent.includes('Gleiche Aussage'));
  await command({action:'replace_source'});await refresh();
  await page.waitForFunction(()=>document.getElementById('ps-shadow-message').textContent.includes('erneute')||document.getElementById('ps-shadow-message').textContent.includes('Erneute'));
  await page.locator('#ps-shadow-stop').click();await page.waitForFunction(()=>document.getElementById('ps-shadow-message').textContent.includes('ist aus'));
  const end=await command({action:'snapshot'});assert.equal(end.writes,0);assert.equal(end.history_reads,0);assert.deepEqual(end.roles,baseline.roles);assert.equal(end.learning,baseline.learning);assert.equal(end.view.state,'disabled');
  assert.equal(posts.some(url=>/presence-runtime|helpers\/provision|transactions\/.+\/apply/.test(url)),false);assert.deepEqual(errors,[]);
  console.log('ok 3 - reload, deadline, identity suspension and stop preserve roles/consent and make zero HA writes or history reads');
 }finally{if(browser)await browser.close();proc.stdin.end();proc.kill('SIGTERM');}
})().catch(e=>{console.error(e);process.exitCode=1;});
