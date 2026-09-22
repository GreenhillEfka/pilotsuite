// Optional browser regression: requires playwright and its Chromium installation.
const {chromium} = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    let inventory = {zone_id: 'example', revision: 0, resolved: true, applied_to_inference: false,
      items: [{entity_id: 'sensor.temperature', name: '<script>unsafe</script>', state: '20', suggested_role: 'temperature', recommended: true, decision: 'unreviewed'},
        {entity_id: 'button.identify', state: null, recommended: false, decision: 'unreviewed'}], missing: []};
    let conflict = false; let writes = 0;
    let zones = [{zone_id: 'example', name: 'Example', area_ids: ['example'], extra_entity_ids: [], enabled: true, profile: 'cellar', revision: 0}];
    await page.route('http://pilotsuite.test/**', async route => {
      const url = new URL(route.request().url());
      const suffix = url.pathname.replace('/ingress/test/', '');
      if (!suffix || suffix.startsWith('assets/')) {
        const name = suffix ? suffix.slice(7) : 'index.html';
        const body = await fs.readFile(path.join(__dirname, '../pilotsuite/pilotsuite/web', name));
        return route.fulfill({body, contentType: name.endsWith('.js') ? 'text/javascript' : name.endsWith('.css') ? 'text/css' : 'text/html'});
      }
      let data;
      if (suffix === 'api/v1/status') data = {ready: true, version: 'test', home_assistant: {connected: true}, golden_zone: {requested_area_ids: ['example'], resolved_area_ids: ['example'], missing_area_ids: [], entity_count: 2}, habitus: {neuron_count: 2, suggestion_count: 0, ruleset: 'test'}};
      else if (suffix === 'api/v1/areas') data = {items: [{area_id: 'example', name: 'Example area'}]};
      else if (suffix === 'api/v1/entity-catalog') data = {items: [{entity_id: 'sensor.temperature', name: 'Temperature', disabled: false}]};
      else if (suffix === 'api/v1/zones') {
        if (route.request().method() === 'POST') {
          const definition = route.request().postDataJSON().definition;
          const created = {zone_id: 'hz_test', revision: 1, ...definition}; zones.push(created);
          return route.fulfill({status: 201, json: created});
        }
        data = {items: zones};
      }
      else if (suffix === 'api/v1/selections/hz_test') data = {...inventory, zone_id: 'hz_test', revision: 1, enabled: false, applied_to_inference: true, items: inventory.items.map(i => ({...i, decision: 'unreviewed'}))};
      else if (suffix === 'api/v1/selections/example') {
        if (route.request().method() === 'PATCH') {
          writes++;
          if (conflict) return route.fulfill({status: 409, json: {message: 'conflict'}});
          const payload = route.request().postDataJSON();
          assert.equal(payload.revision, inventory.revision);
          inventory = {...inventory, applied_to_inference: payload.active, revision: inventory.revision + 1, items: inventory.items.map(item => ({...item, decision: payload.changes[item.entity_id] || item.decision}))};
        }
        data = inventory;
      } else data = {items: [], neurons: []};
      await route.fulfill({json: data});
    });
    await page.goto('http://pilotsuite.test/ingress/test/');
    const first = page.locator('#selection-rows input').first();
    await first.waitFor();
    assert.equal(await first.evaluate(el => el.indeterminate), true);
    await page.locator('#selection-recommend').click();
    assert.equal(await first.isChecked(), true);
    assert.equal(writes, 0);
    assert.equal(await page.locator('#selection-zone').isDisabled(), true);
    await page.evaluate(() => load()); // dashboard polling must preserve draft
    assert.equal(await first.isChecked(), true);
    await page.locator('#selection-save').click();
    await page.waitForFunction(() => document.getElementById('selection-message').textContent.startsWith('Gespeichert'));
    assert.equal(writes, 1);
    assert.equal(await page.locator('#selection-save').isDisabled(), true);
    conflict = true;
    await first.uncheck();
    await page.locator('#selection-save').click();
    await page.waitForFunction(() => document.getElementById('selection-message').textContent.includes('Zwischenzeitlich'));
    assert.equal(await first.isChecked(), false);
    assert.equal(await page.locator('#selection-save').isDisabled(), true);
    page.on('dialog', dialog => dialog.accept());
    await page.locator('#selection-discard').click();
    await page.waitForFunction(() => document.getElementById('selection-message').textContent.startsWith('Inventar geladen'));
    assert.equal(await first.isChecked(), true);
    await page.locator('#selection-search').fill('no-match');
    assert.match(await page.locator('#selection-rows').textContent(), /Keine passenden/);
    conflict = false;
    await page.locator('#selection-active').check();
    await page.locator('#selection-save').click();
    await page.waitForFunction(() => document.getElementById('selection-message').textContent.includes('Bestätigte Auswahl ist'));
    assert.equal(inventory.applied_to_inference, true);
    await page.locator('#zone-editor summary').click();
    await page.locator('#zone-new').click();
    await page.locator('#zone-name').fill('Living space');
    assert.equal(await page.locator('#zone-enabled').isChecked(), false);
    await page.locator('#zone-areas').selectOption(['example']);
    await page.locator('#zone-extras').selectOption(['sensor.temperature']);
    await page.locator('#zone-form button[type=submit]').click();
    await page.waitForFunction(() => document.getElementById('selection-zone').value === 'hz_test');
    assert.equal(zones[1].profile, 'observe');
    assert.deepEqual(zones[1].extra_entity_ids, ['sensor.temperature']);
    assert.deepEqual(errors, []);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
    console.log('Browser regression passed: draft, save, conflict, discard, activation, search, mobile, ingress prefix.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
