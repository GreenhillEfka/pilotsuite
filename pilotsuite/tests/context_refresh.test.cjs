const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

// Exercise the actual browser read function with deterministic deferred transport.
const app = fs.readFileSync(path.join(__dirname, '../pilotsuite/web/app.js'), 'utf8');
const source = app.slice(app.indexOf('async function loadContext()'), app.indexOf('function renderZoneGuide()'));
function setup() {
  const requests = [];
  const scope = {
    selectionZone: 'synthetic_a', contextGeneration: 0, contextData: null,
    renders: 0, historyChecks: 0, invalidations: [],
    invalidateDailyBrief: message => scope.invalidations.push(message),
    json: () => new Promise((resolve, reject) => requests.push({resolve, reject})),
    renderLearning: () => scope.renders++,
    historyCheckRevision: () => scope.historyChecks++,
  };
  vm.createContext(scope); vm.runInContext(source, scope);
  return {scope, requests};
}

test('latest same-zone read wins even when an older response arrives last', async () => {
  const {scope, requests} = setup();
  const older = scope.loadContext(), newer = scope.loadContext();
  requests[1].resolve({revision:2}); await newer;
  requests[0].resolve({revision:1}); await older;
  assert.equal(scope.contextData.revision, 2);
  assert.equal(scope.renders, 1); assert.equal(scope.historyChecks, 1);
});

test('returning to the same zone does not revive its previous request', async () => {
  const {scope, requests} = setup();
  const first = scope.loadContext();
  scope.selectionZone = 'synthetic_b'; const middle = scope.loadContext();
  scope.selectionZone = 'synthetic_a'; const last = scope.loadContext();
  requests[2].resolve({revision:3}); await last;
  requests[1].resolve({revision:2}); await middle;
  requests[0].resolve({revision:1}); await first;
  assert.equal(scope.contextData.revision, 3); assert.equal(scope.renders, 1);
});

test('obsolete read failures do not replace the current success with an error', async () => {
  const {scope, requests} = setup();
  const older = scope.loadContext(), newer = scope.loadContext();
  requests[1].resolve({revision:2}); await newer;
  requests[0].reject(new Error('obsolete transport error'));
  await assert.doesNotReject(older);
  assert.equal(scope.contextData.revision, 2);
});

test('current read failures still propagate to the existing error UI', async () => {
  const {scope, requests} = setup(); const pending = scope.loadContext();
  requests[0].reject(new Error('current transport error'));
  await assert.rejects(pending, /current transport error/);
  assert.equal(scope.renders, 0);
});

test('invalidating an in-flight read preserves a newer mutation result', async () => {
  const {scope, requests} = setup(); const pending = scope.loadContext();
  scope.contextGeneration++; scope.contextData = {revision:2, preference:'accepted'};
  requests[0].resolve({revision:1, preference:null}); await pending;
  assert.equal(scope.contextData.preference, 'accepted'); assert.equal(scope.renders, 0);
});
