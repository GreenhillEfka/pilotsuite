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
    let inventory = {zone_id: 'example', revision: 0, resolved: true, applied_to_inference: true,
      items: [{entity_id: 'sensor.temperature', name: '<script>unsafe</script>', state: '20', suggested_role: 'temperature', recommended: true, decision: 'unreviewed'},
        {entity_id: 'button.identify', state: null, recommended: false, decision: 'unreviewed'}], missing: []};
    let contexts = {};
    const roleCandidates = [{entity_id:'sensor.lux',name:'Helligkeit',suggested_role:'illuminance',decision:'relevant'},{entity_id:'sensor.temperature',name:'Temperature',suggested_role:'temperature',decision:'relevant'},{entity_id:'sensor.second',name:'Second temperature',suggested_role:'temperature',decision:'relevant'},{entity_id:'binary_sensor.p',name:'Presence A',suggested_role:'motion',decision:'relevant'},{entity_id:'binary_sensor.q',name:'Presence B',suggested_role:'motion',decision:'relevant'}];
    let conflict = false; let writes = 0; let draftConflict = false;
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
      else if (suffix === 'api/v1/areas') data = {items: [{area_id: 'example', name: 'Bad'}, {area_id: 'toilet', name: 'Toilette'}]};
      else if (suffix === 'api/v1/entity-catalog') data = {items: [{entity_id: 'sensor.temperature', name: 'Temperature', disabled: false}]};
      else if (suffix === 'api/v1/zones') {
        if (route.request().method() === 'POST') {
          const definition = route.request().postDataJSON().definition;
          const created = {zone_id: 'hz_test', revision: 1, ...definition}; zones.push(created);
          return route.fulfill({status: 201, json: created});
        }
        data = {items: zones, results: zones.filter(z => z.enabled).map(z => ({zone_id: z.zone_id, evaluated_count: 1,
          moods: [{name: z.zone_id === 'example' ? 'cellar_only' : 'bath_only', score: 0.5}],
          neurons: [{entity_id: z.zone_id + '_sensor', kind: 'temperature', value: 20, quality: 'good'}]}))};
      }
      else if (/api\/v1\/zones\/[^/]+\/context$/.test(suffix)) {
        const id = suffix.split('/')[3];
        contexts[id] ||= {revision: 1, config: {roles:{},learning:false,consented_at:null},event_count:0,patterns:[],eligible:false,candidates:roleCandidates,progress:{first_evidence_at:null,last_evidence_at:null,windows:[{start_hour:8,end_hour:10,events:3,days:3,missing_events:2,missing_days:0}]}};
        if (route.request().method() === 'PATCH') {
          const payload=route.request().postDataJSON();
          if (conflict) return route.fulfill({status:409,json:{message:'context conflict'}});
          contexts[id] = {...contexts[id], revision:contexts[id].revision+1,config:{roles:payload.roles,learning:payload.learning,detector:payload.detector || contexts[id].config.detector,context_learning:!!payload.context_learning},eligible:payload.learning};
          if (payload.reset) contexts[id] = {...contexts[id], event_count:0, patterns:[],context_windows:[],coverage:{sampled_slots:0}};
        }
        data={...contexts[id], guide:{next_step:{title:'Bewusste Auswahl', detail:'Nur bestätigte Quellen zählen.', target:'entity-details'},steps:[{title:'Bewusste Auswahl',detail:'Nur bestätigte Quellen zählen.',target:'entity-details',state:'attention'}]}};
      }
      else if (/api\/v1\/zones\/[^/]+\/history(?:\/import)?$/.test(suffix)) {
        const id=suffix.split('/')[3], payload=route.request().postDataJSON();
        if(suffix.endsWith('/import')) {
          assert.equal(payload.consent,true); assert.equal(payload.mode,'states');
          data={receipt:{accepted:3,retained_from_import:3}};
        } else {
          const start=new Date(payload.start).getTime()/1000, end=new Date(payload.end).getTime()/1000;
          data={zone_id:id,revision:contexts[id].revision,start,end,timezone:'Europe/Berlin',
            trends:{basis:payload.mode==='statistics'?'hourly_source_statistics':'sampled_recorded_states',warning:'Lücken sind unbekannt.',
              sources:[{entity_id:'sensor.temperature',kind:'temperature',unit:'°C',record_count:2,points:[[start,20],[end,22]]}],
              references:payload.mode==='statistics'?[]:[{kind:'temperature',unit:'°C',sources:['sensor.temperature'],points:[{t:start,value:20,min:19,max:21},{t:end,value:22,min:21,max:23}]}]},
            activity:{timezone:'Europe/Berlin',limitations:'Keine Genauigkeitsquote.',heatmap:[{weekday:0,start_hour:8,events:3}],checks:[]}};
        }
      }
      else if (/api\/v1\/zones\/[^/]+\/feedback$/.test(suffix)) {
        const id=suffix.split('/')[3]; const payload=route.request().postDataJSON();
        contexts[id].patterns[0].preference=payload.decision; data=contexts[id];
      }
      else if (/api\/v1\/zones\/[^/]+\/drafts(?:\/[^/]+)?$/.test(suffix)) {
        const id=suffix.split('/')[3], method=route.request().method(), payload=route.request().postDataJSON();
        const context=contexts[id]; context.drafts ||= [];
        if (method==='POST') {
          assert.equal(payload.zone_revision,context.revision);
          const existing=context.drafts.find(d=>d.pattern_id===payload.pattern_id);
          data=existing || {id:'draft1',zone_id:id,pattern_id:payload.pattern_id,source_revision:context.revision,revision:1,
            fields:{title:'Neue Routine',goal:'',trigger:'',conditions:'',exceptions:'',manual_override:'',target_ids:[]},
            source_status:'current',state:'incomplete',missing_fields:['goal','trigger','conditions','manual_override','target_ids'],unavailable_targets:[],
            current_pattern:context.patterns[0],automation_check:'not_checked',risk:'not_assessed',execution:{allowed:false,actions:[]}};
          if(!existing) context.drafts.push(data);
        } else if(method==='PATCH') {
          if(draftConflict) return route.fulfill({status:409,json:{message:'draft conflict'}});
          const draft=context.drafts.find(d=>d.id===suffix.split('/')[5]);
          assert.equal(payload.revision,draft.revision); assert.equal(payload.zone_revision,context.revision);
          Object.assign(draft,{fields:payload.fields,revision:draft.revision+1,state:'ready_for_review',missing_fields:[]});
          data=draft;
        } else if(method==='DELETE') {
          context.drafts=context.drafts.filter(d=>d.id!==suffix.split('/')[5]); data={deleted:true};
        } else data={items:context.drafts};
      }
      else if (suffix.startsWith('api/v1/zones/') && route.request().method() === 'PATCH') {
        const id = suffix.split('/').pop(); const index = zones.findIndex(z => z.zone_id === id);
        const payload = route.request().postDataJSON();
        assert.equal(payload.revision, zones[index].revision);
        if (conflict) return route.fulfill({status: 409, json: {message: 'conflict'}});
        zones[index] = {...zones[index], ...payload.definition, revision: payload.revision + 1};
        data = zones[index];
      }
      else if (suffix === 'api/v1/selections/hz_test') data = {...inventory, zone_id: 'hz_test', revision: 1, enabled: zones[1].enabled, applied_to_inference: true, items: inventory.items.map(i => ({...i, decision: 'unreviewed'}))};
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
    await page.waitForFunction(() => document.getElementById('learning-progress').textContent.includes('Noch mindestens 2 Aktivierungen'));
    assert.match(await page.locator('#learning-period').innerText(), /noch keine/);
    assert.equal(await page.locator('.section-nav a').count(), 5);
    await page.locator('.section-nav a[href="#history-section"]').click();
    assert.equal(new URL(page.url()).hash, '#history-section');
    assert.equal(await page.locator('#zone-tabs [tabindex="0"]').count(), 1);
    assert.doesNotMatch(await page.locator('footer').innerText(), /alpha\./);
    await page.locator('#zone-guide-next a').click();
    assert.equal(await page.locator('#entity-details').getAttribute('open'), '');
    assert.equal(writes, 0);
    const first = page.locator('#selection-rows input').first();
    await first.waitFor();
    assert.equal(await first.evaluate(el => el.indeterminate), true);
    await page.locator('#selection-recommend').click();
    assert.equal(await first.isChecked(), true);
    assert.equal(writes, 0);
    assert.equal(await page.locator('#selection-zone').isDisabled(), true);
    assert.match(await page.locator('#edit-status').innerText(), /Ungespeicherte/);
    assert.equal(await page.locator('#refresh').isDisabled(), true);
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
    assert.equal(await page.locator('#selection-active').count(), 0);
    await page.locator('#zone-new').click();
    await page.locator('#zone-name').fill('Living space');
    await page.locator('#zone-areas input[value=example]').check();
    await page.locator('#zone-areas input[value=toilet]').check();
    await page.locator('#zone-extras').selectOption(['sensor.temperature']);
    await page.locator('#zone-form button[type=submit]').click();
    await page.waitForFunction(() => document.getElementById('selection-zone').value === 'hz_test');
    assert.equal(zones[1].profile, 'observe');
    assert.equal(zones[1].enabled, false);
    assert.deepEqual(zones[1].area_ids, ['example', 'toilet']);
    await page.locator('#zone-toggle').click();
    await page.waitForFunction(() => document.getElementById('zone-toggle').textContent === 'Auswertung pausieren');
    assert.equal(zones[1].enabled, true);
    assert.match(await page.locator('#moods').textContent(), /bath only/);
    assert.doesNotMatch(await page.locator('#moods').textContent(), /cellar only/);
    assert.match(await page.locator('#observations').textContent(), /hz_test_sensor/);
    await page.locator('#zone-edit').click();
    await page.locator('#zone-name').fill('Badbereich');
    await page.locator('#zone-form button[type=submit]').click();
    await page.waitForFunction(() => document.getElementById('active-zone-name').textContent === 'Badbereich');
    assert.equal(zones[1].enabled, true);
    await page.getByRole('tab', {name: 'Example', exact: true}).click();
    await page.waitForFunction(() => document.getElementById('active-zone-name').textContent === 'Example');
    assert.match(await page.locator('#moods').textContent(), /cellar only/);
    assert.doesNotMatch(await page.locator('#observations').textContent(), /hz_test_sensor/);
    await page.getByRole('tab', {name: 'Badbereich', exact: true}).click();
    await page.waitForFunction(() => document.getElementById('active-zone-name').textContent === 'Badbereich');
    conflict = true;
    await page.locator('#zone-toggle').click();
    await page.waitForFunction(() => document.getElementById('zone-state-message').textContent.includes('nicht bestätigt'));
    assert.equal(zones[1].enabled, true);
    conflict = false;
    await page.locator('#zone-toggle').click();
    await page.waitForFunction(() => document.getElementById('zone-toggle').textContent === 'Auswertung starten');
    assert.equal(zones[1].enabled, false);
    await page.reload();
    await page.getByRole('tab', {name: 'Badbereich · pausiert', exact: true}).click();
    await page.waitForFunction(() => document.getElementById('active-zone-name').textContent === 'Badbereich');
    assert.match(await page.locator('#zone-state-message').textContent(), /Pausiert/);
    assert.deepEqual(zones[1].extra_entity_ids, ['sensor.temperature']);
    await page.locator('#context-edit').click();
    await page.locator('#role-illuminance input[value="sensor.lux"]').check();
    await page.locator('#role-temperature input[value="sensor.temperature"]').check();
    await page.locator('#role-temperature input[value="sensor.second"]').check();
    await page.locator('#role-presence input[value="binary_sensor.p"]').check();
    await page.locator('#role-presence input[value="binary_sensor.q"]').check();
    assert.equal(await page.locator('#learning-consent').isChecked(), false);
    await page.locator('#learning-consent').check();
    await page.locator('#context-form details summary').click();
    await page.locator('#detector-events').fill('10');
    await page.locator('#detector-days').fill('5');
    await page.locator('#detector-timezone').fill('Europe/Berlin');
    await page.locator('#detector-day-mode').selectOption('weekday_weekend');
    await page.locator('#context-learning-consent').check();
    await page.locator('#context-form button[type=submit]').click();
    await page.waitForFunction(() => document.getElementById('context-form').hidden);
    assert.deepEqual(contexts.hz_test.config.roles.temperature, ['sensor.second','sensor.temperature']);
    assert.deepEqual(contexts.hz_test.config.roles.presence, ['binary_sensor.p','binary_sensor.q']);
    assert.equal(contexts.hz_test.config.learning,true);
    assert.deepEqual(contexts.hz_test.config.detector,{min_events:10,min_days:5,timezone:'Europe/Berlin',day_mode:'weekday_weekend'});
    assert.equal(contexts.hz_test.config.context_learning,true);
    assert.deepEqual(contexts.hz_test.config.roles.illuminance, ['sensor.lux']);
    await page.locator('#context-edit').click();
    assert.equal(await page.locator('#role-presence input[value="binary_sensor.p"]').isChecked(), true);
    assert.equal(await page.locator('#role-presence input[value="binary_sensor.q"]').isChecked(), true);
    assert.match(await page.locator('#role-preview').textContent(), /Präsenz \/ Bewegung: 2 Hauptsensoren/);
    assert.equal(await page.locator('#detector-events').inputValue(),'10');
    assert.equal(await page.locator('#detector-days').inputValue(),'5');
    assert.equal(await page.locator('#detector-timezone').inputValue(),'Europe/Berlin');
    assert.equal(await page.locator('#detector-day-mode').inputValue(),'weekday_weekend');
    assert.equal(await page.locator('#context-learning-consent').isChecked(),true);
    await page.locator('#context-cancel').click();
    contexts.hz_test.event_count=6;
    contexts.hz_test.time_basis='Europe/Berlin';
    contexts.hz_test.coverage={sampled_slots:3,ready_only_slots:1,impaired_slots:2,unobserved_slots_between_checks:1};
    contexts.hz_test.context_windows=[{day_group:'weekday',start_hour:8,end_hour:10,activations:6,days:3,light_on:4,light_off:1,light_unknown:1,lux_count:3,lux_median:25,sources:['sensor.lux'],review_ready:true,proposal:'Lichtbedarf prüfen'}];
    contexts.hz_test.patterns=[{id:'p1',title:'Activity pattern',sources:['binary_sensor.p','binary_sensor.q'],statistics:{activation_count:6,distinct_day_count:3,observed_zone_activations:6,origins:{parented_service_context:4,unknown:2}},confidence:null,confidence_basis:'not_estimated',rule_strength:{rule_id:'activity-v1',threshold_met:true,event_ratio:1.2,day_ratio:1},risk:'read_only',proposal:'Check routine',preference:null}];
    await page.evaluate(() => load());
    await page.waitForFunction(() => document.getElementById('context-observations').textContent.includes('25 lx Median'));
    await page.locator('#learning-details summary').click();
    assert.match(await page.locator('#learning-coverage').innerText(), /2 mit Einschränkungen/);
    assert.match(await page.locator('#learned-patterns').innerText(), /mögliche Automation/);
    assert.doesNotMatch(await page.locator('#learned-patterns').innerText(), /bewiesene Automation/);
    contexts.hz_test.reviews=[{pattern_id:'p1',title:'Synthetic review',evidence_graph:{nodes:[{id:'source',label:'<script>source</script>'},{id:'review',label:'Routine prüfen'}]},warnings:['Keine Schaltfreigabe.'],context:null,next_steps:['Bestehende Automationen prüfen.'],execution:{allowed:false,actions:[]}}];
    contexts.hz_test.reviews[0].temporal_check={state:'reobserved',training_events:6,training_days:3,later_events:1,later_days:1,start:1788739200,end:1789948800,split_at:1789585920,timezone:'Europe/Berlin'};
    await page.evaluate(() => loadContext());
    await page.getByText('Belegkette und Prüfentwurf',{exact:true}).click();
    assert.match(await page.locator('#learned-patterns').innerText(), /Bestehende Automationen prüfen/);
    assert.equal(await page.locator('#learned-patterns script').count(),0);
    assert.match(await page.locator('.temporal-check').innerText(), /Später erneut beobachtet/);
    assert.match(await page.locator('.temporal-check').innerText(), /Früher: 6 Aktivierungen an 3 Tagen; später: 1 an 1 Tagen/);
    const downloadPromise=page.waitForEvent('download');
    await page.getByRole('button',{name:'Prüfentwurf als JSON exportieren'}).click();
    const download=await downloadPromise;
    const brief=JSON.parse(await fs.readFile(await download.path(),'utf8'));
    assert.equal(brief.execution.allowed,false); assert.deepEqual(brief.execution.actions,[]);
    assert.equal(brief.temporal_check.state,'reobserved');
    assert.equal(brief.temporal_check.later_events,1);
    contexts.hz_test.draft_target_candidates=[{entity_id:'light.synthetic',name:'Synthetic lamp'}];
    await page.evaluate(()=>loadContext());
    await page.getByRole('button',{name:'Routine entwerfen',exact:true}).click();
    await page.locator('#routine-form').waitFor({state:'visible'});
    assert.equal(await page.locator('#selection-zone').isDisabled(),true);
    assert.equal(await page.locator('#routine-targets input').isChecked(),false);
    await page.locator('#routine-title').fill('<script>My routine</script>');
    await page.locator('#routine-goal').fill('Comfort with manual control');
    await page.locator('#routine-trigger').fill('Presence in the reviewed window');
    await page.locator('#routine-conditions').fill('Only when dark');
    await page.locator('#routine-manual_override').fill('Manual changes always take priority');
    await page.locator('#routine-targets input').check();
    await page.evaluate(()=>load());
    assert.equal(await page.locator('#routine-goal').inputValue(),'Comfort with manual control');
    for(const width of [390,1440]) {
      await page.setViewportSize({width,height:900});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      if(process.env.PILOTSUITE_SCREENSHOTS) {
        await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS,{recursive:true});
        await page.locator('#routine-form').screenshot({path:path.join(process.env.PILOTSUITE_SCREENSHOTS,`draft-${width}.png`)});
      }
    }
    await page.setViewportSize({width:390,height:844});
    await page.locator('#routine-form button[type=submit]').click();
    await page.locator('#routine-form').waitFor({state:'hidden'});
    await page.waitForFunction(()=>document.getElementById('routine-list').textContent.includes('My routine'));
    assert.equal(await page.locator('#routine-list script').count(),0);
    assert.equal(contexts.hz_test.drafts.length,1);
    assert.deepEqual(contexts.hz_test.drafts[0].fields.target_ids,['light.synthetic']);
    assert.equal(contexts.hz_test.event_count,6);
    await page.getByRole('button',{name:'Entwurf bearbeiten',exact:true}).click();
    assert.equal(await page.locator('#routine-goal').inputValue(),'Comfort with manual control');
    draftConflict=true;
    await page.locator('#routine-goal').fill('Keep my unsaved changes');
    await page.locator('#routine-form button[type=submit]').click();
    await page.waitForFunction(()=>document.getElementById('routine-message').textContent.includes('draft conflict'));
    assert.equal(await page.locator('#routine-goal').inputValue(),'Keep my unsaved changes');
    assert.equal(await page.locator('#routine-form').isVisible(),true);
    draftConflict=false;
    await page.locator('#routine-reload').click();
    await page.waitForFunction(()=>document.getElementById('routine-goal').value==='Comfort with manual control');
    await page.locator('#routine-cancel').click();
    const draftDownloadPromise=page.waitForEvent('download');
    await page.getByRole('button',{name:'Entwurf exportieren',exact:true}).click();
    const draftDownload=await draftDownloadPromise;
    const savedDraft=JSON.parse(await fs.readFile(await draftDownload.path(),'utf8'));
    assert.equal(savedDraft.schema,'pilotsuite-routine-draft-v1');
    assert.equal(savedDraft.execution.allowed,false); assert.deepEqual(savedDraft.execution.actions,[]);
    assert.equal(savedDraft.fields.goal,'Comfort with manual control');
    contexts.hz_test.drafts[0].source_status='zone_changed'; contexts.hz_test.drafts[0].state='needs_review';
    await page.evaluate(()=>loadContext());
    assert.match(await page.locator('#routine-list').innerText(),/Zoneneinstellungen geändert/);
    await page.locator('#pattern-filter').selectOption('accepted');
    assert.match(await page.locator('#learned-patterns').innerText(), /Keine Muster/);
    await page.locator('#pattern-filter').selectOption('open');
    // Freeze an older read while the actual feedback handler saves a newer result.
    let releaseOlderRead;
    let markOlderReadCaptured;
    const olderReadCaptured = new Promise(resolve => { markOlderReadCaptured = resolve; });
    await page.route('**/api/v1/zones/hz_test/context', async route => {
      const oldSnapshot = JSON.parse(JSON.stringify(contexts.hz_test));
      await new Promise(resolve => { releaseOlderRead = resolve; markOlderReadCaptured(); });
      await route.fulfill({json:oldSnapshot});
    }, {times:1});
    await page.evaluate(() => { window.pendingOlderContextRead = loadContext(); });
    await olderReadCaptured;
    await page.getByRole('button',{name:'Passt',exact:true}).click();
    await page.locator('#pattern-filter').selectOption('accepted');
    await page.waitForFunction(() => document.getElementById('learned-patterns').textContent.includes('Deine Präferenz: Passt'));
    releaseOlderRead();
    await page.evaluate(() => window.pendingOlderContextRead);
    assert.match(await page.locator('#learned-patterns').innerText(), /Deine Präferenz: Passt/);
    assert.equal(contexts.hz_test.event_count,6);
    await page.locator('#context-edit').click();
    conflict=true;
    await page.locator('#context-form button[type=submit]').click();
    await page.waitForFunction(() => document.getElementById('context-message').textContent.includes('nicht bestätigt'));
    assert.equal(await page.locator('#context-form').isVisible(),true);
    conflict=false;
    await page.locator('#context-cancel').click();
    contexts.hz_test.enabled=true;
    await page.locator('#history-load').click();
    await page.locator('#history-chart svg').waitFor();
    assert.match(await page.locator('#history-legend').innerText(),/Zonenreferenz/);
    assert.equal(await page.locator('#history-import').isDisabled(),true);
    await page.locator('#history-consent').check();
    assert.equal(await page.locator('#history-import').isEnabled(),true);
    await page.locator('#history-import').click();
    await page.waitForFunction(()=>document.getElementById('history-message').textContent.includes('3 neue Aktivierungen'));
    assert.equal(await page.locator('#history-consent').isChecked(),false);
    await page.locator('#history-mode').selectOption('statistics');
    await page.locator('#history-load').click();
    await page.locator('#history-chart svg').waitFor();
    assert.match(await page.locator('#history-basis').innerText(),/Stundenmittel/);
    await page.locator('#history-consent').check();
    assert.equal(await page.locator('#history-import').isDisabled(),true);
    assert.match(await page.locator('#history-import-help').innerText(), /Stundenmittel/);
    await page.locator('#history-range').selectOption('custom');
    assert.equal(await page.locator('#history-start').isVisible(),true);
    assert.equal(await page.locator('#history-display').isVisible(),false);
    await page.locator('#history-load').click();
    await page.waitForFunction(() => document.getElementById('history-message').textContent.includes('vollständig eingeben'));
    await page.locator('#learning-details summary').click();
    for (const width of [390, 768, 1440]) {
      await page.setViewportSize({width,height:900});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      if (process.env.PILOTSUITE_SCREENSHOTS) {
        await fs.mkdir(process.env.PILOTSUITE_SCREENSHOTS, {recursive:true});
        await page.locator('#zone-overview').screenshot({style:'.section-nav, .skip-link { visibility: hidden !important; }',path:path.join(process.env.PILOTSUITE_SCREENSHOTS, `overview-${width}.png`)});
        await page.locator('#learning-section').screenshot({style:'.section-nav, .skip-link { visibility: hidden !important; }',path:path.join(process.env.PILOTSUITE_SCREENSHOTS, `learning-${width}.png`)});
      }
    }
    await page.setViewportSize({width:390,height:844});
    await page.locator('#learning-reset').click();
    await page.waitForFunction(() => document.getElementById('learning-status').textContent.includes('Lernen ausgeschaltet'));
    assert.equal(contexts.hz_test.event_count,0);
    assert.deepEqual(contexts.hz_test.patterns,[]);
    assert.equal(await page.locator('#neuron-details').getAttribute('open'),null);
    // A failed context read must not retain the preceding zone's learning display.
    await page.route('**/api/v1/zones/example/context', route => route.fulfill({status:503,json:{message:'synthetic unavailable'}}));
    await page.getByRole('tab', {name:'Example',exact:true}).click();
    await page.waitForFunction(() => document.getElementById('learning-status').textContent.includes('nicht verfügbar'));
    assert.equal(await page.locator('#learned-patterns').textContent(), '');
    assert.equal(await page.locator('#routine-list').textContent(), '');
    assert.equal(await page.locator('#learning-sources').textContent(), '');
    assert.equal(await page.locator('#learning-export').getAttribute('href'), null);
    assert.equal(await page.locator('#zone-guide-steps').textContent(), '');
    assert.match(await page.locator('#zone-guide-next').textContent(), /nicht verfügbar/);
    assert.deepEqual(errors, []);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
    console.log('Browser regression passed: draft, save, conflict, discard, activation, search, mobile, ingress prefix.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
