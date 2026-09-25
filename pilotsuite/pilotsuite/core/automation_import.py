"""Import existing HA automations into PilotSuite's review schema without taking execution ownership."""
from __future__ import annotations
import hashlib,json,re
from .selections import InvalidSelection

ALLOWED_ROOT={"id","alias","description","mode","max","max_exceeded","trace","triggers","trigger","conditions","condition","actions","action","variables"}

def _refs(value):
    found=set()
    if isinstance(value,str):
        found.update(re.findall(r"\b[a-z_]+\.[a-z0-9_]+\b",value))
    elif isinstance(value,list):
        for item in value: found.update(_refs(item))
    elif isinstance(value,dict):
        for k,v in value.items():
            found.update(_refs(k)); found.update(_refs(v))
    return found

def import_automation(entity_id, config, *, zone_id, zone_revision, inventory_ids):
    """Create a normalized immutable review snapshot; never executable."""
    if not isinstance(entity_id,str) or not re.fullmatch(r"automation\.[a-z0-9_]+",entity_id):
        raise InvalidSelection("invalid automation identity")
    if not isinstance(config,dict):
        raise InvalidSelection("automation config must be an object")
    if type(zone_revision) is not int or zone_revision < 0:
        raise InvalidSelection("invalid zone revision")
    # Preserve unknown HA fields in source_config; schema fields are projections only.
    encoded=json.dumps(config,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    refs=sorted(_refs(config))
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
                "config":config,"unknown_root_fields":sorted(set(config)-ALLOWED_ROOT)},
      "ownership":{"home_assistant":"execution_owner","pilotsuite":"review_owner"},
      "adoption":{"state":"imported_read_only","takeover_allowed":False,
                  "requirements":["fresh_source_fingerprint","unchanged_zone_revision",
                                  "explicit_user_approval","backup","post_write_verification"]},
      "execution":{"allowed":False,"actions":[]},
    }

def adoption_plan(snapshot, *, current_fingerprint, zone_revision, approve=False):
    if not approve:
        return {"state":"needs_approval","execution":{"allowed":False,"actions":[]}}
    blockers=[]
    if current_fingerprint!=snapshot["source"]["fingerprint"]: blockers.append("source_changed")
    if zone_revision!=snapshot["zone_revision"]: blockers.append("zone_changed")
    if blockers:
        return {"state":"blocked","blockers":blockers,"execution":{"allowed":False,"actions":[]}}
    return {"state":"ready_for_reviewed_takeover",
            "strategy":"preserve_entity_id_then_transform_in_place",
            "backup_required":True,"verify_after_write":True,
            "rollback":"restore_exact_pre_takeover_config",
            "execution":{"allowed":False,"actions":[]}}
