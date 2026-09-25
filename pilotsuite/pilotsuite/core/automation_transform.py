"""Validate an in-place automation takeover candidate while preserving HA identity."""
from __future__ import annotations
import copy

def transformed_config(snapshot, desired):
    if not isinstance(desired,dict) or set(desired)-{"triggers","conditions","actions","mode","id","alias"}:
        raise ValueError("unsupported desired fields")
    src=copy.deepcopy(snapshot["source"]["config"])
    if "use_blueprint" in src and desired:
        raise ValueError("blueprint must be separately resolved before transformation")
    aliases={"triggers":"trigger","conditions":"condition","actions":"action"}
    for field in ("triggers","conditions","actions","mode"):
        if field not in desired: continue
        old_alias=aliases.get(field)
        if old_alias and old_alias in src and field in src:
            raise ValueError("ambiguous singular/plural fields")
        if old_alias and old_alias in src and field not in src:
            src[old_alias]=copy.deepcopy(desired[field])
        else:
            src[field]=copy.deepcopy(desired[field])
    # Never allow PilotSuite to rewrite identity through semantic desired fields.
    for forbidden in ("id","alias"):
        if forbidden in desired and desired[forbidden]!=src.get(forbidden):
            raise ValueError(f"{forbidden} is identity metadata and cannot change during takeover")
    return src

def verify_takeover(before, after, desired, *, actual_entity_id=None):
    expected=transformed_config(before,desired)
    problems=[]
    if after!=expected: problems.append("config_mismatch")
    if actual_entity_id is None: problems.append("entity_identity_not_verified")
    elif before.get("entity_id")!=actual_entity_id:
        problems.append("entity_id_changed")
    return {"verified":not problems,"problems":problems,
            "rollback_required":any(p != "entity_identity_not_verified" for p in problems),"execution":{"allowed":False,"actions":[]}}
