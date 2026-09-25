/* Presentation-only helpers: no configuration storage, inference or execution authority. */
(function(root) {
  'use strict';
  const views = Object.freeze(['cockpit','zone','config','history','workbench','system','all']);
  const roles = Object.freeze({presence:'Präsenz & Bewegung',temperature:'Temperatur',humidity:'Feuchte',
    illuminance:'Helligkeit (Lux)',daylight_binary:'Helligkeitsindikator',light:'Leuchten',
    climate:'Klimaregler',media:'Medienplayer',atmosphere:'Atmosphärenwunsch',reference_temperature:'Vergleichstemperatur'});
  const modules = Object.freeze([
    {id:'presence',title:'Anwesenheit',icon:'presence',roles:['presence'],description:'Quellen, Raumstatus und Nachlauf getrennt prüfen.'},
    {id:'lighting',title:'Beleuchtung',icon:'light',roles:['illuminance','daylight_binary','light'],description:'Tageslicht und Leuchtenzustand klar unterscheiden.'},
    {id:'climate',title:'Raumklima',icon:'climate',roles:['temperature','humidity','climate','reference_temperature'],description:'Messwerte und Regler in einer gemeinsamen Ansicht.'},
    {id:'media',title:'Musik & Atmosphäre',icon:'media',roles:['media','atmosphere'],description:'Player und bewusste Wünsche zuordnen.'}
  ]);
  const number = v => typeof v === 'number' && Number.isFinite(v) ? v.toLocaleString('de-DE',{maximumFractionDigits:1}) : '—';
  const count = v => Number.isSafeInteger(v) && v >= 0 ? v : null;
  function preferences(value) {
    const p = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
    return {view:views.includes(p.view)?p.view:'cockpit',theme:['auto','light','dark'].includes(p.theme)?p.theme:'auto',
      density:p.density==='compact'?'compact':'comfortable',ids:p.ids===true};
  }
  function current(context, inventory, zone) {
    return !!context && !!inventory && !!zone && inventory.zone_id===zone &&
      Number.isSafeInteger(inventory.revision) && inventory.revision>=0 && context.revision===inventory.revision &&
      context.foundation?.zone_id===zone && context.foundation?.revision===inventory.revision;
  }
  function metric(summary, kind) {
    const s=summary?.[kind];
    if(!s || !['available','partial'].includes(s.status)) return '—';
    if(typeof s.value==='number' && Number.isFinite(s.value)) return `${number(s.value)}${s.unit?' '+s.unit:''}`;
    if((kind==='presence'||kind==='light') && count(s.on)!==null && count(s.total)!==null)
      return `${s.on} / ${s.total} aktiv`;
    return '—';
  }
  function diff(before, after) {
    const b=before||{}, a=after||{}, rows=[];
    for(const k of Object.keys(roles)) {
      const old=[...new Set(Array.isArray(b.roles?.[k])?b.roles[k]:[])].sort();
      const next=[...new Set(Array.isArray(a.roles?.[k])?a.roles[k]:[])].sort();
      if(JSON.stringify(old)!==JSON.stringify(next)) rows.push({key:k,label:roles[k],before:old,after:next,kind:'sources'});
    }
    for(const [key,label] of [['learning','Aktivitätslernen'],['context_learning','Lichtkontext lernen']]) {
      if((b[key]===true)!==(a[key]===true)) rows.push({key,label,before:b[key]===true?'An':'Aus',after:a[key]===true?'An':'Aus',kind:'consent'});
    }
    const defaults={min_events:5,min_days:3,timezone:'UTC',day_mode:'all'};
    for(const [key,label] of [['min_events','Mindestaktivierungen'],['min_days','Beobachtungstage'],['timezone','Zeitzone'],['day_mode','Tagesgruppen']]) {
      const old=b.detector?.[key]??defaults[key], next=a.detector?.[key]??defaults[key];
      if(old!==next) rows.push({key,label,before:old,after:next,kind:'detector'});
    }
    return rows;
  }
  const api=Object.freeze({views,roles,modules,number,count,preferences,current,metric,diff});
  if(typeof module!=='undefined' && module.exports) module.exports=api;
  if(root) root.PilotSuiteWorkspaceModel=api;
})(typeof window!=='undefined'?window:null);
