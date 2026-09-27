const test=require('node:test');
const assert=require('node:assert/strict');
const M=require('../pilotsuite/web/workspace-model.js');
test('workspace preferences persist presentation only and reject unknown values',()=>{
  assert.deepEqual(M.preferences({view:'raw',theme:'injected',density:'no',ids:1,token:'NO'}),{view:'cockpit',theme:'auto',density:'comfortable',ids:false});
  assert.deepEqual(Object.keys(M.preferences({household:'NO'})).sort(),['density','ids','theme','view']);
  assert.equal(M.preferences({view:'all',theme:'dark',density:'compact',ids:true}).view,'all');
});
test('workspace never substitutes unknown measurements with zero',()=>{
  for(const value of [null,undefined,'0',NaN,Infinity])assert.equal(M.number(value),'—');
  assert.equal(M.metric({temperature:{status:'unavailable',value:0}},'temperature'),'—');
  assert.equal(M.metric({temperature:{status:'available',value:0,unit:'°C'}},'temperature'),'0 °C');
  assert.equal(M.metric({presence:{status:'available',on:0,total:2}},'presence'),'0 / 2 aktiv');
});
test('workspace requires same zone and revision for source visualization',()=>{
  const inv={zone_id:'a',revision:4},ctx={revision:4,foundation:{zone_id:'a',revision:4}};
  assert.equal(M.current(ctx,inv,'a'),true);
  for(const bad of [{...ctx,revision:3},{...ctx,foundation:{zone_id:'b',revision:4}},null])assert.equal(M.current(bad,inv,'a'),false);
  assert.equal(M.current(ctx,{...inv,revision:true},'a'),false);
});
test('configuration diff is deterministic and does not mutate canonical inputs',()=>{
 const before={roles:{presence:['binary_sensor.b','binary_sensor.a']},learning:false};
 const after={roles:{presence:['binary_sensor.a','binary_sensor.b']},learning:false};
 const snap=JSON.stringify(before);assert.deepEqual(M.diff(before,after),[]);assert.equal(JSON.stringify(before),snap);
 after.roles.presence=['binary_sensor.b'];after.learning=true;
 const rows=M.diff(before,after);assert.deepEqual(rows.map(x=>x.kind),['sources','consent']);assert.equal(rows[1].after,'An');
});
test('algorithm parameters and context consent have separate diff rows',()=>{
 const rows=M.diff({roles:{},detector:{}},{roles:{},detector:{min_events:8,timezone:'Europe/Berlin'},context_learning:true});
 assert.deepEqual(rows.map(x=>x.key),['context_learning','min_events','timezone']);
});
test('effective roles expose derived choices without saving or replacing explicit empty groups',()=>{
 const ctx={config:{roles:{humidity:[]}},effective_roles:{temperature:['sensor.t'],humidity:['sensor.h']}};
 const original=JSON.stringify(ctx), resolved=M.effectiveRoles(ctx);
 assert.deepEqual(resolved,{temperature:['sensor.t'],humidity:[]});
 assert.equal(M.roleOrigin(ctx,'temperature'),'derived');assert.equal(M.roleOrigin(ctx,'humidity'),'manual');
 resolved.temperature.push('sensor.other');assert.equal(JSON.stringify(ctx),original);
 assert.deepEqual(M.effectiveRoles(null),{});
});
test('saving another setting does not silently persist derived roles',()=>{
 const ctx={config:{roles:{humidity:[]}},effective_roles:{temperature:['sensor.t'],humidity:[]}};
 const selected={temperature:['sensor.t'],humidity:[]};
 assert.deepEqual(M.rolesForSave(ctx,selected),{humidity:[]});
 assert.deepEqual(M.rolesForSave(ctx,selected,['temperature']),{humidity:[],temperature:['sensor.t']});
 const result=M.rolesForSave(ctx,{temperature:['sensor.z','sensor.z',null]},['temperature']);
 assert.deepEqual(result,{humidity:[],temperature:['sensor.z']});
 assert.deepEqual(M.rolesForSave(null,null,'temperature'),{});
});
test('comparison temperature is separate and delta requires valid same-unit independent values',()=>{
 const s={temperature:{value:22,status:'available',unit:'°C',sources:['sensor.inside']},
  reference_temperature:[{source:'sensor.outside',value:10,quality:'good',unit:'°C'}]};
 assert.deepEqual(M.temperatureComparison(s,'sensor.outside'),{value:10,unit:'°C',delta:12});
 assert.deepEqual(M.temperatureComparison(s,'sensor.missing'),{value:null,unit:null,delta:null});
 for(const change of [{status:'partial'},{unit:'°F'},{value:NaN},{sources:['sensor.outside']}]){
  assert.equal(M.temperatureComparison({...s,temperature:{...s.temperature,...change}},'sensor.outside').delta,null);
 }
 for(const value of [null,'10',Infinity,NaN]){
  assert.equal(M.temperatureComparison({...s,reference_temperature:[{...s.reference_temperature[0],value}]},'sensor.outside').value,null);
 }
 assert.equal(M.temperatureComparison({...s,reference_temperature:[{...s.reference_temperature[0],value:0}]},'sensor.outside').value,0);
 assert.equal(M.temperatureComparison(null,'sensor.outside').delta,null);
});
test('retained integrity warning counts only bounded known row groups',()=>{
 assert.deepEqual(M.retainedIntegrity({status:'ok',excluded_rows:{activity_evidence:3}}),{degraded:false,affected:3});
 assert.deepEqual(M.retainedIntegrity({status:'degraded',excluded_rows:{activity_evidence:2,private:99},normalized_rows:{activity_context:1}}),{degraded:true,affected:3});
 assert.deepEqual(M.retainedIntegrity({status:'degraded',excluded_rows:{activity_evidence:-1,history_imports:'4'},normalized_rows:{coverage_checks:NaN}}),{degraded:false,affected:0});
 assert.deepEqual(M.retainedIntegrity(null),{degraded:false,affected:0});
});
