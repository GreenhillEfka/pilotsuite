"""Revision-bound helper provisioning contracts; no HA write transport lives here."""
from __future__ import annotations
from dataclasses import dataclass
from .selections import InvalidSelection, SelectionConflict

ALLOWED_HELPERS = {"input_boolean", "timer", "input_select"}

@dataclass(frozen=True)
class ProvisionRequest:
    zone_id: str
    revision: int
    helpers: tuple[tuple[str, str], ...]

def provision_request(inventory, foundation, payload):
    """Validate an explicit request against the exact derived helper plan."""
    if not isinstance(payload, dict) or set(payload) != {"revision", "helpers"}:
        raise InvalidSelection("revision and helpers required; unknown fields rejected")
    if type(payload["revision"]) is not int or payload["revision"] < 0:
        raise InvalidSelection("revision must be a nonnegative integer")
    if payload["revision"] != inventory.get("revision") or foundation.get("revision") != inventory.get("revision"):
        raise SelectionConflict("Zone changed; reload helper plan before provisioning")
    helpers = payload["helpers"]
    if not isinstance(helpers, list) or len(helpers) > 8:
        raise InvalidSelection("helpers must be a list of at most 8 planned helpers")
    planned = {(h.get("domain"), h.get("key")) for h in foundation.get("helper_plan", [])
               if isinstance(h, dict) and h.get("domain") in ALLOWED_HELPERS}
    requested = []
    for item in helpers:
        if not isinstance(item, dict) or set(item) != {"domain", "key"}:
            raise InvalidSelection("each helper requires domain and key")
        pair = (item["domain"], item["key"])
        if pair not in planned:
            raise InvalidSelection("helper is not part of the current zone foundation plan")
        requested.append(pair)
    if len(set(requested)) != len(requested):
        raise InvalidSelection("duplicate helper request")
    return ProvisionRequest(str(inventory["zone_id"]), payload["revision"], tuple(sorted(requested)))

def provisioning_preview(inventory, foundation):
    """Expose ownership and rollback rules before a write capability exists."""
    return {
      "schema": "pilotsuite-helper-provisioning-v1",
      "zone_id": inventory.get("zone_id"), "revision": inventory.get("revision"),
      "helpers": foundation.get("helper_plan", []),
      "ownership": {
        "namespace": "pilotsuite_<zone>_<purpose>",
        "existing_matching_helpers": "reuse_before_create",
        "foreign_helpers": "never_take_ownership_implicitly",
        "delete_policy": "never_delete_foreign_or_preexisting_helper",
      },
      "transaction": {
        "state": "preview_only", "backup_required": True,
        "optimistic_revision_required": True, "post_write_verification_required": True,
        "rollback": "remove_only_helpers_created_by_the_same_verified_transaction",
      },
      "execution": {"allowed": False, "actions": []},
    }
