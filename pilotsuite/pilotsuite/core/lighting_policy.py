"""Bounded daylight-relative lighting policy math; pure and explainable."""
from __future__ import annotations
from math import isfinite

def lighting_target(*, outdoor_lux, occupied, atmosphere="neutral", minimum=15, maximum=85):
    """Return a target percentage, never an action. None means do not change light."""
    if type(occupied) is not bool or not occupied:
        return {"target":None,"reason":"not_occupied","execution":{"allowed":False}}
    if isinstance(outdoor_lux,bool) or not isinstance(outdoor_lux,(int,float)) or not isfinite(outdoor_lux) or outdoor_lux < 0:
        return {"target":None,"reason":"invalid_daylight","execution":{"allowed":False}}
    if any(type(v) not in (int,float) or not isfinite(v) for v in (minimum,maximum)) or not (0 <= minimum <= maximum <= 100):
        raise ValueError("invalid lighting bounds")
    # Piecewise daylight compensation. Deliberately simple and inspectable.
    if outdoor_lux >= 10000: base=minimum
    elif outdoor_lux >= 3000: base=minimum + (maximum-minimum)*0.20
    elif outdoor_lux >= 1000: base=minimum + (maximum-minimum)*0.40
    elif outdoor_lux >= 300: base=minimum + (maximum-minimum)*0.65
    else: base=maximum
    if not isinstance(atmosphere,str):
        return {"target":None,"reason":"invalid_atmosphere","execution":{"allowed":False}}
    offsets={"relax":-10,"focus":10,"social":0,"neutral":0}
    target=max(minimum,min(maximum,base+offsets.get(atmosphere,0)))
    return {"target":round(target),"reason":"daylight_compensation",
            "inputs":{"outdoor_lux":outdoor_lux,"occupied":occupied,"atmosphere":atmosphere},
            "bounds":{"minimum":minimum,"maximum":maximum},
            "execution":{"allowed":False}}

def should_adjust(current, target, *, deadband=5):
    if (any(type(v) not in (int,float) or not isfinite(v) for v in (current,target,deadband))
            or not 0 <= current <= 100 or not 0 <= target <= 100 or not 0 < deadband <= 100):
        return False
    return abs(current-target) >= deadband
