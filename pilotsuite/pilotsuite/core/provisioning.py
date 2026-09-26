"""Bounded helper provisioning for one explicit PilotSuite-owned timer."""
from __future__ import annotations
from dataclasses import dataclass
from .selections import InvalidSelection, SelectionConflict

ALLOWED_HELPERS = {"timer"}
DEFAULT_TIMER = {"duration": "00:05:00", "restore": True}

@dataclass(frozen=True)
class ProvisionRequest:
    zone_id: str
    revision: int
    helpers: tuple[tuple[str, str], ...]

def provision_request(inventory, foundation, payload):
    if not isinstance(payload, dict) or set(payload) != {"revision", "helpers", "confirm"}:
        raise InvalidSelection("revision, helpers and confirm required; unknown fields rejected")
    if payload["confirm"] is not True:
        raise InvalidSelection("explicit confirmation required")
    if type(payload["revision"]) is not int or payload["revision"] < 0:
        raise InvalidSelection("revision must be a nonnegative integer")
    if payload["revision"] != inventory.get("revision") or foundation.get("revision") != inventory.get("revision"):
        raise SelectionConflict("Zone changed; reload helper plan before provisioning")
    helpers = payload["helpers"]
    if not isinstance(helpers, list) or len(helpers) != 1:
        raise InvalidSelection("exactly one planned helper may be provisioned per transaction")
    planned = {(h.get("domain"), h.get("key")) for h in foundation.get("helper_plan", [])
               if isinstance(h, dict) and h.get("domain") in ALLOWED_HELPERS and h.get("create_allowed", True)}
    item = helpers[0]
    if not isinstance(item, dict) or set(item) != {"domain", "key"}:
        raise InvalidSelection("helper requires domain and key")
    pair = (item["domain"], item["key"])
    if pair not in planned:
        raise InvalidSelection("helper is not part of the current executable zone foundation plan")
    raise SelectionConflict("Helferausführung benötigt einen separat verifizierten Transaktionspfad; vorhandene Funktionszuordnung ist verfügbar")

def desired_helper(foundation, domain, key):
    matches=[h for h in foundation.get("helper_plan",[]) if h.get("domain")==domain and h.get("key")==key]
    if len(matches)!=1:
        raise InvalidSelection("helper plan changed; reload")
    helper=dict(matches[0])
    if domain!="timer":
        raise InvalidSelection("this release provisions only the presence-delay timer")
    helper["config"]={**DEFAULT_TIMER, **helper.get("config",{})}
    return helper

def exact_timer(row, helper):
    if not isinstance(row,dict) or row.get("id")!=helper["key"]:
        return False
    cfg=helper["config"]
    return row.get("name")==helper["name"] and row.get("duration")==cfg["duration"] and row.get("restore") is cfg["restore"]

def provisioning_preview(inventory, foundation):
    return {
      "schema": "pilotsuite-helper-provisioning-v2",
      "zone_id": inventory.get("zone_id"), "revision": inventory.get("revision"),
      "helpers": foundation.get("helper_plan", []),
      "ownership": {"namespace": "pilotsuite_<zone>_<purpose>",
        "existing_matching_helpers": "reuse_before_create",
        "foreign_helpers": "never_take_ownership_implicitly",
        "delete_policy": "never_delete_foreign_or_preexisting_helper"},
      "transaction": {"state": "blocked_pending_acceptance", "before_image_required": True,
        "optimistic_revision_required": True, "post_write_verification_required": True,
        "unknown_outcome": "read_back_never_blind_retry",
        "rollback": "not_available_no_write_performed"},
      "execution": {"allowed": False, "actions": [], "reason": "legacy_control_path_not_accepted"},
      "limits": ["Legacy creation is withheld pending transport, identity and recovery acceptance; use confirmed existing bindings.",
                 "Existing helpers are never renamed, deleted or adopted by name.",
                 "No automation, actuator, learning-consent or generic PlanStore action is enabled."]};
