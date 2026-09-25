"""Detect responsibility overlap before adopting or generating HA automation logic."""
from __future__ import annotations

def responsibility_conflicts(existing_snapshots, proposed_modules):
    rows=[]; owners={}
    for snap in existing_snapshots:
        entity=snap.get("entity_id")
        mapping=snap.get("mapping",{}).get("modules",{})
        for module,data in mapping.items():
            if data.get("state")=="matched":
                owners.setdefault(module,[]).append(entity)
    for module in proposed_modules:
        current=sorted(set(owners.get(module,[])))
        rows.append({"module":module,"existing_owners":current,
                     "state":"conflict" if len(current)>1 else "occupied" if current else "free",
                     "requires_review":bool(current)})
    return {"schema":"pilotsuite-responsibility-conflicts-v1","items":rows,
            "blocked":any(r["state"]=="conflict" for r in rows),
            "execution":{"allowed":False,"actions":[]}}
