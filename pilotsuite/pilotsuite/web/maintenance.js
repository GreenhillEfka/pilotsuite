'use strict';
(() => {
  const byId = id => document.getElementById(id);
  const text = (tag, value) => { const node = document.createElement(tag); node.textContent = value; return node; };
  let readId = 0, helperRead = 0, busy = false, data = null, preview = null, zones = [];
  const updateLabels = {current:'Laut Home Assistant aktuell.', available:'Neue Version verfügbar.',
    installing:'Home Assistant meldet eine laufende Installation.', unknown:'Updateinformation derzeit nicht bestätigt.',
    skipped:'Die angebotene Version ist in Home Assistant übersprungen.', version_mismatch:'Versionsabweichung: App und HA-Metadaten erneut prüfen.'};
  async function api(path, payload) {
    const options = {cache:'no-store'};
    if (payload !== undefined) Object.assign(options, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    const response = await fetch(path, options);
    const value = await response.json();
    if (!response.ok) throw new Error(value.message || 'Anfrage fehlgeschlagen. Nichts erneut auf Verdacht ausführen.');
    return value;
  }
  function clearPreview() {
    preview = null; byId('restore-review').hidden = true;
    byId('restore-confirm').checked = false; byId('restore-apply').disabled = true;
  }
  function lock(value) {
    busy = value;
    byId('savepoint-create').disabled = value || !data || data.rescue_mode || data.savepoint_error;
    byId('maintenance-refresh').disabled = value;
    byId('helper-inspect').disabled = value || !data || data.rescue_mode || !zones.length;
    byId('helper-zone').disabled = value || !zones.length;
    for (const button of byId('savepoints').querySelectorAll('button')) button.disabled = value || !data || data.rescue_mode;
    byId('restore-apply').disabled = value || !preview || !byId('restore-confirm').checked;
  }
  function show(message) { byId('maintenance-message').textContent = message; }
  function render(value) {
    byId('maintenance-version').textContent = value.version;
    byId('rescue-warning').hidden = !value.rescue_mode;
    byId('update-message').textContent = (updateLabels[value.update.state] || updateLabels.unknown)
      + (value.update.latest_version ? ' Angebot: ' + value.update.latest_version : '');
    byId('native-install').textContent = value.update.install_available ? 'Neue Version in Home Assistant installieren' : 'PilotSuite in Home Assistant öffnen';
    const history = byId('release-history'); history.replaceChildren();
    for (const row of value.release_history || []) {
      const details = document.createElement('details');
      details.append(text('summary', row.version + (row.running ? ' · installiert' : '')), text('pre', row.notes));
      history.append(details);
    }
    const points = byId('savepoints'); points.replaceChildren();
    if (value.savepoint_error) points.append(text('p','Speicherpunktverzeichnis nicht lesbar. Keine Rücksetzung möglich.'));
    else if (!value.savepoints.length) points.append(text('p','Noch kein lokaler Konfigurations-Speicherpunkt.'));
    for (const point of value.savepoints || []) {
      const card = document.createElement('article');
      card.append(text('h3', point.label), text('p', point.valid ? `${new Date(point.created_at).toLocaleString('de-DE')} · ${point.version} · ${point.zone_count} Zonen · Prüfsumme gültig` : 'Beschädigt oder inkompatibel; Wiederherstellung gesperrt.'));
      if (point.valid && !value.rescue_mode) {
        const button = text('button','Wiederherstellung prüfen'); button.type='button';
        button.addEventListener('click', () => loadPreview(point.id)); card.append(button);
      }
      points.append(card);
    }
  }
  async function refresh() {
    if (busy) return;
    const id = ++readId; helperRead++; clearPreview(); data = null; zones = []; lock(true);
    byId('helper-results').replaceChildren(); byId('helper-message').textContent='';
    byId('update-message').textContent=updateLabels.unknown;
    try {
      const value = await api('api/v1/maintenance');
      const listing = value.rescue_mode ? {items:[]} : await api('api/v1/zones');
      if (id !== readId) return;
      data = value; zones = listing.items || []; render(value);
      const select = byId('helper-zone'); const selected = select.value; select.replaceChildren();
      for (const zone of zones) { const option=text('option', zone.name); option.value=zone.zone_id; select.append(option); }
      if (zones.some(z=>z.zone_id === selected)) select.value=selected;
      show(value.rescue_mode ? 'Rescue-Modus: keine Datenbankänderung möglich.' : 'Wartungsdaten geladen. HA-Konfiguration bleibt unangetastet.');
    } catch (error) {
      data=null; byId('savepoints').replaceChildren(); byId('release-history').replaceChildren();
      byId('helper-zone').replaceChildren(); show(error.message);
    } finally { if (id===readId) lock(false); }
  }
  async function loadPreview(pointId) {
    if (busy || !data || data.rescue_mode) return;
    clearPreview(); lock(true);
    try {
      preview=await api(`api/v1/maintenance/savepoints/${pointId}/preview`, {});
      const list=byId('restore-consequences'); list.replaceChildren();
      for (const line of preview.consequences) list.append(text('li',line));
      const zoneList=byId('restore-zones'); zoneList.replaceChildren();
      zoneList.append(text('p','Betroffen: '+preview.zones.map(z=>z.name).join(', ')));
      zoneList.append(text('p',`${preview.preserved_zone_count} weitere Zonen bleiben unverändert.`));
      byId('restore-review').hidden=false; byId('restore-review').focus();
    } catch (error) { clearPreview(); show(error.message); }
    finally { lock(false); }
  }
  byId('savepoint-form').addEventListener('submit',async event=>{
    event.preventDefault(); if (busy || !data || data.rescue_mode) return;
    clearPreview(); lock(true);
    try {
      await api('api/v1/maintenance/savepoints',{label:byId('savepoint-label').value});
      lock(false); await refresh(); show('Konfigurations-Speicherpunkt angelegt und geprüft. Kein vollständiges HA-Backup.');
    } catch (error) { show(error.message); lock(false); }
  });
  byId('restore-confirm').addEventListener('change',()=>lock(busy));
  byId('restore-cancel').addEventListener('click',()=>{if(!busy)clearPreview();});
  byId('restore-apply').addEventListener('click',async()=>{
    if (busy || !preview || !byId('restore-confirm').checked) return;
    const selected=preview; lock(true);
    try {
      const result=await api(`api/v1/maintenance/savepoints/${selected.id}/restore`, {
        sha256:selected.sha256,basis:selected.basis,confirm_paused_restore:true});
      clearPreview(); lock(false); await refresh();
      show(result.replayed ? 'Dieser Auftrag war bereits abgeschlossen. Keine erneute Wiederherstellung; der aktuelle Stand wurde neu geladen.' : `${result.restored} Zonen-Konfigurationen wiederhergestellt und pausiert. Vorher-Speicherpunkt: ${result.before_savepoint}. Keine HA-Änderung.`);
    } catch(error) { clearPreview(); show(error.message+' Status neu lesen, bevor du erneut bestätigst.'); lock(false); }
  });
  byId('helper-zone').addEventListener('change',()=>{helperRead++;byId('helper-results').replaceChildren();byId('helper-message').textContent='';});
  byId('helper-inspect').addEventListener('click',async()=>{
    if (busy || !data || data.rescue_mode) return;
    const zone=zones.find(z=>z.zone_id===byId('helper-zone').value); if(!zone)return;
    const id=++helperRead; lock(true); byId('helper-results').replaceChildren();byId('helper-message').textContent='Konfigurationen werden ausdrücklich gelesen …';
    try {
      const result=await api(`api/v1/zones/${encodeURIComponent(zone.zone_id)}/helpers/inspect`,{zone_revision:zone.revision});
      if(id!==helperRead)return;
      if(result.zone_id!==zone.zone_id || result.revision!==zone.revision)throw new Error('Veraltete Helferantwort verworfen.');
      for(const row of result.items){
        const card=document.createElement('article'); card.append(text('h3',row.name),text('p',row.entity_id));
        card.append(text('p',row.state==='configuration_read'?'Vorhandene Konfiguration gelesen · nicht automatisch übernommen.':'Vorhandener Registereintrag · separate Prüfung nötig.'));
        card.append(text('p','PilotSuite-Rollen: '+(row.roles.join(', ')||'noch keine ausdrückliche Zuordnung')));
        const details=document.createElement('details');details.append(text('summary','Konfigurationsdetails'),text('pre',JSON.stringify(row.config,null,2)));card.append(details);
        for(const warning of row.warnings)card.append(text('p',warning));
        byId('helper-results').append(card);
      }
      byId('helper-message').textContent=`${result.items.length} vorhandene Helfer in dieser Zone. Keine Änderung und keine Neuanlage.`;
    } catch(error){if(id===helperRead)byId('helper-message').textContent=error.message+' Zone/Status gegebenenfalls neu laden.';}
    finally{lock(false);}
  });
  byId('maintenance-refresh').addEventListener('click',refresh);
  refresh();
})();
