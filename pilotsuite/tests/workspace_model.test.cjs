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
