"""Semantic, non-executable diff between imported HA automation and desired PilotSuite schema."""
from __future__ import annotations
from copy import deepcopy
from .automation_import import ALLOWED_ROOT
from .automation_transform import transformed_config

def semantic_diff(snapshot, desired):
    """Describe changes without generating an HA mutation."""
    src=snapshot.get("source",{}).get("config",{})
    if not isinstance(desired,dict): raise ValueError("desired config must be an object")
    transformed_config(snapshot, desired)  # Same validation as the proposed transform.
    fields=("triggers","conditions","actions","mode")
    aliases={"triggers":"trigger","conditions":"condition","actions":"action"}
    changes=[]
    for field in fields:
        old=src.get(field,src.get(aliases.get(field,""), [] if field!="mode" else "single"))
        new=desired.get(field,old)
        if old!=new:
            changes.append({"field":field,"before":deepcopy(old),"after":deepcopy(new)})
    untouched=sorted(set(src)-ALLOWED_ROOT)
    return {"schema":"pilotsuite-automation-semantic-diff-v1",
            "entity_id":snapshot.get("entity_id"),"source_fingerprint":snapshot.get("source",{}).get("fingerprint"),
            "changes":changes,"preserved_unknown_fields":untouched,
            "risk":{"level":"none" if not changes else "review_required",
                    "reasons":[] if not changes else ["automation_behavior_changes"]},
            "execution":{"allowed":False,"actions":[]}}

def takeover_transaction(snapshot,diff,*,approve=False):
    blockers=[]
    if approve is not True: blockers.append("explicit_approval_required")
    if diff.get("source_fingerprint")!=snapshot.get("source",{}).get("fingerprint"):
        blockers.append("fingerprint_mismatch")
    if not diff.get("changes"): blockers.append("no_change")
    return {"schema":"pilotsuite-automation-takeover-v1","entity_id":snapshot.get("entity_id"),
            "state":"blocked" if blockers else "ready_for_external_executor","blockers":blockers,
            "strategy":"backup_then_in_place_transform_preserve_entity_id",
            "verification":["entity_id_unchanged","config_matches_reviewed_diff","automation_enabled_state_preserved"],
            "rollback":"restore_exact_pre_takeover_config",
            "execution":{"allowed":False,"actions":[]}}
