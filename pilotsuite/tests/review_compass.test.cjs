const {test}=require('node:test');
const assert=require('node:assert/strict');
const {project,nextStep,selectRows,validStep}=require('../pilotsuite/web/review_compass.js');
const fixture=require('./fixtures/review_compass.json');
const time=Date.parse(fixture.comparison.checked_at);
const clone=()=>structuredClone(fixture);
const run=(d,r=null,now=time+1000)=>project(d,'z',3,r,now);

test('canonical baseline preserves five independent checks and one navigation step',()=>{
  const {draft}=clone(),p=run(draft);
  assert.deepEqual(p.checks.map(c=>c.id),['sources','evidence','intent','automations','notes']);
  assert.equal(p.next_step.id,'compare_automations');assert.equal(p.execution.allowed,false);
});
test('matching selected read enriches navigation but grants no permission',()=>{
  const {draft,comparison}=clone(),p=run(draft,comparison);
  assert.equal(p.checks[3].state,'last_read');assert.equal(p.next_step.id,'write_note');
  assert.deepEqual(p.execution,{allowed:false,reason:'navigation_only',actions:[]});
});
test('new source/evidence/intent descriptions always come from the latest GET',()=>{
  const {draft,comparison}=clone();draft.review_compass.checks[1].summary='New retained evidence';
  const p=run(draft,comparison);assert.equal(p.checks[1].summary,'New retained evidence');
  assert.equal(p.checks[3].state,'last_read');
});
test('projection is detached and does not modify draft, notes, report or input order',()=>{
  const data=clone(),before=structuredClone(data),p=run(data.draft,data.comparison);
  p.checks[4].summary='edited';p.basis.source_ids.push('binary_sensor.other');
  assert.deepEqual(data,before);
});
test('wrong or missing schema cannot imply an available compass',()=>{
  for(const schema of [undefined,null,'legacy','approved']) {
    const {draft}=clone();draft.review_compass.schema=schema;assert.equal(run(draft),null);
  }
});
test('another zone, draft revision or note revision invalidates the baseline',()=>{
  const {draft}=clone();
  for(const change of [{zone_id:'other'},{id:'other'},{revision:3},{review_notes:{revision:1,items:[]}}])
    assert.equal(run({...draft,...change}),null);
  assert.equal(project(draft,'other',3),null);assert.equal(project(draft,'z',4),null);
});
test('negative, boolean and unsafe revisions cannot match by coercion',()=>{
  for(const revision of [-1,true,'3',Number.MAX_SAFE_INTEGER+1,NaN,Infinity]) {
    const {draft}=clone();draft.review_compass.basis.zone_revision=revision;
    assert.equal(project(draft,'z',revision),null);
  }
});
test('changed source or target references reject a cached baseline',()=>{
  const {draft}=clone();
  assert.equal(run({...draft,current_pattern:{sources:['binary_sensor.other']}}),null);
  assert.equal(run({...draft,fields:{target_ids:['light.other']}}),null);
});
test('duplicate or invalid references never count as a matching scope',()=>{
  for(const ids of [['light.synthetic','light.synthetic'],[null],[''],[42]]) {
    const {draft}=clone();draft.fields.target_ids=ids;draft.review_compass.basis.target_ids=ids;
    assert.equal(run(draft),null);
  }
});
test('changed response identity or basis does not revive its review sections',()=>{
  const data=clone();
  for(const change of [{zone_id:'other'},{draft_id:'other'},{draft_revision:1},{zone_revision:1},
    {basis:{source_ids:[],target_ids:[]}}]) {
    const p=run(data.draft,{...data.comparison,...change});assert.equal(p.checks[3].state,'unknown');
  }
});
test('independently changed configuration metadata rejects an overlay',()=>{
  const {draft,comparison}=clone();comparison.inspection.config_fingerprint='b'.repeat(64);
  assert.equal(run(draft,comparison).checks[3].state,'unknown');
});
test('valid navigation-age endpoints are inclusive',()=>{
  const {draft,comparison}=clone();
  for(const age of [0,1,299999,300000]) assert.equal(run(draft,comparison,time+age).checks[3].state,'last_read');
});
test('expired, future, invalid or timezone-free times remain unverified',()=>{
  const {draft,comparison}=clone();
  for(const now of [time-1,time+300001,NaN,Infinity]) assert.equal(run(draft,comparison,now).checks[3].state,'unknown');
  for(const checked_at of ['invalid','2026-09-24T10:00:00',null]) {
    const changed=structuredClone(comparison);changed.checked_at=checked_at;changed.review_compass.comparison_checked_at=checked_at;
    assert.equal(run(draft,changed).checks[3].state,'unknown');
  }
});
test('changed review-note revision cannot apply an earlier assessment overlay',()=>{
  const {draft,comparison}=clone();draft.review_notes.revision=1;draft.review_compass.basis.review_revision=1;
  assert.equal(run(draft,comparison).checks[3].state,'unknown');
});
test('unknown actions, service names and URLs are not navigable',()=>{
  for(const id of ['light.turn_on','https://example.invalid','apply','__proto__'])
    assert.equal(validStep({id,priority:1,label:'bad'}),false);
  assert.equal(validStep({id:'inspect_automation',priority:35,label:'Read',automation_id:'light.synthetic'}),false);
  assert.equal(validStep({id:'write_note',priority:50,label:'Write'}),false);
});
test('invalid step or execution fields make a compass unavailable',()=>{
  const {draft}=clone();draft.review_compass.checks[0].next_step={id:'apply',priority:0,label:'Act'};
  assert.equal(run(draft),null);
  for(const execution of [{allowed:true,actions:[]},{allowed:false,actions:[{}]},{allowed:false}]) {
    const {draft:d}=clone();d.review_compass.execution=execution;assert.equal(run(d),null);
  }
});
test('current missing requirements outrank older matching automation progress',()=>{
  const {draft,comparison}=clone();
  draft.review_compass.checks[2].next_step={id:'edit_draft',priority:20,label:'Entwurfsangaben prüfen'};
  assert.equal(run(draft,comparison).next_step.id,'edit_draft');
});
test('navigation uses only backend-declared ordering, never risk or confidence',()=>{
  const {draft}=clone();draft.current_pattern.confidence=.99;draft.current_pattern.preference='accepted';
  draft.risk='low';assert.equal(run(draft).next_step.id,'compare_automations');
  assert.deepEqual(nextStep([{next_step:null}]),{id:'review_limits',priority:60,label:'Offene fachliche Grenzen ansehen'});
});
test('workspace filtering and sorting are stable detached presentation',()=>{
  const {draft}=clone();const second={...structuredClone(draft),id:'b',fields:{...draft.fields,title:'Andere'}};
  const rows=[{draft,compass:{next_step:{id:'compare_automations',priority:40}}},
              {draft:second,compass:{next_step:{id:'edit_draft',priority:20}}}];
  const before=structuredClone(rows);
  assert.equal(selectRows(rows,'all','next')[0].draft.id,'b');
  assert.equal(selectRows(rows,'intent')[0].draft.id,'b');assert.equal(selectRows(rows,'notes').length,0);
  assert.equal(selectRows(rows,'all','saved')[0].draft.id,'d');assert.equal(selectRows(rows,'all','title')[0].draft.id,'b');
  assert.deepEqual(rows,before);
});
test('unknown compass rows remain visible and selectable as unavailable',()=>{
  const rows=[{draft:{id:'x',fields:{title:'X'}},compass:null}];
  assert.equal(selectRows(rows,'all').length,1);assert.equal(selectRows(rows,'unknown').length,1);
});
