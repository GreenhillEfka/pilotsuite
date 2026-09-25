"""Bounded reference extraction for HA automation structures."""
from __future__ import annotations
import re
ENTITY=re.compile(r"^[a-z_]+\.[a-z0-9_]+$")

ENTITY_KEYS={"entity_id"}
def entity_references(value, *, key=None):
    refs=set()
    if isinstance(value,str):
        if key in ENTITY_KEYS and ENTITY.fullmatch(value): refs.add(value)
        elif key in ENTITY_KEYS:
            for part in value.split(","):
                part=part.strip()
                if ENTITY.fullmatch(part): refs.add(part)
        # Templates are intentionally not guessed here; they require separate inspection.
    elif isinstance(value,list):
        for item in value: refs.update(entity_references(item,key=key))
    elif isinstance(value,dict):
        for k,v in value.items(): refs.update(entity_references(v,key=k))
    return refs
