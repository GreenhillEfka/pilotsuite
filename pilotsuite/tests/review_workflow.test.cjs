const test = require('node:test');
const assert = require('node:assert/strict');
const {reviewNoteState, summarizeReviewNotes, reviewNoteInitialDisposition, reviewNoteBasisKey} = require('../pilotsuite/web/review_notes.js');
const draft = {id:'d',zone_id:'z',revision:2,source_status:'current',unavailable_targets:[],
  fields:{target_ids:['light.synthetic']},current_pattern:{sources:['binary_sensor.synthetic']}};
const note = {draft_revision:2,zone_revision:3,automation_id:'automation.synthetic',config_fingerprint:'a'.repeat(64),
  disposition:'reviewed',text:'Original assessment',stale:false};
const report = {draft_id:'d',zone_id:'z',draft_revision:2,zone_revision:3,
  inspection:{entity_id:'automation.synthetic',config_fingerprint:'a'.repeat(64)}};

test('empty notes do not imply completed assessments', () => {
  assert.deepEqual(summarizeReviewNotes({items:[]}), {total:0,open:0,needs_change:0,reviewed:0,
    stale:0,config_changed:0,not_rechecked:0,matches_last_read:0});
});
test('assessment counts and current-basis counts remain independent', () => {
  const result=summarizeReviewNotes({items:[
    {disposition:'reviewed',view_status:'stale'},
    {disposition:'needs_change',view_status:'matches_last_read'},
    {disposition:'open',view_status:'config_changed'},
    {disposition:'reviewed',view_status:'not_rechecked'}]});
  assert.deepEqual(result,{total:4,open:1,needs_change:1,reviewed:2,stale:1,
    config_changed:1,not_rechecked:1,matches_last_read:1});
  assert.equal('approved' in result,false); assert.equal('confidence' in result,false);
});
test('unknown note presentation fields never count as reviewed or verified', () => {
  const result=summarizeReviewNotes({items:[{disposition:'approved',view_status:'safe'},{}]});
  assert.equal(result.open,2); assert.equal(result.not_rechecked,2);
  assert.equal(result.reviewed,0); assert.equal(result.matches_last_read,0);
});
test('summary is detached and never rewrites notes or their execution boundary', () => {
  const source=Object.freeze({items:Object.freeze([Object.freeze({disposition:'reviewed',view_status:'stale'})]),
    execution:Object.freeze({allowed:false})});
  const result=summarizeReviewNotes(source); result.reviewed=900;
  assert.equal(source.items[0].disposition,'reviewed');assert.equal(source.execution.allowed,false);
  assert.equal(summarizeReviewNotes(source).reviewed,1);
});
test('only matching reviewed basis may retain the previous editor selection', () => {
  assert.equal(reviewNoteInitialDisposition(note,draft,report,3),'reviewed');
  assert.equal(reviewNoteInitialDisposition({...note,disposition:'needs_change'},draft,report,3),'needs_change');
});
test('changed config opens as open without erasing authored text or stored disposition', () => {
  const previous=structuredClone(note);
  const changed={...report,inspection:{...report.inspection,config_fingerprint:'b'.repeat(64)}};
  assert.equal(reviewNoteInitialDisposition(note,draft,changed,3),'open');
  assert.deepEqual(note,previous);
});
test('missing inspection, unknown disposition and new notes default to open', () => {
  assert.equal(reviewNoteInitialDisposition(note,draft,null,3),'open');
  assert.equal(reviewNoteInitialDisposition(null,draft,report,3),'open');
  assert.equal(reviewNoteInitialDisposition({...note,disposition:'approved'},draft,report,3),'open');
});
test('cached false stale flag cannot override unavailable sources or targets', () => {
  for (const changed of [{...draft,source_status:'pattern_missing'},
    {...draft,source_status:'zone_changed'}, {...draft,unavailable_targets:['light.synthetic']}]) {
    assert.equal(reviewNoteState(note,changed,report,3),'stale');
    assert.equal(reviewNoteInitialDisposition(note,changed,report,3),'open');
  }
});
test('undefined or empty matching hashes never confirm configuration', () => {
  for (const fingerprint of [undefined,null,'',true]) {
    const n={...note,config_fingerprint:fingerprint};
    const r={...report,inspection:{...report.inspection,config_fingerprint:fingerprint}};
    assert.equal(reviewNoteState(n,draft,r,3),'not_rechecked');
    assert.equal(reviewNoteInitialDisposition(n,draft,r,3),'open');
  }
});
test('basis key canonicalizes source and target order without mutating input', () => {
  const original={...draft,fields:{target_ids:['light.z','light.a']},current_pattern:{sources:['binary_sensor.z','binary_sensor.a']}};
  const before=structuredClone(original);
  const reversed={...original,fields:{target_ids:[...original.fields.target_ids].reverse()},
    current_pattern:{sources:[...original.current_pattern.sources].reverse()}};
  assert.equal(reviewNoteBasisKey(original,report,3),reviewNoteBasisKey(reversed,report,3));
  assert.deepEqual(original,before);
});
test('basis key changes for identity, revisions, references and selected configuration', () => {
  const key=reviewNoteBasisKey(draft,report,3);
  for (const changed of [{...draft,id:'other'},{...draft,zone_id:'other'}, {...draft,revision:3},
    {...draft,fields:{target_ids:['light.other']}}, {...draft,current_pattern:{sources:['binary_sensor.other']}}])
    assert.notEqual(reviewNoteBasisKey(changed,report,3),key);
  assert.notEqual(reviewNoteBasisKey(draft,report,4),key);
  for (const change of [{entity_id:'automation.other'},{config_fingerprint:'b'.repeat(64)}])
    assert.notEqual(reviewNoteBasisKey(draft,{...report,inspection:{...report.inspection,...change}},3),key);
});
test('evidence counts and personal preferences do not change the inspection basis', () => {
  const changed=structuredClone(draft);
  changed.current_pattern.statistics={activation_count:999}; changed.current_pattern.preference='accepted';
  assert.equal(reviewNoteBasisKey(draft,report,3),reviewNoteBasisKey(changed,report,3));
});
