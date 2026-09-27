/* Progressive enhancement adapter. Existing forms, handlers and canonical stores are reused. */
(() => {
  'use strict';
  const M=window.PilotSuiteWorkspaceModel;
  if(!M || !document.getElementById('zone-overview')) return;
  const $=id=>document.getElementById(id), main=document.querySelector('main');
  const E=(tag,text='',cls='')=>{const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e;};
  const B=(text,action,cls='')=>{const b=E('button',text,cls);b.type='button';b.addEventListener('click',action);return b;};
  const A=(text,hash)=>{const a=E('a',text);a.href=hash;return a;};
  const iconPaths={home:'M3 10 12 3 21 10M5 9v12h14V9M9 21v-8h6v8',
    zone:'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z',
    config:'M4 6h16M4 12h16M4 18h16M8 3v6M16 9v6M10 15v6',
    history:'M3 3v18h18M6 15l4-5 4 3 6-8',workbench:'M5 5h14v16H5zM9 3h6v4H9zM8 11h8M8 15h5',
    system:'M12 3v10M7 5a8 8 0 1 0 10 0',presence:'M16 6a4 4 0 1 1-8 0a4 4 0 1 1 8 0M5 22v-3a7 7 0 0 1 14 0v3',
    light:'M9 21h6M9 18h6M8 14a7 7 0 1 1 8 0v3H8z',climate:'M9 14V5a3 3 0 0 1 6 0v9a5 5 0 1 1-6 0M12 9v9',
    media:'M9 18V5l12-3v13M9 18a3 3 0 1 1-3-3h3M21 15a3 3 0 1 1-3-3h3',all:'M4 5h16M4 12h16M4 19h16'};
  function icon(name){const s=document.createElementNS('http://www.w3.org/2000/svg','svg');s.setAttribute('viewBox','0 0 24 24');s.setAttribute('aria-hidden','true');s.classList.add('ps-icon');const p=document.createElementNS(s.namespaceURI,'path');p.setAttribute('d',iconPaths[name]||iconPaths.zone);s.append(p);return s;}
  let prefs=M.preferences(null);try{prefs=M.preferences(JSON.parse(localStorage.getItem('pilotsuite.workspace.v1')||'null'));}catch{}
  let activeView=prefs.view, activeModule='presence', status=null, invalid=true, requestBusy=false, generation=0, lastReview=null, lastReplay=null, lastLightingPreview=null, lastLightingDecision=null, presenceScenario='continuous_then_clear', lightingScenario='daylight_transition';
  let cockpitKey='', modulesKey='', roleFilter='all';
  const titles={cockpit:'Dein Zuhause im Blick',zone:'Zonen & Module',config:'Quellen & Konfiguration',history:'Verläufe & Muster',workbench:'Lernen & Werkbank',system:'Darstellung & System',all:'Alle Bereiche'};
  const notes={cockpit:'Wichtige Werte, offene Schritte und deine Habitus-Zonen.',zone:'Zusammenhänge sehen. Quellen verstehen. Zuständigkeiten getrennt halten.',config:'Erst auswählen, dann zuordnen. Änderungen bleiben bis zum Speichern ein Entwurf.',history:'Echte Messpunkte statt dekorativer Kurven. Du bestimmst den Zeitraum.',workbench:'Belege prüfen, Routinen entwerfen und Entscheidungen nachvollziehen.',system:'Deine Darstellung ist lokal. Hauskonfiguration und Freigaben bleiben unverändert.',all:'Vollständige Arbeitsansicht ohne Bereichswechsel.'};
  const panels=[];
  const mark=(node,view)=>{if(node){node.dataset.psView=view;panels.push(node);}return node;};
  const fieldStatus=E('p','','ps-notice');fieldStatus.id='ps-notice';fieldStatus.setAttribute('role','status');fieldStatus.hidden=true;
  function announce(message){fieldStatus.textContent=message;fieldStatus.hidden=!message;}
  function dirty(){return !!(selectionBusy||contextEditing||zoneFormOpen||selectionDraft?.dirty||
    (typeof routineDirty!=='undefined'&&routineDirty)||(typeof reviewNoteDirty!=='undefined'&&reviewNoteDirty)||(typeof historyBusy!=='undefined'&&historyBusy)||requestBusy||window.PilotSuiteOrganization?.dirty());}
  function valid(){return !invalid && !contextEditing && !zoneFormOpen && !selectionDraft?.dirty &&
    M.current(contextData,selectionDraft?.inventory,selectionZone) && !invalidFoundationContexts.has(contextData);}
  function savePrefs(){try{localStorage.setItem('pilotsuite.workspace.v1',JSON.stringify(prefs));}catch{announce('Darstellung gilt für diese Sitzung. Browser-Speicherung ist nicht verfügbar.');}}
  function applyPrefs(){const auto=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.dataset.psTheme=prefs.theme==='auto'?auto:prefs.theme;document.documentElement.dataset.psDensity=prefs.density;document.documentElement.dataset.psIds=String(prefs.ids);}
  const oldHero=document.querySelector('.hero');
  document.querySelector('footer').textContent='PilotSuite · Quellen, Beobachtung und Ausführungsrechte bleiben getrennt. Dieses Redesign erweitert keine Freigaben.';
  $('refresh').classList.add('ps-refresh');document.querySelector('.topbar').append($('refresh'));
  oldHero.querySelector('h2').textContent='Weniger suchen. Mehr verstehen.';
  oldHero.querySelector('.lede').textContent='Deine Habitus-Zonen, nachvollziehbare Quellen und konkrete nächste Schritte. Alles bleibt bei dir.';
  oldHero.querySelector('.eyebrow').textContent='PILOTSUITE · WORKSPACE';mark(oldHero,'cockpit');
  const system=mark(document.querySelector('section[aria-label="Systemstatus"]'),'system');
  document.querySelector('.section-nav').hidden=true;
  document.querySelector('.topbar .mode').textContent='Kontext · Planung · gezielte Freigaben';
  const sidebar=E('aside','','ps-sidebar');sidebar.setAttribute('aria-label','PilotSuite Navigation');
  const brand=E('div','','ps-brand');brand.append(icon('zone'),E('strong','PilotSuite'),E('small','WORKSPACE'));sidebar.append(brand);
  const nav=E('nav','','ps-nav');nav.setAttribute('aria-label','Arbeitsbereiche');sidebar.append(nav);
  for(const [view,label,name] of [['cockpit','Cockpit','home'],['zone','Zonenmodule','zone'],['config','Konfiguration','config'],['history','Verläufe','history'],['workbench','Werkbank','workbench'],['system','System','system']]){
    const a=A(label,'#ps-'+view);a.dataset.psNav=view;a.prepend(icon(name));nav.append(a);
  }
  const foot=E('div','','ps-sidebar-foot');foot.append(A('Alle Bereiche','#ps-all'),A('Wartung & Speicherpunkte','maintenance'),E('small','Lokale Daten. Bewusste Freigaben.'));sidebar.append(foot);
  document.body.insertBefore(sidebar,document.querySelector('.topbar'));
  const heading=E('div','','ps-page-heading'), h=E('h2',titles[activeView]);h.id='ps-view-title';h.tabIndex=-1;
  const subtitle=E('p',notes[activeView],'ps-muted');subtitle.id='ps-view-note';heading.append(h,subtitle);main.prepend(heading,fieldStatus);
  const zonePanel=$('zone-overview');zonePanel.classList.add('ps-zone-context');
  const overview=$('zone-summary');
  const zoneModule=mark(E('section','','panel ps-modules'),'zone');zoneModule.id='ps-zone';zoneModule.setAttribute('aria-label','Zonenmodule');
  const moduleCards=E('div','','ps-module-grid');moduleCards.id='ps-module-grid';
  const moduleDetail=E('div','','ps-module-detail');moduleDetail.id='ps-module-detail';
  zoneModule.append(overview,moduleCards,moduleDetail);zonePanel.after(zoneModule);
  mark(document.querySelector('[aria-labelledby="guide-title"]'),'cockpit zone');
  mark(document.querySelector('[aria-labelledby="daily-brief-title"]'),'cockpit');
  mark(document.querySelector('[aria-labelledby="foundation-title"]'),'zone');
  mark($('zone-setup'),'config');mark($('history-section'),'history');mark($('learning-section'),'workbench');
  for(const section of main.querySelectorAll(':scope > section')) {
    if(section===zonePanel||panels.includes(section))continue;mark(section,'zone');
  }
  const rolePanel=mark(E('section','','panel ps-role-panel'),'config');rolePanel.id='ps-roles';
  const roleSummary=E('div','','ps-role-summary');roleSummary.id='ps-role-summary';
  const editTools=E('div','','selection-tools');editTools.append($('context-edit'));
  rolePanel.append(E('h2','Hauptquellen & Lernfreigaben'),E('p','Eine Rollenpflege für alle Module. Suchfilter verändern keine Auswahl.'),roleSummary,editTools,$('context-form'));
  $('zone-setup').after(rolePanel);
  const organizationPanel=mark(E('section','','panel'),'config');
  rolePanel.after(organizationPanel);
  window.PilotSuiteOrganization?.mount(organizationPanel,async()=>{await loadSelection(selectionZone);});
  $('learning-section').prepend(A('Sensorrollen und Lernfreigaben konfigurieren','#ps-roles'));
  // Keep outcomes visible in every view, including form conflicts and learning feedback.
  main.insertBefore($('context-message'),heading.nextSibling);
  const cockpit=mark(E('section','','ps-cockpit'),'cockpit');cockpit.id='ps-cockpit';
  const metrics=E('div','','ps-kpis');metrics.id='ps-kpis';
  const filters=E('div','','selection-tools');const searchLabel=E('label','Zone finden');const search=E('input');search.type='search';search.id='ps-zone-search';search.placeholder='Name oder Bereich …';searchLabel.append(search);
  const filterLabel=E('label','Auswertung');const filter=E('select');filter.id='ps-zone-filter';
  for(const [v,t] of [['all','Alle Zonen'],['active','Aktiv'],['paused','Pausiert']]){const o=E('option',t);o.value=v;filter.append(o);}filterLabel.append(filter);filters.append(searchLabel,filterLabel);
  const cards=E('div','','ps-zone-grid');cards.id='ps-zone-grid';const matchCount=E('p','','ps-muted');matchCount.id='ps-zone-matches';matchCount.setAttribute('role','status');
  cockpit.append(metrics,E('h2','Deine Zonen'),filters,matchCount,cards);oldHero.after(cockpit);
  for(const input of [search,filter])input.addEventListener('input',()=>renderCockpit(true));
  const appearance=mark(E('section','','panel'),'system');appearance.id='ps-system';appearance.append(E('h2','Darstellung nach deinem Geschmack'),E('p','Nur auf diesem Gerät gespeichert. Kein Einfluss auf Automationen, Auswertung oder Lernfreigaben.'));
  const appearanceTools=E('div','','selection-tools');
  for(const [key,label,options] of [['theme','Farbschema',[['auto','System'],['light','Hell'],['dark','Dunkel']]],['density','Informationsdichte',[['comfortable','Großzügig'],['compact','Kompakt']]]]){
    const l=E('label',label),s=E('select');s.id='ps-'+key;
    for(const [v,t] of options){const o=E('option',t);o.value=v;s.append(o);}s.value=prefs[key];
    s.addEventListener('change',()=>{prefs[key]=s.value;applyPrefs();savePrefs();});l.append(s);appearanceTools.append(l);
  }
  const idLabel=E('label',''),idBox=E('input');idBox.type='checkbox';idBox.id='ps-show-ids';idBox.checked=prefs.ids;idLabel.append(idBox,document.createTextNode('Technische Kennungen immer zeigen'));idBox.addEventListener('change',()=>{prefs.ids=idBox.checked;applyPrefs();savePrefs();});
  appearance.append(appearanceTools,idLabel,A('Versionen, Sicherungen und Rescue öffnen','maintenance'));system.before(appearance);
  const form=$('context-form'),roleGroups=[...form.querySelectorAll('.role-group')];
  const filterBar=E('div','','ps-role-filters');filterBar.setAttribute('aria-label','Quellengruppen filtern');
  for(const [key,label] of [['all','Alle Rollen'],...M.modules.map(m=>[m.id,m.title])])filterBar.append(B(label,()=>setRoleFilter(key)));
  form.querySelector('fieldset').prepend(filterBar);
  for(const group of roleGroups){const choices=group.querySelector('.role-choices'),key=choices.id.slice(5);group.dataset.psRole=key;
    const label=E('label','Quellen suchen','ps-role-search'),input=E('input');input.type='search';input.setAttribute('aria-label',M.roles[key]+' durchsuchen');input.placeholder='Name oder Entitäts-ID';label.append(input);
    const n=E('p','','ps-role-count');n.setAttribute('role','status');choices.before(label,n);
    input.addEventListener('input',()=>filterRole(group));
    choices.addEventListener('change',()=>{filterRole(group);renderDiff();});
  }
  const diffPanel=E('details','','ps-diff');diffPanel.id='ps-config-diff';diffPanel.open=true;diffPanel.append(E('summary','Änderungsvorschau'),E('div'));
  form.querySelector('fieldset').insertBefore(diffPanel,form.querySelector('fieldset').lastElementChild);
  form.addEventListener('input',renderDiff);form.addEventListener('change',renderDiff);
  function filterRole(group){const input=group.querySelector('input[type=search]'),q=input.value.trim().toLocaleLowerCase('de');let shown=0,chosen=0;
    for(const l of group.querySelectorAll('.role-choices > label')){const c=l.querySelector('input[type=checkbox]');if(c?.checked)chosen++;l.hidden=!!q&&!l.textContent.toLocaleLowerCase('de').includes(q)&&!c?.value.toLowerCase().includes(q);if(!l.hidden)shown++;}
    const total=group.querySelectorAll('.role-choices > label').length;group.querySelector('.ps-role-count').textContent=`${chosen} ausgewählt · ${shown} von ${total} sichtbar`;
  }
  function setRoleFilter(id){roleFilter=id;const chosen=M.modules.find(m=>m.id===id);for(const group of roleGroups)group.hidden=!!chosen&&!chosen.roles.includes(group.dataset.psRole);[...filterBar.children].forEach((b,i)=>b.setAttribute('aria-pressed',String((i===0?'all':M.modules[i-1].id)===id)));}
  function renderDiff(){if(form.hidden||!contextData)return;for(const g of roleGroups)filterRole(g);
    const selected=Object.fromEntries(Object.keys(M.roles).map(k=>[k,[...$('role-'+k).querySelectorAll('input[type=checkbox]:checked')].map(i=>i.value)]));
    const after={roles:selected,learning:$('learning-consent').checked,context_learning:$('learning-consent').checked&&$('context-learning-consent').checked,
      detector:{min_events:Number($('detector-events').value),min_days:Number($('detector-days').value),timezone:$('detector-timezone').value.trim(),day_mode:$('detector-day-mode').value}};
    const before={...contextData.config,roles:contextData.effective_roles||contextData.config.roles},rows=M.diff(before,after),root=diffPanel.lastElementChild;
    diffPanel.firstElementChild.textContent=`Änderungsvorschau · ${rows.length} ${rows.length===1?'Änderung':'Änderungen'}`;root.replaceChildren();
    if(!rows.length){root.append(E('p','Keine Änderung gegenüber dem angezeigten Stand.'));return;}
    for(const row of rows){const item=E('div','','ps-diff-row');item.append(E('strong',row.label),E('span',Array.isArray(row.before)?row.before.map(nameOf).join(', ')||'Keine':String(row.before)),E('span','→'),E('span',Array.isArray(row.after)?row.after.map(nameOf).join(', ')||'Keine':String(row.after)));root.append(item);}
    if(rows.some(r=>r.key==='presence')&&contextData.event_count>0)root.append(E('p','Achtung: Ein Präsenzquellenwechsel entfernt bisherige Lernbelege und Musterfeedback dieser Zone.','ps-warning'));
    root.append(E('p','Noch nicht gespeichert. Vorhandene Sicherheitsbestätigungen gelten weiterhin.','ps-muted'));
  }
  function nameOf(id){return selectionDraft?.inventory?.items?.find(i=>i.entity_id===id)?.name||id;}
  function renderCockpit(force=false){const q=search.value.trim().toLocaleLowerCase('de'),mode=filter.value;
    const data=zoneDefinitions.filter(z=>(mode==='all'||(mode==='active'&&z.enabled)||(mode==='paused'&&!z.enabled))&&[z.name,...(z.area_ids||[])].join(' ').toLocaleLowerCase('de').includes(q));
    const key=JSON.stringify([data,zoneResults.map(z=>[z.zone_id,z.counts,z.summary]),selectionZone,status?.ready]);if(!force&&key===cockpitKey)return;cockpitKey=key;
    metrics.replaceChildren();for(const [title,value,detail] of [['Datenverbindung',status?(status.ready?'Verbunden':'Nicht bereit'):'Wird geprüft','Keine Aussage über Schaltfreigaben'],['Habitus-Zonen',String(zoneDefinitions.length),`${zoneDefinitions.filter(z=>z.enabled).length} für Auswertung aktiv`],['Ausgewertete Quellen',status?.ready?(M.count(status?.habitus?.neuron_count)??'—'):'—','Aktuelle Projektion, keine Personenanzahl'],['Vorschläge',status?.ready?(M.count(status?.habitus?.suggestion_count)??'—'):'—','Hinweise, keine automatischen Aktionen']]){const a=E('article','','ps-kpi');a.append(E('span',title),E('strong',String(value)),E('small',detail));metrics.append(a);}
    const focused=document.activeElement?.dataset?.psZone;cards.replaceChildren();matchCount.textContent=`${data.length} von ${zoneDefinitions.length} Zonen`;
    if(!data.length)cards.append(E('p',zoneDefinitions.length?'Keine Zone passt zum Filter.':'Noch keine Zone eingerichtet. Über „+ Neue Zone“ beginnen.','ps-empty'));
    for(const z of data){const r=zoneResults.find(x=>x.zone_id===z.zone_id),card=E('article','','ps-zone-card');const title=E('div','','ps-card-heading');title.append(icon('zone'),E('h3',z.name),E('span',z.enabled?'Auswertung aktiv':'Pausiert','ps-badge'));card.append(title);
      const values=E('div','','ps-zone-values');for(const [kind,label] of [['temperature','Temperatur'],['humidity','Feuchte'],['illuminance','Helligkeit']]){const d=E('div');d.append(E('strong',status?.ready&&z.enabled?M.metric(r?.summary,kind):'—'),E('small',label));values.append(d);}card.append(values);
      const counts=r?.counts;if(counts){const rel=M.count(counts.relevant),open=M.count(counts.unreviewed),ignored=M.count(counts.ignored);const total=(rel??0)+(open??0)+(ignored??0);
        if(total&&rel!==null){const meter=E('meter');meter.min=0;meter.max=total;meter.value=rel;meter.setAttribute('aria-label',`${rel} von ${total} Entitäten relevant`);card.append(meter);}
        card.append(E('p',`${rel??'—'} relevant · ${open??'—'} ungeprüft · ${ignored??'—'} ignoriert`,'ps-muted'));
      }else card.append(E('p','Bestandszahlen derzeit nicht ausgewertet.','ps-muted'));
      const open=B('Zone öffnen →',async()=>{if(dirty()){announce('Bitte den offenen Entwurf speichern oder abbrechen.');return;}invalid=true;generation++;lastReview=null;lastReplay=null;lastLightingPreview=null;lastLightingDecision=null;$('selection-zone').value=z.zone_id;await loadSelection(z.zone_id);navigate('zone');});open.dataset.psZone=z.zone_id;card.append(open);cards.append(card);
    }
    if(focused)[...cards.querySelectorAll('button')].find(b=>b.dataset.psZone===focused)?.focus({preventScroll:true});
  }
  function renderModules(force=false){window.PilotSuiteOrganization?.context(selectionZone,contextData?.revision);const ok=valid();const f=ok?contextData.foundation:null;
    const key=JSON.stringify([ok,f,activeModule,status?.ready,contextData?.effective_roles,
      zoneResults.find(z=>z.zone_id===selectionZone)?.summary]);if(!force&&key===modulesKey)return;modulesKey=key;
    moduleCards.replaceChildren();moduleDetail.replaceChildren();roleSummary.replaceChildren();
    if(!ok){moduleCards.append(E('p','Zonenstand nicht bestätigt oder Bearbeitung offen. Nach erfolgreichem Laden wird die Quellenansicht aktualisiert.','ps-empty'));return;}
    const configured=M.effectiveRoles(contextData),validated=f.validated_roles||{};
    for(const m of M.modules){const card=B('',()=>{activeModule=m.id;renderModules(true);moduleCards.querySelector(`[data-ps-module="${m.id}"]`)?.focus({preventScroll:true});});card.className='ps-module-card';card.dataset.psModule=m.id;card.setAttribute('aria-pressed',String(activeModule===m.id));
      const assigned=new Set(m.roles.flatMap(k=>configured[k]||[])).size,accepted=new Set(m.roles.flatMap(k=>validated[k]||[])).size;
      card.append(icon(m.icon),E('strong',m.title),E('span',`${assigned} zugeordnet · ${status?.ready?accepted:'—'} aktuell nutzbar`),E('small',m.id==='presence'?'Runtime separat prüfen; hier keine Aktivierung.':'Steuerung noch nicht implementiert.'));if(assigned){const meter=E('meter');meter.min=0;meter.max=assigned;meter.value=status?.ready?accepted:0;meter.setAttribute('aria-label',status?.ready?`${accepted} von ${assigned} zugeordneten Quellen nutzbar`:'Nutzbarkeit bei fehlender Verbindung nicht bestätigt');card.append(meter);}moduleCards.append(card);
    }
    const m=M.modules.find(x=>x.id===activeModule);moduleDetail.append(E('h3',m.title),E('p',m.description,'ps-muted'));
    const flow=E('div','','ps-flow');flow.setAttribute('aria-label',m.title+': Quellen, Referenz und Umsetzung');
    const sources=E('section','','ps-flow-node');sources.append(E('h4','01 · Zugeordnete Quellen'));
    for(const role of m.roles){const ids=configured[role]||[];const row=E('div','','ps-source-group');row.append(E('strong',M.roles[role]));
      if(ids.length&&M.roleOrigin(contextData,role)==='derived')row.append(E('small','Automatisch abgeleitet · noch nicht manuell bestätigt','ps-muted'));
      if(!ids.length)row.append(E('span','Nicht zugeordnet','ps-muted'));
      for(const id of ids){const chip=E('span','','ps-chip');const usable=status?.ready===true&&(validated[role]||[]).includes(id);chip.dataset.psQuality=usable?'ok':'unknown';chip.append(document.createTextNode(nameOf(id)),E('small',usable?'Zugeordnet & aktuell nutzbar':'Nicht nutzbar / ungeklärt'),E('code',id,'ps-technical-id'));row.append(chip);}sources.append(row);}
    const reference=E('section','','ps-flow-node');reference.append(E('h4','02 · Zonenreferenz'),E('p',m.id==='presence'?'Mindestens eine gültige Quelle aktiv. Logischen Raumstatus und Rohsensoren nicht doppelt als unabhängige Belege zählen.':m.id==='climate'?'Gültige Temperatur- und Feuchtequellen: Median mit Min/Max. Regler sind keine zusätzlichen Messwerte.':m.id==='lighting'?'Lux, binärer Helligkeitsindikator und Leuchtenzustand sind getrennte Größen.':'Player und ausdrücklicher Atmosphärenwunsch. Keine Emotion wird aus Sensoren behauptet.'));
    const output=E('section','','ps-flow-node');output.append(E('h4','03 · Umsetzung'),E('span',m.id==='presence'?'Runtime-Status hier nicht geprüft':'Noch keine Steuerung','ps-badge'),E('p','Quellenzuordnung ist keine Ausführungsfreigabe. Bestehende HA-Logik bleibt unverändert.'));
    const configure=B('Quellen konfigurieren',()=>{if(dirty())return;navigate('config');setRoleFilter(m.id);$('context-edit').click();});output.append(configure);flow.append(sources,reference,output);moduleDetail.append(flow);
    if(m.id==='climate') {
      const box=E('section','','ps-temperature-comparison');box.id='ps-temperature-comparison';
      box.append(E('h4','Externe Vergleichstemperatur · optional'),E('p',
        'Nur zur Einordnung, z. B. außen oder im Nachbarraum. Kein Sollwert und kein Beitrag zum Zonenmedian.','ps-muted'));
      const ids=configured.reference_temperature||[];
      const summary=status?.ready?zoneResults.find(z=>z.zone_id===selectionZone)?.summary:null;
      if(!ids.length)box.append(E('p','Nicht zugeordnet – für die Zonentemperatur nicht erforderlich.','ps-muted'));
      for(const id of ids) {
        const v=M.temperatureComparison(summary,id),row=E('p');
        row.append(E('strong',nameOf(id)+': '),document.createTextNode(
          v.value===null?'Nicht verfügbar':`${M.number(v.value)} ${v.unit||''}`));
        if(v.delta!==null)row.append(document.createTextNode(` · Zone minus Vergleich: ${M.number(v.delta)} ${v.unit}`));
        box.append(row);
      }
      moduleDetail.append(box);
    }
    if(m.id==='lighting') {
      const decisionSection=E('section','','ps-lighting-decision');decisionSection.append(E('h4','Aktueller Licht-Entscheidungscheck'),E('p','Liest den aktuellen Zonenstand und passende Automationsstrukturen erst nach Klick. Keine Speicherung, keine Außenlichtbehauptung und keine Geräteaktion.','ps-muted'));
      const decision=B('Aktuellen Lichtstand prüfen',runLightingDecision);decision.id='ps-lighting-decision';decision.disabled=requestBusy;decisionSection.append(decision);const decisionResult=E('div');decisionResult.id='ps-lighting-decision-result';decisionResult.setAttribute('role','status');decisionSection.append(decisionResult);moduleDetail.append(decisionSection);renderLightingDecision();
      const previewSection=E('section','','ps-lighting-preview');previewSection.append(E('h4','Tageslicht- und Stimmungsvorschau'),E('p','Nur feste Testdaten. Zeigt Totzone, Stabilitätszeit, Mindestabstand, manuelle Sperre und Ziel-Fähigkeiten – ohne Hauszugriff oder Speicherung.','ps-muted'));
      const previewLabel=E('label','Szenario'),previewSelect=E('select');previewSelect.id='ps-lighting-scenario';
      for(const [value,label] of [['daylight_transition','Tageslicht wird dunkler und wieder heller'],['threshold_chatter','Schwankung an einer Helligkeitsgrenze'],['manual_override','Manuelle Bedienung hat Vorrang'],['lux_unavailable','Helligkeitsquelle nicht verfügbar'],['night_vacancy','Nächtliches Verlassen'],['capability_limits','Begrenzte Leuchten-Fähigkeiten'],['brightness_unavailable','Aktuelle Leuchtenhelligkeit unbekannt']]){const option=E('option',label);option.value=value;previewSelect.append(option);}previewSelect.value=lightingScenario;previewSelect.addEventListener('change',()=>lightingScenario=previewSelect.value);previewLabel.append(previewSelect);
      const preview=B('Lichtvorschau berechnen',runLightingPreview);preview.id='ps-lighting-preview';preview.disabled=requestBusy;previewSection.append(previewLabel,preview);const previewResult=E('div');previewResult.id='ps-lighting-preview-result';previewResult.setAttribute('role','status');previewSection.append(previewResult);moduleDetail.append(previewSection);renderLightingPreview();
    }
    if(m.id==='presence'){const seq=E('div','','ps-state-machine');seq.setAttribute('aria-label','Geplante Zustandsfolge, kein Live-Zustand');for(const t of ['Belegt','Nachlauf','Frei / Unklar'])seq.append(E('span',t));moduleDetail.append(E('h4','Zustandsmodell · kein Live-Zustand'),seq,E('p','Ein Zeitablauf allein beweist keine Abwesenheit. Fehlende Quellen bleiben unklar.','ps-muted'));
      const replaySection=E('section','','ps-presence-replay');replaySection.append(E('h4','Erklärung mit synthetischem Szenario'),E('p','Nur Testdaten: keine Haushaltsbeobachtung, keine Speicherung und keine Aktivierung.','ps-muted'));
      const replayLabel=E('label','Szenario'),replaySelect=E('select');replaySelect.id='ps-presence-scenario';
      for(const [value,label] of [['continuous_then_clear','Dauerpräsenz, Nachlauf und Ablauf'],['pulse_refresh','Bewegungsimpuls erneuert Nachlauf'],['restart_during_grace','Neustart während des Nachlaufs'],['unknown_source','Unklare Quelle'],['dependency_unknown','Unklare Gruppenabhängigkeit']]){const option=E('option',label);option.value=value;replaySelect.append(option);}replaySelect.value=presenceScenario;replaySelect.addEventListener('change',()=>presenceScenario=replaySelect.value);replayLabel.append(replaySelect);
      const replay=B('Synthetisches Szenario ansehen',runReplay);replay.id='ps-presence-replay';replay.disabled=requestBusy;replaySection.append(replayLabel,replay);const replayResult=E('div');replayResult.id='ps-presence-replay-result';replayResult.setAttribute('role','status');replaySection.append(replayResult);moduleDetail.append(replaySection);renderReplay();
      const review=B('Bestehende Präsenzlogik prüfen',runReview);review.id='ps-adoption-review';review.disabled=requestBusy||!f.presence_contract?.logical_owner||!f.presence_contract?.raw_sources?.length;moduleDetail.append(review,E('p','Expliziter Konfigurationsabruf. Keine Übernahme, keine Aktivierung.','ps-muted'));const result=E('div');result.id='ps-review-result';result.setAttribute('role','status');moduleDetail.append(result);renderReview();}
    for(const [role,ids] of Object.entries(configured)){if(!(role in M.roles)||!ids.length)continue;const row=E('p');row.append(E('strong',M.roles[role]+': '),document.createTextNode(ids.map(nameOf).join(' · ')));roleSummary.append(row);}if(!roleSummary.children.length)roleSummary.append(E('p','Noch keine Hauptquellen zugeordnet. Entitäten bestätigen und anschließend Rollen auswählen.'));
  }
  async function runReview(){if(!valid()||requestBusy)return;const zone=selectionZone,revision=contextData.revision,g=++generation;requestBusy=true;lastReview=null;renderModules(true);
    try{const response=await json(`api/v1/zones/${encodeURIComponent(zone)}/presence-adoption/review`,{method:'POST',body:JSON.stringify({revision})});
      if(g!==generation||zone!==selectionZone||revision!==contextData?.revision||!valid())return;
      if(response?.schema!=='pilotsuite-presence-adoption-v1'||response.zone_id!==zone||response.revision!==revision||response.execution?.allowed!==false||!Array.isArray(response.automations))throw new Error('Prüfantwort passt nicht zum aktuellen Zonenstand.');
      lastReview={zone,revision,response};
    }catch(error){if(g===generation&&zone===selectionZone)lastReview={zone,revision,error:'Prüfung nicht bestätigt. '+error.message};}
    finally{requestBusy=false;renderModules(true);}
  }
  function renderReview(){const root=$('ps-review-result');if(!root)return;if(!lastReview||lastReview.zone!==selectionZone||lastReview.revision!==contextData?.revision){root.textContent=requestBusy?'Bestandsprüfung läuft …':'Noch keine aktuelle Bestandsprüfung.';return;}
    if(lastReview.error){root.textContent=lastReview.error;return;}const d=lastReview.response;root.append(E('p',`${M.count(d.summary?.related)??'—'} verwandte Automationen · ${M.count(d.summary?.conflicts)??'—'} mögliche Schreibkonflikte`));
    for(const row of d.automations.slice(0,50)){const p=E('p');p.append(E('strong',row.automation_id),document.createTextNode(row.classification==='conflict'?' · Schreiberkonflikt prüfen':' · Entitätsbezug prüfen'));root.append(p);}
    root.append(E('p','Nur Strukturprüfung. Kein Treffer ist kein Nachweis für Konfliktfreiheit. Templates, indirekte Aufrufe und reales Laufzeitverhalten bleiben gesondert zu prüfen.','ps-warning'));
  }
  async function runReplay(){if(!valid()||requestBusy)return;const zone=selectionZone,revision=contextData.revision,scenario=presenceScenario,g=++generation;requestBusy=true;lastReplay=null;renderModules(true);
    try{const response=await json(`api/v1/zones/${encodeURIComponent(zone)}/presence-runtime/replay`,{method:'POST',body:JSON.stringify({revision,scenario})});
      if(g!==generation||zone!==selectionZone||revision!==contextData?.revision||!valid())return;
      if(response?.schema!=='pilotsuite-presence-replay-v1'||response.zone_id!==zone||response.revision!==revision||response.persisted!==false||response.execution?.allowed!==false||!Array.isArray(response.scenario?.steps))throw new Error('Szenarioantwort passt nicht zum aktuellen Zonenstand.');
      lastReplay={zone,revision,response};
    }catch(error){if(g===generation&&zone===selectionZone)lastReplay={zone,revision,error:'Szenario nicht bestätigt. '+error.message};}
    finally{requestBusy=false;renderModules(true);}
  }
  function renderReplay(){const root=$('ps-presence-replay-result');if(!root)return;if(!lastReplay||lastReplay.zone!==selectionZone||lastReplay.revision!==contextData?.revision){root.textContent=requestBusy?'Szenario wird berechnet …':'Noch kein Szenario berechnet.';return;}
    if(lastReplay.error){root.textContent=lastReplay.error;return;}const d=lastReplay.response,labels={occupied:'Belegt',grace:'Nachlauf',vacant:'Frei',unknown:'Unklar'};
    root.append(E('p',d.scenario.title));const list=E('ol');for(const step of d.scenario.steps){const item=E('li');item.append(E('strong',`+${step.at_seconds} s · ${labels[step.state]||'Unklar'}`),document.createTextNode(' — '+step.explanation));if(step.proposed_actions?.length)item.append(E('small','Simulation: '+step.proposed_actions.join(', ')+' · nicht ausgeführt','ps-muted'));list.append(item);}root.append(list,E('p','Ergebnis wurde nicht gespeichert. Es erteilt kein Ausführungsrecht.','ps-warning'));
  }
  async function runLightingDecision(){if(!valid()||requestBusy)return;const zone=selectionZone,revision=contextData.revision,g=++generation;requestBusy=true;lastLightingDecision=null;renderModules(true);
    try{const response=await json(`api/v1/zones/${encodeURIComponent(zone)}/lighting-decision`,{method:'POST',body:JSON.stringify({revision})});
      if(g!==generation||zone!==selectionZone||revision!==contextData?.revision||!valid())return;
      if(response?.schema!=='pilotsuite-lighting-decision-v1'||response.zone_id!==zone||response.revision!==revision||response.persisted!==false||response.execution?.allowed!==false||!Array.isArray(response.automation_review?.items))throw new Error('Prüfantwort passt nicht zum aktuellen Zonenstand.');
      lastLightingDecision={zone,revision,response};
    }catch(error){if(g===generation&&zone===selectionZone)lastLightingDecision={zone,revision,error:'Lichtcheck nicht bestätigt. '+error.message};}
    finally{requestBusy=false;renderModules(true);}
  }
  function renderLightingDecision(){const root=$('ps-lighting-decision-result');if(!root)return;if(!lastLightingDecision||lastLightingDecision.zone!==selectionZone||lastLightingDecision.revision!==contextData?.revision){root.textContent=requestBusy?'Lichtstand wird geprüft …':'Noch kein aktueller Lichtcheck.';return;}
    if(lastLightingDecision.error){root.textContent=lastLightingDecision.error;return;}const d=lastLightingDecision.response,o=d.current_zone_observation||{},a=d.automation_review||{};
    const lux=o.illuminance?.value,unit=o.illuminance?.unit||'';root.append(E('p',lux===null||lux===undefined?'Innen-Helligkeit derzeit nicht auswertbar.':`Innen-Helligkeit: ${M.number(lux)} ${unit} · ${o.illuminance?.aggregation||'ohne bestätigte Aggregation'}`),E('p',`Leuchtenzustand: ${o.light?.active===true?'mindestens eine an':o.light?.active===false?'aus':'unklar'} · ${a.items.length} passende Automationsstrukturen gelesen.`,'ps-muted'),E('p','Außenhelligkeit nicht bestätigt. Ein aktueller Transport-Snapshot beweist keine aktuelle physische Messung.','ps-warning'));
    for(const row of a.items.slice(0,20)){const p=E('p');p.append(E('strong',row.automation_id||'Unbekannte Automation'),document.createTextNode(row.state==='direct_path'?' · direkter Quellen-/Lichtbezug':' · Bezug vorhanden, Wirkung nicht vollständig aufgelöst'));root.append(p);}
    root.append(E('p','Vorhandene Automation bedeutet weder Duplikat noch sichere Lösung. Keine Sicherheitsquote und keine Ausführungsfreigabe.','ps-warning'));
    const next=d.next_step;if(next?.id==='configure_sources'){const button=B(next.label,()=>{if(dirty())return;navigate('config');setRoleFilter('lighting');$('context-edit').click();});root.append(button);}else if(next?.id==='reload_zone'){root.append(B(next.label,()=>$('refresh').click()));}else if(next?.id==='run_synthetic_preview'){root.append(B(next.label,()=>{$('ps-lighting-scenario')?.focus();$('ps-lighting-preview')?.scrollIntoView({block:'nearest'});}));}
    root.append(E('p','Prüfergebnis wurde nicht gespeichert.','ps-muted'));
  }
  async function runLightingPreview(){if(!valid()||requestBusy)return;const zone=selectionZone,revision=contextData.revision,scenario=lightingScenario,g=++generation;requestBusy=true;lastLightingPreview=null;renderModules(true);
    try{const response=await json(`api/v1/zones/${encodeURIComponent(zone)}/lighting-preview`,{method:'POST',body:JSON.stringify({revision,scenario})});
      if(g!==generation||zone!==selectionZone||revision!==contextData?.revision||!valid())return;
      if(response?.schema!=='pilotsuite-lighting-preview-v1'||response.zone_id!==zone||response.revision!==revision||response.persisted!==false||response.execution?.allowed!==false||!Array.isArray(response.scenario?.steps))throw new Error('Vorschauantwort passt nicht zum aktuellen Zonenstand.');
      lastLightingPreview={zone,revision,response};
    }catch(error){if(g===generation&&zone===selectionZone)lastLightingPreview={zone,revision,error:'Lichtvorschau nicht bestätigt. '+error.message};}
    finally{requestBusy=false;renderModules(true);}
  }
  function renderLightingPreview(){const root=$('ps-lighting-preview-result');if(!root)return;if(!lastLightingPreview||lastLightingPreview.zone!==selectionZone||lastLightingPreview.revision!==contextData?.revision){root.textContent=requestBusy?'Lichtvorschau wird berechnet …':'Noch keine Lichtvorschau berechnet.';return;}
    if(lastLightingPreview.error){root.textContent=lastLightingPreview.error;return;}const d=lastLightingPreview.response,labels={stabilizing:'Stabilisierung',suggest:'Vorschlag',hold:'Halten',rate_limited:'Mindestabstand',within_deadband:'Totzone',capability_limited:'Fähigkeit begrenzt',input_unavailable:'Istwert fehlt'};
    const inputs=d.zone_inputs||{},count=role=>`${inputs[role]?.currently_usable??'—'}/${inputs[role]?.configured??'—'}`;
    root.append(E('p',d.scenario.title),E('p',`Zonenbezug: Leuchten ${count('light')} · Innen-Lux ${count('illuminance')} · binäre Helligkeit ${count('daylight_binary')} (nutzbar/zugeordnet)`,'ps-muted'),E('p','Der Tageslichtwert dieses Szenarios ist fest und synthetisch. Innen-Lux oder Eigenlicht bestätigen keine Außenhelligkeit.','ps-warning'));
    const list=E('ol');for(const step of d.scenario.steps){const item=E('li');item.append(E('strong',`+${step.at_seconds} s · ${labels[step.status]||'Prüfung'}`),document.createTextNode(' — '+step.explanation));const settings=step.proposed_settings||{};const parts=[];if(Object.hasOwn(settings,'on'))parts.push(settings.on?'Ein':'Aus');if(Object.hasOwn(settings,'brightness_pct'))parts.push(`${settings.brightness_pct} %`);if(Object.hasOwn(settings,'color_temp_kelvin'))parts.push(`${settings.color_temp_kelvin} K`);if(parts.length)item.append(E('small','Vorschau: '+parts.join(' · ')+' · nicht ausgeführt','ps-muted'));list.append(item);}root.append(list,E('p','Ergebnis wurde nicht gespeichert. Lux, Helligkeitsprozent, Atmosphäre und Ausführungsrecht bleiben getrennt.','ps-warning'));
  }
  function viewForHash(hash){const id=decodeURIComponent(hash.slice(1));if(id.startsWith('ps-')&&M.views.includes(id.slice(3)))return id.slice(3);const node=$(id),owner=node?.closest('[data-ps-view]')?.dataset.psView.split(' ')[0];return owner?(activeView==='all'?'all':owner):null;}
  function navigate(view,{focus=false,hash=true}={}){if(!M.views.includes(view))return false;
    if(view!==activeView&&dirty()){announce('Bearbeitung läuft. Bitte speichern oder abbrechen, bevor du den Arbeitsbereich wechselst.');return false;}
    activeView=view;prefs.view=view;savePrefs();for(const panel of panels)panel.hidden=view!=='all'&&!panel.dataset.psView.split(' ').includes(view);
    for(const link of nav.children){if(link.dataset.psNav===view)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');}
    $('ps-view-title').textContent=titles[view];$('ps-view-note').textContent=notes[view];if(hash)history.replaceState(null,'','#ps-'+view);if(focus)$('ps-view-title').focus();return true;
  }
  document.addEventListener('click',event=>{const link=event.target.closest('a');if(!link)return;const href=link.getAttribute('href')||'';
    if(href==='maintenance'||link.id==='release-install'){if(dirty()){event.preventDefault();event.stopImmediatePropagation();announce('Offene Änderungen zuerst speichern oder abbrechen.');}return;}
    if(!href.startsWith('#'))return;let view;try{view=viewForHash(href);}catch{return;}if(!view)return;
    if(!navigate(view,{hash:false})){event.preventDefault();event.stopImmediatePropagation();return;}
    const target=$(href.slice(1));for(let p=target;p&&p!==main;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;
    if(href.startsWith('#ps-')&&M.views.includes(href.slice(4))){event.preventDefault();history.pushState(null,'',href);$('ps-view-title').focus();}
  },true);
  window.addEventListener('hashchange',()=>{let view;try{view=viewForHash(location.hash);}catch{return;}if(view&&!navigate(view,{hash:false}))history.replaceState(null,'','#ps-'+activeView);});
  for(const id of ['zone-new','zone-edit','context-edit'])$(id).addEventListener('click',event=>{if(activeView!=='config'&&activeView!=='all'&&!navigate('config')){event.preventDefault();event.stopImmediatePropagation();}},true);
  const errors=new MutationObserver(()=>{if(!$('error').hidden){window.PilotSuiteOrganization?.invalidate();status=null;invalid=true;generation++;lastReview=null;lastReplay=null;lastLightingPreview=null;lastLightingDecision=null;renderCockpit(true);renderModules(true);}});errors.observe($('error'),{attributes:true,attributeFilter:['hidden']});
  $('context-cancel').addEventListener('click',()=>{if(!contextEditing&&!selectionBusy)loadContext().catch(()=>announce('Gespeicherte Rollen konnten nicht neu geladen werden. Erneut öffnen.'));});
  const observer=new MutationObserver(()=>{if(!form.hidden){setRoleFilter(roleFilter);renderDiff();}});observer.observe(form,{attributes:true,attributeFilter:['hidden']});
  // Preserve organization drafts across legacy zone controls and background refreshes.
  document.addEventListener('click',event=>{
    if(window.PilotSuiteOrganization?.dirty() && event.target.closest('#zone-overview button, #zone-setup button, #ps-roles button, #refresh, #learning-section button')) {
      event.preventDefault();event.stopImmediatePropagation();announce('Ordnungsentwurf zuerst speichern oder verwerfen.');
    }
  },true);
  $('selection-zone').addEventListener('change',event=>{if(window.PilotSuiteOrganization?.dirty()){event.target.value=selectionZone;event.stopImmediatePropagation();announce('Ordnungsentwurf zuerst speichern oder verwerfen.');}},true);
  window.addEventListener('beforeunload',event=>{if(window.PilotSuiteOrganization?.dirty()){event.preventDefault();event.returnValue='';}});
  const oldWorkspaceLoad=load;load=function(...args){return window.PilotSuiteOrganization?.dirty()?Promise.resolve():oldWorkspaceLoad(...args);};
  // Narrow bridge to the existing renderer: no new polling, data owner or write endpoint.
  const oldStatus=renderStatus;renderStatus=function(s){oldStatus(s);status=s;renderCockpit();};
  const oldZone=renderZoneView;renderZoneView=function(){oldZone();renderCockpit();renderModules();};
  const oldLearning=renderLearning;renderLearning=function(){oldLearning();invalid=false;renderModules();};
  const oldInvalid=invalidateDailyBrief;invalidateDailyBrief=function(...args){oldInvalid(...args);invalid=true;generation++;lastReview=null;lastReplay=null;lastLightingPreview=null;lastLightingDecision=null;renderModules(true);};
  const oldFoundation=renderFoundationJourney;renderFoundationJourney=function(...args){oldFoundation(...args);renderModules();const b=$('helper-provision');if(b&&!valid())b.disabled=true;};
  const oldPreview=renderRolePreview;renderRolePreview=function(){oldPreview();renderDiff();};
  // Global freshness is separate from module configuration and action authority.
  const oldText=text;text=function(id,value){oldText(id,value);if(id==='context-message'&&value)announce(value);};
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',applyPrefs);
  setRoleFilter('all');applyPrefs();document.body.classList.add('ps-workspace-ready');
  invalid=!M.current(contextData,selectionDraft?.inventory,selectionZone);
  let hashView=null;try{hashView=viewForHash(location.hash);}catch{}if(hashView)activeView=hashView;navigate(hashView||activeView,{hash:false});renderCockpit(true);renderModules(true);
})();
