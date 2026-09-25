"""Read-only controlled adoption analysis for existing presence automations."""
from __future__ import annotations
import hashlib,json,re
from pilotsuite.ha.client import HomeAssistantError

def adoption_targets(runtime):
    refs=set(runtime.get("raw_sources") or [])
    for key in ("owner","timer"):
        if runtime.get(key): refs.add(runtime[key])
    return sorted(refs)

def classify_inspection(inspection, runtime):
    limitations=set(inspection.get("limitations") or [])
    sections=inspection.get("sections") or {}
    source_refs={e for s in sections.get("triggers",[]) for e in s.get("source_references",[])}
    target_refs={e for s in sections.get("actions",[]) for e in s.get("target_references",[])}
    raw=set(runtime.get("raw_sources") or []);owner=runtime.get("owner");timer=runtime.get("timer")
    direct_sources=sorted(raw & source_refs)
    writes_owner=bool(owner and owner in target_refs);writes_timer=bool(timer and timer in target_refs)
    blockers=sorted(limitations | ({"no_direct_presence_source_trigger"} if not direct_sources else set()))
    overlap=bool(direct_sources or writes_owner or writes_timer)
    return {"automation_id":inspection["entity_id"],"fingerprint":inspection["config_fingerprint"],
      "overlap":overlap,"direct_presence_sources":direct_sources,"writes_owner":writes_owner,"writes_timer":writes_timer,
      "limitations":sorted(limitations),"blockers":blockers,
      "classification":"conflict" if overlap and (writes_owner or writes_timer) else "related" if overlap else "unrelated",
      "takeover_ready":overlap and not blockers and not writes_owner and not writes_timer}

def adoption_plan(zone_id,revision,runtime,inspections):
    rows=[classify_inspection(i,runtime) for i in inspections]
    related=[r for r in rows if r["classification"]!="unrelated"]
    payload={"zone_id":zone_id,"revision":revision,"runtime_basis":{"owner":runtime.get("owner"),
      "raw_sources":runtime.get("raw_sources",[]),"timer":runtime.get("timer")},"automations":related}
    fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    conflicts=[r["automation_id"] for r in related if r["classification"]=="conflict"]
    blockers=sorted({b for r in related for b in r["blockers"]})
    return {"schema":"pilotsuite-presence-adoption-v1",**payload,"fingerprint":fingerprint,
      "summary":{"related":len(related),"conflicts":len(conflicts),"unresolved":len(blockers)},
      "conflicting_automations":conflicts,"blockers":blockers,
      "recommendation":"review_conflicts" if conflicts or blockers else "ready_for_separate_takeover_approval",
      "execution":{"allowed":False,"actions":[]},
      "boundaries":["No automation is enabled, disabled, edited or deleted.","Configuration structure is not runtime proof.",
                    "Takeover requires a separate backup-bound approval and fresh fingerprint recheck."]}

def validate_automation_ids(ids):
    if not isinstance(ids,list) or len(ids)>50 or any(not isinstance(x,str) or not re.fullmatch(r"automation\.[a-z0-9_]+",x) for x in ids):
        raise HomeAssistantError("Invalid related automation identities")
    return sorted(set(ids))
