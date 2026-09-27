/* Explicit live shadow session; GET reads cannot start collection or execute HA actions. */
(() => {
  'use strict';
  const E=(tag,text='',cls='')=>{const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e;};
  const B=(label,fn)=>{const b=E('button',label);b.type='button';b.addEventListener('click',fn);return b;};
  const labels={occupied:'Belegt',grace:'Nachlauf',vacant:'Frei',unknown:'Unklar',
    disabled:'Aus',running:'Schattenbetrieb',basis_changed:'Grundlage geändert',zone_paused:'Zone pausiert',invalid_checkpoint:'Zwischenstand ungültig'};
  let root=null,zone=null,revision=null,generation=0,busy=false,editing=false,stale=false,valid=false;
  let data=null,form=null,message=null,results=null,controls=null,lastRead=0,requestNumber=0;
  const eligible=()=>valid && root && !root.hidden && root.getClientRects().length>0;
  const currentBasis=(z,r,g)=>z===zone&&r===revision&&g===generation&&valid;
  const stateLabel=s=>labels[s]||'Unklar';
  const showTime=ts=>typeof ts==='number'&&Number.isFinite(ts)?new Date(ts*1000).toLocaleTimeString('de-DE'):'—';
  function note(text){if(message)message.textContent=text;}
  function safeResponse(d,z,r){
    return d?.schema==='pilotsuite-presence-shadow-v1'&&d.zone_id===z&&d.revision===r&&
      d.execution?.allowed===false&&Array.isArray(d.execution.actions)&&d.execution.actions.length===0&&
      ['disabled','running','basis_changed','zone_paused','invalid_checkpoint'].includes(d.state)&&
      Array.isArray(d.inputs?.sources)&&Array.isArray(d.inputs?.lights)&&Array.isArray(d.inputs?.lux_candidates);
  }
  async function request(method,payload){
    const response=await fetch(`api/v1/zones/${encodeURIComponent(zone)}/presence-shadow`,{
      method,headers:{'Content-Type':'application/json'},cache:'no-store',
      ...(payload?{body:JSON.stringify(payload)}:{})});
    const body=await response.json();
    if(!response.ok)throw Error(body.message||'Anfrage nicht bestätigt');return body;
  }
  async function read(){
    if(!eligible()||busy||editing)return;
    const z=zone,r=revision,g=generation,q=++requestNumber;lastRead=Date.now();
    try{
      const value=await request('GET');
      if(!currentBasis(z,r,g)||q!==requestNumber)return;
      if(!safeResponse(value,z,r))throw Error('Die Antwort passt nicht zum aktuellen Zonenstand. Neu laden.');
      data=value;stale=false;render();
    }catch(e){if(currentBasis(z,r,g)&&q===requestNumber){data=null;results.replaceChildren();note('Nicht aktuell: '+e.message);renderControls();}}
  }
  function renderControls(){
    controls.replaceChildren();
    const open=B(data?.enabled?'Schattenkonfiguration ändern':'Schattenvergleich konfigurieren',openEditor);
    open.id='ps-shadow-configure';open.disabled=!valid||!data||busy||editing;controls.append(open);
    const refresh=B('Vergleich aktualisieren',read);refresh.id='ps-shadow-refresh';refresh.disabled=busy||editing;controls.append(refresh);
    const stop=B('Schattenvergleich stoppen',()=>mutate('stop'));stop.id='ps-shadow-stop';stop.disabled=!valid||!data||data.state==='disabled'||busy||editing;controls.append(stop);
  }
  function render(){
    if(!root)return;renderControls();results.replaceChildren();
    if(!data)return;
    note(data.message);
    const d=data.current;
    const sourceLine=E('p',`${data.inputs.sources.length} bestätigte Rohquellen · HA-Vergleich: ${data.inputs.owner||'nicht zugeordnet'}`,'ps-muted');results.append(sourceLine);
    if(!d){results.append(E('p',data.state==='running'?'Noch kein aktueller Vergleich. Verbindung und Quellen prüfen.':'Der Vergleich verändert weder vorhandene Automationen noch deren Zuständigkeit.','ps-muted'));return;}
    const cards=E('div','','ps-shadow-cards');
    for(const [title,value,detail] of [
      ['Home Assistant',d.ha_status?.state==='on'?'Belegt':d.ha_status?.state==='off'?'Frei':'Unklar','Aktueller Bestandsstatus, kein Eingang des PilotSuite-Kerns'],
      ['PilotSuite',stateLabel(d.computed?.state),d.explanation||''],
      ['Vergleich',d.comparison==='same'?'Gleiche Aussage':d.comparison==='different'?'Abweichung prüfen':'Nicht bewertbar','Keine Bewertung, welches System richtig liegt']]){
      const c=E('article','','ps-kpi');c.append(E('span',title),E('strong',value),E('small',detail));cards.append(c);
    }
    results.append(cards);
    const deadline=d.computed?.deadline;
    const seconds=typeof deadline==='number'&&Number.isFinite(deadline)?Math.max(0,Math.ceil(deadline-d.observed_at)):null;
    results.append(E('p',`Abgleich ${showTime(d.observed_at)} · Nachlauf ${seconds===null?'nicht aktiv':seconds+' s bis '+showTime(deadline)} · Generation ${d.computed?.generation??'—'}`,'ps-muted'));
    const sources=E('details');sources.append(E('summary','Quellen und Meldealter'));
    for(const row of (d.sources||[]).slice(0,20)){
      const p=E('p');p.append(E('strong',row.entity_id),document.createTextNode(` · ${row.mode==='continuous'?'Dauerpräsenz':'Bewegungsimpuls'} · ${row.usable?row.state:'unklar'} · Meldealter ${typeof row.age_seconds==='number'?row.age_seconds+' s':'unbekannt'}`));sources.append(p);
    }
    sources.append(E('p','Meldealter beschreibt den HA-Zeitstempel, nicht die garantierte Messgenauigkeit. Ein unveränderter Sensor kann eine größere zulässige Meldefrist benötigen.','ps-muted'));results.append(sources);
    const lights=E('section','','ps-shadow-light');lights.append(E('h4','Lichtbedarf · nur Vorschlag'));
    if(d.manual_hold)lights.append(E('p','Manuelle Bedienung, Sperre oder deren unklarer Zustand hält den Lichtvorschlag an.','ps-warning'));
    if(!d.daylight?.usable)lights.append(E('p','Keine aktuell nutzbare, ausdrücklich als Außenreferenz bestätigte Luxquelle. Innenraum-Lux wird nicht als Außenhelligkeit verwendet.','ps-muted'));
    for(const row of (d.lights||[]).slice(0,20)){
      const c=E('div','','ps-shadow-light-row');c.append(E('strong',row.entity_id),E('p',row.reason||'Kein bestätigter Vorschlag.'));
      const s=row.settings||{},parts=[];
      if(typeof s.on==='boolean')parts.push(s.on?'Einschalten':'Ausschalten');
      if(Number.isFinite(s.brightness_pct)&&s.brightness_pct>=0&&s.brightness_pct<=100)parts.push(`${s.brightness_pct} %`);
      if(Number.isFinite(s.color_temp_kelvin)&&s.color_temp_kelvin>=1500&&s.color_temp_kelvin<=10000)parts.push(`${s.color_temp_kelvin} K`);
      c.append(E('span',parts.join(' · ')||'Kein neuer Stellvorschlag','ps-badge'));lights.append(c);
    }
    if(!d.lights?.length)lights.append(E('p','Noch keine ausdrücklich zugeordneten Leuchten.','ps-muted'));
    lights.append(E('p','Keine Lampe, kein Timer, kein Raumstatus wird geschaltet. Musik/TV und automatische Optimierung sind nicht Teil dieses Vergleichs.','ps-muted'));results.append(lights);
  }
  function field(label,control){const l=E('label',label);l.append(control);form.append(l);return control;}
  function select(options,value){const s=E('select');for(const [v,label] of options){const o=E('option',label);o.value=v;s.append(o);}s.value=value;return s;}
  function number(label,id,value,min,max){const n=E('input');n.type='number';n.id=id;n.min=min;n.max=max;n.step=1;n.value=value;field(label,n);return n;}
  function openEditor(){
    if(!valid||!data||busy||editing)return;editing=true;stale=false;generation++;form.replaceChildren();form.hidden=false;
    form.append(E('h4','Schattenbetrieb ausdrücklich konfigurieren'),E('p','Speichert nur die folgenden Einstellungen und jeweils den letzten Betriebszwischenstand. Läuft nach App-Neustart weiter, solange die bestätigte Grundlage unverändert ist. Keine Verlaufs- oder Lernsammlung.','ps-muted'));
    const s=data.spec||{},sources=data.inputs.sources;
    for(const row of sources){const choice=select([['continuous','Dauerpräsenz'],['pulse','Bewegungsimpuls']],s.source_modes?.[row.entity_id]||row.suggested_mode);choice.dataset.shadowSource=row.entity_id;field(row.name+' · Signaltyp',choice);if(row.blocked_reason)form.append(E('p',row.blocked_reason,'ps-warning'));}
    number('Nachlauf (Sekunden)','ps-shadow-grace',s.grace_seconds??300,1,86400);
    number('Maximales HA-Meldealter (Sekunden)','ps-shadow-age',s.max_source_age_seconds??1800,30,86400);
    field('Optionale zugeordnete Luxquelle',Object.assign(select([['','Keine'],...data.inputs.lux_candidates.map(id=>[id,id])],s.lux_source||''),{id:'ps-shadow-lux'}));
    const outdoor=E('input');outdoor.type='checkbox';outdoor.id='ps-shadow-outdoor';outdoor.checked=s.lux_provenance==='outdoor';field('Diese Quelle ist nach meiner Prüfung eine Außen-Tageslichtreferenz (nicht vom eigenen Raumlicht beeinflusst)',outdoor);
    field('Gewünschtes Atmosphärenprofil',Object.assign(select([['neutral','Neutral'],['focus','Fokus'],['relax','Entspannen'],['social','Gesellig'],['movie','Film']],s.atmosphere||'neutral'),{id:'ps-shadow-atmosphere'}));
    number('Minimale Zielhelligkeit (%)','ps-shadow-min',s.minimum_pct??15,0,100);
    number('Maximale Zielhelligkeit (%)','ps-shadow-max',s.maximum_pct??85,0,100);
    const off=E('input');off.type='checkbox';off.id='ps-shadow-off';off.checked=s.off_when_vacant===true;field('Bei bestätigtem Frei: Ausschalten vorschlagen (auch tagsüber)',off);
    form.append(E('p','Ein fehlender manueller Override ist kein Beweis für freie Steuerungsrechte. Vorgeschlagen werden nur Eigenschaften zugeordneter Leuchten.','ps-muted'));
    if(data.inputs.issues.length)form.append(E('p','Zuerst in Bestand & Ordnung prüfen: '+data.inputs.issues.join(', '),'ps-warning'));
    const actions=E('div','','selection-tools');const start=B('Schattenvergleich bestätigen und starten',()=>mutate('start'));start.id='ps-shadow-start';start.disabled=data.inputs.issues.length>0||!data.inputs.zone_enabled;
    actions.append(start,B('Verwerfen',()=>{editing=false;stale=false;form.hidden=true;form.replaceChildren();renderControls();read();}));form.append(actions);renderControls();
  }
  async function mutate(operation){
    if(busy||!data||!valid||stale)return;
    if(operation==='start'&&!window.confirm('Diesen Schattenvergleich mit den angezeigten Quellen und Grenzen starten? Er berechnet dauerhaft lokale Zwischenstände, führt aber keine HA-Aktion aus und lernt keine Präferenzen.'))return;
    const spec=operation==='start'?{
      source_modes:Object.fromEntries([...form.querySelectorAll('[data-shadow-source]')].map(e=>[e.dataset.shadowSource,e.value])),
      grace_seconds:Number(document.getElementById('ps-shadow-grace').value),
      max_source_age_seconds:Number(document.getElementById('ps-shadow-age').value),
      lux_source:document.getElementById('ps-shadow-lux').value||null,
      lux_provenance:document.getElementById('ps-shadow-outdoor').checked?'outdoor':'unconfirmed',
      atmosphere:document.getElementById('ps-shadow-atmosphere').value,
      minimum_pct:Number(document.getElementById('ps-shadow-min').value),maximum_pct:Number(document.getElementById('ps-shadow-max').value),
      off_when_vacant:document.getElementById('ps-shadow-off').checked}:null;
    const z=zone,r=revision,g=generation;busy=true;renderControls();for(const e of form.elements)e.disabled=true;
    note('Schattenkonfiguration wird geprüft …');
    try{
      const value=await request('POST',{operation,revision:r,confirm:true,...(spec?{spec}:{})});
      if(!currentBasis(z,r,g))throw Error('Zonenstand während der Anfrage geändert. Bitte neu laden.');
      if(!safeResponse(value,z,r+1))throw Error('Unbestätigte Speicherantwort. Zustand neu laden, nicht blind wiederholen.');
      editing=false;busy=false;form.hidden=true;form.replaceChildren();data=value;revision=value.revision;generation++;
      // Refresh the canonical shared revision, never patch a parallel role store.
      await loadSelection(z);
      if(zone===z){data=value;render();}
    }catch(e){note('Nicht bestätigt: '+e.message+' Keine automatische Wiederholung.');}
    finally{busy=false;for(const e of form.elements)e.disabled=false;renderControls();}
  }
  function context(target,z,r,ok,module,view){
    if(!root){root=target;root.append(E('h3','Präsenz-Livevergleich & Lichtbedarf'),E('p','Echte bestätigte Quellen im Schattenbetrieb. Kein Steuerungswechsel.','ps-muted'));
      message=E('p','','ps-muted');message.setAttribute('role','status');message.id='ps-shadow-message';
      controls=E('div','','selection-tools');form=E('form','','ps-shadow-form');form.id='ps-shadow-form';form.hidden=true;form.addEventListener('submit',e=>e.preventDefault());
      results=E('div');results.id='ps-shadow-result';root.append(message,controls,form,results);
    }
    target.hidden=!['presence','lighting'].includes(module)||!['zone','all'].includes(view);
    if(zone!==z||revision!==r){
      generation++;requestNumber++;
      if(editing){stale=true;note('Zonenstand geändert. Entwurf verwerfen und neu laden.');document.getElementById('ps-shadow-start')?.setAttribute('disabled','');return;}
      zone=z;revision=r;data=null;results.replaceChildren();lastRead=0;
    }
    valid=!!ok;
    if(!valid){generation++;requestNumber++;results.replaceChildren();if(!editing){data=null;note('Aktueller Zonenstand wird geprüft …');}renderControls();return;}
    if(!data&&!editing&&!busy){renderControls();read();}
  }
  setInterval(()=>{if(eligible()&&!document.hidden&&!editing&&!busy&&Date.now()-lastRead>=5000)read();},1000);
  window.PilotSuiteShadow={context,dirty:()=>editing||busy,invalidate:()=>{valid=false;generation++;requestNumber++;results?.replaceChildren();}};
})();
