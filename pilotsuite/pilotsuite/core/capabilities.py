"""Research-backed capability model for zone comfort; deterministic and vendor-neutral."""
from __future__ import annotations

CAPABILITIES={
 "presence":{"requires":["presence"],"optional":["timer"],"principle":"event_driven_with_reconciliation"},
 "lighting":{"requires":["light"],"one_of":["illuminance","daylight_binary"],"optional":["atmosphere","sun"],"principle":"bounded_adaptation_manual_override"},
 "media":{"requires":["media"],"optional":["presence","atmosphere","queue"],"principle":"preserve_existing_playback"},
 "climate":{"requires":["climate","temperature"],"optional":["humidity","window","weather"],"principle":"slow_control_separate_setpoint_activity"},
}

def capability_matrix(roles):
    rows=[]
    for name,spec in CAPABILITIES.items():
        missing=[r for r in spec.get("requires",[]) if not roles.get(r)]
        alternatives=spec.get("one_of",[])
        if alternatives and not any(roles.get(r) for r in alternatives):
            missing.append("one_of:"+"/".join(alternatives))
        rows.append({"module":name,"state":"ready" if not missing else "needs_sources",
                     "missing":missing,"optional_available":[r for r in spec.get("optional",[]) if roles.get(r)],
                     "principle":spec["principle"]})
    return {"schema":"pilotsuite-capability-matrix-v1","items":rows,
            "execution":{"allowed":False,"actions":[]}}
