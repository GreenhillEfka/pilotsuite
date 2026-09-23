/* Scoped history UI: local SVGs, no external chart service, no auto-import. */
let historyData = null;
let historyRequest = null;
let historyBusy = false;
let historyGeneration = 0;
const historyLabels = {temperature:'Temperatur',humidity:'Feuchte',illuminance:'Helligkeit',presence:'Präsenz',light:'Licht',activity:'Präsenz + Licht'};
function historyInvalidate() {
  historyGeneration++; historyData=null; historyRequest=null;
  byId('history-display').hidden=true; byId('history-consent').checked=false;
  byId('history-import').disabled=true; text('history-message','Verläufe für diese Auswahl neu laden.');
}
function historyCheckRevision() {
  if (historyData && (historyData.zone_id !== selectionZone || historyData.revision !== contextData?.revision)) historyInvalidate();
}
function historyImportEnabled() {
  byId('history-import').disabled = historyBusy || !historyData || !byId('history-consent').checked || !contextData?.config.learning || !contextData?.enabled || historyRequest?.mode !== 'states' || historyData.end-historyData.start > 14*86400 || historyData.start < Date.now()/1000-14*86400-60;
}
byId('history-range').addEventListener('change', () => {
  const custom=byId('history-range').value==='custom';
  byId('history-start-label').hidden=!custom; byId('history-end-label').hidden=!custom;
  historyInvalidate();
});
for (const id of ['history-mode','history-start','history-end']) byId(id).addEventListener('change',historyInvalidate);
for (const id of ['history-kind','history-sources']) byId(id).addEventListener('change',renderHistoryChart);
byId('history-consent').addEventListener('change',historyImportEnabled);
byId('history-load').addEventListener('click',async () => {
  if (historyBusy || selectionBusy || contextEditing || selectionDraft?.dirty) { text('history-message','Offene Änderungen zuerst speichern oder verwerfen.'); return; }
  historyInvalidate(); const generation=historyGeneration, zone=selectionZone;
  historyBusy=true; byId('history-load').disabled=true; text('history-message','Lade ausgewählte HA-Quellen …');
  try {
    await loadContext();
    const end = byId('history-range').value==='custom' ? new Date(byId('history-end').value) : new Date(Date.now()-5000);
    const start = byId('history-range').value==='custom' ? new Date(byId('history-start').value) : new Date(+end-Number(byId('history-range').value)*86400000);
    const payload={start:start.toISOString(),end:end.toISOString(),mode:byId('history-mode').value,revision:contextData.revision};
    const result=await json(`api/v1/zones/${encodeURIComponent(zone)}/history`,{method:'POST',body:JSON.stringify(payload)});
    if (generation!==historyGeneration || zone!==selectionZone) return;
    historyData=result; historyRequest=payload; byId('history-display').hidden=false;
    const available=result.trends.sources.filter(s => s.record_count>0).length;
    text('history-message',`${available} von ${result.trends.sources.length} Quellen mit Datensätzen. Zeitraum ${historyDate(result.start)} bis ${historyDate(result.end)}. Keine Daten werden durch den Abruf dauerhaft importiert.`);
    renderHistoryChart(); renderHistoryActivity();
  } catch(error) { if(generation===historyGeneration) text('history-message',`Abruf nicht abgeschlossen: ${error.message}`); }
  finally { historyBusy=false; byId('history-load').disabled=false; historyImportEnabled(); }
});
byId('history-import').addEventListener('click',async () => {
  if (byId('history-import').disabled || selectionBusy || contextEditing || selectionDraft?.dirty) return;
  const zone=selectionZone, generation=historyGeneration;
  historyBusy=true; historyImportEnabled();
  text('history-message','Prüfe und übernehme freigegebene Aktivierungen …');
  try {
    const result=await json(`api/v1/zones/${encodeURIComponent(zone)}/history/import`,{method:'POST',body:JSON.stringify({...historyRequest,consent:true})});
    if (zone!==selectionZone || generation!==historyGeneration) return;
    await loadSelection(zone);
    text('history-message',`${result.receipt.accepted} neue Aktivierungen übernommen; ${result.receipt.retained_from_import} innerhalb der Speichergrenze erhalten. Doppelte oder zeitnahe Belege wurden ausgelassen. Rohhistorie und Lichtkontext wurden nicht gespeichert.`);
  } catch(error) { if(zone===selectionZone) text('history-message',`Import nicht bestätigt: ${error.message}`); }
  finally { historyBusy=false; byId('history-consent').checked=false; historyImportEnabled(); }
});
function historyDate(t) {
  return new Date(t*1000).toLocaleString('de-DE',{timeZone:historyData?.timezone || 'UTC',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'})+' '+(historyData?.timezone || 'UTC');
}
function historySvg(tag, attrs={}, value=null) {
  const element=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for (const [key,v] of Object.entries(attrs)) element.setAttribute(key,String(v));
  if (value!==null) element.textContent=value;
  return element;
}
function renderHistoryChart() {
  if(!historyData) return;
  const kind=byId('history-kind').value, data=historyData.trends;
  const reference=data.references.find(r=>r.kind===kind);
  const curves=[];
  if(kind==='activity') for(const r of data.references.filter(r=>['presence','light'].includes(r.kind))) curves.push({name:historyLabels[r.kind],points:r.points.map(p=>[p.t,p.value]),unit:null});
  if(reference) curves.push({name:'Zonenreferenz',points:reference.points.map(p=>[p.t,p.value]),unit:reference.unit});
  if(reference && !['presence','light'].includes(kind)) {
    curves.push({name:'Minimum der Hauptquellen',points:reference.points.map(p=>[p.t,p.min]),unit:reference.unit});
    curves.push({name:'Maximum der Hauptquellen',points:reference.points.map(p=>[p.t,p.max]),unit:reference.unit});
  }
  if(byId('history-sources').checked || !reference) for(const s of data.sources.filter(s=>s.kind===kind || (kind==='activity' && byId('history-sources').checked && ['presence','light'].includes(s.kind)))) curves.push({name:s.entity_id,points:s.points,unit:s.unit});
  const values=curves.flatMap(c=>c.points.map(p=>p[1])).filter(v=>v!==null).map(Number);
  const root=byId('history-chart'); root.replaceChildren();
  byId('history-legend').replaceChildren(); byId('history-table').replaceChildren();
  text('history-basis',`${data.basis==='hourly_source_statistics'?'Stundenmittel je Quelle; keine gemeinsame Zonenreferenz':'Zonenreferenz aus abgetasteten Zuständen'} · ${historyLabels[kind]} · ${historyData.timezone}. ${data.warning}`);
  if(!values.length) {root.textContent='Keine auswertbaren Werte dieser Klasse im geladenen Zeitraum.'; return;}
  const binary=['presence','light','activity'].includes(kind);
  let low=binary?0:Math.min(...values), high=binary?1:Math.max(...values);
  if(high===low) {high+=1;low-=1;}
  const x=t=>62+(t-historyData.start)/(historyData.end-historyData.start)*650;
  const y=v=>210-(Number(v)-low)/(high-low)*170;
  const svg=historySvg('svg',{viewBox:'0 0 760 270',role:'img','aria-label':`${historyLabels[kind]} im Zeitverlauf`});
  for(let i=0;i<3;i++) {
    const value=low+(high-low)*i/2;
    svg.append(historySvg('line',{x1:62,x2:712,y1:y(value),y2:y(value),class:'history-grid'}));
    svg.append(historySvg('text',{x:54,y:y(value)+4,'text-anchor':'end'},Number(value.toFixed(1)).toLocaleString('de-DE')));
  }
  svg.append(historySvg('text',{x:62,y:22},binary?'0 = inaktiv / aus · 1 = aktiv / an':curves[0]?.unit||''));
  for(const [t,anchor] of [[historyData.start,'start'],[(historyData.start+historyData.end)/2,'middle'],[historyData.end,'end']])
    svg.append(historySvg('text',{x:x(t),y:244,'text-anchor':anchor},historyDate(t).split(' ').slice(0,2).join(' ')));
  const colors=['#72e6b2','#e2af62','#a4a9f7','#70c8f0','#ed91c4','#d2df74'];
  curves.forEach((c,index)=>{
    const color=colors[index%colors.length]; let d='',last=null;
    for(const [t,v] of c.points) {
      if(v===null || (last && data.basis==='hourly_source_statistics' && t-last>3601)) {last=null;}
      if(v===null) continue;
      d+=last===null?`M${x(t)} ${y(v)} `:binary?`H${x(t)} V${y(v)} `:`L${x(t)} ${y(v)} `; last=t;
      // Points retain isolated observations that would otherwise have no stroke.
      const dot=historySvg('circle',{cx:x(t),cy:y(v),r:1.7,fill:color});
      dot.append(historySvg('title',{},`${c.name}: ${v} ${c.unit||''} · ${historyDate(t)}`));svg.append(dot);
    }
    svg.append(historySvg('path',{d,fill:'none',stroke:color,'stroke-width':index?1.2:2.5}));
    const legend=document.createElement('p'); legend.textContent=c.name;
    legend.style.color=color;byId('history-legend').append(legend);
  });
  root.append(svg);
  const table=document.createElement('table');
  const header=document.createElement('tr');
  for(const label of ['Zeit',...curves.map(c=>c.name)]) {const th=document.createElement('th');th.textContent=label;header.append(th);} table.append(header);
  const times=[...new Set(curves.flatMap(c=>c.points.map(p=>p[0])))].sort((a,b)=>a-b);
  const maps=curves.map(c=>new Map(c.points));
  for(const t of times) {const row=document.createElement('tr'); for(const value of [historyDate(t),...maps.map(m=>m.get(t)??'unbekannt')]) {const td=document.createElement('td');td.textContent=String(value);row.append(td);}table.append(row);}
  byId('history-table').append(table);
}
function renderHistoryActivity() {
  const root=byId('history-heatmap'), check=byId('history-validation');root.replaceChildren();check.replaceChildren();
  const activity=historyData.activity;
  if(!activity) {root.textContent='Historische Musterprüfung benötigt Lernfreigabe und genaue Zustandsverläufe.';return;}
  const table=document.createElement('table'), header=document.createElement('tr');
  for(const label of ['Tag',...Array.from({length:12},(_,i)=>`${i*2}–${i*2+2}`)]) {const th=document.createElement('th');th.textContent=label;header.append(th);}table.append(header);
  const maximum=Math.max(1,...activity.heatmap.map(e=>e.events));
  ['Mo','Di','Mi','Do','Fr','Sa','So'].forEach((day,index)=>{const row=document.createElement('tr');const name=document.createElement('th');name.textContent=day;row.append(name);
    for(let b=0;b<12;b++) {const cell=document.createElement('td');const n=activity.heatmap.find(e=>e.weekday===index&&e.start_hour===b*2)?.events;
      cell.textContent=n??'—';cell.title=n?`${n} Aktivierungen`:'Keine Belege; keine Aussage über Abwesenheit';if(n) cell.style.backgroundColor=`rgba(51,161,113,${0.15+0.5*n/maximum})`;row.append(cell);}table.append(row);});
  root.append(table);
  const note=document.createElement('p');note.textContent=`${activity.timezone}. ${activity.limitations}`;check.append(note);
  if(!activity.checks.length) {const p=document.createElement('p');p.textContent='Noch kein Zeitfenster mit ausreichenden Belegen im früheren Abschnitt.';check.append(p);}
  for(const c of activity.checks) {const p=document.createElement('p');p.textContent=`${c.start_hour}–${c.start_hour+2} Uhr (${c.day_group}): früher ${c.training_events} Aktivierungen an ${c.training_days} Tagen; später ${c.later_events} an ${c.later_days} Tagen. ${c.state==='reobserved'?'Erneut beobachtet, noch keine bestätigte Regel.':'Spätere Belege fehlen; Ergebnis offen.'}`;check.append(p);}
}
