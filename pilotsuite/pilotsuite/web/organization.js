/* Inventory & order: one canonical server profile, explicit reads and confirmed edits. */
(() => {
  'use strict';
  const E=(tag,text='',cls='')=>{const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e;};
  const B=(label,action)=>{const b=E('button',label);b.type='button';b.addEventListener('click',action);return b;};
  const labels={presence_sources:'Präsenzquellen',presence_status:'Raumstatus',presence_timer:'Nachlauftimer',
    presence_duration:'Nachlauf-Dauer',manual_override:'Manuelle Bedienung',automation_blocker:'Automatiksperre',
    presence_automations:'Zuständige Automationen'};
  const timingLabels={observe:'Nur beobachten / noch nicht zugeordnet',existing_for:'Bestehender for:-Nachlauf',timer:'Vorhandener Timer',external:'Andere Bestandslogik'};
  const statusLabels={present:'Vorhanden',missing:'Referenz fehlt',disabled:'Deaktiviert',unavailable:'Nicht verfügbar',snapshot_stale:'Datenstand nicht aktuell'};
  const outcomeLabels={preview:'Vorschau – noch nicht ausgeführt',applying:'Unterbrochen oder noch in Bearbeitung – nicht wiederholen',verified:'Änderung zurückgelesen',attention:'Teilweise / unklar – Einzelstatus prüfen',unchanged:'Bereits einheitlich'};
  let root,message,form,reports,planPanel,history,data=null,basis=null,loadedBasis=null,draft={},initial='',busy=false,serial=0,afterSave;
  const selections={}, searches={};
  const encode=()=>JSON.stringify({assignments:Object.fromEntries(Object.entries(draft).map(([k,v])=>[k,[...v].sort()])),timing:form?.querySelector('#org-timing')?.value||'observe'});
  const changed=()=>data!==null&&initial!==encode();
  const notice=t=>{if(message)message.textContent=t;};
  const request=async(path,options={})=>{const response=await fetch(path,{headers:{'Content-Type':'application/json'},...options});const d=await response.json();if(!response.ok)throw Error(d.message||'Zugriff nicht bestätigt');return d;};
  const path=()=>`api/v1/zones/${encodeURIComponent(basis.zone)}/organization`;
  const assertCurrent=()=>{if(!data||!basis||!loadedBasis||loadedBasis.zone!==basis.zone||loadedBasis.revision!==basis.revision)throw Error('Zonenstand geändert. Bestand neu laden; Entwurf bleibt sichtbar.');};
  async function run(fn){if(busy)return;busy=true;updateButtons();try{await fn();}catch(error){notice(error.message);}finally{busy=false;updateButtons();}}
  function updateButtons(){if(!root)return;root.querySelectorAll('input,select').forEach(e=>{if(busy){if(e.dataset.orgWasDisabled===undefined)e.dataset.orgWasDisabled=String(e.disabled);e.disabled=true;}else if(e.dataset.orgWasDisabled!==undefined){e.disabled=e.dataset.orgWasDisabled==='true';delete e.dataset.orgWasDisabled;}});root.querySelectorAll('button[data-org-write]').forEach(b=>b.disabled=busy||!data||!loadedBasis||loadedBasis.zone!==basis?.zone||loadedBasis.revision!==basis?.revision);const save=root.querySelector('#org-save');if(save)save.disabled=busy||!changed();}
  async function load(){if(selectionBusy||contextEditing||zoneFormOpen||selectionDraft?.dirty){notice('Andere Bearbeitung zuerst speichern oder abbrechen.');return;}if(changed()){notice('Entwurf zuerst speichern oder verwerfen.');return;}return run(async()=>{
    const current={...basis},generation=++serial;
    const response=await request(path());
    if(generation!==serial||current.zone!==basis.zone||current.revision!==basis.revision)return;
    if(response.zone_id!==current.zone||response.revision!==current.revision)throw Error('Serverstand hat sich geändert. Zonenansicht aktualisieren.');
    data=response;loadedBasis=current;render();notice('Globaler Bestand geladen. Zuordnung ist keine Steuerungs- oder Lernfreigabe.');
  });}
  function chosen(role,eid){const row=data.catalog.find(r=>r.entity_id===eid);return row?`${row.name} · ${eid}`:eid+' · Identität ungeklärt';}
  function choose(role,eid){if(busy)return;const max=data.roles[role].max;
    if(draft[role].has(eid))draft[role].delete(eid);
    else if(max===1)draft[role]=new Set([eid]);
    else if(draft[role].size<max)draft[role].add(eid);
    else{notice(`Maximal ${max} Zuordnungen für ${labels[role]}.`);return;}
    drawChoices(role);updateButtons();
  }
  function drawChoices(role){const node=selections[role];node.replaceChildren();const picked=E('div','','org-picked');
    for(const eid of draft[role]){const chip=B(chosen(role,eid)+' ×',()=>choose(role,eid));chip.className='org-chip';chip.setAttribute('aria-label',labels[role]+': '+eid+' entfernen');picked.append(chip);}node.append(picked);
    const q=searches[role].value.trim().toLocaleLowerCase('de');const candidates=data.catalog.filter(r=>data.roles[role].domains.includes(r.entity_id.split('.')[0])&&!r.disabled&&r.in_registry&&[r.name,r.entity_id,r.area_id||'',r.platform||''].join(' ').toLocaleLowerCase('de').includes(q));
    node.append(E('p',`${draft[role].size} gewählt · ${candidates.length} passend · bis zu 30 Treffer angezeigt`,'ps-muted'));
    const list=E('div','','org-candidates');
    for(const row of candidates.slice(0,30)){const b=B('',()=>choose(role,row.entity_id));b.dataset.orgCandidate=row.entity_id;b.dataset.orgRole=role;b.setAttribute('aria-pressed',String(draft[role].has(row.entity_id)));
      b.append(E('strong',row.name),E('code',row.entity_id),E('small',[row.area_id||'Ohne HA-Bereich',row.derived?'Abgeleiteter / logischer Status':row.platform||'Plattform unklar',row.state||'Kein Zustand',row.unit||''].join(' · ')));list.append(b);}node.append(list);
  }
  function render(){form.replaceChildren();reports.replaceChildren();planPanel.replaceChildren();history.replaceChildren();
    draft=Object.fromEntries(Object.keys(labels).map(k=>[k,new Set((data.bindings.assignments[k]||[]).map(r=>r.entity_id||r.saved_entity_id))]));
    const timingLabel=E('label','Nachlaufverfahren');const select=E('select');select.id='org-timing';for(const [v,t] of Object.entries(timingLabels)){const o=E('option',t);o.value=v;select.append(o);}select.value=data.bindings.timing;select.addEventListener('change',updateButtons);timingLabel.append(select);form.append(timingLabel);
    const groups=E('div','','org-role-grid');
    for(const role of Object.keys(labels)){const group=E('details');group.dataset.orgGroup=role;group.open=['presence_status','presence_timer','presence_automations'].includes(role);
      const summary=E('summary',labels[role]);group.append(summary);const label=E('label','Bestand durchsuchen');const search=E('input');search.type='search';search.setAttribute('aria-label',labels[role]+' im gesamten Bestand suchen');search.placeholder='Name, ID, Bereich oder Plattform …';label.append(search);searches[role]=search;
      const choices=E('div');selections[role]=choices;search.addEventListener('input',()=>drawChoices(role));group.append(label,choices);groups.append(group);drawChoices(role);
    }form.append(groups);
    const actions=E('div','','selection-tools');const save=B('Funktionszuordnung speichern',()=>run(async()=>{
      assertCurrent();if(!window.confirm('Diese Funktionszuordnung speichern? Bestehende Lernquellen, Lernfreigaben und HA-Steuerung bleiben unverändert.'))return;
      const payload={revision:data.revision,...JSON.parse(encode()),confirm:true};
      const result=await request(path(),{method:'PATCH',body:JSON.stringify(payload)});
      if(result.zone_id!==basis.zone)throw Error('Zonenwechsel während des Speicherns; aktuellen Stand neu laden.');
      initial=encode();notice('Funktionszuordnung gespeichert. Keine Haussteuerung aktiviert.');
      data=null;loadedBasis=null;form.replaceChildren();reports.replaceChildren();planPanel.replaceChildren();history.replaceChildren();
      await afterSave();
      const fresh=await request(path());
      if(fresh.zone_id!==basis.zone||fresh.revision!==basis.revision)throw Error('Gespeichert; aktuellen Bestand bitte erneut laden.');
      data=fresh;loadedBasis={...basis};render();
    }));save.id='org-save';actions.append(save,B('Entwurf verwerfen',()=>{if(busy)return;if(data)render();notice('Lokaler Entwurf verworfen.');}));form.append(actions);
    const analysis=B('Ausgewählte Automationen analysieren',()=>run(async()=>{
      assertCurrent();const generation=++serial,zid=basis.zone,rev=data.revision;
      const response=await request(path()+'/analyze',{method:'POST',body:JSON.stringify({revision:rev,automation_ids:[...draft.presence_automations]})});
      if(generation!==serial||zid!==basis.zone||rev!==basis.revision)return;
      drawReports(response);notice('Strukturprüfung abgeschlossen. Keine Referenz oder Automation verändert.');
    }));analysis.id='org-analyze';analysis.dataset.orgWrite='read';form.append(analysis,E('p','Die Auswahl darf zunächst ein Entwurf bleiben. Analyse liest nur die ausgewählten Automationen, keine komplette Verbraucherlandschaft.','ps-muted'));
    const names=E('details');names.id='org-naming';names.append(E('summary','Einheitliche Namen & technische Bereinigung'));
    for(const row of data.naming){const line=E('label','','org-name-row');const check=E('input');check.type='checkbox';check.value=row.role;check.disabled=!row.name_change_eligible;check.dataset.orgNameRole=row.role;
      line.append(check,E('span',row.current_name+' → '+row.proposed_name),E('code',row.entity_id));names.append(line);
      if(row.shared_zone_ids?.length)names.append(E('p','Gemeinsam genutzt mit '+row.shared_zone_ids.join(', ')+'. Einseitige Umbenennung gesperrt; gemeinsamen Namensraum klären.','ps-warning'));
      names.append(E('p',`Technische Ziel-ID: ${row.proposed_entity_id}. ${row.entity_id_change.collision?'Namenskollision. ':''}ID-Migration gesperrt: Skripte, Szenen, Dashboards, Helferkonfigurationen und externe Verbraucher noch nicht vollständig geprüft.`,'ps-muted'));}
    if(!data.naming.length)names.append(E('p','Zuerst vorhandene Helferfunktionen zuordnen und speichern.'));
    const preview=B('Namensbereinigung prüfen',()=>run(async()=>{assertCurrent();if(changed())throw Error('Funktionszuordnung vor der Namensbereinigung speichern.');const response=await request(path()+'/names',{method:'POST',body:JSON.stringify({revision:data.revision,roles:[...names.querySelectorAll('input:checked')].map(x=>x.value)})});drawPlan(response);}));preview.id='org-name-preview';preview.dataset.orgWrite='preview';names.append(preview);form.append(names);
    for(const p of data.plans){const b=B(`${outcomeLabels[p.state]||p.state} · ${p.kind} · ${p.id.slice(0,8)}`,()=>run(async()=>{assertCurrent();drawPlan(await request(path()+'/plans/'+p.id));}));b.className='org-plan-history';history.append(b);}
    initial=encode();updateButtons();
  }
  function drawReports(response){reports.replaceChildren();if(response.zone_id!==basis.zone||response.revision!==basis.revision)throw Error('Veraltete Analyse verworfen');
    for(const missed of response.unread)reports.append(E('p',`${missed.automation_id}: Konfiguration nicht lesbar. Prüfung unvollständig.`,'ps-warning'));
    for(const report of response.reports){const panel=E('details');panel.open=true;panel.append(E('summary',report.automation_id));
      panel.append(E('p','Nachlauf erkannt: '+(report.timing_methods.map(x=>timingLabels[x]).join(' / ')||'Kein unterstütztes Verfahren erkannt'),'ps-muted'));
      const replacements={};for(const finding of report.findings){const row=E('article','','org-finding');row.dataset.orgFinding=finding.entity_id;row.append(E('strong',finding.name),E('code',finding.entity_id),E('span',statusLabels[finding.status]||finding.status,'ps-badge'));
        if(finding.derived)row.append(E('small','Abgeleitete Quelle: keine zusätzliche unabhängige Messung.'));
        for(const hint of finding.role_hints){if(finding.status==='present'){const b=B('Als '+labels[hint]+' vormerken',()=>{if(!draft[hint].has(finding.entity_id))choose(hint,finding.entity_id);notice('Vorgemerkt, noch nicht gespeichert.');});row.append(b);}}
        const places=E('details');places.append(E('summary','Fundstellen und Bedeutung'));for(const ref of finding.references)places.append(E('p',`${ref.path} · ${ref.kind==='template_literal'?'statisch erkennbare Template-Referenz':'direkte Referenz'} · ${ref.enabled===true?'aktiv':ref.enabled===false?'deaktivierter Zweig':'Aktivierung unbekannt'}`));row.append(places);
        if(finding.candidates.length){const label=E('label','Ersatzkandidat ausdrücklich wählen');const select=E('select');select.dataset.orgReplacement=finding.entity_id;const blank=E('option','Keine Ersetzung');blank.value='';select.append(blank);
          for(const c of finding.candidates){const option=E('option',`${c.name} · ${c.entity_id} · ${c.unit||'Einheit unklar'} · ${c.reasons.includes('storage_key_matches_old_object_id')?'Speicherkennung passt':'Ähnlichkeit, keine Identitätsbestätigung'}`);option.value=c.entity_id;select.append(option);}select.addEventListener('change',()=>{if(select.value)replacements[finding.entity_id]=select.value;else delete replacements[finding.entity_id];});label.append(select);row.append(label);}
        panel.append(row);
      }
      panel.append(E('p','Grenzen: '+(report.limitations.join(', ')||'Nur direkte Strukturprüfung; keine nachgewiesene Verhaltensgleichheit'),'ps-warning'));
      const repair=B('Gewählte Reparaturstellen prüfen',()=>run(async()=>{assertCurrent();drawPlan(await request(path()+'/repair-preview',{method:'POST',body:JSON.stringify({revision:data.revision,automation_id:report.automation_id,fingerprint:report.fingerprint,replacements})}));}));repair.dataset.orgWrite='preview';panel.append(repair);reports.append(panel);
    }
    updateButtons();
  }
  function drawPlan(plan){planPanel.replaceChildren();planPanel.append(E('h3',outcomeLabels[plan.state]||plan.state));if(plan.state==='unchanged'){planPanel.append(E('p',plan.message));return;}
    planPanel.dataset.planId=plan.id;
    for(const op of plan.operations){const row=E('p','','org-plan-change');row.append(E('strong',op.entity_id||op.path),E('span',`${op.before_entity_id||op.before||'Standardname ohne Override'} → ${op.after_entity_id||op.after||'Standardname ohne Override'}`));if(op.outcome)row.append(E('small',op.outcome+(op.write_response_confirmed===false?' · Antwort verloren, Zielzustand gelesen; keine Rücknahmeberechtigung abgeleitet':'')));planPanel.append(row);}
    if(plan.kind==='repair_review'){
      planPanel.append(E('p','Reparaturvorschau gespeichert. Die aufgeführten Stellen wurden erneut gegen die Automation geprüft. Dieser Release schreibt noch keine Automationskonfiguration; auch ein passender Ersatz ist noch kein Nachweis gleichen Verhaltens.','ps-warning'));return;
    }
    planPanel.append(E('p','Ändert nur die Anzeigenamen dieser Helfer. Entity-IDs, Werte, Bereiche, Labels und Verbraucher bleiben unverändert. HA und PilotSuite sind keine gemeinsame atomare Transaktion; Teilstände werden einzeln protokolliert. Anzeigenamen-basierte Vorlagen und Sprachassistenten können betroffen sein.','ps-muted'));
    if(plan.state==='preview'){const l=E('label');const c=E('input');c.type='checkbox';c.id='org-confirm-names';l.append(c,document.createTextNode('Genau diese Anzeigenamen ändern'));const apply=B('Geprüften Namensplan anwenden',()=>run(async()=>{assertCurrent();if(changed())throw Error('Offenen Zuordnungsentwurf zuerst speichern oder verwerfen');if(!c.checked)return;drawPlan(await request(path()+'/plans/'+plan.id+'/apply',{method:'POST',body:JSON.stringify({sha256:plan.sha256,confirm:true})}));}));apply.id='org-apply-names';apply.disabled=true;c.addEventListener('change',()=>apply.disabled=!c.checked||busy);planPanel.append(l,apply);}
    else {planPanel.append(B('Gespeicherten Planstatus laden',()=>run(async()=>{assertCurrent();drawPlan(await request(path()+'/plans/'+plan.id));})));
      if(plan.operations.some(op=>op.outcome==='verified'&&op.write_response_confirmed))planPanel.append(B('Rücknahme prüfen',()=>run(async()=>{assertCurrent();drawPlan(await request(path()+'/plans/'+plan.id+'/restore-preview',{method:'POST',body:JSON.stringify({revision:basis.revision})}));})));
      if(plan.state!=='verified')planPanel.append(E('p','Nicht vollständig bestätigt. Bereits bestätigte Änderungen sind oben markiert. Unklare Operationen werden nicht automatisch wiederholt.','ps-warning'));
    }
  }
  window.PilotSuiteOrganization={
    mount(node,onSaved){root=node;afterSave=onSaved;root.id='ps-organization';root.append(E('h2','Bestand & Ordnung'),E('p','Vorhandene Logik verstehen, Funktionen verbindlich zuordnen und Helfernamen vereinheitlichen. Keine automatische Übernahme der Steuerung.'));
      message=E('p','','edit-status');message.id='org-message';message.setAttribute('role','status');form=E('div');form.id='org-form';reports=E('div');reports.id='org-reports';planPanel=E('section');planPanel.id='org-plan';planPanel.setAttribute('aria-label','Geprüfter Ordnungsplan');history=E('div');history.id='org-history';
      const loadButton=B('Bestand & Zuordnungen laden',load);loadButton.id='org-load';root.append(loadButton,message,form,reports,planPanel,E('h3','Gespeicherte Pläne'),history);},
    context(zone,revision){if(!zone||!Number.isSafeInteger(revision))return;
      if(basis&&(basis.zone!==zone||basis.revision!==revision)){serial++;if(!changed()){data=null;initial='';loadedBasis=null;form.replaceChildren();reports.replaceChildren();planPanel.replaceChildren();history.replaceChildren();}notice('Zonenstand geändert. Bestand erneut laden.');}
      basis={zone,revision};updateButtons();},
    dirty:()=>busy||changed(),
    invalidate(){serial++;loadedBasis=null;reports?.replaceChildren();notice('Datenstand nicht bestätigt. Bestand neu laden; offene Auswahl bleibt erhalten.');updateButtons();}
  };
})();
