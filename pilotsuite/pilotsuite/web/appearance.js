/* Shared presentation preferences only. No household data or network access. */
(() => {
  'use strict';
  const model=window.PilotSuiteWorkspaceModel;
  if(!model) return;
  const storageKey='pilotsuite.workspace.v1';
  let prefs=model.preferences(null);
  try { prefs=model.preferences(JSON.parse(localStorage.getItem(storageKey)||'null')); } catch {}
  const query=window.matchMedia('(prefers-color-scheme: dark)');
  function apply(){
    document.documentElement.dataset.psTheme=prefs.theme==='auto'?(query.matches?'dark':'light'):prefs.theme;
    document.documentElement.dataset.psDensity=prefs.density;
    document.documentElement.dataset.psIds=String(prefs.ids);
    for(const key of ['theme','density']){
      const control=document.getElementById('maintenance-'+key);
      if(control) control.value=prefs[key];
    }
  }
  for(const key of ['theme','density']){
    const control=document.getElementById('maintenance-'+key);
    control?.addEventListener('change',()=>{
      // Merge the latest allowed values so another open workspace's view is retained.
      try { prefs=model.preferences(JSON.parse(localStorage.getItem(storageKey)||'null')); } catch {}
      prefs=model.preferences({...prefs,[key]:control.value});apply();
      try {localStorage.setItem(storageKey,JSON.stringify(prefs));} catch {
        const message=document.getElementById('maintenance-message');
        if(message)message.textContent='Darstellung geändert; Browser-Speicherung nicht verfügbar. Gilt nur für diese Sitzung.';
      }
    });
  }
  window.addEventListener('storage',event=>{
    if(event.key===storageKey){try{prefs=model.preferences(JSON.parse(event.newValue||'null'));apply();}catch{}}
  });
  query.addEventListener('change',apply);apply();
})();
