"""Deterministic presence state machine; timer expiry never proves vacancy by itself."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PresenceDecision:
    state: str
    desired_owner: bool | None
    timer_action: str | None
    reason: str

def evaluate_presence(source_states, timer_state):
    values=list(source_states.values()) if isinstance(source_states,dict) else list(source_states or [])
    if not values: return PresenceDecision("unknown",None,None,"no_sources")
    if any(v=="on" for v in values): return PresenceDecision("occupied",True,"cancel","positive_source")
    if any(v!="off" for v in values): return PresenceDecision("unknown",None,None,"source_unknown")
    if timer_state in ("active","paused"): return PresenceDecision("grace",True,None,"all_clear_timer_running")
    if timer_state=="idle": return PresenceDecision("grace",True,"start","all_clear_start_grace")
    if timer_state=="finished": return PresenceDecision("vacant",False,None,"expiry_and_all_sources_clear")
    return PresenceDecision("unknown",None,None,"timer_unknown")

def presence_contract(foundation):
    module=(foundation.get("modules") or {}).get("presence") or {}
    logical=list(module.get("logical_sources") or []); raw=list(module.get("raw_sources") or [])
    helpers={h.get("domain"):h for h in foundation.get("helper_plan",[]) if isinstance(h,dict)}
    return {"schema":"pilotsuite-presence-foundation-v2","logical_owner":logical[0] if len(logical)==1 else None,
      "raw_sources":raw,"timer_key":(helpers.get("timer") or {}).get("key"),
      "state_machine":["occupied","grace","vacant","unknown"],
      "rules":["Any valid positive raw source asserts occupied.",
        "Loss of all positive raw sources starts grace; it does not assert vacant.",
        "Timer expiry re-checks every configured source before vacancy.",
        "Unknown/unavailable source at expiry yields unknown, never vacant.",
        "Restart/reconnect re-evaluates current sources and timer state before any write."],
      "execution":{"allowed":bool(raw),"actions":["timer.start","timer.cancel","input_boolean.turn_on","input_boolean.turn_off"] if raw else []}}

def takeover_classification(existing_refs, contract):
    refs=set(existing_refs or []);raw=set(contract.get("raw_sources") or [])
    owner=contract.get("logical_owner");timer=contract.get("timer_key")
    if not refs:return {"state":"supplement","reason":"no_related_logic"}
    if owner and owner in refs and raw & refs:return {"state":"reuse","reason":"existing_logic_references_owner_and_raw_sources"}
    if owner and owner in refs:return {"state":"inspect","reason":"owner_referenced_but_source_semantics_unverified"}
    if timer and ("timer."+timer) in refs:return {"state":"inspect","reason":"timer_reference_exists_without_verified_owner"}
    return {"state":"inspect","reason":"related_logic_requires_configuration_review"}
