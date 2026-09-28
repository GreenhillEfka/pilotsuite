const test=require('node:test'),assert=require('node:assert/strict');
const M=require('../pilotsuite/web/zone-presence-model.js');
test('canonical current state is the only presence truth; missing never means vacant',()=>{
 const data={analysis_enabled:true,mode:'compare',current:{state:'occupied',explanation:'Signal aktiv'}};
 assert.equal(M.summary(data).state,'Belegt');
 assert.equal(M.summary({...data,current:{state:'grace'}}).state,'Nachlauf');
 assert.equal(M.summary({...data,current:{state:'vacant'}}).state,'Frei');
 for(const current of [null,{state:'unknown'},{state:'unavailable'},{state:'new_state'}]){
  assert.equal(M.summary({...data,current}).state,'Unklar');
 }
 assert.equal(M.summary(null).state,'Unklar');
 assert.equal(M.summary({...data,analysis_enabled:false}).state,'Pausiert');
 assert.equal(M.summary({...data,mode:'paused'}).state,'Pausiert');
});
test('publication is distinct from calculation and cannot be claimed without a package',()=>{
 const data={analysis_enabled:true,mode:'publish',current:{state:'occupied',valid:true},publication:'verified',publication_checked_at:100};
 assert.equal(M.summary(data).publication,'Nicht eingerichtet');
 const packageData={...data,package:{entities:{sensor:'binary_sensor.demo'}}};
 assert.equal(M.summary(packageData).publication,'Zuletzt bestätigt');
 assert.equal(M.summary(packageData).publicationCheckedAt,100);
 assert.equal(M.summary({...packageData,current:null}).publication,'Nicht bestätigt','an expired current view cannot confirm cached publication');
 for(const publication of ['not_published','unknown_or_conflict','suspended_after_unknown_outcome','unexpected']){
  assert.equal(M.summary({...packageData,publication}).publication,'Nicht bestätigt');
 }
 assert.equal(M.summary({...packageData,mode:'compare'}).publication,'Nur vergleichen');
 assert.equal(M.summary({...packageData,mode:'paused'}).publication,'Pausiert');
 assert.equal(M.summary({...packageData,analysis_enabled:false}).publication,'Pausiert');
});
test('a publication label needs an explicit dated readback and valid presence',()=>{
 const data={analysis_enabled:true,mode:'publish',package:{entities:{sensor:'binary_sensor.demo'}},
  current:{state:'occupied',valid:true},publication:'verified',publication_checked_at:100};
 for(const publication_checked_at of [undefined,null,NaN,Infinity,'100',true,0,-1]){
  const result=M.summary({...data,publication_checked_at});
  assert.equal(result.publication,'Nicht bestätigt');assert.equal(result.publicationCheckedAt,null);
 }
 for(const current of [null,{state:'unknown',valid:false},{state:'vacant',valid:false},{state:'occupied'}]){
  const result=M.summary({...data,current});
  assert.equal(result.publication,'Nicht bestätigt');assert.equal(result.publicationCheckedAt,null);
 }
});
test('numeric unknown values split curves, zero remains a measurement',()=>{
 const p=M.plot({kind:'numeric',points:[[0,0],[1,5],[2,null],[3,0]]},0,4);
 assert.equal(p.segments.length,2);assert.equal(p.segments[0][0].value,0);assert.equal(p.segments[1][0].value,0);
});
test('categorical idle and paused are not collapsed into off',()=>{
 const p=M.plot({kind:'state',points:[[0,'off'],[1,'playing'],[2,'paused'],[3,'idle']]},0,4);
 assert.equal(new Set(p.segments[0].map(p=>p.y)).size,4);assert.equal(p.labels.length,4);
});
test('nonfinite, unavailable and malformed values do not acquire numeric zero',()=>{
 const p=M.plot({kind:'numeric',points:[[0,NaN],[1,'unavailable'],[2,Infinity],[3,null]]},0,4);
 assert.equal(p.error,'no_values');assert.equal(p.segments.length,0);
});
test('unit conflicts are not placed on a shared numerical axis',()=>{
 assert.equal(M.plot({kind:'numeric',unit_conflict:true,points:[[0,5]]},0,1).error,'unit_conflict');
});
test('invalid periods, reversed and nonfinite timestamps are refused',()=>{
 assert.equal(M.plot({},3,1).error,'invalid_window');assert.equal(M.plot({},0,Infinity).error,'invalid_window');
});
test('single measured value remains a point, not fabricated window duration',()=>{
 const p=M.plot({kind:'numeric',points:[[5,4]]},0,10);assert.equal(p.segments[0].length,1);assert.equal(p.segments[0][0].at,5);
});
test('series values outside the requested period are ignored',()=>{
 const p=M.plot({kind:'numeric',points:[[-1,8],[5,2],[99,200]]},0,10);assert.equal(p.labels[0].value,2);
});
test('source data are not mutated by presentation sorting',()=>{
 const input={kind:'numeric',points:[[8,3],[2,5]]},copy=JSON.stringify(input);M.plot(input,0,10);assert.equal(JSON.stringify(input),copy);
});
