"""Import existing HA automations into PilotSuite's review schema without taking execution ownership."""
from __future__ import annotations
import hashlib
import json
import re
from copy import deepcopy
from .ha_references import entity_references
from .selections import InvalidSelection

ALLOWED_ROOT={"id","alias","description","mode","max","max_exceeded","trace","triggers","trigger","conditions","condition","actions","action","variables","initial_state","use_blueprint"}

def import_automation(entity_id, config, *, zone_id, zone_revision, inventory_ids):
    """Create a normalized immutable review snapshot; never executable."""
    if not isinstance(entity_id,str) or len(entity_id)>255 or not re.fullmatch(r"automation\.[a-z0-9_]+",entity_id):
        raise InvalidSelection("invalid automation identity")
    if not isinstance(config,dict):
        raise InvalidSelection("automation config must be an object")
    if type(zone_revision) is not int or zone_revision < 0:
        raise InvalidSelection("invalid zone revision")
    if not isinstance(zone_id,str) or not 1 <= len(zone_id) <= 255:
        raise InvalidSelection("invalid zone identity")
    if not isinstance(inventory_ids,(set,list,tuple)) or len(inventory_ids)>10000 or any(
            not isinstance(e,str) or len(e)>255 for e in inventory_ids):
        raise InvalidSelection("invalid zone inventory")
    limitations=set()
    pending=[(config,0)]
    nodes=0
    while pending:
        value,depth=pending.pop()
        nodes+=1
        if depth>32 or nodes>10000:
            raise InvalidSelection("automation structure exceeds review limits")
        if isinstance(value,dict):
            if any(not isinstance(k,str) for k in value):
                raise InvalidSelection("automation object keys must be text")
            if set(value)&{"area_id","device_id","label_id","floor_id","use_blueprint"}:
                limitations.add("indirect_references_not_resolved")
            if value.get("enabled") is False:
                limitations.add("disabled_steps_included_as_structure")
            pending.extend((v,depth+1) for v in value.values())
        elif isinstance(value,list):
            pending.extend((v,depth+1) for v in value)
        elif isinstance(value,str) and any(marker in value for marker in ("{{","{%","{#")):
            limitations.add("templates_not_evaluated")
    try:
        encoded=json.dumps(config,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
    except (ValueError,TypeError,RecursionError) as exc:
        raise InvalidSelection("automation is not bounded JSON") from exc
    if len(encoded.encode("utf-8"))>128*1024:
        raise InvalidSelection("automation exceeds review size limit")
    config=json.loads(encoded)
    if set(config)-ALLOWED_ROOT:
        limitations.add("unknown_fields_preserved_not_interpreted")
    refs=sorted(entity_references(config))
    zone_refs=sorted(set(refs)&set(inventory_ids))
    external_refs=sorted(set(refs)-set(inventory_ids))
    triggers=config.get("triggers",config.get("trigger",[]))
    conditions=config.get("conditions",config.get("condition",[]))
    actions=config.get("actions",config.get("action",[]))
    return {
      "schema":"pilotsuite-imported-automation-v1","entity_id":entity_id,
      "zone_id":zone_id,"zone_revision":zone_revision,
      "title":str(config.get("alias") or entity_id)[:120],
      "description":str(config.get("description") or "")[:1000],
      "mode":config.get("mode","single"),
      "projection":{"triggers":triggers,"conditions":conditions,"actions":actions,
                    "zone_references":zone_refs,"external_references":external_refs},
      "source":{"fingerprint":hashlib.sha256(encoded.encode()).hexdigest(),
                "config":deepcopy(config),"unknown_root_fields":sorted(set(config)-ALLOWED_ROOT)},
      "limitations":sorted(limitations),
      "reference_coverage":"static_entity_id_fields_only",
      "persisted":False,
      "ownership":{"home_assistant":"execution_owner","pilotsuite":"review_owner"},
      "adoption":{"state":"imported_read_only","takeover_allowed":False,
                  "requirements":["fresh_source_fingerprint","unchanged_zone_revision",
                                  "explicit_user_approval","backup","post_write_verification"]},
      "execution":{"allowed":False,"actions":[]},
    }

def adoption_plan(snapshot, *, current_fingerprint, zone_revision, approve=False):
    if approve is not True:
        return {"state":"needs_approval","execution":{"allowed":False,"actions":[]}}
    blockers=[]
    if current_fingerprint!=snapshot["source"]["fingerprint"]: blockers.append("source_changed")
    if type(zone_revision) is not int or zone_revision!=snapshot["zone_revision"]: blockers.append("zone_changed")
    if blockers:
        return {"state":"blocked","blockers":blockers,"execution":{"allowed":False,"actions":[]}}
    return {"state":"ready_for_reviewed_takeover",
            "strategy":"preserve_entity_id_then_transform_in_place",
            "backup_required":True,"verify_after_write":True,
            "rollback":"restore_exact_pre_takeover_config",
            "execution":{"allowed":False,"actions":[]}}
