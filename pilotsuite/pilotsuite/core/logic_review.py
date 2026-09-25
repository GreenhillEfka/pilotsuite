"""Conservative classification of existing HA logic against a zone foundation."""
from __future__ import annotations

def classify_logic(entity_id, references, *, owner=None, raw_sources=(), targets=(), missing=()):
    refs=set(references or ()); raw=set(raw_sources or ()); tg=set(targets or ()); miss=set(missing or ())
    evidence=[]
    if owner and owner in refs: evidence.append("logical_owner")
    if raw & refs: evidence.append("raw_presence")
    if tg & refs: evidence.append("zone_target")
    if miss & refs:
        return {"entity_id":entity_id,"state":"repair","reason":"references_missing_entities",
                "evidence":evidence,"missing":sorted(miss & refs),"execution":{"allowed":False}}
    if owner and owner in refs and raw & refs:
        return {"entity_id":entity_id,"state":"reuse","reason":"owner_and_raw_source_relationship",
                "evidence":evidence,"missing":[],"execution":{"allowed":False}}
    if refs & (raw|tg|({owner} if owner else set())):
        return {"entity_id":entity_id,"state":"inspect","reason":"related_semantics_not_proven",
                "evidence":evidence,"missing":[],"execution":{"allowed":False}}
    return {"entity_id":entity_id,"state":"unrelated","reason":"no_foundation_reference",
            "evidence":[],"missing":[],"execution":{"allowed":False}}

def summarize_logic(rows):
    states=("reuse","repair","inspect","unrelated")
    return {"schema":"pilotsuite-existing-logic-review-v1","items":rows,
            "counts":{s:sum(1 for r in rows if r.get("state")==s) for s in states},
            "execution":{"allowed":False,"actions":[]}}
