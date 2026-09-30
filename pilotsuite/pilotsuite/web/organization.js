/* Inventory & order: one canonical server profile, explicit reads and confirmed edits. */
(() => {
  'use strict';
  const E=(tag,text='',cls='')=>{const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e;};
  const B=(label,action)=>{const b=E('button',label);b.type='button';b.addEventListener('click',action);return b;};
  const labels={presence_sources:'Präsenzquellen',presence_status:'Raumstatus / interner Boolean',presence_timer:'Nachlauftimer',
    presence_output:'Öffentlicher Zonen-Präsenzsensor',
    presence_duration:'Nachlauf-Dauer',manual_override:'Manuelle Bedienung',automation_blocker:'Automatiksperre',
    presence_automations:'Anwesenheitsautomationen',lighting_automations:'Lichtautomationen',other_automations:'Weitere Automationen'};
  const topics=[
    {id:'presence',role:'presence_automations',title:'Anwesenheit',description:'Quellen, Raumstatus und Nachlauf der vorhandenen Anwesenheitskette.'},
    {id:'lighting',role:'lighting_automations',title:'Licht',description:'Bestehende Lichtregeln und ihre Abhängigkeit vom Zonenstatus.'},
    {id:'other',role:'other_automations',title:'Weitere Automationen',description:'Weitere ausdrücklich zugeordnete Regeln. Keine automatische Sortierung nach Namen.'}
  ];
  const timingLabels={observe:'Nur beobachten / noch nicht zugeordnet',existing_for:'Bestehender for:-Nachlauf',timer:'Vorhandener Timer',external:'Andere Bestandslogik'};
  const statusLabels={present:'Vorhanden',missing:'Referenz fehlt',disabled:'Deaktiviert',unavailable:'Nicht verfügbar',snapshot_stale:'Datenstand nicht aktuell'};
  const outcomeLabels={preview:'Vorschau – noch nicht ausgeführt',applying:'Unterbrochen oder noch in Bearbeitung – nicht wiederholen',verified:'Änderung zurückgelesen',attention:'Teilweise / unklar – Einzelstatus prüfen',unchanged:'Bereits einheitlich'};
  let root,message,form,reports,planPanel,history,data=null,basis=null,loadedBasis=null,draft={},initial='',busy=false,serial=0,afterSave,scanOffset=0,selectionOffset=0,pendingSave=false;
  let reportView={reports:new Map(),unread:new Map(),filter:'attention',mode:'selection',requested:0,total:0};
  const reportReplacements=new Map();
  const selections={}, searches={};
  let requestedRole=null;
  function focusRequestedRole(){
    if(!requestedRole||requestedRole.zone!==basis?.zone||!data||busy||pendingSave||!loadedBasis||loadedBasis.revision!==basis?.revision||!root?.getClientRects().length)return;
    const role=requestedRole.role,group=form.querySelector('[data-org-group="'+role+'"]');if(!group)return;
    const helpers=group.closest('#org-helpers');if(helpers)helpers.open=true;group.open=true;
    searches[role]?.focus();group.scrollIntoView({block:'center'});requestedRole=null;
  }
  const encode=()=>JSON.stringify({assignments:Object.fromEntries(Object.entries(draft).map(([k,v])=>[k,[...v].sort()])),timing:form?.querySelector('#org-timing')?.value||'observe'});
  const changed=()=>data!==null&&initial!==encode();
  const notice=t=>{if(message)message.textContent=t;};
  const request=async(path,options={})=>{const response=await fetch(path,{headers:{'Content-Type':'application/json'},...options});const d=await response.json();if(!response.ok){const error=Error(d.message||'Zugriff nicht bestätigt');error.status=response.status;throw error;}return d;};
  const path=()=>`api/v1/zones/${encodeURIComponent(basis.zone)}/organization`;
  const assertCurrent=()=>{if(!data||!basis||!loadedBasis||loadedBasis.zone!==basis.zone||loadedBasis.revision!==basis.revision)throw Error('Zonenstand geändert. Bestand neu laden; Entwurf bleibt sichtbar.');};
  const ticket=()=>({zone:basis.zone,revision:basis.revision,serial});
  const current=t=>t.serial===serial&&t.zone===basis?.zone&&t.revision===basis?.revision;
  const triggerAttention=report=>(report?.trigger_integrity?.selectors||[]).some(row=>row.state!=='matched');
  const referenceAttention=report=>(report?.findings||[]).some(row=>row.status!=='present');
  const lifecycleAttention=report=>(report?.presence_lifecycle?.findings||[]).some(row=>row.state==='review');
  const reportAttention=report=>triggerAttention(report)||referenceAttention(report)||lifecycleAttention(report);
  function resetReports(){reportView={reports:new Map(),unread:new Map(),filter:'attention',mode:'selection',requested:0,total:0};reportReplacements.clear();reports?.replaceChildren();}
  async function requestPlan(suffix,options={}){
    assertCurrent();const t=ticket(),response=await request(path()+suffix,options);
    if(!current(t))return;
    if(response.state!=='unchanged'&&response.zone_id!==t.zone)throw Error('Plan gehört nicht zur aktuellen Zone. Bestand erneut laden.');
    drawPlan(response);
  }
  async function run(fn){if(busy)return;busy=true;updateButtons();try{await fn();}catch(error){notice(error.message);}finally{busy=false;updateButtons();}}
  function updateButtons(){if(!root)return;root.querySelectorAll('input,select').forEach(e=>{if(busy||pendingSave){if(e.dataset.orgWasDisabled===undefined)e.dataset.orgWasDisabled=String(e.disabled);e.disabled=true;}else if(e.dataset.orgWasDisabled!==undefined){e.disabled=e.dataset.orgWasDisabled==='true';delete e.dataset.orgWasDisabled;}});root.querySelectorAll('button[data-org-write]').forEach(b=>b.disabled=busy||!data||!loadedBasis||loadedBasis.zone!==basis?.zone||loadedBasis.revision!==basis?.revision);const save=root.querySelector('#org-save');if(save)save.disabled=busy||pendingSave||!changed();const load=root.querySelector('#org-load');if(load)load.textContent=pendingSave?'Gespeicherten Stand prüfen':'Bestand & Zuordnungen laden';}
  async function load(){if(selectionBusy||contextEditing||zoneFormOpen||selectionDraft?.dirty){notice('Andere Bearbeitung zuerst speichern oder abbrechen.');return;}if(changed()&&!pendingSave){notice('Entwurf zuerst speichern oder verwerfen.');return;}return run(async()=>{
    if(pendingSave){if(!window.confirm('Gespeicherten Stand nur lesen und bei Erfolg anstelle der sichtbaren lokalen Auswahl anzeigen? Es wird nichts erneut gespeichert.'))return;const savedZone=pendingSave.zone;await afterSave();if(basis.zone!==savedZone)throw Error('Andere Zone geöffnet; lokale Auswahl bleibt sichtbar.');}
    const current={...basis},generation=++serial;
    const response=await request(path());
    if(generation!==serial||current.zone!==basis.zone||current.revision!==basis.revision)return;
    if(response.zone_id!==current.zone||response.revision!==current.revision)throw Error('Serverstand hat sich geändert. Zonenansicht aktualisieren.');
    data=response;loadedBasis=current;pendingSave=false;scanOffset=0;render();notice('Globaler Bestand geladen. Zuordnung ist keine Steuerungs- oder Lernfreigabe.');
  }).then(focusRequestedRole);}
  function chosen(role,eid){const row=data.catalog.find(r=>r.entity_id===eid);return row?`${row.name} · ${eid}`:eid+' · Identität ungeklärt';}
  function choose(role,eid){if(busy||pendingSave)return;const max=data.roles[role].max;
    if(draft[role].has(eid))draft[role].delete(eid);
    else if(max===1)draft[role]=new Set([eid]);
    else if(draft[role].size<max)draft[role].add(eid);
    else{notice(`Maximal ${max} Zuordnungen für ${labels[role]}.`);return;}
    drawChoices(role);updateButtons();
    if(topics.some(t=>t.role===role)){selectionOffset=0;scanOffset=0;resetReports();drawAutomationTopics();resetAnalysisButton();resetScanButton();}
  }
  const selectedAutomations=()=>[...new Set(topics.flatMap(t=>[...(draft[t.role]||[])]))].sort();
  function resetAnalysisButton(){const b=root?.querySelector('#org-analyze');if(b)b.textContent='Ausgewählte Automationen analysieren';}
  function resetScanButton(){const b=root?.querySelector('#org-scan');if(b){b.textContent='Globalen Automationsbestand paketweise prüfen';b.disabled=false;}}
  function drawAutomationTopics(){
    for(const topic of topics){
      const target=form.querySelector('[data-org-topic="'+topic.id+'"] .org-topic-summary');if(!target)continue;
      target.replaceChildren();const ids=[...(draft[topic.role]||[])];
      if(!ids.length){target.append(E('p','Noch keine Automation zugeordnet.','ps-muted'));continue;}
      const list=E('ul','','org-automation-list');target.append(list);
      for(const eid of ids){
        const bound=(data.bindings.assignments[topic.role]||[]).find(r=>(r.entity_id||r.saved_entity_id)===eid);
        const row=bound||data.catalog.find(r=>r.entity_id===eid);
        const status=!data.fresh?'Datenstand nicht bestätigt':!row||row.status==='identity_unresolved'?'Identität ungeklärt':row.disabled?'Im Register deaktiviert':row.state==='on'?'Aktiviert in HA':row.state==='off'?'Deaktiviert in HA':'Aktivierung unbekannt';
        const item=E('li');item.append(E('strong',row?.name||eid),E('span',bound?'Zuordnung gespeichert':'Noch nicht gespeichert','ps-badge'),E('p',status+' · Beim Laden gemeldeter Stand; kein Verhaltensnachweis.','ps-muted'));
        const shared=row?.shared_zone_ids||[];
        if(shared.length)item.append(E('p','Auch zugeordnet in: '+shared.join(', ')+'. Gemeinsame Automation, keine Kopie.','ps-warning'));
        const otherTopics=topics.filter(t=>t.role!==topic.role&&draft[t.role]?.has(eid)).map(t=>t.title);
        if(otherTopics.length)item.append(E('p','Auch unter '+otherTopics.join(' / ')+'. Dasselbe Objekt.','ps-muted'));
        item.append(E('code',eid,'ps-technical-id'));list.append(item);
      }
    }
  }
  function drawChoices(role){const node=selections[role],hadFocus=node.contains(document.activeElement),focusedId=document.activeElement?.dataset.orgCandidate;node.replaceChildren();const picked=E('div','','org-picked');
    for(const eid of draft[role]){const chip=B(chosen(role,eid)+' ×',()=>choose(role,eid));chip.className='org-chip';chip.setAttribute('aria-label',labels[role]+': '+eid+' entfernen');picked.append(chip);}node.append(picked);
    const q=searches[role].value.trim().toLocaleLowerCase('de');const candidates=data.catalog.filter(r=>data.roles[role].domains.includes(r.entity_id.split('.')[0])&&(role!=='presence_output'||['occupancy','presence'].includes(r.device_class))&&!r.disabled&&r.in_registry&&[r.name,r.entity_id,r.area_id||'',r.platform||''].join(' ').toLocaleLowerCase('de').includes(q));
    node.append(E('p',`${draft[role].size} gewählt · ${candidates.length} passend · bis zu 30 Treffer angezeigt`,'ps-muted'));
    const list=E('div','','org-candidates');
    for(const row of candidates.slice(0,30)){const b=B('',()=>choose(role,row.entity_id));b.dataset.orgCandidate=row.entity_id;b.dataset.orgRole=role;b.setAttribute('aria-pressed',String(draft[role].has(row.entity_id)));
      b.append(E('strong',row.name),E('code',row.entity_id),E('small',[row.area_id||'Ohne HA-Bereich',row.derived?'Abgeleiteter / logischer Status':row.platform||'Plattform unklar',row.state||'Kein Zustand',row.unit||''].join(' · ')));list.append(b);}node.append(list);
    if(hadFocus){const replacement=[...list.querySelectorAll('button')].find(b=>b.dataset.orgCandidate===focusedId);(replacement||searches[role]).focus({preventScroll:true});}
  }
  function render(){const helperOpen=form.querySelector('#org-helpers')?.open||false;const view=new Map([...form.querySelectorAll('[data-org-group]')].map(e=>[e.dataset.orgGroup,{open:e.open,query:e.querySelector('input[type=search]')?.value||''}]));scanOffset=0;selectionOffset=0;form.replaceChildren();resetReports();planPanel.replaceChildren();history.replaceChildren();
    draft=Object.fromEntries(Object.keys(labels).map(k=>[k,new Set((data.bindings.assignments[k]||[]).map(r=>r.entity_id||r.saved_entity_id))]));
    const topicGrid=E('div','','org-topic-grid');form.append(topicGrid);
    const topicNodes={};
    for(const topic of topics){const section=E('section','','org-topic');section.dataset.orgTopic=topic.id;section.append(E('h3',topic.title),E('p',topic.description,'ps-muted'),E('div','','org-topic-summary'));topicGrid.append(section);topicNodes[topic.role]=section;}
    const helpers=E('details');helpers.id='org-helpers';helpers.open=helperOpen;helpers.append(E('summary','Anwesenheitskette & vorhandene Helfer zuordnen'),E('p','Sensoren → Bestandsautomation mit Nachlauf → Boolean → öffentlicher Präsenzsensor. Hier verbinden, nicht die HA-Regeln oder deren Zeiten verändern.','ps-muted'));
    const suggested=data.setup_suggestions?.assignments||{};
    if(Object.keys(suggested).length){
      const proposal=E('section');proposal.id='org-zone-suggestions';proposal.append(E('h3','Aus deiner Zone vorbefüllen'));
      for(const [role,ids] of Object.entries(suggested))proposal.append(E('p',labels[role]+': '+ids.map(id=>chosen(role,id)).join(', ')));
      proposal.append(E('p','Nur eindeutig gespeicherte Zonenrollen und bestätigte Rohquellen. Vorhandene oder bereits bearbeitete Zuordnungen bleiben erhalten. Noch nichts gespeichert.','ps-muted'),
        B('Diese Zonenvorschläge vormerken',()=>run(async()=>{
          assertCurrent();let count=0;
          for(const [role,ids] of Object.entries(suggested))if(draft[role]&&!draft[role].size){
            draft[role]=new Set(ids);drawChoices(role);count+=ids.length;
            const group=form.querySelector('[data-org-group="'+role+'"]');if(group)group.open=true;
          }
          notice(count?`${count} Zuordnungen vorgemerkt. Gemeinsam prüfen und einmal speichern.`:'Bestehende Auswahl bleibt erhalten; keine freie Funktion zu ergänzen.');
        })));
      helpers.append(proposal);helpers.open=true;
    }
    const timingLabel=E('label','Nachlaufverfahren der Bestandskette');const select=E('select');select.id='org-timing';for(const [v,t] of Object.entries(timingLabels)){const o=E('option',t);o.value=v;select.append(o);}select.value=data.bindings.timing;select.addEventListener('change',updateButtons);timingLabel.append(select);helpers.append(timingLabel);
    const groups=E('div','','org-role-grid');
    for(const role of Object.keys(labels)){const group=E('details');group.dataset.orgGroup=role;group.open=view.get(role)?.open??['presence_status','presence_timer','presence_output'].includes(role);
      const summary=E('summary',topicNodes[role]?'Automationen zuordnen':labels[role]);group.append(summary);const label=E('label','Bestand durchsuchen');const search=E('input');search.type='search';search.value=view.get(role)?.query||'';search.setAttribute('aria-label',labels[role]+' im gesamten Bestand suchen');search.placeholder='Name, ID, Bereich oder Plattform …';label.append(search);searches[role]=search;
      const choices=E('div');selections[role]=choices;search.addEventListener('input',()=>drawChoices(role));group.append(label,choices);(topicNodes[role]||groups).append(group);drawChoices(role);
    }helpers.append(groups);form.append(helpers);drawAutomationTopics();
    const actions=E('div','','selection-tools');const save=B('Funktionszuordnung speichern',()=>run(async()=>{
      assertCurrent(); // The explicit save commits the visible mapping; no second generic confirmation.
      const origin=ticket(),payload={revision:data.revision,...JSON.parse(encode()),confirm:true};
      pendingSave=origin;
      let acknowledged=false;
      try{
        const result=await request(path(),{method:'PATCH',body:JSON.stringify(payload)});
        acknowledged=true;
        if(!current(origin)||result.zone_id!==origin.zone||result.saved!==true)throw Error('Speicherantwort passt nicht mehr zur Ansicht.');
        // Keep the visible draft until the canonical reload has actually succeeded.
        await afterSave();
        const refreshed=ticket(),fresh=await request(path());
        if(!current(refreshed)||fresh.zone_id!==origin.zone||fresh.revision!==basis.revision)throw Error('Nachladen nicht bestätigt.');
        data=fresh;loadedBasis={...basis};pendingSave=false;render();
        notice('Funktionszuordnung gespeichert und erneut geladen. Keine Haussteuerung aktiviert.');
      }catch(error){
        if(!acknowledged&&error.status>=400&&error.status<500){pendingSave=false;throw error;}
        loadedBasis=null;
        notice('Speicherstand noch nicht abgeglichen. Auswahl bleibt sichtbar; nicht erneut speichern. „Gespeicherten Stand prüfen“ liest nur den aktuellen Stand.');
      }
    }));save.id='org-save';actions.append(save,B('Entwurf verwerfen',()=>{if(busy)return;if(pendingSave){notice('Speicherstand zuerst über „Gespeicherten Stand prüfen“ abgleichen.');return;}if(data)render();notice('Lokaler Entwurf verworfen.');}));form.append(actions);
    const analysis=B('Ausgewählte Automationen analysieren',()=>run(async()=>{
      assertCurrent();const generation=++serial,zid=basis.zone,rev=data.revision;
      const ids=selectedAutomations();
      if(!ids.length){notice('Zuerst mindestens eine Automation zuordnen.');return;}
      if(selectionOffset>=ids.length)selectionOffset=0;
      const slice=ids.slice(selectionOffset,selectionOffset+8);
      const response=await request(path()+'/analyze',{method:'POST',body:JSON.stringify({revision:rev,automation_ids:slice})});
      if(generation!==serial||zid!==basis.zone||rev!==basis.revision)return;
      const nextOffset=selectionOffset+slice.length;
      scanOffset=0;resetScanButton();
      drawReports(response,{append:true,reset:selectionOffset===0,mode:'selection',requested:nextOffset,total:ids.length});
      reportView.filter='all';renderReports();selectionOffset=nextOffset;
      analysis.textContent=selectionOffset<ids.length?'Nächste ausgewählte Automationen analysieren':'Auswahl erneut analysieren';
      notice(nextOffset+' von '+ids.length+' ausgewählten Automationen angefragt. Keine Referenz oder Automation verändert; Verhaltensprüfung bleibt offen.');
    }));analysis.id='org-analyze';analysis.dataset.orgWrite='read';form.append(analysis,E('p','Die Auswahl darf zunächst ein Entwurf bleiben. Jeder Klick liest höchstens acht verschiedene Automationen aus allen Themen; gemeinsam zugeordnete Regeln nur einmal. Keine komplette Verbraucherlandschaft.','ps-muted'));
    const scan=B('Globalen Automationsbestand paketweise prüfen',()=>run(async()=>{
      assertCurrent();const generation=++serial,zid=basis.zone,rev=data.revision;
      const ids=data.catalog.filter(r=>r.entity_id.startsWith('automation.')).map(r=>r.entity_id).sort();
      const slice=ids.slice(scanOffset,scanOffset+8);
      if(!slice.length){notice('Alle katalogisierten Automationspakete wurden angefragt. Nicht lesbare und dynamische Verbraucher bleiben ungeklärt.');return;}
      const response=await request(path()+'/analyze',{method:'POST',body:JSON.stringify({revision:rev,automation_ids:slice})});
      if(generation!==serial||zid!==basis.zone||rev!==basis.revision)return;
      const nextOffset=scanOffset+slice.length;
      drawReports(response,{append:true,reset:scanOffset===0,mode:'inventory',requested:nextOffset,total:ids.length});scanOffset=nextOffset;selectionOffset=0;resetAnalysisButton();
      notice(`Paket geprüft: ${scanOffset} von ${ids.length} katalogisierten Automationen angefragt. ${response.unread.length} in diesem Paket nicht lesbar. Kein vollständiger Verbraucher- oder Verhaltensnachweis.`);
      scan.textContent=scanOffset<ids.length?'Nächste bis zu acht Automationen prüfen':'Alle katalogisierten Pakete angefragt';
      scan.disabled=scanOffset>=ids.length;
    }));scan.id='org-scan';const globalScan=E('details');globalScan.id='org-global-scan';globalScan.append(E('summary','Zonenübergreifenden Bestand prüfen'),scan,E('p','Nicht auf diese Zone eingeschränkt. Jeder Klick liest höchstens acht weitere Konfigurationen; diese Prüfung ersetzt die Auswahlprüfung in der Ergebnisliste.','ps-muted'));form.append(globalScan);

    const names=E('details');names.id='org-naming';names.append(E('summary','Einheitliche Namen & technische Bereinigung'));
    for(const row of data.naming){const line=E('label','','org-name-row');const check=E('input');check.type='checkbox';check.value=row.role;check.disabled=!row.name_change_eligible;check.dataset.orgNameRole=row.role;
      line.append(check,E('span',row.current_name+' → '+row.proposed_name),E('code',row.entity_id));names.append(line);
      if(row.shared_zone_ids?.length)names.append(E('p','Gemeinsam genutzt mit '+row.shared_zone_ids.join(', ')+'. Einseitige Umbenennung gesperrt; gemeinsamen Namensraum klären.','ps-warning'));
      names.append(E('p',`Technische Ziel-ID: ${row.proposed_entity_id}. ${row.entity_id_change.collision?'Namenskollision. ':''}ID-Migration gesperrt: Skripte, Szenen, Dashboards, Helferkonfigurationen und externe Verbraucher noch nicht vollständig geprüft.`,'ps-muted'));}
    if(!data.naming.length)names.append(E('p','Zuerst vorhandene Helferfunktionen zuordnen und speichern.'));
    const preview=B('Namensbereinigung prüfen',()=>run(async()=>{assertCurrent();if(changed())throw Error('Funktionszuordnung vor der Namensbereinigung speichern.');await requestPlan('/names',{method:'POST',body:JSON.stringify({revision:data.revision,roles:[...names.querySelectorAll('input:checked')].map(x=>x.value)})});}));preview.id='org-name-preview';preview.dataset.orgWrite='preview';names.append(preview);form.append(names);
    for(const p of data.plans){const b=B(`${outcomeLabels[p.state]||p.state} · ${p.kind} · ${p.id.slice(0,8)}`,()=>run(async()=>{assertCurrent();await requestPlan('/plans/'+p.id);}));b.className='org-plan-history';history.append(b);}
    initial=encode();updateButtons();
  }
  function drawReports(response,options={}){if(response.zone_id!==basis.zone||response.revision!==basis.revision)throw Error('Veraltete Analyse verworfen');
    if(options.reset)resetReports();
    if(!options.append){resetReports();reportView.filter='all';reportView.mode='selection';reportView.requested=(response.reports?.length||0)+(response.unread?.length||0);reportView.total=reportView.requested;scanOffset=0;const scan=root?.querySelector('#org-scan');if(scan){scan.textContent='Globalen Automationsbestand paketweise prüfen';scan.disabled=false;}}
    else {reportView.mode=options.mode||'inventory';reportView.requested=options.requested||reportView.requested;reportView.total=options.total||reportView.total;}
    for(const row of response.reports||[]){reportView.reports.set(row.automation_id,row);reportView.unread.delete(row.automation_id);}
    for(const row of response.unread||[]){if(!reportView.reports.has(row.automation_id))reportView.unread.set(row.automation_id,row);}
    renderReports();
  }
  function renderReports(){reports.replaceChildren();
    const allReports=[...reportView.reports.values()];const allUnread=[...reportView.unread.values()];
    const missingCount=allReports.filter(referenceAttention).length,triggerCount=allReports.filter(triggerAttention).length,lifecycleCount=allReports.filter(lifecycleAttention).length;
    const toolbar=E('section','','org-report-tools');
    const summary=E('p',reportView.mode==='inventory'
      ?`Geprüft: ${reportView.requested} von ${reportView.total} · ${allReports.length} lesbar · ${allUnread.length} nicht lesbar · ${missingCount} mit Referenzhinweisen · ${triggerCount} mit Auslöserhinweisen · ${lifecycleCount} mit Präsenzablauf-Hinweisen`
      :`Auswahl: ${reportView.requested} von ${reportView.total} angefragt · ${allReports.length} lesbar · ${allUnread.length} nicht lesbar · ${missingCount} mit Referenzhinweisen · ${triggerCount} mit Auslöserhinweisen · ${lifecycleCount} mit Präsenzablauf-Hinweisen`,'ps-muted');
    summary.id='org-report-summary';summary.setAttribute('role','status');
    const label=E('label','Ergebnisse anzeigen');const filter=E('select');filter.id='org-report-filter';filter.setAttribute('aria-controls','org-report-list');
    for(const [value,text] of [['attention','Handlungsbedarf'],['lifecycle','Präsenzablauf fachlich prüfen'],['missing','Referenzen fehlen oder sind nicht aktuell'],['trigger','Auslöserkennungen auffällig'],['unread','Nicht lesbar'],['all','Alle gelesenen Ergebnisse']]){const option=E('option',text);option.value=value;filter.append(option);}
    filter.value=reportView.filter;filter.addEventListener('change',()=>{reportView.filter=filter.value;renderReports();});label.append(filter);toolbar.append(summary,label);reports.append(toolbar);
    const list=E('div');list.id='org-report-list';reports.append(list);
    const showUnread=['attention','unread','all'].includes(reportView.filter);
    if(showUnread)for(const missed of allUnread.sort((a,b)=>a.automation_id.localeCompare(b.automation_id))){const warning=E('p',`${missed.automation_id}: Konfiguration nicht lesbar. Prüfung unvollständig.`,'ps-warning');warning.dataset.orgUnread=missed.automation_id;list.append(warning);}
    const visible=allReports.filter(report=>reportView.filter==='all'||(reportView.filter==='attention'&&reportAttention(report))||(reportView.filter==='lifecycle'&&lifecycleAttention(report))||(reportView.filter==='missing'&&referenceAttention(report))||(reportView.filter==='trigger'&&triggerAttention(report)))
      .sort((a,b)=>Number(reportAttention(b))-Number(reportAttention(a))||Number(lifecycleAttention(b))-Number(lifecycleAttention(a))||Number(triggerAttention(b))-Number(triggerAttention(a))||a.automation_id.localeCompare(b.automation_id));
    for(const report of visible){const panel=E('details');panel.open=true;panel.dataset.orgReport=report.automation_id;panel.append(E('summary',report.automation_id));
      panel.append(E('p','Nachlauf erkannt: '+(report.timing_methods.map(x=>timingLabels[x]).join(' / ')||'Kein unterstütztes Verfahren erkannt'),'ps-muted'));
      appendTriggerIntegrity(panel, report.trigger_integrity);
      const lifecycle=report.presence_lifecycle;
      if(lifecycle?.findings?.length){const review=E('section','','org-lifecycle');review.append(E('h4','Präsenzablauf fachlich prüfen'));
        const copy={boundary_close_can_clear_presence:'Ein geschlossenes Zugangselement kann den abgeleiteten Raumstatus ausschalten. Türschluss belegt nicht, dass niemand mehr im Bereich ist.',activity_edge_only_refreshes_timeout:'Der Nachlauf wird bei einem erkannten Bewegungsbeginn gestartet oder erneuert. Solange der Sensor ohne Zustandswechsel aktiv bleibt, entsteht kein weiterer Startimpuls.'};
        for(const finding of lifecycle.findings){const evidence=finding.evidence||[];const paths=[...new Set(evidence.flatMap(row=>row.trigger_paths||[]))];review.append(E('p',`${copy[finding.id]||'Präsenzlogik benötigt eine fachliche Prüfung'} Fundstellen: ${paths.join(', ')||'statisch nicht vollständig auflösbar'}. Nächster Schritt: gewünschtes Anwesenheits- und Nachlaufverhalten in der bestehenden HA-Automation prüfen; nichts wird automatisch geändert.`,'ps-warning'));}
        review.append(E('p','Struktureller Hinweis, kein Laufzeitbeweis und keine Sicherheits- oder Reparaturfreigabe.','ps-muted'));panel.append(review);}
      if(!reportReplacements.has(report.automation_id))reportReplacements.set(report.automation_id,new Map());const replacements=reportReplacements.get(report.automation_id);
      for(const finding of report.findings){const row=E('article','','org-finding');row.dataset.orgFinding=finding.entity_id;row.append(E('strong',finding.name),E('code',finding.entity_id),E('span',statusLabels[finding.status]||finding.status,'ps-badge'));
        if(finding.derived)row.append(E('small','Abgeleitete Quelle: keine zusätzliche unabhängige Messung.'));
        for(const hint of finding.role_hints){if(finding.status==='present'){const b=B('Als '+labels[hint]+' vormerken',()=>{if(!draft[hint].has(finding.entity_id))choose(hint,finding.entity_id);notice('Vorgemerkt, noch nicht gespeichert.');});row.append(b);}}
        const places=E('details');places.append(E('summary','Fundstellen und Bedeutung'));for(const ref of finding.references)places.append(E('p',`${ref.path} · ${ref.kind==='template_literal'?'statisch erkennbare Template-Referenz':'direkte Referenz'} · ${ref.enabled===true?'aktiv':ref.enabled===false?'deaktivierter Zweig':'Aktivierung unbekannt'}`));row.append(places);
        if(finding.candidates.length){const label=E('label','Ersatzkandidat ausdrücklich wählen');const select=E('select');select.dataset.orgReplacement=finding.entity_id;const blank=E('option','Keine Ersetzung');blank.value='';select.append(blank);
          for(const c of finding.candidates){const option=E('option',`${c.name} · ${c.entity_id} · ${c.unit||'Einheit unklar'} · ${c.reasons.includes('storage_key_matches_old_object_id')?'Speicherkennung passt':'Ähnlichkeit, keine Identitätsbestätigung'}`);option.value=c.entity_id;select.append(option);}select.value=replacements.get(finding.entity_id)||'';select.addEventListener('change',()=>{if(select.value)replacements.set(finding.entity_id,select.value);else replacements.delete(finding.entity_id);});label.append(select);row.append(label);}
        panel.append(row);
      }
      panel.append(E('p','Grenzen: '+(report.limitations.join(', ')||'Nur direkte Strukturprüfung; keine nachgewiesene Verhaltensgleichheit'),'ps-warning'));
      const repair=B('Gewählte Reparaturstellen prüfen',()=>run(async()=>{assertCurrent();await requestPlan('/repair-preview',{method:'POST',body:JSON.stringify({revision:data.revision,automation_id:report.automation_id,fingerprint:report.fingerprint,replacements:Object.fromEntries(replacements)})});}));repair.dataset.orgWrite='preview';panel.append(repair);list.append(panel);
    }
    if(!list.children.length)list.append(E('p',reportView.filter==='all'?'Keine gelesenen Ergebnisse vorhanden.':'Für diesen Filter liegt in der aktuellen Prüfsitzung kein Ergebnis vor.','ps-muted'));
    updateButtons();
  }
  async function requestMetadataPlan(plan, action, body){
    assertCurrent();if(changed())throw Error('Offene Zuordnung zuerst speichern oder verwerfen');
    const t=ticket();const result=await request(`api/v1/zones/${encodeURIComponent(t.zone)}/ontology/${plan.id}/${action}`,{method:'POST',body:JSON.stringify(body)});
    if(!current(t))return;
    if(result.binding){
      await afterSave();if(basis?.zone!==t.zone)return;
      const updated=await request(path());
      if(updated.zone_id!==basis.zone||updated.revision!==basis.revision)throw Error('Zonenstand neu laden');
      data=updated;loadedBasis={...basis};render();
    }
    drawPlan(result);
  }
  function drawMetadataPlan(plan){
    planPanel.append(E('p','Zonen- und Rollenlabels sowie die ausdrücklich gezeigten Anzeigenamen. Technische IDs und physische Orte bleiben erhalten.'));
    const names=plan.details.label_names||{};
    for(const op of plan.operations){
      const row=E('div','','org-plan-change');
      if(op.effect==='create_zone_label')row.append(E('strong','Neues Zonenlabel: '+op.name),E('p',op.receipt?.label?'Anlagebeleg vorhanden: '+op.receipt.label.label_id:'Noch kein Anlagebeleg. Ein gleicher Name beweist keine eigene Anlage.'));
      else row.append(E('strong',op.entity_id),E('p',`${op.before.name||'Standardname'} → ${op.after.name||'Standardname'}`),
        E('p','Labels vorher: '+(op.before.labels.map(id=>names[id]||id).join(', ')||'keine')),
        E('p','Labels danach: '+(op.after.labels.map(id=>names[id]||id).join(', ')||'keine')));
      if(op.outcome)row.append(E('small',op.outcome));planPanel.append(row);
    }
    if(plan.binding)planPanel.append(E('p','Zonenlabel verbunden; Anlage und Zuordnung zurückgelesen.'));
    planPanel.append(B('Gespeicherten Planstatus laden',()=>run(async()=>{await requestPlan('/plans/'+plan.id);})));
    if(plan.revision===basis.revision&&plan.state==='preview'){
      planPanel.append(B('Diesen Zonenplan anwenden',()=>run(()=>requestMetadataPlan(plan,'apply',{sha256:plan.sha256,confirm:true}))));
    }else if(plan.revision===basis.revision&&['applying','attention'].includes(plan.state)&&plan.details.creates_zone_label&&!plan.operations.some(op=>op.outcome==='conflict')){
      planPanel.append(E('p','Unklare Schritte werden nur zurückgelesen. Bereits bestätigte Anlage wird nicht wiederholt; noch nicht begonnene Schritte des bestätigten Plans können weiterlaufen.','ps-warning'),
        B('Bestätigten Zonenplan weiterprüfen',()=>run(()=>requestMetadataPlan(plan,'apply',{sha256:plan.sha256,confirm:true}))));
    }
    if(plan.state==='verified')planPanel.append(B('Metadaten-Rücknahme prüfen',()=>run(()=>requestMetadataPlan(plan,'restore-preview',{revision:basis.revision}))));
    for(const limit of plan.details.limits||[])planPanel.append(E('p',limit,'ps-muted'));
  }
  function drawPlan(plan){planPanel.replaceChildren();planPanel.append(E('h3',outcomeLabels[plan.state]||plan.state));if(plan.state==='unchanged'){planPanel.append(E('p',plan.message));return;}
    planPanel.dataset.planId=plan.id;
    if(plan.kind==='ontology'||plan.kind==='structure_labels'){drawMetadataPlan(plan);return;}
    if(plan.kind==='presence_helper'||plan.kind==='presence_package'){
      planPanel.append(E('p',plan.kind==='presence_helper'?'Einzelhelfer-Anlageplan einschließlich gegebenenfalls geplanter Beschriftung. Kein Anschluss und keine Steuerungsübernahme.':'Eigenes Ausgangspaket; kein Namensplan.'));
      for(const op of plan.operations)planPanel.append(E('p',op.entity_id+' · '+(op.outcome||'Noch nicht angelegt'),'org-plan-change'));
      planPanel.append(E('p','Gespeicherter Anlegenachweis, kein aktueller Funktionsbeleg. Unklare Ergebnisse nicht blind wiederholen. Angelegte Helfer werden hier nicht gelöscht.','ps-warning'));
      return;
    }
    for(const op of plan.operations){const row=E('p','','org-plan-change');row.append(E('strong',op.entity_id||op.path),E('span',`${op.before_entity_id||op.before||'Standardname ohne Override'} → ${op.after_entity_id||op.after||'Standardname ohne Override'}`));if(op.outcome)row.append(E('small',op.outcome+(op.write_response_confirmed===false?' · Antwort verloren, Zielzustand gelesen; keine Rücknahmeberechtigung abgeleitet':'')));planPanel.append(row);}
    if(plan.kind==='repair_review'){
      planPanel.append(E('p','Reparaturvorschau gespeichert. Die aufgeführten Stellen wurden erneut gegen die Automation geprüft. Dieser Release schreibt noch keine Automationskonfiguration; auch ein passender Ersatz ist noch kein Nachweis gleichen Verhaltens.','ps-warning'));return;
    }
    planPanel.append(E('p','Ändert nur die Anzeigenamen dieser Helfer. Entity-IDs, Werte, Bereiche, Labels und Verbraucher bleiben unverändert. HA und PilotSuite sind keine gemeinsame atomare Transaktion; Teilstände werden einzeln protokolliert. Anzeigenamen-basierte Vorlagen und Sprachassistenten können betroffen sein.','ps-muted'));
    if(plan.state==='preview'&&plan.revision!==basis.revision){planPanel.append(E('p','Vorschau stammt aus einem älteren Zonenstand. Bitte einen neuen Plan prüfen.','ps-warning'));return;}
    if(plan.state==='preview'){const l=E('label');const c=E('input');c.type='checkbox';c.id='org-confirm-names';l.append(c,document.createTextNode('Genau diese Anzeigenamen ändern'));const apply=B('Geprüften Namensplan anwenden',()=>run(async()=>{assertCurrent();if(changed())throw Error('Offenen Zuordnungsentwurf zuerst speichern oder verwerfen');if(!c.checked)return;await requestPlan('/plans/'+plan.id+'/apply',{method:'POST',body:JSON.stringify({sha256:plan.sha256,confirm:true})});}));apply.id='org-apply-names';apply.disabled=true;c.addEventListener('change',()=>apply.disabled=!c.checked||busy);planPanel.append(l,apply);}
    else {planPanel.append(B('Gespeicherten Planstatus laden',()=>run(async()=>{assertCurrent();await requestPlan('/plans/'+plan.id);})));
      if(plan.operations.some(op=>op.outcome==='verified'&&op.write_response_confirmed))planPanel.append(B('Rücknahme prüfen',()=>run(async()=>{assertCurrent();await requestPlan('/plans/'+plan.id+'/restore-preview',{method:'POST',body:JSON.stringify({revision:basis.revision})});})));
      if(plan.state!=='verified')planPanel.append(E('p','Nicht vollständig bestätigt. Bereits bestätigte Änderungen sind oben markiert. Unklare Operationen werden nicht automatisch wiederholt.','ps-warning'));
    }
  }
  window.PilotSuiteOrganization={
    focusRole(role){if(!Object.hasOwn(labels,role)||!basis)return;requestedRole={role,zone:basis.zone};window.requestAnimationFrame(focusRequestedRole);},
    mount(node,onSaved){root=node;afterSave=onSaved;root.id='ps-organization';root.append(E('h2','Vorhandene Automationen & Helfer'),E('p','Anwesenheit, Licht und weitere Aufgaben getrennt zuordnen. Dieselbe Automation darf mehreren Themen oder Zonen dienen; sie wird nicht kopiert.'));
      root.append(E('p','Home Assistant steuert weiterhin. Zuordnen speichert nur die Verbindung; Prüfen liest die Struktur. Beides bestätigt weder korrektes Verhalten noch eine Steuerungsübernahme.','ps-muted'));
      const back=E('a','Zur Zonenansicht und zum Bestandsvergleich');back.href='#ps-zone';back.id='org-back-zone';root.append(back);
      message=E('p','','edit-status');message.id='org-message';message.setAttribute('role','status');form=E('div');form.id='org-form';reports=E('div');reports.id='org-reports';planPanel=E('section');planPanel.id='org-plan';planPanel.setAttribute('aria-label','Geprüfter Ordnungsplan');history=E('div');history.id='org-history';
      const loadButton=B('Bestand & Zuordnungen laden',load);loadButton.id='org-load';root.append(loadButton,message,form,reports,planPanel,E('h3','Gespeicherte Pläne'),history);},
    context(zone,revision){if(!zone||!Number.isSafeInteger(revision))return;
      if(basis&&basis.zone!==zone)requestedRole=null;
      if(basis&&(basis.zone!==zone||basis.revision!==revision)){serial++;resetReports();if(!changed()&&!pendingSave){data=null;initial='';loadedBasis=null;form.replaceChildren();planPanel.replaceChildren();history.replaceChildren();}notice('Zonenstand geändert. Bestand erneut laden.');}
      basis={zone,revision};updateButtons();},
    dirty:()=>busy||!!pendingSave||changed(),
    invalidate(){serial++;loadedBasis=null;resetReports();planPanel?.replaceChildren();notice('Datenstand nicht bestätigt. Bestand neu laden; offene Auswahl bleibt erhalten.');updateButtons();}
  };
})();
