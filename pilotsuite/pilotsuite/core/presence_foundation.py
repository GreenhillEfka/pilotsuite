"""Pure presence-foundation model for deterministic HA automation generation."""
from __future__ import annotations

def presence_contract(foundation):
    module=(foundation.get("modules") or {}).get("presence") or {}
    logical=list(module.get("logical_sources") or [])
    raw=list(module.get("raw_sources") or [])
    helpers={h.get("domain"):h for h in foundation.get("helper_plan",[]) if isinstance(h,dict)}
    return {
      "schema":"pilotsuite-presence-foundation-v1",
      "logical_owner": logical[0] if len(logical)==1 else None,
      "raw_sources": raw,
      "timer_key": (helpers.get("timer") or {}).get("key"),
      "state_machine":["occupied","grace","vacant","unknown"],
      "rules":[
        "Any valid positive raw source may assert occupied.",
        "Loss of all positive raw sources starts grace; it does not assert vacant.",
        "Timer expiry must re-check every configured source before vacant.",
        "Unknown/unavailable source at expiry yields unknown, never vacant.",
        "Home Assistant restart/reload must re-evaluate current sources and timer state.",
        "Consumer timers may be longer than presence grace but never redefine occupancy.",
      ],
      "execution":{"allowed":False,"actions":[]},
    }

def takeover_classification(existing_refs, contract):
    """Classify existing HA logic without claiming semantic equivalence."""
    refs=set(existing_refs or [])
    raw=set(contract.get("raw_sources") or [])
    owner=contract.get("logical_owner")
    timer=contract.get("timer_key")
    if not refs:
        return {"state":"supplement","reason":"no_related_logic"}
    if owner and owner in refs and raw & refs:
        return {"state":"reuse","reason":"existing_logic_references_owner_and_raw_sources"}
    if owner and owner in refs:
        return {"state":"inspect","reason":"owner_referenced_but_source_semantics_unverified"}
    if timer and ("timer."+timer) in refs:
        return {"state":"inspect","reason":"timer_reference_exists_without_verified_owner"}
    return {"state":"inspect","reason":"related_logic_requires_configuration_review"}
