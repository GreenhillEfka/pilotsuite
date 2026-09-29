/* Zone-first configurator. Relevance authorizes analysis; writes use explicit plans. */
(() => {
 'use strict';
 const E=(t,txt='',cls='')=>{const e=document.createElement(t);e.textContent=txt;if(cls)e.className=cls;return e;};
 const B=(text,fn)=>{const b=E('button',text);b.type='button';b.addEventListener('click',fn);return b;};
 const select=(items,value)=>{const s=E('select');for(const [v,t] of items){const o=E('option',t);o.value=v;s.append(o);}s.value=value??'';return s;};
 const number=(value,min,max)=>{const n=E('input');n.type='number';n.value=value;n.min=min;n.max=max;return n;};
 const labelled=(text,input)=>{const l=E('label',text);input.setAttribute('aria-label',text);l.append(input);return l;};
 const fmt=v=>typeof v==='number'&&Number.isFinite(v)?v.toLocaleString('de-DE',{maximumFractionDigits:1}):'—';
 const date=t=>typeof t==='number'?new Date(t*1000).toLocaleString('de-DE'):'—';
 const state=s=>({occupied:'Belegt',grace:'Nachlauf',vacant:'Frei',unknown:'Unklar',on:'An',off:'Aus',unavailable:'Nicht verfügbar'}[s]||s||'Unklar');
 let root,zone,revision,valid=false,generation=0,editing=false,busy=false,data=null,last=0,historyData=null,ontology=null,plan=null;
 let output,notice,tools,editor,charts,existingReview=null;
 const eligible=()=>root&&!root.hidden&&root.getClientRects().length&&valid;
 const current=(z,r,g)=>zone===z&&revision===r&&generation===g&&valid;
 function note(t){if(notice)notice.textContent=t;}
 const editingChanged=()=>window.PilotSuiteWorkspaceEditingChanged?.();
 async function api(suffix,method='GET',body){
   const z=zone;const response=await fetch(`api/v1/zones/${encodeURIComponent(z)}/${suffix}`,{
     method,cache:'no-store',headers:{'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
   let value;try{value=await response.json();}catch{throw Error('Keine gültige Antwort');}
   if(!response.ok)throw Error(value.message||'Anfrage nicht bestätigt');return value;
 }
 async function read({background=false}={}){
   if(!eligible()||busy||editing)return;
   const z=zone,r=revision,g=generation;last=Date.now();
   try{const value=await api('presence');if(!current(z,r,g))return;
     if(value.schema!=='pilotsuite-zone-presence-v2'||value.zone_id!==z||value.revision!==r)throw Error('Zonenstand geändert; neu laden');
     data=value;
     const scroller=document.scrollingElement,position=scroller?.scrollTop;
     render();
     if(background&&scroller&&scroller.scrollTop!==position)scroller.scrollTop=position;
   }catch(e){if(current(z,r,g)){data=null;unavailable(e.message);}}
 }
 function unavailable(message){
   if(editing)return;
   output.replaceChildren(E('h3','Unklar'),E('p',message,'ps-warning'));
   tools.querySelectorAll('button').forEach(button=>button.disabled=button.id!=='ps-zone-refresh'||!valid);
   note('Keine bestätigte aktuelle Entscheidung. Unklar bedeutet nicht frei.');
 }
 function mount(host){
   host.replaceChildren();root=host;
   root.append(E('h2','Anwesenheit'),E('p','Bestandsmeldung, zuständige Steuerung und eigene Bewertung getrennt prüfen.','ps-muted'));
   notice=E('p','','ps-notice');notice.setAttribute('role','status');tools=E('div','','selection-tools');editor=E('div');output=E('div');charts=E('div');
   root.append(output,notice,tools,editor,charts);
 }
 function render(){
   if(!data||editing)return;
   if(!tools.firstElementChild){
     const configure=B('PilotSuite-Bewertung konfigurieren',openEditor);configure.id='ps-zone-configure';
     const refresh=B('Aktualisieren',()=>read());refresh.id='ps-zone-refresh';
     tools.append(configure,refresh,B('Sensordaten & Verläufe',openHistory),B('Entitäten → Ontologie',openOntology));
     const helperOptions=E('details');helperOptions.id='ps-helper-options';helperOptions.append(E('summary','Fehlende Helfer · Möglichkeiten prüfen'));
     helperOptions.append(E('p','Zuerst vorhandenen Boolean, Timer und Präsenzsensor verbinden. Ein fehlender oder nicht erreichbarer zugeordneter Helfer wird nicht automatisch ersetzt.'));
     const single=B('Einzelnen fehlenden Helfer vorbereiten',prepareMissingHelper);single.id='ps-helper-single';helperOptions.append(single);
     helperOptions.append(E('p','Ein eigenes Ausgangspaket umfasst Boolean, Gültigkeit, Frist, Timer und öffentlichen Sensor. Kein einzelner Ersatzhelfer für eine bestehende HA-Kette; deren Automation wird nicht angeschlossen oder übernommen.','ps-muted'));
     const prepare=B('Eigenen Anwesenheitssensor vorbereiten',preparePackage);prepare.id='ps-zone-prepare';helperOptions.append(prepare);tools.append(helperOptions);
   }
   tools.querySelector('#ps-zone-prepare').hidden=!!data.package;
   tools.querySelector('#ps-helper-options').hidden=!!data.package;
   const horizontal=output.querySelector('.ps-zone-scroll')?.scrollLeft||0;
   const openSources=output.querySelector('[data-ps-live=sources]')?.open||false;
   const openTrace=output.querySelector('[data-ps-live=trace]')?.open||false;
   const openReview=output.querySelector('[data-ps-live=existing-review]')?.open??true;
   const openCalculation=output.querySelector('[data-ps-live=calculation]')?.open||false;
   const focusedLive=output.contains(document.activeElement)?document.activeElement.closest('[data-ps-live]')?.dataset.psLive:null;
   output.replaceChildren();
   tools.querySelectorAll('button').forEach(button=>button.disabled=busy);
   const model=window.PilotSuiteZonePresenceModel,d=data.current,summary=model.summary(data),headline=model.headline(data);
   const hasExisting=headline.kind==='existing',cards=E('div','','ps-presence-summary');
   const publicationHint=(data.package?.entities?.sensor||'Kein eigenes Ausgangspaket. Die Präsenzberechnung ist davon unabhängig.')+
      (summary.publicationCheckedAt!==null?' · Rückleseprüfung: '+date(summary.publicationCheckedAt):'');
   const addCard=(target,id,title,value,hint)=>{const c=E('article','','ps-kpi');if(id)c.id=id;c.append(E('span',title),E('strong',value),E('small',hint));target.append(c);};
   addCard(cards,'ps-presence-state',headline.title,headline.state,headline.reason);
   const ownDeadline=d?.valid===true&&d?.deadline;
   const addCalculation=target=>{
     if(hasExisting)addCard(target,'ps-presence-calculation','PilotSuite-Vergleich',summary.state,summary.reason);
     addCard(target,'','PilotSuite-Nachlauf',ownDeadline?fmt(d.remaining_seconds)+' s':'—',ownDeadline?date(d.deadline):'Kein bestätigter eigener Nachlauf');
     addCard(target,'ps-presence-publication','Eigene HA-Veröffentlichung',summary.publication,publicationHint);
   };
   if(hasExisting){
     const chain=data.existing,timer=chain.timer,labels=model.existing(chain);
     const timed=chain.fresh===true&&timer?.available===true&&timer.state==='active'&&typeof timer.finishes_at==='number'&&typeof timer.remaining_seconds==='number';
     addCard(cards,'','Nachlauf des Bestands',timed?fmt(timer.remaining_seconds)+' s':labels.timer,
       timed?'Gemeldete Frist: '+date(timer.finishes_at):'HA-Timerstatus; weder sein Ablauf noch „Inaktiv“ beweist Abwesenheit.');
     addCard(cards,'','Anbindung · keine Übernahme',headline.controller,headline.authority);
   }else addCalculation(cards);
   output.append(cards);
   renderExisting(openReview);
   if(hasExisting){const comparison=E('details');comparison.dataset.psLive='calculation';comparison.open=openCalculation;
     comparison.append(E('summary','PilotSuite-Vergleich & eigenes Ausgangspaket'),E('p','Unabhängige Bewertung, kein Ersatz für die Bestandsmeldung. Diese Zeiten verändern den HA-Nachlauf nicht.','ps-muted'));
     const values=E('div','','ps-presence-summary');addCalculation(values);comparison.append(values);output.append(comparison);
   }
   const missing=d?.sources?.filter(s=>s.required&&!s.usable)||[];
   if(missing.length)output.append(E('p',`${missing.length} erforderliche Quelle(n) derzeit nicht nutzbar. Eine Datenlücke ist kein Freibeleg. Die PilotSuite-Bewertung berücksichtigt diese Quellenkombination; sie erklärt nicht automatisch die HA-Bestandslogik.`,'ps-warning'));
   if(d){const table=E('table','','ps-zone-source-table');const header=E('tr');for(const text of ['Quelle','Signaltyp','Zustand','Meldealter','Indirekte Frist'])header.append(E('th',text));table.append(header);
      for(const s of d.sources){const tr=E('tr');for(const text of [s.name||s.entity_id,s.kind,state(s.state),s.age_seconds===null?'Ereignisorientiert / unbekannt':fmt(s.age_seconds)+' s',date(s.support_until)])tr.append(E('td',text));table.append(tr);}
      const sources=E('details');sources.dataset.psLive='sources';sources.open=openSources;
      sources.append(E('summary',`PilotSuite-Belege · Aktuelle Quellen (${d.sources.length})`));
      const wrap=E('div','','ps-zone-scroll');wrap.append(table);sources.append(wrap);output.append(sources);wrap.scrollLeft=horizontal;
      sources.append(E('p','Bestandsvergleich: '+(d.comparison==='same'?'Übereinstimmung':d.comparison==='different'?'Abweichung':'Nicht beurteilbar')+' · HA-Zustand: '+state(d.ha_state),'ps-muted'));
      const trace=data.trace||[];if(trace.length){
        const history=E('details');history.dataset.psLive='trace';history.open=openTrace;
        history.append(E('summary',`Sitzungsverlauf (${trace.length})`),E('p','Höchstens 128 Zustandswechsel im Arbeitsspeicher, keine historische Recorder-Aufzeichnung.','ps-muted'),chart({name:'Präsenzentscheidung im aktuellen Lauf',record_count:trace.length,changes:Math.max(0,trace.length-1),kind:'state',points:trace.map(r=>[r.observed_at,state(r.state)])},{start:trace[0].observed_at,end:Math.max(d.observed_at,trace[0].observed_at+1)}));output.append(history);
      }
      if(focusedLive)output.querySelector(`[data-ps-live="${focusedLive}"] summary`)?.focus({preventScroll:true});
   }
   note(summary.state==='Pausiert'?'PilotSuite-Bewertung pausiert. Eine vorhandene HA-Steuerung läuft davon unabhängig.':'Relevant erlaubt Live- und verfügbare Historienauswertung. Änderungen in Home Assistant brauchen eine eigene Bestätigung.');
 }
 function renderExisting(openReview){
   const existing=data.existing,labels=window.PilotSuiteZonePresenceModel.existing(existing);
   const section=E('section');section.id='ps-existing-presence';section.append(E('h3','Bestehende Anwesenheitssteuerung'));
   section.append(E('p','Bestehende Automationen bleiben zuständig. PilotSuite liest und vergleicht; diese Zuordnung schaltet nichts.','ps-muted'));
   const connect=organizationLink(existing?.configured?'Bestandszuordnung bearbeiten':'Vorhandenen Bestand verbinden','presence_status');connect.id='ps-existing-connect';section.append(connect);
   if(!existing?.configured){section.append(E('p','Vorhandenen Boolean, Timer und öffentlichen Präsenzsensor zuordnen. Auch Helfer ohne HA-Bereich sind auswählbar.','ps-muted'));
     const links=E('div','','selection-tools');for(const [text,role] of [['Boolean wählen','presence_status'],['Timer wählen','presence_timer'],['Präsenzsensor wählen','presence_output']])links.append(organizationLink(text,role));section.append(links);output.append(section);return;}
   const chain=E('div','','ps-presence-summary');
   for(const [key,title] of [['owner','Raumstatus / Boolean'],['timer','Nachlauftimer'],['sensor','Öffentlicher Präsenzsensor']]){
     const item=existing[key],card=E('article','','ps-kpi');card.dataset.existingRole=key;
     card.append(E('span',title),E('strong',labels[key]),E('small',item?(item.name+' · '+(item.entity_id||item.saved_entity_id)):'Keine Zuordnung; nichts wird automatisch erzeugt.'));
     if(item?.binding_status==='identity_unresolved')card.append(E('small','Identität ungeklärt; keine Ersatzentität übernommen.','ps-warning'));
     if(item?.own_output)card.append(E('small','PilotSuite-eigener Ausgang: kein unabhängiger Bestandsvergleich.','ps-warning'));
     if(key==='timer'&&item?.available&&existing.fresh){
       card.append(E('small',item.remaining_seconds!==null?`Gemeldete Frist: ${date(item.finishes_at)} · ${fmt(item.remaining_seconds)} s`:'Keine bestätigte laufende Frist.'));
     }card.append(organizationLink(item?'Zuordnung prüfen':'Vorhandenen Helfer wählen',{owner:'presence_status',timer:'presence_timer',sensor:'presence_output'}[key]));chain.append(card);
   }section.append(chain);
   const comparison=E('p',`PilotSuite ↔ ${existing.comparison_reference==='sensor'?'Bestands-Präsenzsensor':'Bestands-Raumstatus'}: ${labels.comparison}`);
   comparison.id='ps-existing-comparison';section.append(comparison);
   if(existing.chain_consistency==='different'&&existing.fresh)section.append(E('p','Boolean und öffentlicher Bestands-Präsenzsensor widersprechen sich aktuell. Es wird nichts automatisch korrigiert.','ps-warning'));
   if(!existing.sensor)section.append(E('p','Kein öffentlicher Bestands-Präsenzsensor zugeordnet; ein Boolean allein bestätigt diese Stufe noch nicht.','ps-warning'));
   const timing={observe:'Nachlaufverfahren noch nicht zugeordnet.',timer:'Vorhandener Timer ist als Nachlaufverfahren angegeben.',existing_for:'Bestandsautomation nutzt for:-Nachlauf; ein separater Timer ist nicht zwingend erforderlich.',external:'Nachlauf liegt in einer anderen Bestandslogik; ein separater Timer ist nicht zwingend erforderlich.'};
   section.append(E('p',(timing[existing.timing]||timing.observe)+' Zeiten werden in der bestehenden HA-Konfiguration gepflegt, nicht im PilotSuite-Vergleich.','ps-muted'));
   section.append(organizationLink('Anwesenheitsautomationen zuordnen','presence_automations'));
   const review=B('Übernahme vorhandener Automationen prüfen',reviewExisting);review.id='ps-existing-review';review.disabled=busy||!existing.fresh;section.append(review);
   section.append(E('p',`${existing.automations?.length||0} Automation(en) zugeordnet. Prüfung ergänzt direkt verknüpfte Automationen; keine vollständige Verbraucher- oder Verhaltensgarantie.`,'ps-muted'));
   if(existingReview){
     const report=E('details');report.open=openReview;report.dataset.psLive='existing-review';report.append(E('summary','Letzte Strukturprüfung · '+date(existingReview.checked_at)));
     report.append(E('p','Historische Prüfsicht, keine laufende Überwachung der Automationskonfiguration. Vor Änderungen erneut prüfen. Steuerung unverändert.','ps-muted'));
     const reuse=E('section');reuse.id='ps-existing-reuse';reuse.append(E('h4','Bestand weiterverwenden – Übernahmeprüfung'));
     reuse.append(E('p','Ausgangspunkt: Vorhandene Automationen, Boolean, Timer und Präsenzsensor behalten. Eine passende Struktur ist noch kein Nachweis gleichen oder sicheren Verhaltens.'));
     reuse.append(E('p','Jetzt → nach dieser Prüfung: Bestehende Automationen steuern weiterhin. Keine Konfigurationsänderung vorgeschlagen oder ausgeführt; es gibt daher nichts zurückzunehmen.'));
     const checks=E('ul');
     const checkLabels={timing:'Auslöser, Bedingungen und Nachlauf im tatsächlichen Ablauf prüfen.',unknown_inputs:'Unbekannte und unverfügbare Quellen dürfen nicht stillschweigend frei bedeuten.',manual_override:'Manuelle Eingriffe und Sperren mit ihrer tatsächlichen Bedeutung erhalten.',dependencies:'Weitere Verbraucher, Skripte und indirekte Abhängigkeiten prüfen.',single_writer:'Vor einer Steuerungsübergabe konkurrierende Schreiber für jedes Ziel klären.',backup_recovery:'Vor Änderungen konkreten Vorher-/Nachherplan, Freigabe, Sicherung und Rückweg festlegen.'};
     for(const check of existingReview.reuse_review?.checks||[]){if(checkLabels[check.id])checks.append(E('li','Offen: '+checkLabels[check.id]));}
     reuse.append(checks,E('p','Automationsänderung und Steuerungsübergabe sind hier noch nicht ausführbar. Die Prüfung bereitet eine kontrollierte Übernahme vor, sie ersetzt keine Freigabe.','ps-warning'));report.append(reuse);
     for(const row of existingReview.automations){
       const entry=E('article','','ps-zone-source-edit');entry.dataset.existingAutomation=row.automation_id;
       const usage={writer:'Steuert den Bestandsstatus / Nachlauf',mixed_writer:'Gemischte Steuerung mit weiteren Aktionen',consumer:'Verwendet den Bestandsstatus',related:'Weitere direkte Verbindung',unrelated:'Keine direkte Verbindung erkannt'}[row.usage]||'Ungeklärt';
       const identity=E('p');identity.append(E('code',row.automation_id));
       entry.append(E('strong',usage),identity,E('p','Bei Prüfung: '+(row.observed_enabled===true?'aktiv':row.observed_enabled===false?'ausgeschaltet':'Aktivierung unklar')));
       const effects=[];if(row.writes_owner)effects.push('schaltet Raumstatus');if(row.writes_timer)effects.push('schaltet Nachlauf');if(row.reads_status?.length)effects.push('liest '+row.reads_status.join(', '));if(row.reads_timer)effects.push('liest Timer');
       if(effects.length)entry.append(E('p',effects.join(' · ')));
       const reuseLabel={retain_controller:'Zur Weiterverwendung als bestehende Steuerung prüfen; nicht allein wegen des Schreibzugriffs ersetzen.',review_mixed_controller:'Gemischte Logik einzeln prüfen. Nicht die ganze Automation deaktivieren: Weitere Aktionen könnten betroffen sein.',retain_consumer:'Bestehenden Verbraucher erhalten; bei einer späteren Änderung seine Eingänge gesondert prüfen.',inspect_relationship:'Zuordnung und tatsächliches Verhalten erst klären; keine Übernahmebereitschaft belegt.'}[row.reuse_disposition];
       if(reuseLabel)entry.append(E('p',reuseLabel,'ps-muted'));
       if(row.affected_entities?.length)entry.append(E('p','Direkt erkannte Bezüge: '+row.affected_entities.join(', ')));
       if(row.limitations.length)entry.append(E('p','Nicht vollständig aufgelöst: '+row.limitations.join(', '),'ps-warning'));
       report.append(entry);
     }
     if(!existingReview.automations.length)report.append(E('p','Keine Automationen in dieser begrenzten Suche gefunden. Das beweist nicht, dass keine Verbraucher existieren.','ps-warning'));
     section.append(report);
   }output.append(section);
 }
 function organizationLink(text,role){const link=E('a',text);link.href='#ps-organization';link.addEventListener('click',()=>window.PilotSuiteOrganization?.focusRole(role));return link;}
 async function reviewExisting(){
   if(!data?.existing?.configured||busy||editing)return;
   const z=zone,r=revision,g=generation;busy=true;existingReview=null;render();note('Bestandsautomationen werden ausschließlich gelesen …');
   try{const result=await api('presence-adoption/review','POST',{revision:r});
     if(!current(z,r,g))return;
     if(result.mode!=='existing_control'||result.zone_id!==z||result.revision!==r||result.execution?.allowed!==false||result.reuse_review?.apply_implemented!==false)throw Error('Bestandsprüfung gehört nicht mehr zum aktuellen Stand.');
     existingReview=result;
   }catch(e){if(current(z,r,g))note('Bestandsprüfung nicht bestätigt: '+e.message);}
   finally{busy=false;if(current(z,r,g)&&data){const message=notice.textContent;render();note(existingReview?'Bestandsprüfung abgeschlossen. Keine Automation verändert.':message);}editingChanged();}
 }
 async function reloadBasis(){if(typeof loadSelection==='function'&&zone)await loadSelection(zone);else if(typeof load==='function')await load();}
 function startEditor(title){editing=true;editor.replaceChildren(E('h3',title));tools.querySelectorAll('button').forEach(b=>b.disabled=true);}
 function cancel(){if(busy)return;editing=false;plan=null;editor.replaceChildren();render();reloadBasis().catch(()=>note('Aktuellen Zonenstand erneut laden.')).finally(editingChanged);}
 async function save(action){if(busy)return;busy=true;try{await action();}catch(e){note(e.message);}finally{busy=false;if(!editing){try{await reloadBasis();}catch{note('Aktuellen Zonenstand erneut laden.');}if(data)render();else if(eligible())await read();}editingChanged();}}
 function openEditor(){
   if(!data||busy)return;startEditor('PilotSuite-Bewertung · Quellen und Zeiten');
   const form=E('form');form.id='ps-zone-form';const values=data.spec;
   const controls=E('div','','ps-zone-form-grid');
   const grace=number(values.grace_seconds,1,86400),clear=number(values.clear_seconds,0,300),support=number(values.support_limit_seconds,0,14400);
   const mode=select([['compare','Vergleichen'],['publish','Eigenen HA-Anwesenheitssensor veröffentlichen'],['paused','Präsenzinstanz pausieren']],data.mode);
   const comparison=select([['','Kein Vergleich'],...data.catalog.filter(e=>e.entity_id.startsWith('input_boolean.')||e.entity_id.startsWith('binary_sensor.')).map(e=>[e.entity_id,e.name])],values.comparison_entity||'');
   controls.append(labelled('Nachlauf (s)',grace),labelled('Stabile Freiphase (s)',clear),labelled('Maximale Nutzungsstützung (s)',support),labelled('Betriebsmodus',mode),labelled('Zusätzlicher Vergleichsstatus (nur lesen)',comparison));form.append(controls);
   form.append(E('p','Die Zeiten hier gelten nur für die eigene PilotSuite-Bewertung. Bestehende Automationen und deren Timer werden dadurch nicht verändert. Für Boolean, Timer und öffentlichen Sensor „Vorhandenen Bestand verbinden“ nutzen.','ps-muted'));
   form.append(E('p','Ein ausgeschalteter Ereignissensor ist nicht allein wegen fehlender Zustandswechsel veraltet. Meldealter 0 nutzt seinen gültigen HA-Zustand; periodische Quellen können eine Altersgrenze erhalten.','ps-muted'));
   const selected=new Map(values.sources.map(s=>[s.entity_id,s]));const candidates=data.catalog.filter(e=>selected.has(e.entity_id)||e.entity_id.startsWith('binary_sensor.')||e.entity_id.startsWith('media_player.'));
   const inputs=[];const filter=E('input');filter.type='search';filter.placeholder='Quellen suchen';filter.setAttribute('aria-label','Präsenzquellen suchen');form.append(filter);
   const list=E('div','','ps-zone-source-editor');
   for(const e of candidates){
      const v=selected.get(e.entity_id)||{kind:e.entity_id.startsWith('media_player.')?'support':e.device_class==='motion'?'pulse':'continuous',required:true,max_age:0,group:e.entity_id,can_start:!e.entity_id.startsWith('media_player.'),active_states:e.entity_id.startsWith('media_player.')?['playing']:['on']};
      const row=E('fieldset','','ps-zone-source-edit');const enabled=E('input');enabled.type='checkbox';enabled.checked=selected.has(e.entity_id);
      const title=E('legend');title.append(enabled,document.createTextNode(' '+e.name));row.append(title,E('code',e.entity_id));
      const kind=select([['continuous','Dauerpräsenz'],['pulse','Aktivitätsimpuls'],['support','Nutzungsindiz']],v.kind);
      const required=E('input');required.type='checkbox';required.checked=v.kind==='support'?false:v.required;
      const begin=E('input');begin.type='checkbox';begin.checked=v.can_start;
      const age=number(v.max_age,0,86400),group=E('input');group.value=v.group;group.maxLength=80;
      const active=E('input');active.value=v.active_states.join(', ');active.maxLength=200;
      const fields=E('div','','ps-zone-form-grid');fields.append(labelled('Typ',kind),labelled('Meldealter (s; 0 = ereignisbasiert)',age),labelled('Gemeinsame Indiz-/Abdeckungsgruppe',group),labelled('Aktivzustände, kommasepariert',active),labelled('Für Freigabe erforderliche Abdeckung',required),labelled('Darf Aufenthalt beginnen',begin));row.append(fields);list.append(row);
      kind.addEventListener('change',()=>{if(kind.value==='support')required.checked=false;});
      inputs.push({e,row,enabled,kind,required,begin,age,group,active});
   }form.append(list);filter.addEventListener('input',()=>{const q=filter.value.toLowerCase();for(const i of inputs)i.row.hidden=!(i.e.name+' '+i.e.entity_id).toLowerCase().includes(q);});
   const submit=E('button','Konfiguration speichern');submit.type='submit';form.append(submit,B('Verwerfen',cancel));
   form.addEventListener('submit',event=>{event.preventDefault();save(async()=>{
      const spec={grace_seconds:Number(grace.value),clear_seconds:Number(clear.value),support_limit_seconds:Number(support.value),comparison_entity:comparison.value||null,
        sources:inputs.filter(i=>i.enabled.checked).map(i=>({entity_id:i.e.entity_id,kind:i.kind.value,required:i.required.checked,max_age:Number(i.age.value),group:i.group.value,can_start:i.begin.checked,active_states:i.active.value.split(',').map(x=>x.trim()).filter(Boolean)}))};
      if(mode.value==='publish'&&!window.confirm('Nur das verifizierte eigene Ausgangspaket dieser Zone veröffentlichen? Bestehende Automationen werden nicht übernommen.'))return;
      const next=await api('presence','PUT',{revision,spec,mode:mode.value});
      editing=false;data=next;revision=next.revision;editor.replaceChildren();render();
   });});editor.append(form);grace.focus();grace.scrollIntoView({block:'center'});
 }
 function chart(series,period=historyData){
   const article=E('article','','ps-zone-chart');article.append(E('h4',series.name),E('p',`${series.record_count} Mess-/Zustandspunkte · ${series.changes} bekannte Wechsel${series.decimated?' · Anzeige verdichtet':''}`,'ps-muted'));
   if(series.unit_conflict){article.append(E('p','Einheitenkonflikt: keine gemeinsame Zahlenachse.','ps-warning'));return article;}
   const pts=series.points||[],model=window.PilotSuiteZonePresenceModel.plot(series,period.start,period.end);
   if(model.error){article.append(E('p',model.error==='no_values'?'Keine gültigen aufgezeichneten Werte; Datenlücken sind nicht Null.':'Keine gemeinsame Darstellung möglich; einzelne Zustände stehen in der Tabelle.'));}
   else{
     const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 820 150');svg.setAttribute('role','img');svg.setAttribute('aria-label',series.name+' Zeitverlauf mit Datenlücken');
     for(const segment of model.segments){let d='';for(const [i,p] of segment.entries())d+=i?(model.numeric?` L ${p.x} ${p.y}`:` H ${p.x} V ${p.y}`):`M ${p.x} ${p.y}`;
       const line=document.createElementNS(ns,'path');line.setAttribute('d',d);line.setAttribute('class','ps-zone-line');svg.append(line);
       if(segment.length===1){const c=document.createElementNS(ns,'circle');c.setAttribute('cx',segment[0].x);c.setAttribute('cy',segment[0].y);c.setAttribute('r','3');c.setAttribute('class','ps-zone-point');svg.append(c);}
     }
     for(const item of model.labels){const tx=document.createElementNS(ns,'text');tx.setAttribute('x','5');tx.setAttribute('y',String(item.y));tx.textContent=model.numeric?fmt(item.value)+(series.unit?' '+series.unit:''):item.value;svg.append(tx);}
     const times=E('p',date(period.start)+' – '+date(period.end),'ps-muted');article.append(svg,times);
   }
   const details=E('details');details.append(E('summary','Messwerte als Tabelle'));const table=E('table');
   for(const [t,v] of pts.slice(-200)){const tr=E('tr');tr.append(E('td',date(t)),E('td',v===null?'Unbekannt':String(v)));table.append(tr);}details.append(table);article.append(details);return article;
 }
 async function openHistory(){
   if(!data||busy)return;startEditor('Sensordaten & historische Zustände');
   editor.append(E('p','Automatisch werden zunächst 24 Stunden geladen. Ältere Zeiträume sind ohne neue Freigabe abrufbar; bis 31 Tage je Anfrage. Nicht aufgezeichnete Zeiträume bleiben Lücken.','ps-muted'));
   const preset=select([['1','1 Stunde'],['6','6 Stunden'],['24','24 Stunden'],['168','7 Tage'],['720','30 Tage']],'24');
   const ending=E('input');ending.type='datetime-local';ending.value=new Date(Date.now()-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16);
   const choices=E('div','','ps-zone-data-choices');const checks=[];
   for(const item of data.catalog){const c=E('input');c.type='checkbox';c.checked=checks.length<12;c.value=item.entity_id;checks.push(c);choices.append(labelled(item.name,c));}
   editor.append(labelled('Zeitraum',preset),labelled('Ende (lokale Zeit)',ending),choices);
   const fetchData=async()=>save(async()=>{const ids=checks.filter(c=>c.checked).map(c=>c.value);const end=new Date(ending.value).getTime();
     if(!Number.isFinite(end))throw Error('Gültiges Datum erforderlich');const z=zone,r=revision,g=generation;
     const result=await api('data','POST',{revision:r,start:new Date(end-Number(preset.value)*3600000).toISOString(),end:new Date(end).toISOString(),entity_ids:ids});
     if(!current(z,r,g))return;historyData=result;charts.replaceChildren(E('h3','Reale Sensorverläufe'),E('p',result.warning,'ps-muted'));
     for(const series of result.sources)charts.append(chart(series));note(`${result.record_count} aufgezeichnete Punkte ausgewertet; keine Datenfreigabe zusätzlich erforderlich.`);
   });
   editor.append(B('Zeitraum laden',fetchData),B('Ansicht schließen',()=>{editing=false;editor.replaceChildren();render();editingChanged();}));await fetchData();
 }
 async function preparePackage(){if(!data||busy)return;startEditor('Eigenen Anwesenheitssensor bereitstellen');editor.append(B('Schließen',cancel));await save(async()=>{
   plan=await api('presence/package','POST',{revision});renderPlan('presence/package');
 });}
 function prepareMissingHelper(){
   if(!data||busy)return;startEditor('Fehlenden Bestandshelfer ergänzen');
   const role=select([['presence_status','Interner Boolean'],['presence_timer','Nachlauftimer']],'presence_status');
   const duration=number(180,1,86400),durationLabel=labelled('Timerdauer (Sekunden)',duration);
   const update=()=>{durationLabel.hidden=role.value!=='presence_timer';};role.addEventListener('change',update);update();
   editor.append(E('p','Nur einen tatsächlich fehlenden Baustein anlegen. Vorhandene Helfer zuerst verbinden; ein Timer ist bei einer bestehenden for:-Regel nicht automatisch erforderlich.'),
     labelled('Fehlende Funktion',role),durationLabel,
     E('p','Die Anlage verbindet keine Automation und meldet keine Anwesenheit. Ein neuer Boolean auf Aus und ein inaktiver Timer sind kein Freibeleg. Ein öffentlicher Sensor benötigt zusätzlich eine geprüfte Gültigkeitslogik.','ps-warning'),
     B('Einzelhelfer-Plan prüfen',()=>save(async()=>{
       if(role.value==='presence_timer'&&!duration.reportValidity())return;
       plan=await api('presence/package','POST',{revision,helper_role:role.value,duration_seconds:role.value==='presence_timer'?Number(duration.value):null});renderPlan('presence/package');
     })),B('Verwerfen',cancel));role.focus();
 }
 function renderPlan(path){
   editor.replaceChildren(E('h3','Änderungsvorschau'));
   if(plan.state==='migration_required'){editor.append(E('p',plan.reason,'ps-warning'),B('Schließen',cancel));return;}
   if(plan.kind==='presence_helper'){
     const op=plan.operations[0];editor.append(E('p','Ein neuer, noch nicht angeschlossener Helfer für: '+op.suggested_display_name),E('pre',op.entity_id,'ps-zone-plan'));
     if(plan.details.duration_seconds!==null)editor.append(E('p','Vorgesehene Timerdauer: '+plan.details.duration_seconds+' Sekunden. Keine Änderung einer bestehenden HA-Nachlaufregel.'));
     editor.append(E('p','Zuordnung, Automationen und Steuerungsverantwortung bleiben unverändert. Der Anfangszustand belegt keine Anwesenheit oder Abwesenheit. Anzeigename und Habitus-Rollen können später separat geprüft werden.','ps-warning'),
       E('p','Rückweg: keine automatische Löschung. Vor Entfernen des neu angelegten Helfers seine Verbraucher prüfen.'),
       B('Diesen einzelnen Helfer anlegen',()=>save(async()=>{
         if(!window.confirm('Genau diesen neuen Helfer in Home Assistant anlegen, ohne Zuordnung oder Automationsänderung?'))return;
         const result=await api(`presence/package/${plan.id}/apply`,'POST',{sha256:plan.sha256,confirm:true});
         editor.replaceChildren(E('h3',result.state==='verified'?'Helferanlage bestätigt · Anschluss noch offen':'Helferanlage nicht vollständig bestätigt'),
           E('pre',op.entity_id,'ps-zone-plan'),E('p',result.state==='verified'?'Bestand aktualisieren und den Helfer ausdrücklich zuordnen. Die verantwortliche Automation und die Gültigkeit des öffentlichen Sensors müssen separat geprüft werden.':'Nicht blind erneut anlegen. Den gespeicherten Plan unter Automationen prüfen.'),B('Schließen',cancel));
       })),B('Schließen',cancel));return;
   }
   editor.append(E('p',path==='ontology'?'Anzeigename und Rollenlabels. Technische ID und physische Bereiche bleiben erhalten.':'Neue interne Helfer und ein Template-Anwesenheitssensor. Keine bestehende Automation wird verändert; Veröffentlichung bleibt zunächst aus.'));
   if(path==='presence/package'){
     editor.append(E('p','Bestehende Zuordnung bleibt erhalten. Dieses zusätzliche Paket steuert keine vorhandene Automation und veröffentlicht zunächst nichts.','ps-warning'));
     const meanings={anwesenheit_intern:['Interner Anwesenheitsstatus','Boolean als eigener Zustandsspeicher.'],entscheidung_gueltig:['Gültigkeit der Entscheidung','Trennt eine gültige Entscheidung von unbekannten Daten.'],gueltig_bis:['Ablauffrist der Gültigkeit','Begrenzt die Gültigkeit ohne frische Bestätigung.'],nachlauf:['Eigener Nachlauftimer','Bildet den PilotSuite-Nachlauf ab; ersetzt keinen Bestands-Timer.'],sensor:['Öffentlicher Anwesenheitssensor','Meldet den eigenen Zustand mit Gültigkeitsprüfung.']};
     const list=E('ol');for(const operation of plan.operations){const [title,description]=meanings[operation.role]||['Weitere geplante Änderung','Technische Details vor der Bestätigung prüfen.'];const item=E('li','','ps-package-change');item.append(E('strong',title),E('p',description),E('code',operation.entity_id));list.append(item);}editor.append(list);
     editor.append(E('p','Rückweg: Veröffentlichung ausgeschaltet lassen. Angelegte Helfer werden hier nicht automatisch gelöscht; eine spätere Entfernung braucht eine eigene Prüfung ihrer Verbraucher.','ps-muted'));
   }
   const details=E('details');details.append(E('summary','Technische Änderungsdetails'));const raw=E('pre',JSON.stringify(plan.operations,null,2));raw.className='ps-zone-plan';details.append(raw);editor.append(details);
   const apply=B('Genau diesen Plan anwenden',()=>save(async()=>{
     if(!window.confirm('Angezeigte Änderungen jetzt in Home Assistant ausführen?'))return;
     const result=await api(`${path}/${plan.id}/apply`,'POST',{sha256:plan.sha256,confirm:true});
     editor.append(E('p','Planstatus: '+result.state,'ps-notice'));apply.disabled=true;
     if(result.state==='verified'&&path==='ontology')editor.append(B('Rücknahme prüfen',()=>save(async()=>{plan=await api(`ontology/${result.id}/restore-preview`,'POST',{revision});renderPlan('ontology');})));
     if(result.state!=='verified')note('Nicht vollständig bestätigt. Nicht wiederholen; vorhandenen Planstatus prüfen.');
   }));editor.append(apply,B('Schließen',cancel));
 }
 async function openOntology(){
   if(!data||busy)return;startEditor('Entität benennen und ontologisch zuordnen');
   await save(async()=>{
     ontology=await api('ontology');const eligible=ontology.catalog.filter(r=>r.in_registry&&!r.disabled);
     if(!eligible.length)throw Error('Keine aktive stabile Entität für die Zuordnung verfügbar');
     const entities=select(eligible.map(r=>[r.entity_id,r.name+' · '+r.entity_id]),eligible[0].entity_id);
     const name=E('input');name.maxLength=120;const target=E('input');target.placeholder='Unverändert lassen';
     const zoneLabel=select([['','Zonenlabel auswählen'],...ontology.labels.map(l=>[l.label_id,l.name])],'');
     const roleBox=E('div','','ps-zone-data-choices'),roleInputs=[];
     for(const role of ontology.roles){const i=E('input');i.type='checkbox';i.value=role;roleInputs.push(i);roleBox.append(labelled(role,i));}
     const update=()=>{const r=ontology.catalog.find(r=>r.entity_id===entities.value);name.value=r?.name||'';target.value=r?.entity_id||'';};entities.addEventListener('change',update);update();
     editor.append(labelled('Entität',entities),labelled('Anzeigename',name),labelled('Technische Entity-ID (Migration wird separat geprüft)',target),labelled('Logische Zonenmitgliedschaft',zoneLabel),roleBox,
       E('p','Verbindliche Rollen aus „Habituszonen“. Vorhandene andere Labels und physische Bereiche bleiben erhalten. Label-/namenbasierte Automationen können auf eine Änderung reagieren.','ps-warning'),
       B('Änderungsplan prüfen',()=>save(async()=>{plan=await api('ontology','POST',{revision,entity_id:entities.value,name:name.value,zone_label:zoneLabel.value,roles:roleInputs.filter(i=>i.checked).map(i=>i.value),target_entity_id:target.value});renderPlan('ontology');})),B('Verwerfen',cancel));
   });
 }
 const poll=window.setInterval(()=>{if(eligible()&&!document.hidden&&!editing&&!busy&&Date.now()-last>5000)read({background:true});},5000);
 window.addEventListener('pagehide',()=>window.clearInterval(poll),{once:true});
 window.PilotSuiteZonePresence={
   context(host,z,r,ok,module,view){
     if(root!==host)mount(host);host.hidden=!['zone','config','history','all'].includes(view);
     if(z!==zone||r!==revision){generation++;zone=z;revision=r;data=null;historyData=null;existingReview=null;last=0;if(!editing){output.replaceChildren();charts.replaceChildren();}}
     valid=ok;
     if(!ok&&!editing){last=0;unavailable('Grundlage wird aktualisiert; keine veraltete Aussage.');}
     if(eligible()&&!editing&&!busy&&Date.now()-last>5000)read();
   },dirty:()=>editing||busy,
   invalidate(){valid=false;generation++;data=null;existingReview=null;last=0;if(output)unavailable('Quelle oder Verbindung geändert; neu laden.');if(charts&&!editing)charts.replaceChildren();}
 };
})();
