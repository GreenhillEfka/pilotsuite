// Full actual app, canonical temporary stores, no HA credentials or actuator calls.
const {chromium} = require(process.env.PILOTSUITE_PLAYWRIGHT || 'playwright');
const {spawn} = require('node:child_process');
const {createInterface} = require('node:readline');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const root = path.resolve(__dirname, '..');
  const fixture = spawn(process.env.PYTHON || 'python', ['scripts/daily_brief_browser_fixture.py'], {
    cwd: root, env: {...process.env, PYTHONPATH: path.join(root, 'pilotsuite')}, stdio: ['pipe', 'pipe', 'pipe']});
  let stderr = '';
  fixture.stderr.on('data', data => { stderr = (stderr + data).slice(-12000); });
  const lines = createInterface({input: fixture.stdout})[Symbol.asyncIterator]();
  const deadline = async (promise, label) => {
    let timer;
    try { return await Promise.race([promise, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(label + ': ' + stderr)), 20000);
    })]); } finally { clearTimeout(timer); }
  };
  const read = async () => {
    const item = await deadline(lines.next(), 'Fixture timeout');
    if (item.done) throw new Error('Fixture stopped: ' + stderr);
    return JSON.parse(item.value);
  };
  const command = async value => { fixture.stdin.write(JSON.stringify(value) + '\n'); return read(); };
  let browser;
  try {
    const info = await read();
    browser = await chromium.launch({headless: true,
      ...(process.env.PILOTSUITE_CHROMIUM ? {executablePath: process.env.PILOTSUITE_CHROMIUM} : {})});
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    page.setDefaultTimeout(10000);
    page.on('dialog', dialog => dialog.accept());
    const errors = [], writes = [], external = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {
      if (!['GET', 'HEAD'].includes(request.method())) writes.push(request.method() + ' ' + request.url());
      if (new URL(request.url()).origin !== new URL(info.url).origin) external.push(request.url());
    });
    await page.goto(info.url);
    await page.waitForFunction(() => contextData?.daily_brief?.candidate && !selectionBusy);
    const brief = page.locator('#daily-brief');
    const candidate = brief.locator('a[data-pattern-id]');
    assert.equal(await candidate.getAttribute('data-pattern-id'), info.pattern_id);
    assert.match(await brief.textContent(), /12 Aktivierungen an 6 Tagen/);
    assert.match(await brief.textContent(), /aufbewahrte Belege/);
    assert.doesNotMatch(await brief.textContent(), /Heute|Tagesprognose:.*gut/);
    const initial = await command({action: 'snapshot'});
    assert.equal(initial.related_reads, 0); assert.equal(initial.config_reads, 0);

    // Same-basis rendering retains keyboard focus and expanded limits.
    await brief.locator('summary').click(); await candidate.focus();
    await page.evaluate(() => renderDailyBrief());
    assert.equal(await page.evaluate(() => document.activeElement.dataset.patternId), info.pattern_id);
    assert.equal(await brief.locator('details').getAttribute('open'), '');
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'pattern-workbench');

    // Real retained draft editor, not a replacement UI stub. No save is requested.
    await page.evaluate(() => openRoutineEditor(contextData.drafts[0]));
    const authored = '<img src=x onerror="window.briefCanary=true">';
    await page.locator('#routine-goal').fill(authored);
    await page.evaluate(async () => { await loadContext(); });
    assert.equal(await page.locator('#routine-goal').inputValue(), authored);
    assert.equal(await page.locator('#routine-form').isVisible(), true);
    assert.equal(await page.evaluate(() => window.briefCanary), undefined);
    assert.deepEqual(await command({action: 'snapshot'}), initial);
    await page.locator('#routine-cancel').click();

    // Hold a real request: the old candidate must disappear before it completes.
    let release;
    const gate = new Promise(resolve => { release = resolve; });
    const routeURL = info.url + 'api/v1/zones/a/context';
    await page.route(routeURL, async route => { await gate; await route.continue(); });
    await page.evaluate(() => { window.pendingBrief = loadSelection('a'); });
    await page.waitForFunction(() => selectionBusy && !byId('daily-brief').querySelector('a'));
    assert.equal(await candidate.count(), 0);
    release(); await page.evaluate(async () => { await window.pendingBrief; });
    await page.unroute(routeURL);
    assert.equal(await candidate.count(), 1);

    // Failed refresh cannot be rendered again as a valid old candidate.
    await page.route(routeURL, route => route.abort('failed'));
    await page.evaluate(async () => { try { await loadContext(); } catch (_) {} renderDailyBrief(); });
    assert.equal(await candidate.count(), 0);
    await page.unroute(routeURL);
    await page.evaluate(async () => { await loadContext(); });
    assert.equal(await candidate.count(), 1);
    assert.deepEqual(await command({action: 'snapshot'}), initial);

    // Server-side status/source changes flow through the actual context endpoint.
    await command({action: 'connection', connected: false});
    await page.evaluate(async () => { await loadContext(); });
    assert.equal(await candidate.count(), 0); assert.match(await brief.textContent(), /Verbindung/);
    await command({action: 'connection', connected: true});
    await page.evaluate(async () => { await loadContext(); });
    assert.equal(await candidate.count(), 1);
    await command({action: 'source_state', state: 'unavailable'});
    await page.evaluate(async () => { await loadSelection('a'); });
    assert.equal(await candidate.count(), 0);
    await command({action: 'source_state', state: 'off'});
    await page.evaluate(async () => { await loadSelection('a'); });
    assert.equal(await candidate.count(), 1);
    for (const [decision, label] of [['rejected', 'abgelehnt'], ['later', 'vertagt']]) {
      await command({action: 'feedback', decision});
      await page.evaluate(async () => { await loadContext(); });
      assert.equal(await candidate.count(), 0); assert.match(await brief.textContent(), new RegExp(label));
      assert.equal(await page.evaluate(() => contextData.event_count), 12);
    }
    await command({action: 'feedback', decision: 'accepted'});
    await page.evaluate(async () => { await loadContext(); });
    assert.equal(await candidate.count(), 1);

    for (const width of [390, 1440]) {
      await page.setViewportSize({width, height: 1000});
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'overflow');
      if (process.env.PILOTSUITE_SCREENSHOTS) {
        await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS, {recursive: true});
        await brief.screenshot({path: path.join(process.env.PILOTSUITE_SCREENSHOTS, `daily-brief-${width}.png`)});
      }
    }
    await page.evaluate(async () => { document.activeElement?.blur(); await loadSelection('b'); });
    assert.equal(await candidate.count(), 0); assert.doesNotMatch(await brief.textContent(), /12 Aktivierungen/);
    const final = await command({action: 'snapshot'});
    assert.equal(final.related_reads, 0); assert.equal(final.config_reads, 0);
    assert.deepEqual(writes, []); assert.deepEqual(external, []); assert.deepEqual(errors, []);
    console.log('Daily-brief full-app browser contracts: OK (synthetic, no HA writes)');
  } finally {
    if (browser) await browser.close();
    fixture.stdin.end();
    const exit = new Promise(resolve => fixture.exitCode !== null ? resolve(fixture.exitCode) : fixture.once('exit', resolve));
    try { assert.equal(await deadline(exit, 'Fixture cleanup timeout'), 0, stderr); }
    finally { if (fixture.exitCode === null) fixture.kill('SIGTERM'); }
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
