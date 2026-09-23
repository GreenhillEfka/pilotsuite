const test = require('node:test');
const assert = require('node:assert/strict');
const {reviewNoteState} = require('../pilotsuite/web/review_notes.js');
const draft = {id:'d',zone_id:'z',revision:2};
const note = {draft_revision:2,zone_revision:3,automation_id:'automation.synthetic',config_fingerprint:'a'};
const report = {draft_id:'d',zone_id:'z',draft_revision:2,zone_revision:3,
  inspection:{entity_id:'automation.synthetic',config_fingerprint:'a'}};
test('saved fingerprint without fresh read remains unverified', () => {
  assert.equal(reviewNoteState(note,draft,null,3),'not_rechecked');
});
test('matching fingerprint describes only the last read', () => {
  assert.equal(reviewNoteState(note,draft,report,3),'matches_last_read');
});
test('configuration changes invalidate the personal assessment basis', () => {
  assert.equal(reviewNoteState(note,draft,{...report,inspection:{...report.inspection,config_fingerprint:'b'}},3),'config_changed');
});
test('other automation and other zone reports are not evidence for this note', () => {
  assert.equal(reviewNoteState(note,draft,{...report,zone_id:'other'},3),'not_rechecked');
  assert.equal(reviewNoteState(note,draft,{...report,inspection:{...report.inspection,entity_id:'automation.other'}},3),'not_rechecked');
});
test('draft and zone changes are stale even with an unchanged config', () => {
  assert.equal(reviewNoteState(note,{...draft,revision:3},report,3),'stale');
  assert.equal(reviewNoteState(note,draft,report,4),'stale');
});
test('server-side source invalidation takes priority over a matching hash', () => {
  assert.equal(reviewNoteState({...note,stale:true},draft,report,3),'stale');
});
test('a stale comparison cannot confirm a saved note', () => {
  assert.equal(reviewNoteState(note,draft,{...report,draft_revision:1},3),'not_rechecked');
});
