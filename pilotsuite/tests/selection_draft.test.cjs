const {test} = require('node:test');
const assert = require('node:assert/strict');
const {SelectionDraft} = require('../pilotsuite/web/selections.js');
const fixture = () => ({revision: 3, items: [
  {entity_id: 'sensor.new', decision: 'unreviewed', recommended: true},
  {entity_id: 'sensor.ignored', decision: 'ignored', recommended: true},
  {entity_id: 'button.identify', decision: 'unreviewed', recommended: false},
], missing: [{entity_id: 'sensor.missing', decision: 'relevant'}]});

test('recommendations preserve explicit rejection and original inventory', () => {
  const inventory = fixture(); const draft = new SelectionDraft(inventory);
  draft.recommend();
  assert.deepEqual(draft.changes, {'sensor.new': 'relevant'});
  assert.equal(inventory.items[0].decision, 'unreviewed');
  assert.equal(draft.decisions.get('sensor.ignored'), 'ignored');
});
test('undo is clean; missing entity decisions remain editable', () => {
  const draft = new SelectionDraft(fixture());
  draft.set('sensor.new', 'ignored'); assert.equal(draft.dirty, true);
  draft.set('sensor.new', 'unreviewed'); assert.equal(draft.dirty, false);
  draft.set('sensor.missing', 'ignored');
  assert.deepEqual(draft.changes, {'sensor.missing': 'ignored'});
});
test('unknown IDs and invalid decisions are rejected', () => {
  const draft = new SelectionDraft(fixture());
  assert.throws(() => draft.set('sensor.foreign', 'relevant'));
  assert.throws(() => draft.set('sensor.new', 'on'));
  assert.equal(draft.dirty, false);
});
test('activation is an explicit reversible draft change', () => {
  const draft = new SelectionDraft(fixture());
  assert.equal(draft.active, false);
  draft.active = true;
  assert.equal(draft.dirty, true);
  assert.deepEqual(draft.changes, {});
  draft.active = false;
  assert.equal(draft.dirty, false);
});
