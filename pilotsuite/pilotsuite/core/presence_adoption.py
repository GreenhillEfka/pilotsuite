"""Read-only controlled adoption analysis for existing presence automations."""
from __future__ import annotations
import hashlib,json,re
from pilotsuite.ha.client import HomeAssistantError

def adoption_targets(runtime):
    refs=set(runtime.get("raw_sources") or [])
    for key in ("owner","timer","sensor"):
        if runtime.get(key): refs.add(runtime[key])
    return sorted(refs)

def classify_inspection(inspection, runtime):
    limitations=set(inspection.get("limitations") or [])
    sections=inspection.get("sections") or {}
    alignment=inspection.get("alignment") or {}
    if isinstance(alignment.get("source_trigger_references"),list) and isinstance(alignment.get("target_action_references"),list):
        source_refs=set(alignment["source_trigger_references"])
        target_refs=set(alignment["target_action_references"])
    else:
        # Compatibility for retained synthetic/older inspection contracts.  A
        # step without the field predates structural availability and remains
        # equivalent to the old direct-reference projection.
        source_refs={e for s in sections.get("triggers",[]) if s.get("availability","available")=="available" for e in s.get("source_references",[])}
        target_refs={e for s in sections.get("actions",[]) if s.get("availability","available")=="available" for e in s.get("target_references",[])}
    raw=set(runtime.get("raw_sources") or []);owner=runtime.get("owner");timer=runtime.get("timer")
    status_ids={e for e in (owner,runtime.get("sensor")) if e}
    read_refs={e for section in ("triggers","conditions") for step in sections.get(section,[])
               if step.get("availability","available")=="available"
               for e in step.get("source_references",[])+step.get("target_references",[])}
    reads_status=sorted(status_ids & read_refs)
    reads_timer=bool(timer and timer in read_refs)
    direct_sources=sorted(raw & source_refs)
    def controls(eid, services):
        return bool(eid and eid in target_refs and any(
            step.get('availability','available')=='available' and eid in step.get('target_references',[]) and
            ('service' not in step or step['service'] in services) for step in sections.get('actions',[])))
    writes_owner=controls(owner, {'input_boolean.turn_on','input_boolean.turn_off','input_boolean.toggle',
                                  'homeassistant.turn_on','homeassistant.turn_off','homeassistant.toggle'})
    writes_timer=controls(timer, {'timer.start','timer.cancel','timer.pause','timer.finish','timer.change'})
    other_actions=any(step.get("kind")=="service_call" and step.get("availability")=="available" and
        (step.get("other_reference_count",0)>0 or not step.get("target_references"))
        for step in sections.get("actions",[]))
    blockers=sorted(limitations | ({"no_direct_presence_source_trigger"} if not direct_sources and not reads_status and not reads_timer else set()))
    overlap=bool(direct_sources or writes_owner or writes_timer or reads_status or reads_timer or target_refs)
    writer=writes_owner or writes_timer
    affected=sorted(set(direct_sources + reads_status +
        ([owner] if writes_owner else []) + ([timer] if writes_timer or reads_timer else [])))
    return {"automation_id":inspection["entity_id"],"fingerprint":inspection["config_fingerprint"],
      "overlap":overlap,"direct_presence_sources":direct_sources,"writes_owner":writes_owner,"writes_timer":writes_timer,
      "reads_status":reads_status,"reads_timer":reads_timer,"other_actions":other_actions,
      "usage":"mixed_writer" if writer and other_actions else "writer" if writer else
              "consumer" if reads_status else "related" if overlap else "unrelated",
      "limitations":sorted(limitations),"blockers":blockers,
      "classification":"conflict" if overlap and (writes_owner or writes_timer) else "related" if overlap else "unrelated",
      # Compatibility field: structure alone never establishes takeover readiness.
      # A current writer conflicts only with a second controller, not with reuse.
      "takeover_ready":False,"affected_entities":affected,
      "reuse_disposition":"review_mixed_controller" if writer and other_actions else
                         "retain_controller" if writer else "retain_consumer" if reads_status else
                         "inspect_relationship"}

def adoption_plan(zone_id,revision,runtime,inspections,*,include_unrelated=False):
    rows=[classify_inspection(i,runtime) for i in inspections]
    related=[r for r in rows if r["classification"]!="unrelated"]
    payload={"zone_id":zone_id,"revision":revision,"runtime_basis":{"owner":runtime.get("owner"),
      "raw_sources":runtime.get("raw_sources",[]),"timer":runtime.get("timer"),
      "sensor":runtime.get("sensor")},"automations":rows if include_unrelated else related}
    fingerprint=hashlib.sha256(json.dumps({"view":payload,"inspected":rows},sort_keys=True,separators=(",",":")).encode()).hexdigest()
    conflicts=[r["automation_id"] for r in related if r["classification"]=="conflict"]
    # Unresolved/disabled relationships must not vanish into a clean verdict.
    blockers=sorted({b for r in rows for b in r["blockers"]})
    return {"schema":"pilotsuite-presence-adoption-v1",**payload,"fingerprint":fingerprint,
      "summary":{"related":len(related),"conflicts":len(conflicts),"unresolved":len(blockers)},
      "conflicting_automations":conflicts,"blockers":blockers,
      "recommendation":"review_existing_control" if related else "inspect_missing_relationships",
      "reuse_review":{"controller_before":"existing_automations","controller_after":"existing_automations",
        "proposed_changes":[],"apply_implemented":False,
        "checks":[{"id":key,"state":"open"} for key in
                  ("timing","unknown_inputs","manual_override","dependencies","single_writer","backup_recovery")]},
      "execution":{"allowed":False,"actions":[]},
      "boundaries":["No automation is enabled, disabled, edited or deleted.","Configuration structure is not runtime proof.",
                    "Takeover requires a separate backup-bound approval and fresh fingerprint recheck."]}

def validate_automation_ids(ids):
    if not isinstance(ids,list) or len(ids)>50 or any(not isinstance(x,str) or not re.fullmatch(r"automation\.[a-z0-9_]+",x) for x in ids):
        raise HomeAssistantError("Invalid related automation identities")
    return sorted(set(ids))


def validate_existing_inputs(config, catalog, spec):
    """A comparison output cannot confirm its own independent assessment."""
    from .organization import binding_view
    from .selections import InvalidSelection
    bindings = binding_view(config, catalog)['assignments']
    outputs = {row.get('entity_id') for role in ('presence_status', 'presence_output')
               for row in bindings.get(role, [])}
    if outputs & {row['entity_id'] for row in spec['sources']}:
        raise InvalidSelection('Bestandsausgang darf nicht zugleich Eingang der unabhängigen Präsenzbewertung sein')


def existing_presence_view(config, catalog, observations, current, *, fresh, now, owned=()):
    """Project saved organization bindings only; neither a controller nor a second config."""
    from .organization import binding_view
    from .presence_kernel import timestamp
    from math import ceil
    bindings = binding_view(config, catalog)["assignments"]
    result = {"authority": "existing_automations", "control_enabled": False,
              "fresh": bool(fresh), "configured": False, "timing": config.get("organization", {}).get("timing", "observe"),
              "automations": [{key: row.get(key) for key in ('entity_id', 'saved_entity_id', 'name', 'status')}
                              for row in bindings.get("presence_automations", [])], "comparison": "unassessable"}
    for key, role in (("owner", "presence_status"), ("timer", "presence_timer"), ("sensor", "presence_output")):
        rows = bindings.get(role, [])
        if not rows:
            result[key] = None
            continue
        result["configured"] = True
        row = rows[0]
        eid = row.get("entity_id")
        usable = bool(fresh and row.get("status") in ("bound", "renamed", "exact_id_only") and
                      row.get("in_registry") and not row.get("disabled") and eid not in owned)
        if key == 'sensor' and row.get('device_class') not in ('occupancy', 'presence'):
            usable = False
        value = observations.get(eid, {}).get("state") if usable else None
        allowed = ("active", "paused", "idle") if key == "timer" else ("on", "off")
        usable = usable and value in allowed
        item = {"entity_id": eid, "saved_entity_id": row["saved_entity_id"], "name": row["name"],
                "binding_status": row["status"], "state": value if usable else "unknown",
                "available": usable, "own_output": eid in owned, "comparison": "unassessable"}
        if key != "timer" and usable and current and current.get("valid") and type(current.get("occupied")) is bool:
            item["comparison"] = "same" if current["occupied"] == (value == "on") else "different"
        if key == "timer":
            attrs = observations.get(eid, {}).get("attributes") or {}
            end = timestamp(attrs.get("finishes_at")) if usable and value == "active" else None
            item["remaining_seconds"] = max(0, ceil(end - now)) if end is not None else None
            item["finishes_at"] = end
        result[key] = item
    result["configured"] = result["configured"] or bool(result["automations"])
    reference = result["sensor"] or result["owner"]
    result["comparison_reference"] = "sensor" if result["sensor"] else "owner" if result["owner"] else None
    if reference:
        result["comparison"] = reference["comparison"]
    owner, sensor = result["owner"], result["sensor"]
    result["chain_consistency"] = ("same" if owner["state"] == sensor["state"] else "different") if (
        owner and sensor and owner["available"] and sensor["available"]) else "unassessable"
    return result
