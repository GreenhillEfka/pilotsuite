"""Conservative presence-lifecycle review for existing HA automations.

The projection recognizes only literal trigger selectors and direct service calls.
It reports review questions, never execution truth, safety or a repair instruction.
Authored trigger IDs and household entity IDs do not leave this module.
"""
from __future__ import annotations

import re


ENTITY = re.compile(r"[a-z_]+\.[a-z0-9_]+")
BOUNDARY_CLASSES = frozenset(("door", "garage_door", "opening", "window"))
ACTIVITY_CLASSES = frozenset(("motion", "occupancy", "presence"))


def _identifier(value):
    if type(value) is int:
        return str(value)
    if isinstance(value, str) and len(value) <= 512 and not any(mark in value for mark in ("{{", "{%", "{#")):
        return value
    return None


def _entities(value):
    values = value if isinstance(value, list) else value.split(",") if isinstance(value, str) else []
    result = set()
    for item in values:
        if isinstance(item, str) and ENTITY.fullmatch(item.strip()):
            result.add(item.strip())
    return result


def _selectors(value, limitations):
    """Return one static trigger-ID set, or None when branch meaning is ambiguous."""
    found = []
    ambiguous = False

    def walk(node):
        nonlocal ambiguous
        if isinstance(node, list):
            for child in node:
                walk(child)
            return
        if not isinstance(node, dict):
            return
        if node.get("condition") == "trigger":
            raw = node.get("id")
            raw = raw if isinstance(raw, list) else [raw]
            ids = {_identifier(item) for item in raw}
            if None in ids or not ids:
                limitations.add("dynamic_trigger_selector")
            else:
                found.append(ids)
        if node.get("condition") in ("or", "not"):
            ambiguous = True
            limitations.add("conditional_semantics_not_evaluated")
        for key in ("conditions", "and", "or", "not"):
            if key in node:
                walk(node[key])

    walk(value)
    if len(found) == 1 and not ambiguous:
        return found[0]
    if len(found) > 1:
        limitations.add("multiple_trigger_selectors")
    return None


def _presence_calls(actions, trigger_ids, limitations, path="/actions"):
    calls = []

    def narrowed(current, selected):
        return current & selected if selected is not None else current

    def walk(value, possible, path):
        if isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, possible, f"{path}/{index}")
            return
        if not isinstance(value, dict):
            return
        if value.get("enabled") is False:
            return
        if "enabled" in value and type(value.get("enabled")) is not bool:
            limitations.add("dynamic_enablement")
            return
        call = value.get("action", value.get("service"))
        if isinstance(call, str) and call in ("input_boolean.turn_on", "input_boolean.turn_off", "timer.start"):
            targets = set()
            for container in (value.get("target"), value.get("data")):
                if isinstance(container, dict):
                    targets.update(_entities(container.get("entity_id")))
            if targets:
                calls.append({"service": call, "targets": targets, "trigger_ids": set(possible), "path": path})
            else:
                limitations.add("dynamic_or_indirect_service_target")
        choices = value.get("choose")
        if isinstance(choices, list):
            selected = set()
            for index, branch in enumerate(choices):
                if not isinstance(branch, dict):
                    limitations.add("unsupported_branch_structure")
                    continue
                ids = _selectors(branch.get("conditions", []), limitations)
                if ids is not None:
                    selected.update(ids)
                    walk(branch.get("sequence", []), narrowed(possible, ids), f"{path}/choose/{index}/sequence")
                else:
                    limitations.add("branch_trigger_scope_unknown")
            if "default" in value:
                walk(value["default"], possible - selected, f"{path}/default")
        elif "choose" in value:
            limitations.add("unsupported_branch_structure")
        if "if" in value:
            ids = _selectors(value.get("if"), limitations)
            if ids is not None:
                walk(value.get("then", []), narrowed(possible, ids), f"{path}/then")
                walk(value.get("else", []), possible - ids, f"{path}/else")
            else:
                limitations.add("branch_trigger_scope_unknown")
        for key in ("sequence", "parallel"):
            if key in value:
                walk(value[key], possible, f"{path}/{key}")
        repeat = value.get("repeat")
        if isinstance(repeat, dict) and "sequence" in repeat:
            walk(repeat["sequence"], possible, f"{path}/repeat/sequence")

    walk(actions, set(trigger_ids), path)
    return calls


def inspect_presence_lifecycle(config, catalog, fresh=True):
    """Derive bounded review findings from an already size-validated config."""
    if not fresh:
        return {"schema": "pilotsuite-presence-lifecycle-v1", "findings": [],
                "limitations": ["snapshot_stale"], "coverage": "literal_trigger_branches_and_direct_calls_only",
                "execution": {"allowed": False, "actions": []}}
    by_id = {row.get("entity_id"): row for row in catalog if isinstance(row, dict)}
    limitations = set()
    key = "triggers" if "triggers" in config else "trigger"
    raw = config.get(key, [])
    triggers = raw if isinstance(raw, list) else [raw] if isinstance(raw, dict) else []
    declared = {}
    for index, trigger in enumerate(triggers):
        if not isinstance(trigger, dict):
            limitations.add("unsupported_trigger_structure")
            continue
        identifier = _identifier(trigger.get("id", index))
        kind = trigger.get("trigger", trigger.get("platform"))
        entities = _entities(trigger.get("entity_id"))
        if identifier is None:
            limitations.add("dynamic_trigger_identity")
            continue
        if trigger.get("enabled") is False:
            category = None
            declared.setdefault(identifier, []).append({"category": category,
                "path": f"/{key}/{index}" if isinstance(raw, list) else f"/{key}"})
            continue
        if "enabled" in trigger and type(trigger.get("enabled")) is not bool:
            limitations.add("dynamic_enablement")
            category = None
            declared.setdefault(identifier, []).append({"category": category,
                "path": f"/{key}/{index}" if isinstance(raw, list) else f"/{key}"})
            continue
        classes = {by_id.get(entity, {}).get("device_class") for entity in entities}
        classes.discard(None)
        category = None
        if kind == "state" and classes & BOUNDARY_CLASSES and trigger.get("to") in ("off", "closed"):
            category = "boundary_closed"
        elif kind == "state" and classes & ACTIVITY_CLASSES and trigger.get("to") in ("on", "home", "detected"):
            category = "activity_started"
        elif kind == "event" and trigger.get("event_type") == "timer.finished":
            category = "timer_finished"
        declared.setdefault(identifier, []).append({"category": category,
            "path": f"/{key}/{index}" if isinstance(raw, list) else f"/{key}"})

    action_key = "actions" if "actions" in config else "action"
    calls = _presence_calls(config.get(action_key, []), declared, limitations, f"/{action_key}")
    on_targets = {target for call in calls if call["service"] == "input_boolean.turn_on" for target in call["targets"]}
    off_targets = {target for call in calls if call["service"] == "input_boolean.turn_off" for target in call["targets"]}
    status_targets = on_targets & off_targets
    findings = []

    boundary_evidence = []
    for call in calls:
        if call["service"] != "input_boolean.turn_off" or not (call["targets"] & status_targets):
            continue
        paths = sorted({row["path"] for item in call["trigger_ids"] for row in declared.get(item, [])
                        if row["category"] == "boundary_closed"})
        if paths:
            boundary_evidence.append({"trigger_paths": paths, "action_path": call["path"]})
    if boundary_evidence:
        findings.append({"id": "boundary_close_can_clear_presence", "state": "review",
            "evidence": boundary_evidence, "next_step": "review_presence_exit_semantics"})

    motion_evidence = []
    for call in calls:
        if call["service"] != "timer.start":
            continue
        paths = sorted({row["path"] for item in call["trigger_ids"] for row in declared.get(item, [])
                        if row["category"] == "activity_started"})
        if paths:
            motion_evidence.append({"trigger_paths": paths, "action_path": call["path"]})
    if motion_evidence:
        findings.append({"id": "activity_edge_only_refreshes_timeout", "state": "review",
            "evidence": motion_evidence, "next_step": "review_presence_timeout_semantics"})

    return {"schema": "pilotsuite-presence-lifecycle-v1", "findings": findings,
            "limitations": sorted(limitations), "coverage": "literal_trigger_branches_and_direct_calls_only",
            "execution": {"allowed": False, "actions": []}}
