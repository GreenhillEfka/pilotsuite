"""Non-authoritative helper inventory hints. No creation/ownership authorization."""
from __future__ import annotations
from copy import deepcopy


def reconcile_helpers(foundation, catalog):
    """Registry hints cannot prove absence in HA helper collections or semantics."""
    by_id = {i["entity_id"]: i for i in catalog
             if isinstance(i, dict) and isinstance(i.get("entity_id"), str)}
    by_name = {}
    for item in by_id.values():
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            by_name.setdefault(name.strip().casefold(), []).append(item)
    rows = []
    for helper in foundation.get("helper_plan", []):
        entity_id = helper.get("existing_entity_id") or f"{helper['domain']}.{helper['key']}"
        exact = by_id.get(entity_id)
        label = helper.get("name", "").strip().casefold()
        if helper.get("identity_resolved") is False:
            state, reason = "unverified", "saved_identity_unresolved_do_not_replace_or_create"
        elif exact is not None:
            state, reason = "inspect", "exact_id_found_configuration_and_ownership_unverified"
        elif label and by_name.get(label):
            state, reason = "conflict", "name_match_requires_explicit_resolution"
        else:
            state, reason = "unverified", "registry_absence_does_not_prove_helper_absence"
        rows.append({**deepcopy(helper), "entity_id": entity_id, "state": state,
                     "reason": reason, "ownership_verified": False})
    return {"schema": "pilotsuite-helper-reconciliation-v1",
            "zone_id": foundation.get("zone_id"), "revision": foundation.get("revision"),
            "basis": "entity_registry_only", "items": rows,
            "counts": {k: sum(r["state"] == k for r in rows)
                       for k in ("reuse", "create", "conflict", "inspect", "unverified")},
            "execution": {"allowed": False, "actions": []}}
