// Shared appearance controller, DOM test doubles only: not a browser/visual acceptance.
const test=require('node:test');const assert=require('node:assert/strict');const vm=require('node:vm');const fs=require('node:fs');const path=require('node:path');
const model=require('../pilotsuite/web/workspace-model.js');
function fixture(initial){
 const source=fs.readFileSync(path.join(__dirname,'../pilotsuite/web/appearance.js'),'utf8');
 const dataset={},controls={},stored=new Map([['pilotsuite.workspace.v1',JSON.stringify(initial)]]);
 for(const id of ['maintenance-theme','maintenance-density','maintenance-message'])controls[id]={value:'',textContent:'',listeners:{},addEventListener(name,fn){this.listeners[name]=fn;}};
 const media={matches:false,listeners:{},addEventListener(name,fn){this.listeners[name]=fn;}},events={};
 const window={PilotSuiteWorkspaceModel:model,matchMedia:()=>media,addEventListener(name,fn){events[name]=fn;}};
 const storage={getItem:key=>stored.get(key),setItem:(key,val)=>stored.set(key,val)};
 vm.runInNewContext(source,{window,document:{documentElement:{dataset},getElementById:id=>controls[id]},localStorage:storage});
 return {dataset,controls,stored,storage,media,events};
}
test('maintenance uses the same validated theme and density preferences',()=>{
 const f=fixture({theme:'dark',density:'compact',view:'config',ids:true,token:'SHOULD_NOT_PERSIST'});
 assert.equal(f.dataset.psTheme,'dark');assert.equal(f.dataset.psDensity,'compact');
 f.controls['maintenance-theme'].value='light';f.controls['maintenance-theme'].listeners.change();
 const saved=JSON.parse(f.stored.get('pilotsuite.workspace.v1'));
 assert.deepEqual(saved,{theme:'light',density:'compact',view:'config',ids:true});assert.equal(f.dataset.psTheme,'light');
});
test('system theme follows OS and storage changes without household I/O',()=>{
 const f=fixture({theme:'auto'});assert.equal(f.dataset.psTheme,'light');f.media.matches=true;f.media.listeners.change();assert.equal(f.dataset.psTheme,'dark');
 f.events.storage({key:'pilotsuite.workspace.v1',newValue:JSON.stringify({theme:'light',density:'compact'})});assert.equal(f.dataset.psTheme,'light');assert.equal(f.dataset.psDensity,'compact');
});
test('unavailable local storage keeps controls usable and reports session-only appearance',()=>{
 const f=fixture({theme:'dark'});f.storage.setItem=()=>{throw Error('storage denied');};
 f.controls['maintenance-density'].value='compact';f.controls['maintenance-density'].listeners.change();
 assert.equal(f.dataset.psDensity,'compact');assert.match(f.controls['maintenance-message'].textContent,/nur für diese Sitzung/);
});
