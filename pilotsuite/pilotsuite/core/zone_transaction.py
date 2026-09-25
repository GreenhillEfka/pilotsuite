"""Generate an explicit, non-executable transaction plan for zone foundation changes."""
from __future__ import annotations
from .selections import InvalidSelection, SelectionConflict

def build_transaction_plan(inventory, foundation, reconciliation, payload):
    if not isinstance(payload,dict) or set(payload)!={"revision","approve"} or payload["approve"] is not True:
        raise InvalidSelection("explicit approve=true and revision required")
    rev=inventory.get("revision")
    if type(payload["revision"]) is not int or payload["revision"]!=rev or foundation.get("revision")!=rev:
        raise SelectionConflict("Zone changed; reload before planning changes")
    conflicts=[x for x in reconciliation.get("items",[]) if x.get("state")=="conflict"]
    if conflicts:
        return {"schema":"pilotsuite-zone-transaction-v1","zone_id":inventory.get("zone_id"),"revision":rev,
                "state":"blocked","blockers":[{"type":"helper_conflict","entity_id":x.get("entity_id")} for x in conflicts],
                "steps":[],"execution":{"allowed":False,"actions":[]}}
    creates=[x for x in reconciliation.get("items",[]) if x.get("state")=="create"]
    reuses=[x for x in reconciliation.get("items",[]) if x.get("state")=="reuse"]
    steps=[{"phase":"backup","required":True,"scope":"affected_entities"},
           {"phase":"verify_revision","revision":rev},
           *[{"phase":"reuse_helper","entity_id":x["entity_id"],"write":False} for x in reuses],
           *[{"phase":"create_helper","domain":x["domain"],"key":x["key"],"write":True} for x in creates],
           {"phase":"verify","requirements":["entity_exists","expected_domain","zone_revision_unchanged"]},
           {"phase":"rollback","scope":"created_in_this_transaction_only"}]
    return {"schema":"pilotsuite-zone-transaction-v1","zone_id":inventory.get("zone_id"),"revision":rev,
            "state":"ready_for_external_executor" if creates else "no_write_needed","blockers":[],"steps":steps,
            "execution":{"allowed":False,"actions":[]}}
