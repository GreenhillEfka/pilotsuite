// Render canonical server checks and same-basis transient review sections.
// No HA read, save, learning decision or execution is triggered by projection.
(function (global) {
  'use strict';
  const SCHEMA = 'pilotsuite-review-compass-v1';
  const IDS = ['sources','evidence','intent','automations','notes'];
  const ACTIONS = new Set(['review_sources','edit_draft','review_evidence','compare_automations',
    'open_matches','inspect_automation','write_note','review_limits']);
  const STATES = new Set(['missing','stale','partial','observed','unknown','described','limited','last_read']);
  const LABELS = {missing:'Fehlt',stale:'Grundlage verändert',partial:'Eingeschränkt',observed:'Beobachtet',
    unknown:'Nicht geprüft',described:'Beschrieben',limited:'Begrenzter Vergleich',last_read:'Zum letzten Lesen'};
  const GROUPS = {review_sources:'sources',edit_draft:'intent',review_evidence:'evidence',
    compare_automations:'automation',open_matches:'automation',inspect_automation:'automation',
    write_note:'notes',review_limits:'limits'};
  const validRevision = n => Number.isSafeInteger(n) && n >= 0;
  const list = value => Array.isArray(value) && value.length <= 20 && value.every(x=>typeof x==='string' && x.length>0 && x.length<=255) && new Set(value).size===value.length
    ? [...value].sort() : null;
  const equalIds = (a,b) => {a=list(a);b=list(b);return a!==null && b!==null && JSON.stringify(a)===JSON.stringify(b);};
  const validStep = s => s && ACTIONS.has(s.id) && Number.isSafeInteger(s.priority) && s.priority >= 0
    && s.priority <= 100 && typeof s.label === 'string' && s.label.length <= 160
    && (!('automation_id' in s) || (typeof s.automation_id==='string' && /^automation\.[a-z0-9_]{1,244}$/.test(s.automation_id)))
    && (!['inspect_automation','write_note'].includes(s.id) || !!s.automation_id);
  function validCompass(c) {
    return c?.schema===SCHEMA && c.execution?.allowed===false && Array.isArray(c.execution?.actions)
      && c.execution.actions.length===0 && Array.isArray(c.checks) && c.checks.length===5
      && c.checks.every((check,i)=>check?.id===IDS[i] && STATES.has(check.state)
        && typeof check.title==='string' && typeof check.summary==='string' && Array.isArray(check.facts)
        && (check.next_step==null || validStep(check.next_step)));
  }
  function matchesDraft(b, d, zone, revision) {
    return b && d && b.zone_id===zone && d.zone_id===zone && b.draft_id===d.id
      && validRevision(revision) && validRevision(d.revision) && d.revision>0
      && validRevision(d.review_notes?.revision ?? 0) && b.zone_revision===revision
      && b.draft_revision===d.revision && b.review_revision===(d.review_notes?.revision ?? 0)
      && b.source_revision===d.source_revision
      && equalIds(b.source_ids,d.current_pattern?.sources || []) && equalIds(b.target_ids,d.fields?.target_ids || [])
      && typeof b.scope_fingerprint==='string' && /^[0-9a-f]{64}$/.test(b.scope_fingerprint);
  }
  function nextStep(checks) {
    // Generic presentation order declared by the backend; no confidence/safety calculation.
    return checks.map(c=>c.next_step).filter(validStep)
      .sort((a,b)=>a.priority-b.priority || a.id.localeCompare(b.id))[0]
      || {id:'review_limits',priority:60,label:'Offene fachliche Grenzen ansehen'};
  }
  function project(draft, zone, revision, comparison=null, now=Date.now()) {
    const base=draft?.review_compass;
    if (!validCompass(base) || !matchesDraft(base.basis,draft,zone,revision)) return null;
    const result=structuredClone(base);
    const overlay=comparison?.review_compass;
    const checked=typeof comparison?.checked_at==='string' && /(?:Z|[+-]\d{2}:\d{2})$/.test(comparison.checked_at) ? Date.parse(comparison.checked_at) : NaN;
    const age=(now-checked)/1000;
    if (validCompass(overlay) && matchesDraft(overlay.basis,draft,zone,revision)
        && overlay.basis.scope_fingerprint===base.basis.scope_fingerprint
        && comparison.draft_id===draft.id && comparison.zone_id===zone
        && comparison.draft_revision===draft.revision && comparison.zone_revision===revision
        && equalIds(comparison.basis?.source_ids,base.basis.source_ids)
        && equalIds(comparison.basis?.target_ids,base.basis.target_ids)
        && overlay.comparison_checked_at===comparison.checked_at
        && (overlay.inspection_basis?.automation_id ?? null)===(comparison.inspection?.entity_id ?? null)
        && (overlay.inspection_basis?.config_fingerprint ?? null)===(comparison.inspection?.config_fingerprint ?? null)
        && Number.isFinite(age) && age>=0 && age<=300) {
      // Fresh source/evidence/intent sections always come from the current GET.
      result.checks.splice(3,2,...structuredClone(overlay.checks.slice(3)));
      result.comparison_checked_at=comparison.checked_at;
    } else {
      result.comparison_checked_at=null;
    }
    result.next_step=nextStep(result.checks);
    result.execution={allowed:false,reason:'navigation_only',actions:[]};
    return result;
  }
  function selectRows(rows, filter='all', sort='next') {
    const result=rows.filter(row=>filter==='all' || (GROUPS[row.compass?.next_step?.id] || 'unknown')===filter);
    if (sort==='next') result.sort((a,b)=>(a.compass?.next_step?.priority ?? 100)-(b.compass?.next_step?.priority ?? 100)
      || String(a.draft.id).localeCompare(String(b.draft.id)));
    else if (sort==='title') result.sort((a,b)=>String(a.draft.fields?.title || '').localeCompare(String(b.draft.fields?.title || ''),'de')
      || String(a.draft.id).localeCompare(String(b.draft.id)));
    // 'saved' preserves the canonical PlanStore update order.
    return result;
  }
  const api={project,nextStep,selectRows,matchesDraft,validStep};
  if (typeof module!=='undefined' && module.exports) module.exports=api;
  global.PilotSuiteReviewCompass=api;
  if (typeof document==='undefined') return;

  let view={zone:null,filter:'all',sort:'next'};
  const expanded=new Set();
  const locked=()=>selectionBusy || contextEditing || zoneFormOpen || !!selectionDraft?.dirty;
  const forDraft=d=>project(d,selectionZone,contextData?.revision,typeof comparisonFor==='function' ? comparisonFor(d) : null);
  function focusSection(id) {
    const el=byId(id); if (!el) return;
    if (el.tagName==='DETAILS') el.open=true;
    if (!el.hasAttribute('tabindex')) el.tabIndex=-1;
    el.scrollIntoView({block:'start'});el.focus({preventScroll:true});
  }
  function navigate(draft, shown, card) {
    if (locked()) return;
    const current=contextData?.drafts?.find(d=>d.id===draft.id && d.zone_id===selectionZone);
    const latest=current && forDraft(current);
    const step=latest?.next_step;
    if (!step || !validStep(step) || JSON.stringify(step)!==JSON.stringify(shown.next_step)
        || JSON.stringify(latest.basis)!==JSON.stringify(shown.basis)) {
      text('routine-message','Prüfgrundlage inzwischen verändert oder Lesestand abgelaufen. Aktuellen nächsten Schritt erneut auswählen.');
      document.activeElement?.blur(); renderRoutineDrafts(); return;
    }
    switch(step.id) {
      case 'review_sources': focusSection('learning-section'); break;
      case 'edit_draft': openRoutineEditor(current); break;
      case 'review_evidence': focusSection('pattern-workbench'); break;
      case 'compare_automations': compareRoutine(current); break;
      case 'inspect_automation': compareRoutine(current,step.automation_id); break;
      case 'write_note':
        if (typeof openReviewNote==='function' && comparisonFor(current)?.inspection?.entity_id===step.automation_id) openReviewNote(current);
        break;
      case 'open_matches': {
        const match=card.querySelector('.routine-comparison button');
        if (match) { match.scrollIntoView({block:'center'});match.focus(); }
        break;
      }
      case 'review_limits': {
        const details=card.querySelector('.review-compass-details');details.open=true;
        const target=card.querySelector('.automation-inspection') || details;
        target.tabIndex=-1;target.scrollIntoView({block:'start'});target.focus({preventScroll:true});
        break;
      }
    }
  }
  function render(card,draft) {
    const compass=forDraft(draft);
    const section=document.createElement('section');section.className='review-compass';
    const title=document.createElement('h5');title.textContent='Prüfkompass';section.append(title);
    if (!compass) {
      const p=document.createElement('p');p.textContent='Prüfkompass für diesen Stand nicht verfügbar. Vorhandene Entwurfsfunktionen bleiben erhalten; neu laden liest nur Daten.';
      section.append(p);card.append(section);return;
    }
    const summary=document.createElement('p');summary.className='review-compass-next';
    summary.textContent=`Nächster Schritt: ${compass.next_step.label}.`;
    const basis=document.createElement('p');basis.className='review-compass-basis';
    basis.textContent=`Entwurf ${compass.basis.draft_revision} · Zone ${compass.basis.zone_revision} · Bewertungen ${compass.basis.review_revision}. Nur Entscheidungshilfe, keine Ausführungsfreigabe.`;
    const button=document.createElement('button');button.type='button';button.className='review-compass-action';
    button.textContent=compass.next_step.label+(compass.next_step.automation_id ? ' · '+compass.next_step.automation_id : '');
    button.disabled=locked() || (compass.next_step.id==='write_note' && typeof openReviewNote!=='function');
    button.addEventListener('click',()=>navigate(draft,compass,card));
    const details=document.createElement('details');details.className='review-compass-details';details.open=expanded.has(draft.id);
    const label=document.createElement('summary');label.textContent='Fünf Prüfbereiche und ihre Belege';details.append(label);
    details.addEventListener('toggle',()=>{if(details.open) expanded.add(draft.id);else expanded.delete(draft.id);});
    const list=document.createElement('ol');list.className='review-compass-checks';
    for (const check of compass.checks) {
      const li=document.createElement('li');li.dataset.check=check.id;
      const heading=document.createElement('strong');heading.textContent=check.title+' · '+LABELS[check.state];
      const why=document.createElement('p');why.textContent=check.summary;li.append(heading,why);
      for (const fact of check.facts) {
        if (typeof fact?.label!=='string' || typeof fact?.value!=='string') continue;
        const p=document.createElement('p');p.className='review-compass-fact';p.textContent=fact.label+': '+fact.value;li.append(p);
      }
      list.append(li);
    }
    const limits=document.createElement('p');limits.className='review-compass-limits';
    limits.textContent='Nicht prüfbar bedeutet nicht unbedenklich. Eigene Bewertungen, Musterzahlen, Risiko und Ausführungsrecht bleiben getrennt. Keine automatische Prüfung oder Speicherung. Ein ausdrücklicher Lesestand wird höchstens fünf Minuten zur Navigation verwendet; danach erneut lesen.';
    details.append(list,limits);section.append(summary,basis,button,details);card.append(section);
  }
  function workspace(root,drafts) {
    if (view.zone!==selectionZone) {view={zone:selectionZone,filter:'all',sort:'next'};expanded.clear();}
    let toolbar=byId('review-compass-workspace');
    if (!toolbar) {
      toolbar=document.createElement('div');toolbar.id='review-compass-workspace';toolbar.className='review-compass-workspace';
      for (const [id,title,options] of [
        ['review-compass-filter','Nächster Arbeitsschritt',[['all','Alle Entwürfe'],['sources','Quellen klären'],['intent','Angaben ergänzen'],['evidence','Belege ansehen'],['automation','Automationen prüfen'],['notes','Bewertung festhalten'],['limits','Fachliche Grenzen'],['unknown','Prüfstand nicht verfügbar']]],
        ['review-compass-sort','Sortierung',[['next','Nach nächstem Arbeitsschritt'],['saved','Zuletzt bearbeitet'],['title','Nach Titel']]]]) {
        const label=document.createElement('label');label.htmlFor=id;label.textContent=title;
        const select=document.createElement('select');select.id=id;
        for(const [value,textValue] of options) {const o=document.createElement('option');o.value=value;o.textContent=textValue;select.append(o);}
        select.addEventListener('change',()=>{if(locked())return;view[id.endsWith('filter')?'filter':'sort']=select.value;contextGeneration++;renderRoutineDrafts();});
        toolbar.append(label,select);
      }
      const count=document.createElement('p');count.id='review-compass-count';count.setAttribute('role','status');count.setAttribute('aria-live','polite');toolbar.append(count);
      root.before(toolbar);
      root.addEventListener('focusout',()=>queueMicrotask(()=>{if(!document.activeElement?.closest('#routine-list'))renderRoutineDrafts();}));
    }
    toolbar.hidden=!drafts.length;
    byId('review-compass-filter').value=view.filter;byId('review-compass-sort').value=view.sort;
    byId('review-compass-filter').disabled=byId('review-compass-sort').disabled=locked();
    const rows=drafts.map(d=>({draft:d,compass:forDraft(d)}));
    const selected=selectRows(rows,view.filter,view.sort);
    text('review-compass-count',`${selected.length} von ${drafts.length} Entwürfen in dieser Zone. Reihenfolge ist eine Arbeitshilfe, keine Risikobewertung.`);
    return selected.map(r=>r.draft);
  }
  Object.assign(api,{render,workspace,forDraft});
  const css=document.createElement('link');css.rel='stylesheet';css.href=endpoint('assets/review_compass.css');document.head.append(css);
  renderLearning();
})(typeof globalThis==='object' ? globalThis : this);
