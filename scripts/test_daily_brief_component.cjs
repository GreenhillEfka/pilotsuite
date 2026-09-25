// Component tests with real canonical-owner projections, no browser network.
// Actual app functions and SelectionDraft; surrounding renderers are explicit stubs.
const {chromium}=require(process.env.PILOTSUITE_PLAYWRIGHT || 'playwright');
const {spawn}=require('node:child_process');
const {createInterface}=require('node:readline');
const path=require('node:path');
const fs=require('node:fs/promises');
const assert=require('node:assert/strict');
function bounded(promise,label,ms=15000){let timer;return Promise.race([promise,
  new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error(label+' timed out')),ms);})]).finally(()=>clearTimeout(timer));}
(async()=>{
  const root=path.resolve(__dirname,'..');
  const fixture=spawn(process.env.PYTHON || 'python',['scripts/daily_brief_browser_fixture.py','--stdio-only'],{
    cwd:root,env:{...process.env,PYTHONPATH:path.join(root,'pilotsuite')},stdio:['pipe','pipe','pipe']});
  let stderr='';fixture.stderr.on('data',d=>{stderr=(stderr+d).slice(-12000);});
  const lines=createInterface({input:fixture.stdout})[Symbol.asyncIterator]();
  const read=async()=>{const item=await bounded(lines.next(),'Fixture response');if(item.done)throw new Error(stderr);return JSON.parse(item.value);};
  const command=async data=>{fixture.stdin.write(JSON.stringify(data)+'\n');return read();};
  let browser,checks=0;
  const ok=label=>console.log(`ok ${++checks} - ${label}`);
  try{
    await read();const value=await command({action:'projection'});
    const before=await command({action:'snapshot'});
    const app=await fs.readFile(path.join(root,'pilotsuite/pilotsuite/web/app.js'),'utf8');
    const selections=await fs.readFile(path.join(root,'pilotsuite/pilotsuite/web/selections.js'),'utf8');
    const from=app.indexOf('async function loadContext()'),to=app.indexOf('function renderLearning()');
    assert.ok(from>=0 && to>from,'actual source functions must exist');
    browser=await chromium.launch({headless:true,...(process.env.PILOTSUITE_CHROMIUM?{executablePath:process.env.PILOTSUITE_CHROMIUM}:{})});
    const page=await browser.newPage({viewport:{width:390,height:844}});
    const network=[],errors=[];page.on('request',r=>network.push(r.url()));page.on('pageerror',e=>errors.push(e.message));
    await page.setContent('<!doctype html><html lang="de"><meta charset="utf-8"><style>body{font:16px system-ui;margin:16px}p{overflow-wrap:anywhere}h1{font-size:1.25rem;overflow-wrap:anywhere}</style><h1>Synthetische Komponentenprüfung</h1><div id="daily-brief"></div><div id="selection-message"></div><details id="pattern-workbench"><summary>Werkbank-Testziel</summary></details><input id="outside" value="Ungespeicherter Text"></html>');
    const prelude=`${selections}\nlet selectionZone='a',contextGeneration=0;
      const byId=id=>document.getElementById(id);
      let contextData=${JSON.stringify(value.report)};
      let selectionDraft=new SelectionDraft(${JSON.stringify(value.inventory)});
      const pending=[];
      function json(){return new Promise((resolve,reject)=>pending.push({resolve,reject}));}
      const text=(id,value)=>{byId(id).textContent=value;};
      function renderSelection(){} function renderZoneView(){}
      function renderLearning(){renderDailyBrief();}
      function begin(){window.latest=loadContext().catch(()=>false);}`;
    await page.addScriptTag({content:prelude+app.slice(from,to)+app.slice(app.indexOf('function selectionChanged()'),app.indexOf('async function loadSelection('))+'\nrenderDailyBrief();'});
    const brief=page.locator('#daily-brief'),link=brief.locator('a');
    assert.equal(await link.count(),1);assert.match(await brief.textContent(),/12 Aktivierungen an 6 Tagen/);
    ok('actual ContextStore projection renders');
    const resolve=async data=>{
      await page.evaluate(data=>{pending.shift().resolve(data);},data);
      await page.evaluate(()=>window.latest);
    };
    const refresh=async()=>{await page.evaluate(()=>begin());await resolve((await command({action:'projection'})).report);};
    await brief.locator('summary').click();await brief.locator('summary').focus();
    await page.evaluate(()=>begin());
    assert.equal(await link.count(),0);
    await resolve((await command({action:'projection'})).report);
    assert.equal(await brief.locator('details').getAttribute('open'),'');
    assert.equal(await page.evaluate(()=>document.activeElement.textContent),'Grundlage und Grenzen');
    ok('reload hides candidate while preserving equal-content expansion and focus after response');
    await link.focus();await page.evaluate(()=>begin());await page.locator('#outside').focus();
    await resolve((await command({action:'projection'})).report);
    assert.equal(await page.evaluate(()=>document.activeElement.id),'outside');
    ok('completed request does not steal focus from user input');
    await link.focus();await refresh();assert.equal(await page.evaluate(()=>document.activeElement.dataset.patternId),value.report.daily_brief.candidate.pattern_id);
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(()=>document.activeElement.id),'pattern-workbench');
    assert.equal(await page.locator('#pattern-workbench').getAttribute('open'),'');
    assert.deepEqual(before,await command({action:'snapshot'}));
    ok('restored candidate binds the new context and navigates without mutation');
    await page.evaluate(()=>{begin();pending.shift().reject(new Error('synthetic failure'));});await page.evaluate(()=>window.latest);
    await page.evaluate(()=>renderDailyBrief());assert.equal(await link.count(),0);await refresh();assert.equal(await link.count(),1);
    ok('failed read never resurrects the old candidate');
    await page.evaluate(()=>{selectionDraft.set('light.synthetic','ignored');selectionChanged();});assert.equal(await link.count(),0);
    assert.equal(await page.evaluate(()=>selectionDraft.dirty),true);
    await page.evaluate(()=>selectionDraft.set('light.synthetic','relevant'));await refresh();assert.equal(await link.count(),1);
    assert.equal(await page.locator('#outside').inputValue(),'Ungespeicherter Text');
    assert.deepEqual(before,await command({action:'snapshot'}));
    ok('unsaved selection and text are preserved, not implicitly saved');
    await command({action:'feedback',decision:'rejected'});await refresh();assert.equal(await link.count(),0);assert.match(await brief.textContent(),/1 abgelehnt/);
    await command({action:'feedback',decision:'later'});await refresh();assert.match(await brief.textContent(),/1 vertagt/);
    await command({action:'feedback',decision:'accepted'});await refresh();assert.equal(await link.count(),1);
    ok('real preference projections exclude rejected and deferred patterns');
    await command({action:'connection',ready:false});await refresh();assert.equal(await link.count(),0);assert.match(await brief.textContent(),/Verbindung/);
    await command({action:'connection',ready:true});await refresh();assert.equal(await link.count(),1);
    ok('disconnected projection withholds and fresh recovered projection restores');
    const foreign=await command({action:'projection',zone_id:'b'});
    await page.evaluate(v=>{selectionZone='b';selectionDraft=new SelectionDraft(v.inventory);contextData=v.report;renderDailyBrief();},foreign);
    assert.equal(await link.count(),0);assert.ok(!(await brief.textContent()).includes('12 Aktivierungen'));
    const current=await command({action:'projection'});
    await page.evaluate(v=>{selectionZone='a';selectionDraft=new SelectionDraft(v.inventory);contextData=v.report;renderDailyBrief();},current);
    assert.equal(await link.count(),1);
    ok('real second-zone response never inherits the first zone candidate');
    for(const width of [390,1440]){
      await page.setViewportSize({width,height:844});
      const layout=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,
        overflowing:[...document.querySelectorAll('body *')].map(el=>({tag:el.tagName,id:el.id,
          text:el.textContent.slice(0,80),left:el.getBoundingClientRect().left,right:el.getBoundingClientRect().right,
          scroll:el.scrollWidth,client:el.clientWidth})).filter(el=>el.right>innerWidth+1 || el.left<0 || el.scroll>el.client+1)}));
      assert.ok(layout.scroll<=layout.width+1,'Horizontal overflow: '+JSON.stringify(layout));
      if(process.env.PILOTSUITE_SCREENSHOTS){await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS,{recursive:true});await page.screenshot({path:path.join(process.env.PILOTSUITE_SCREENSHOTS,`daily-brief-component-${width}.png`),fullPage:true});}
    }
    assert.deepEqual(network,[]);assert.deepEqual(errors,[]);
    ok('responsive component with zero browser network requests and zero script errors');
    console.log(`Daily brief component: ${checks} checks passed; NOT full-shell or live acceptance`);
  }finally{
    if(browser)await browser.close();fixture.stdin.end();
    try{const exit=await bounded(new Promise(resolve=>{if(fixture.exitCode!==null)return resolve(fixture.exitCode);fixture.once('exit',resolve);}), 'cleanup',5000);if(exit!==0)throw new Error(stderr);}
    catch(e){fixture.kill('SIGTERM');throw e;}
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
