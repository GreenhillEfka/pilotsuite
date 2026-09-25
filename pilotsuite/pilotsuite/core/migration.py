"""Migration ledger for staged HA→PilotSuite automation adoption."""
from __future__ import annotations
from datetime import UTC,datetime

STATES=("discovered","imported","reviewed","approved","applied","verified","rolled_back")

def transition(record,new_state,*,fingerprint=None,note=""):
    old=record.get("state","discovered")
    if old not in STATES or new_state not in STATES: raise ValueError("invalid migration state")
    allowed={
      "discovered":{"imported"},"imported":{"reviewed"},"reviewed":{"approved","imported"},
      "approved":{"applied","reviewed"},"applied":{"verified","rolled_back"},
      "verified":{"rolled_back"},"rolled_back":{"reviewed"}}
    if new_state not in allowed.get(old,set()): raise ValueError("invalid migration transition")
    out=dict(record);out["state"]=new_state
    out["revision"]=int(record.get("revision",0))+1
    out["updated_at"]=datetime.now(UTC).isoformat()
    if fingerprint is not None: out["source_fingerprint"]=fingerprint
    history=list(record.get("history",[]));history.append({"from":old,"to":new_state,"note":note[:500]})
    out["history"]=history[-50:]
    return out

def new_record(entity_id,zone_id,fingerprint):
    return {"schema":"pilotsuite-automation-migration-v1","entity_id":entity_id,"zone_id":zone_id,
            "source_fingerprint":fingerprint,"state":"discovered","revision":0,"history":[],
            "execution":{"allowed":False,"actions":[]}}
