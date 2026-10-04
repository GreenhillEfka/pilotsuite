/* One structural workspace, using the existing zone editor, stores and metadata plans. */
(() => {
 'use strict';
 const M=window.PilotSuiteWorkspaceModel,$=id=>document.getElementById(id),main=document.querySelector('main');
 const E=(tag,text='',cls='')=>{const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e;};
 const B=(text,fn)=>{const b=E('button',text);b.type='button';b.addEventListener('click',fn);return b;};
 const A=(text,view)=>{const a=E('a',text);a.href='#ps-'+view;return a;};
 let prefs=M.preferences(null);try{prefs=M.preferences(JSON.parse(localStorage.getItem('pilotsuite.workspace.v1')||'null'));}catch{}
 let view=prefs.view,busy=false,plan=null,planZone=null,verification=null,verificationZone=null,docKey='',cardKey='';
 const names={cockpit:'Habituszonen',config:'Zone bearbeiten',documentation:'Zonendokumentation'};
 const dirty=()=>busy||!!plan||zoneFormOpen||selectionBusy||!!selectionDraft?.dirty;
 const notice=E('p','','ps-notice');notice.id='ps-notice';notice.setAttribute('role','status');notice.hidden=true;
 function say(message){notice.textContent=message;notice.hidden=!message;}
 function savePrefs(){try{localStorage.setItem('pilotsuite.workspace.v1',JSON.stringify(prefs));}catch{say('Darstellung gilt nur für diese Sitzung.');}}
 function appearance(){const auto=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.dataset.psTheme=prefs.theme==='auto'?auto:prefs.theme;document.documentElement.dataset.psDensity=prefs.density;document.documentElement.dataset.psIds=String(prefs.ids);}
 const sidebar=E('aside','','ps-sidebar');sidebar.setAttribute('aria-label','PilotSuite Navigation');
 const brand=E('div','','ps-brand');brand.append(E('strong','PilotSuite'),E('small','HABITUSZONEN'));sidebar.append(brand);
 const nav=E('nav','','ps-nav');nav.setAttribute('aria-label','Arbeitsbereiche');
 for(const [id,title] of Object.entries(names))nav.append(A(title,id));sidebar.append(nav);
 const foot=E('div','','ps-sidebar-foot'),theme=E('select');theme.setAttribute('aria-label','Farbschema');
 for(const [id,title] of [['auto','Systemdarstellung'],['light','Hell'],['dark','Dunkel']])theme.append(new Option(title,id));
 theme.value=prefs.theme;theme.addEventListener('change',()=>{prefs.theme=theme.value;appearance();savePrefs();});
 const maintenance=E('a','Sicherung & Wiederherstellung');maintenance.href='maintenance';foot.append(theme,maintenance);sidebar.append(foot);
 document.body.insertBefore(sidebar,document.querySelector('.topbar'));
 $('refresh').textContent='Bestand aktualisieren';document.querySelector('.topbar').append($('refresh'));
 document.querySelector('.topbar .mode').textContent='Zonen · Zuordnungen · Dokumentation';
 document.querySelector('footer').textContent='PilotSuite · Habituszonen nachvollziehbar aufbauen.';
 const heading=E('div','','ps-page-heading'),title=E('h2');title.id='ps-view-title';title.tabIndex=-1;
 const subtitle=E('p','Bereiche und Tags zu einer klaren Zonenstruktur verbinden.','ps-muted');heading.append(title,subtitle);
 for(const child of [...main.children])child.hidden=true;
 main.prepend(heading,notice);heading.hidden=false;
 const context=$('zone-overview');context.hidden=false;
 for(const id of ['zone-toggle','zone-counts','zone-summary','zone-state-message'])$(id).hidden=true;
 $('zone-edit').textContent='Struktur bearbeiten';
 const cockpit=E('section','','panel');cockpit.id='ps-cockpit';
 const connection=E('p','','ps-muted');connection.id='ps-connection';
 const search=E('input');search.type='search';search.id='ps-zone-search';search.placeholder='Name oder Bereich';
 const searchLabel=E('label','Zone finden');searchLabel.append(search);
 const cards=E('div','','ps-zone-grid');cards.id='ps-zone-grid';cockpit.append(connection,searchLabel,cards);context.after(cockpit);
 const setup=$('zone-setup');setup.querySelector('h2').textContent='Bereiche, Mitglieder und Tags';
 for(const child of [...setup.children])if(child.id!=='zone-editor'&&child.tagName!=='H2')child.hidden=true;
 $('zone-editor').open=true;$('zone-editor').querySelector('summary').textContent='Zonenstruktur';
 const editorHint=$('zone-editor').querySelector('p');editorHint.textContent='Mitgliedschaft und Darstellungsrollen gemeinsam speichern. Der HA-Labelabgleich folgt mit einer konkreten Vorschau.';
 const runtimeHint=$('zone-fields').querySelector(':scope > p');if(runtimeHint)runtimeHint.textContent='Bestehende Auswertungseinstellungen bleiben erhalten. Neue Zonen starten ohne Auswertung.';
 $('zone-profile').closest('details').hidden=true;
 const configIntro=E('p','„Struktur bearbeiten“ öffnet die gespeicherten Zuordnungen. Neue Zone über „+ Neue Zone“.','ps-muted');setup.prepend(configIntro);
 const docs=E('section','','panel');docs.id='ps-structure-documentation';
 const docBody=E('div');docBody.id='ps-structure-body';const actions=E('div','','selection-tools');
 const verify=B('Mit Home Assistant prüfen',verifyNow);verify.id='ps-structure-verify';
 const sync=B('Labeländerungen vorbereiten',preview);sync.id='ps-structure-sync';
 const download=B('Dokumentation herunterladen',exportDocumentation);download.id='ps-structure-export';
 actions.append(verify,sync,download);const plans=E('div');plans.id='ps-structure-plan';
 docs.append(docBody,actions,plans);setup.after(docs);
 $('edit-status').hidden=true;$('error').hidden=true;
 const explanation={structure_not_saved:'Noch keine Zonenstruktur gespeichert.',label_not_bound:'Neues Zonenlabel noch nicht angelegt.',label_missing:'Verbundenes HA-Label fehlt.',no_members:'Noch keine Mitglieder gespeichert.',role_labels_ambiguous:'Benötigte Rollenlabels fehlen oder sind mehrdeutig.',areas_missing:'Gespeicherte Bereiche fehlen in Home Assistant.',extra_ha_members:'Das HA-Label umfasst weitere Entitäten. Mitglieder erneut einlesen und bewusst übernehmen oder im HA-Bestand klären.',ha_link_unresolved:'Eine gespeicherte Licht- oder Sound-Verknüpfung ist nicht mehr eindeutig erreichbar.',renamed:'Entität umbenannt; gespeicherte Identität bewusst klären.',disabled:'Entität deaktiviert.',identity_unresolved:'Identität fehlt oder ist mehrdeutig.',membership_missing:'Zonenlabel fehlt an Entität und Gerät.',roles_differ:'HA-Rollen weichen von der gespeicherten Struktur ab.'};
 explanation.shared_roles_conflict='Gespeicherte Rollen widersprechen einer weiteren Zone. Die gemeinsame Zuordnung zuerst klären.';
 const linkNames={light_group:'Gemeinsame Lichtgruppe',light_automation:'Freigabe der HA-Lichtautomatik',shutdown_script:'Manuelle Zonenabschaltung',sound_player:'Sound-Cloud-Player',sound_presence:'Präsenzfreigabe für Sound-Cloud',sound_cloud_switch:'Sound-Cloud-Zonenschalter',sound_favorite:'Favoriten-Vorauswahl',sound_daytime_volume:'Tageszeit-Lautstärke'};
 function zone(){return zoneDefinitions.find(z=>z.zone_id===selectionZone);}
 function basis(){return structureData?.zone_id===selectionZone&&structureData.revision===zone()?.revision;}
 function currentVerification(){return basis()&&verificationZone===selectionZone&&verification?.revision===structureData.revision?verification:null;}
 function busyControls(){for(const button of [verify,sync,download])button.disabled=dirty()||!basis();sync.disabled||=!structureData?.profile;for(const button of plans.querySelectorAll('button'))button.disabled=busy;}
 function renderCards(){
  const q=search.value.trim().toLocaleLowerCase('de'),data=zoneDefinitions.filter(z=>[z.name,...z.area_ids].join(' ').toLocaleLowerCase('de').includes(q));
  const key=JSON.stringify([data,selectionZone,zoneStructures,zoneAreaNames]);if(key===cardKey)return;cardKey=key;
  const focused=document.activeElement?.dataset?.psZone;cards.replaceChildren();
  for(const z of data){const saved=zoneStructures[z.zone_id],card=E('article','','ps-zone-card');card.append(E('h3',z.name),E('p',`${z.area_ids.length} Bereiche · ${saved?.saved?saved.member_count+' gespeicherte Mitglieder':'Mitgliedschaft noch offen'}`,'ps-muted'),E('p',z.area_ids.map(id=>zoneAreaNames[id]||id).join(' · ')||'Bereiche noch offen'),E('p',saved?.saved?(saved.label_id?'Label verbunden · HA-Abgleich in der Dokumentation':`Label „${saved.label_name}“ noch anzulegen`):'Struktur noch nicht eingerichtet','ps-muted'));
   if(saved?.ha_link_kinds?.length)card.append(E('p',`${saved.ha_link_kinds.includes('light_group')?'Licht verknüpft':'Licht offen'} · ${saved.ha_link_kinds.includes('sound_player')?'Sound-Cloud verknüpft':'Sound-Cloud ohne Player'}`,'ps-muted'));
   const open=B('Zone öffnen',async()=>{if(dirty()){say('Offene Änderungen zuerst speichern oder abbrechen.');return;}
    await loadSelection(z.zone_id);navigate('documentation',{focus:true});});open.dataset.psZone=z.zone_id;card.append(open);cards.append(card);}
  if(!data.length)cards.append(E('p',zoneDefinitions.length?'Keine passende Zone.':'Noch keine Zone. Mit „+ Neue Zone“ beginnen.'));
  if(focused)[...cards.querySelectorAll('button')].find(b=>b.dataset.psZone===focused)?.focus({preventScroll:true});
 }
 function renderDocument(){
  busyControls();if(plan)return;
  const key=JSON.stringify([structureData,zone(),currentVerification()]);if(key===docKey)return;docKey=key;
  docBody.replaceChildren(E('h2',zone()?.name||'Zonendokumentation'));
  if(!basis()){docBody.append(E('p','Gespeicherter Zonenstand noch nicht bestätigt. Bestand aktualisieren.','ps-warning'));return;}
  const p=structureData.profile,v=currentVerification();
  const status=E('p',v?({synchronized:'Struktur stimmt mit Home Assistant überein',different:'Abweichungen in der Struktur',unconfigured:'Struktur noch nicht eingerichtet',unconfirmed:'HA-Prüfung nicht bestätigt'}[v.state]||'Prüfung offen'):'HA-Abgleich noch offen','ps-structure-status');status.id='ps-structure-status';docBody.append(status);
  if(v?.checked_at)docBody.append(E('p','Prüfstand: '+new Date(v.checked_at).toLocaleString('de-DE')+' · Revision '+structureData.revision+'. Eine spätere HA-Änderung erfordert eine neue Prüfung.','ps-muted'));
  docBody.append(E('p','Bereiche: '+(v?.areas?.map(a=>a.name||a.area_id).join(', ')||zone().area_ids.join(', ')||'Noch keine')),
   E('p','Zonenlabel: '+(v?.label_name||p?.label_name||p?.label_id||'Noch nicht verbunden')),
   E('p','Mitglieder: '+Object.keys(p?.members||{}).length));
  if(!p)docBody.append(E('p','Struktur bearbeiten und vorhandenes Zonenlabel einlesen oder ein neues planen.','ps-muted'));
  const links=E('section','','ps-zone-links');links.append(E('h3','Vorhandene Steuerungen'));
  for(const [kind,name] of Object.entries(linkNames)){
   const saved=p?.ha_links?.[kind],check=v?.ha_links?.[kind];
   links.append(E('p',`${name}: ${saved?.entity_id||'Nicht verknüpft'}${check&&check.status!=='bound'?' · Zuordnung prüfen: '+check.status:''}`,saved&&check&&check.status!=='bound'?'ps-warning':'ps-muted'));
  }
  links.append(E('p','Licht und Sound-Cloud bleiben Home-Assistant-Funktionen. PilotSuite dokumentiert hier ihre Zuordnung; manuelle Bedienung hat Vorrang und nur die bestehende Sound-Cloud verwaltet ihre eigenen Teilnehmer. Diese Prüfung schaltet keine Geräte.','ps-muted'));
  docBody.append(links);
  for(const issue of v?.issues||[])docBody.append(E('p',explanation[issue]||issue,'ps-warning'));
  if(v?.extra_members?.length)docBody.append(E('p','Zusätzlich in HA: '+v.extra_members.join(', '),'ps-warning'));
  if(v?.missing_areas?.length)docBody.append(E('p','Fehlende Bereiche: '+v.missing_areas.join(', '),'ps-warning'));
  const members=E('div','','ps-structure-members');
  for(const [eid,member] of Object.entries(p?.members||{})){
   const identity=structureData.member_identities.find(r=>r.saved_entity_id===eid),check=v?.members?.find(r=>r.entity_id===eid),row=E('article','','ps-structure-member');
   row.append(E('strong',identity?.name||eid),E('code',eid),E('p',member.roles.join(' · ')||'Noch keine Darstellungsrolle','ps-muted'));
   if(check)row.append(E('small',check.membership_source==='device'?'Zonenlabel vom Gerät':check.membership_source==='entity'?'Zonenlabel an der Entität':'Labelmitgliedschaft nicht bestätigt'));
   if(check?.device_roles?.length)row.append(E('small','Rollen vom Gerät geerbt: '+check.device_roles.join(', ')));
   const gaps=check?.issues||((identity&&identity.status!=='bound')?[identity.status]:[]);
   for(const issue of gaps)row.append(E('p',explanation[issue]||issue,'ps-warning'));members.append(row);
  }docBody.append(members);
  const receipts=E('details');receipts.append(E('summary','Gespeicherte Änderungsbelege'));
  for(const item of structureData.plans||[])receipts.append(B(`${new Date(item.created_at*1000).toLocaleString('de-DE')} · ${item.state}`,()=>openPlan(item.id)));
  if(!structureData.plans?.length)receipts.append(E('p','Noch kein HA-Änderungsplan gespeichert.'));docBody.append(receipts);
  const guide=E('details');guide.append(E('summary','Bereiche, Tags und Rollen verstehen'),E('p','HA-Bereiche beschreiben den physischen Ort. Ein Zonenlabel verbindet Entitäten und Geräte zu einer logischen Zone. Habitus-Rollen bestimmen ihre Darstellung. Mehrere Zonen können Mitglieder teilen; Rollenlabels gelten global.'),E('p','Dieser Prüfstand bestätigt die Struktur. Präsenzverhalten und Geräte-Steuerung werden später separat abgenommen.'));docBody.append(guide);
 }
 function render(){renderCards();renderDocument();connection.textContent=dashboardStatus?.home_assistant?.connected?'Mit Home Assistant verbunden · letzter Bestand '+formatTime(dashboardStatus.home_assistant.last_refresh_at):'HA-Verbindung derzeit nicht bestätigt';}
 async function run(fn){if(busy)return;busy=true;busyControls();try{await fn();}catch(e){say(e.message);}finally{busy=false;busyControls();}}
 async function verifyNow(){if(dirty()||!basis())return;await run(async()=>{
  verification=null;docKey='';renderDocument();const zid=selectionZone;
  try{const result=await json(`api/v1/zones/${encodeURIComponent(zid)}/structure?verify=1`);
   if(zid!==selectionZone)return;structureData=result;verification={...result.verification,revision:result.revision};verificationZone=zid;say('HA-Struktur frisch gelesen.');
  }catch(e){verification={state:'unconfirmed',revision:structureData?.revision};verificationZone=zid;throw e;}
  finally{docKey='';renderDocument();}
 });}
 async function preview(){if(dirty()||!basis())return;await run(async()=>{
  const zid=selectionZone;plan=await json(`api/v1/zones/${encodeURIComponent(zid)}/structure/preview`,{method:'POST',body:JSON.stringify({revision:structureData.revision})});planZone=zid;renderPlan();
 });}
 async function openPlan(id){if(dirty())return;await run(async()=>{plan=await json(`api/v1/zones/${encodeURIComponent(selectionZone)}/organization/plans/${encodeURIComponent(id)}`);planZone=selectionZone;renderPlan();});}
 function planPath(p){return p.kind==='structure_labels'||p.kind==='ontology'?'ontology':'organization/plans';}
 function renderPlan(){
  plans.replaceChildren(E('h3','Konkreter HA-Änderungsplan'));if(!plan)return;
  if(plan.state==='unchanged')plans.append(E('p',plan.message+' Für die vollständige Mitgliedschaft anschließend „Mit Home Assistant prüfen“ verwenden.'));
  else {
   plans.append(E('p','Namen, technische Kennungen und physische Bereiche bleiben erhalten. Geändert werden ausschließlich die aufgeführten Labels.'));
   const labels=plan.details?.label_names||{};
   for(const op of plan.operations||[]){if(op.effect==='create_zone_label'){plans.append(E('p','Zonenlabel anlegen: '+op.name));continue;}
    const old=op.before?.labels||[],next=op.after?.labels||[];plans.append(E('strong',op.entity_id),E('p','Hinzufügen: '+(next.filter(x=>!old.includes(x)).map(x=>labels[x]||x).join(', ')||'keine')+' · Entfernen: '+(old.filter(x=>!next.includes(x)).map(x=>labels[x]||x).join(', ')||'keine')));}
   for(const limit of plan.details?.limits||[])plans.append(E('p',limit,'ps-muted'));
   plans.append(E('p','Planstatus: '+plan.state));
   if(['draft','preview'].includes(plan.state))plans.append(B('Genau diese Labels abgleichen',()=>run(async()=>{
    let result;try{result=await json(`api/v1/zones/${encodeURIComponent(planZone)}/${planPath(plan)}/${encodeURIComponent(plan.id)}/apply`,{method:'POST',body:JSON.stringify({sha256:plan.sha256,confirm:true})});}
    catch(error){plan={...plan,state:'Antwort offen – gespeicherten Planstatus lesen'};verification=null;renderPlan();throw error;}
    plan=result;verification=null;renderPlan();say(result.state==='verified'?'Labeländerung bestätigt. Plan schließen und Struktur frisch prüfen.':'Ergebnis nicht vollständig bestätigt. Gespeicherten Beleg prüfen; nicht blind wiederholen.');
   })));
   if(plan.state==='verified')plans.append(B('Rücknahme vorbereiten',()=>run(async()=>{
    const current=await json(`api/v1/zones/${encodeURIComponent(planZone)}/structure`);
    plan=await json(`api/v1/zones/${encodeURIComponent(planZone)}/${planPath(plan)}/${encodeURIComponent(plan.id)}/restore-preview`,{method:'POST',body:JSON.stringify({revision:current.revision})});renderPlan();
   })));
   plans.append(B('Gespeicherten Planstatus lesen',()=>run(async()=>{plan=await json(`api/v1/zones/${encodeURIComponent(planZone)}/organization/plans/${encodeURIComponent(plan.id)}`);renderPlan();})));
  }
  plans.append(B('Plan schließen',()=>run(async()=>{plan=null;plans.replaceChildren();await reloadZones(selectionZone);docKey='';render();})));
 }
 function exportDocumentation(){if(!basis()||dirty())return;
  const doc={format:'pilotsuite-zone-documentation',zone:zone(),structure:structureData.profile,identities:structureData.member_identities,verification:currentVerification(),plans:structureData.plans||[],exported_at:new Date().toISOString()};
  const url=URL.createObjectURL(new Blob([JSON.stringify(doc,null,2)],{type:'application/json'})),a=E('a');a.href=url;a.download='pilotsuite-zone-'+selectionZone+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 function navigate(next,{focus=false,hash=true}={}){
  next=M.primaryView(next);if(next!==view&&dirty()){say('Offene Änderungen zuerst speichern oder abbrechen.');return false;}
  if(next!==view)say('');view=next;prefs.view=view;savePrefs();title.textContent=names[view];cockpit.hidden=view!=='cockpit';setup.hidden=view!=='config';docs.hidden=view!=='documentation';
  $('zone-tabs').hidden=view==='cockpit';$('zone-heading').hidden=view==='cockpit';
  for(const a of nav.children){if(a.hash==='#ps-'+view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}
  if(hash)history.replaceState(null,'','#ps-'+view);if(focus)title.focus();render();return true;
 }
 function route(hash){const next=hash.slice(4);return hash.startsWith('#ps-')&&M.views.includes(next)?next:'cockpit';}
 document.addEventListener('click',event=>{
  const a=event.target.closest('a');if(a?.getAttribute('href')?.startsWith('#')){event.preventDefault();event.stopImmediatePropagation();const next=route(a.hash);if(navigate(next,{focus:true,hash:false}))history.pushState(null,'','#ps-'+next);return;}
  if(dirty()&&event.target.closest('#zone-new,#zone-edit,#zone-tabs button,#refresh,a[href="maintenance"]')){event.preventDefault();event.stopImmediatePropagation();say('Offene Änderungen zuerst speichern oder abbrechen.');}
 },true);
 window.addEventListener('hashchange',()=>{const next=route(location.hash);if(!navigate(next,{hash:false}))history.replaceState(null,'','#ps-'+view);else if(location.hash!=='#ps-'+next)history.replaceState(null,'','#ps-'+next);});
 for(const id of ['zone-new','zone-edit'])$(id).addEventListener('click',event=>{if(!navigate('config')){event.preventDefault();event.stopImmediatePropagation();}},true);
 window.addEventListener('beforeunload',event=>{if(dirty()){event.preventDefault();event.returnValue='';}});
 search.addEventListener('input',()=>{cardKey='';renderCards();});matchMedia('(prefers-color-scheme: dark)').addEventListener('change',appearance);
 const oldSelection=renderSelection;renderSelection=function(){oldSelection();busyControls();};
 const oldZone=renderZoneView;renderZoneView=function(){oldZone();render();};
 const oldStatus=renderStatus;renderStatus=function(status){oldStatus(status);render();};
 const oldLoad=load;load=function(...args){return busy||plan||zoneFormOpen?Promise.resolve():oldLoad(...args);};
 const errors=new MutationObserver(()=>{if(!$('error').hidden){verification=null;docKey='';say($('error').textContent);render();}});errors.observe($('error'),{attributes:true,attributeFilter:['hidden']});
 window.PilotSuiteWorkspaceBusy=()=>busy||!!plan;
 appearance();document.body.classList.add('ps-workspace-ready');navigate(route(location.hash||'#ps-'+prefs.view));
})();
