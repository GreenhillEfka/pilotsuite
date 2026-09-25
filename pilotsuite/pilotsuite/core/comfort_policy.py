"""Pure media/climate comfort policies. Suggestions only, never HA actions."""
from __future__ import annotations

def media_intent(*, occupied, atmosphere, already_playing=False, manual_block=False):
    if manual_block or not occupied:
        return {"intent":"none","reason":"blocked_or_unoccupied","execution":{"allowed":False}}
    if already_playing:
        return {"intent":"preserve","reason":"existing_playback_has_priority","execution":{"allowed":False}}
    if atmosphere in {"relax","social","focus"}:
        return {"intent":"suggest","profile":atmosphere,"execution":{"allowed":False}}
    return {"intent":"none","reason":"no_explicit_media_context","execution":{"allowed":False}}

def climate_intent(*, occupied, temperature, target, humidity=None, window_open=False):
    if window_open:
        return {"intent":"hold","reason":"window_open","execution":{"allowed":False}}
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) for v in (temperature,target)):
        return {"intent":"unknown","reason":"invalid_temperature","execution":{"allowed":False}}
    delta=target-temperature
    if not occupied and abs(delta) < 2:
        return {"intent":"hold","reason":"unoccupied_no_large_deviation","execution":{"allowed":False}}
    intent="warm" if delta > 0.5 else "cool" if delta < -0.5 else "hold"
    return {"intent":intent,"delta":round(delta,2),"humidity":humidity,
            "note":"relative humidity is context, not proof of dehumidification",
            "execution":{"allowed":False}}
