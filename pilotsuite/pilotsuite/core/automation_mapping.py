"""Map imported automation behavior into PilotSuite zone responsibilities."""
from __future__ import annotations

def schema_mapping(snapshot, foundation):
    refs=set(snapshot.get("projection",{}).get("zone_references",[]))
    modules=foundation.get("modules",{})
    buckets={}
    role_refs={
      "presence":set((modules.get("presence") or {}).get("sources",[])),
      "lighting":set((modules.get("lighting") or {}).get("lights",[]))|set((modules.get("lighting") or {}).get("illuminance",[]))|set((modules.get("lighting") or {}).get("daylight_binary",[])),
      "media":set((modules.get("media") or {}).get("players",[])),
      "climate":set((modules.get("climate") or {}).get("controllers",[]))|set((modules.get("climate") or {}).get("temperature",[]))|set((modules.get("climate") or {}).get("humidity",[])),
    }
    for name,known in role_refs.items():
        hit=sorted(refs&known)
        buckets[name]={"references":hit,"state":"matched" if hit else "not_evidenced"}
    matched=set().union(*(set(v["references"]) for v in buckets.values()))
    return {"schema":"pilotsuite-automation-schema-mapping-v1","modules":buckets,
            "unmapped_zone_references":sorted(refs-matched),
            "external_references":snapshot.get("projection",{}).get("external_references",[]),
            "classification":"multi_module" if sum(v["state"]=="matched" for v in buckets.values())>1 else
                             "single_module" if any(v["state"]=="matched" for v in buckets.values()) else "unmapped",
            "execution":{"allowed":False,"actions":[]}}
