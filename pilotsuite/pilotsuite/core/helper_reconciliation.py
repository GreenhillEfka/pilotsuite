"""Inventory-aware reconciliation of planned zone helpers; pure/read-only."""
from __future__ import annotations

def reconcile_helpers(foundation, catalog):
    """Classify planned helpers as reuse/create/conflict without guessing aliases."""
    by_id={i.get("entity_id"):i for i in catalog if isinstance(i,dict) and isinstance(i.get("entity_id"),str)}
    by_name={}
    for item in catalog:
        if not isinstance(item,dict): continue
        name=(item.get("name") or "").strip().casefold()
        if name: by_name.setdefault(name,[]).append(item)
    rows=[]
    for helper in foundation.get("helper_plan",[]):
        domain,key=helper.get("domain"),helper.get("key")
        entity_id=f"{domain}.{key}" if domain and key else None
        exact=by_id.get(entity_id)
        if exact:
            state="reuse"; reason="exact_entity_id"
        else:
            # Names are hints only. Never silently reuse a similar/duplicate helper.
            label=(helper.get("name") or "").strip().casefold()
            hints=by_name.get(label,[]) if label else []
            state="conflict" if hints else "create"
            reason="ambiguous_name_match" if hints else "no_exact_existing_helper"
        rows.append({**helper,"entity_id":entity_id,"state":state,"reason":reason})
    return {"schema":"pilotsuite-helper-reconciliation-v1","items":rows,
            "counts":{k:sum(1 for r in rows if r["state"]==k) for k in ("reuse","create","conflict")},
            "execution":{"allowed":False,"actions":[]}}
