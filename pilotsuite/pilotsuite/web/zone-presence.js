/* Zone-first configurator. Relevance authorizes analysis; writes use explicit plans. */
(() => {
 'use strict';
 const E=(t,txt='',cls='')=>{const e=document.createElement(t);e.textContent=txt;if(cls)e.className=cls;return e;};
 const B=(text,fn)=>{const b=E('button',text);b.type='button';b.addEventListener('click',fn);return b;};
 const select=(items,value)=>{const s=E('select');for(const [v,t] of items){const o=E('option',t);o.value=v;s.append(o);}s.value=value??'';return s;};
 const number=(value,min,max)=>{const n=E('input');n.type='number';n.value=value;n.min=min;n.max=max;return n;};
 const labelled=(text,input)=>{const l=E('label',text);l.append(input);return l;};
 const fmt=v=>typeof v==='number'&&Number.isFinite(v)?v.toLocaleString('de-DE',{maximumFractionDigits:1}):'—';
 const date=t=>typeof t==='number'?new Date(t*1000).toLocaleString('de-DE'):'—';
 const state=s=>({occupied:'Belegt',grace:'Nachlauf',vacant:'Frei',unknown:'Unklar',on:'An',off:'Aus',unavailable:'Nicht verfügbar'}[s]||s||'Unklar');
 let root,zone,revision,valid=false,generation=0,editing=false,busy=false,data=null,last=0,historyData=null,ontology=null,plan=null;
 let output,notice,tools,editor,charts;
 const eligible=()=>root&&!root.hidden&&root.getClientRects().length&&valid;
 const current=(z,r,g)=>zone===z&&revision===r&&generation===g&&valid;
 function note(t){if(notice)notice.textContent=t;}
 async function api(suffix,method='GET',body){
   const z=zone;const response=await fetch(`api/v1/zones/${encodeURIComponent(z)}/${suffix}`,{
     method,cache:'no-store',headers:{'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
   let value;try{value=await response.json();}catch{throw Error('Keine gültige Antwort');}
   if(!response.ok)throw Error(value.message||'Anfrage nicht bestätigt');return value;
 }
 async function read(){
   if(!eligible()||busy||editing)return;
   const z=zone,r=revision,g=generation;last=Date.now();
   try{const value=await api('presence');if(!current(z,r,g))return;
     if(value.schema!=='pilotsuite-zone-presence-v2'||value.zone_id!==z||value.revision!==r)throw Error('Zonenstand geändert; neu laden');
     data=value;render();
   }catch(e){if(current(z,r,g)){data=null;output.replaceChildren();note(e.message);}}
 }
 function mount(host){
   host.replaceChildren();root=host;
   root.append(E('h2','Zoneninstanz · Präsenz, Daten & Ordnung'),E('p','Relevant = Live- und verfügbare Historienauswertung. Keine weiteren Datenfreigaben. Ein HA-Ausgang wird nur über das geprüfte Helferpaket veröffentlicht.','ps-muted'));
   notice=E('p','','ps-notice');notice.setAttribute('role','status');tools=E('div','','selection-tools');editor=E('div');output=E('div');charts=E('div');
   root.append(notice,tools,editor,output,charts);
 }
 function render(){
   if(!data||editing)return;tools.replaceChildren();output.replaceChildren();
   const configure=B('Präsenz konfigurieren',openEditor);configure.id='ps-zone-configure';
   tools.append(configure,B('Aktualisieren',read),B('Sensordaten & Verläufe',openHistory),B('Entitäten → Ontologie',openOntology));
   if(!data.package)tools.append(B('Eigenen Anwesenheitssensor vorbereiten',preparePackage));
   if(busy)tools.querySelectorAll('button').forEach(button=>button.disabled=true);
   const d=data.current;const cards=E('div','','ps-shadow-cards');
   for(const [title,value,hint] of [
      ['Präsenz',d?state(d.state):'Nicht aktuell',d?.explanation||data.status],
      ['Bestandsvergleich',d?.comparison==='same'?'Übereinstimmung':d?.comparison==='different'?'Abweichung':'Nicht beurteilbar',d?state(d.ha_state):'—'],
      ['Nachlauf',d?.deadline?fmt(d.remaining_seconds)+' s':'—',d?.deadline?date(d.deadline):'Kein laufender Nachlauf'],
      ['Ausgang',data.mode==='publish'?'Veröffentlichung eingerichtet':'Nur vergleichen',(data.package?.entities?.sensor||'Noch kein eigenes Ausgangspaket')+' · '+(data.publication||'not_published')]]){
      const c=E('article','','ps-kpi');c.append(E('span',title),E('strong',value),E('small',hint));cards.append(c);
   } output.append(cards);
   if(d){const table=E('table','','ps-zone-source-table');const header=E('tr');for(const text of ['Quelle','Signaltyp','Zustand','Meldealter','Indirekte Frist'])header.append(E('th',text));table.append(header);
      for(const s of d.sources){const tr=E('tr');for(const text of [s.name||s.entity_id,s.kind,state(s.state),s.age_seconds===null?'Ereignisorientiert / unbekannt':fmt(s.age_seconds)+' s',date(s.support_until)])tr.append(E('td',text));table.append(tr);}
      const wrap=E('div','','ps-zone-scroll');wrap.append(table);output.append(wrap);
      const trace=data.trace||[];if(trace.length){output.append(E('p','Sitzungsverlauf · höchstens 128 Zustandswechsel im Arbeitsspeicher, keine historische Recorder-Aufzeichnung.','ps-muted'),chart({name:'Präsenzentscheidung im aktuellen Lauf',record_count:trace.length,changes:Math.max(0,trace.length-1),kind:'state',points:trace.map(r=>[r.observed_at,state(r.state)])},{start:trace[0].observed_at,end:Math.max(d.observed_at,trace[0].observed_at+1)}));}
   }
   note(data.analysis_enabled?'Auswertung anhand relevanter Quellen. Historische Werte werden nicht als heutige Präsenzereignisse abgespielt.':'Zone pausiert; keine aktuelle Auswertung.');
 }
 async function reloadBasis(){if(typeof loadSelection==='function'&&zone)await loadSelection(zone);else if(typeof load==='function')await load();}
 function startEditor(title){editing=true;editor.replaceChildren(E('h3',title));tools.querySelectorAll('button').forEach(b=>b.disabled=true);}
 function cancel(){if(busy)return;editing=false;plan=null;editor.replaceChildren();render();reloadBasis().catch(()=>note('Aktuellen Zonenstand erneut laden.'));}
 async function save(action){if(busy)return;busy=true;try{await action();}catch(e){note(e.message);}finally{busy=false;if(!editing){try{await reloadBasis();}catch{note('Aktuellen Zonenstand erneut laden.');}if(data)render();else if(eligible())await read();}}}
 function openEditor(){
   if(!data||busy)return;startEditor('Präsenzverhalten je Zone');
   const form=E('form');form.id='ps-zone-form';const values=data.spec;
   const controls=E('div','','ps-zone-form-grid');
   const grace=number(values.grace_seconds,1,86400),clear=number(values.clear_seconds,0,300),support=number(values.support_limit_seconds,0,14400);
   const mode=select([['compare','Vergleichen'],['publish','Eigenen HA-Anwesenheitssensor veröffentlichen'],['paused','Präsenzinstanz pausieren']],data.mode);
   const comparison=select([['','Kein Vergleich'],...data.catalog.filter(e=>e.entity_id.startsWith('input_boolean.')||e.entity_id.startsWith('binary_sensor.')).map(e=>[e.entity_id,e.name])],values.comparison_entity||'');
   controls.append(labelled('Nachlauf (s)',grace),labelled('Stabile Freiphase (s)',clear),labelled('Maximale Nutzungsstützung (s)',support),labelled('Betriebsmodus',mode),labelled('Bestehender HA-Anwesenheitsstatus',comparison));form.append(controls);
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
   });});editor.append(form);
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
   editor.append(B('Zeitraum laden',fetchData),B('Ansicht schließen',()=>{editing=false;editor.replaceChildren();render();}));await fetchData();
 }
 async function preparePackage(){if(!data||busy)return;startEditor('Eigenen Anwesenheitssensor bereitstellen');await save(async()=>{
   plan=await api('presence/package','POST',{revision});renderPlan('presence/package');
 });}
 function renderPlan(path){
   editor.replaceChildren(E('h3','Änderungsvorschau'));
   if(plan.state==='migration_required'){editor.append(E('p',plan.reason,'ps-warning'),B('Schließen',cancel));return;}
   editor.append(E('p',path==='ontology'?'Anzeigename und Rollenlabels. Technische ID und physische Bereiche bleiben erhalten.':'Neue interne Helfer und ein Template-Anwesenheitssensor. Keine bestehende Automation wird verändert; Veröffentlichung bleibt zunächst aus.'));
   const details=E('pre',JSON.stringify(plan.operations,null,2));details.className='ps-zone-plan';editor.append(details);
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
     ontology=await api('ontology');const entities=select(ontology.catalog.filter(r=>r.in_registry&&!r.disabled).map(r=>[r.entity_id,r.name+' · '+r.entity_id]),'');
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
 const poll=window.setInterval(()=>{if(eligible()&&!document.hidden&&!editing&&!busy&&Date.now()-last>5000)read();},5000);
 window.addEventListener('pagehide',()=>window.clearInterval(poll),{once:true});
 window.PilotSuiteZonePresence={
   context(host,z,r,ok,module,view){
     if(root!==host)mount(host);host.hidden=!['zone','config','history','all'].includes(view)||!['presence','lighting'].includes(module);
     if(z!==zone||r!==revision){generation++;zone=z;revision=r;data=null;historyData=null;last=0;if(!editing){output.replaceChildren();charts.replaceChildren();}}
     valid=ok;
     if(!ok&&!editing){output.replaceChildren();note('Grundlage wird aktualisiert; keine veraltete Aussage.');}
     if(eligible()&&!editing&&!busy&&Date.now()-last>5000)read();
   },dirty:()=>editing||busy,
   invalidate(){valid=false;generation++;data=null;if(output)output.replaceChildren();if(charts)charts.replaceChildren();if(tools)tools.querySelectorAll('button').forEach(button=>button.disabled=true);note('Quelle oder Verbindung geändert; neu laden.');}
 };
})();
