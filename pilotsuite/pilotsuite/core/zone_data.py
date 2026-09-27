"""Measured state histories with explicit gaps, units and display-only decimation."""
from math import isfinite
from statistics import mean
from datetime import datetime, UTC
from .history import timestamp
from .selections import InvalidSelection


def validate_window(start,end,now):
    a,b=timestamp(start),timestamp(end)
    if a is None or b is None or not 0<=a<b<=now+5 or b-a>31*86400:
        raise InvalidSelection('Zeitzonenbezogener Zeitraum bis 31 Tage je Abruf erforderlich; ältere Zeiträume sind zulässig')
    return a,b


def scalar(value):
    if value in (None,'unknown','unavailable'):return None
    if not isinstance(value,(str,int,float,bool)):return None
    if isinstance(value,str) and len(value)>200:return None
    try:
        number=float(value)
        if isfinite(number):return number
        return None
    except (ValueError,TypeError):
        return value


def series_for(records,catalog,start,end,*,limit=1200):
    by_id={r['entity_id']:r for r in catalog};result=[]
    for eid,rows in records.items():
        points={};unit=by_id.get(eid,{}).get('unit');units=set()
        for row in rows:
            if not isinstance(row,dict):continue
            stamp=timestamp(row.get('lu',row.get('last_updated',row.get('last_changed'))))
            if stamp is None or stamp>end:continue
            attrs=row.get('a',row.get('attributes',{})) or {}
            if isinstance(attrs,dict) and isinstance(attrs.get('unit_of_measurement'),str):
                units.add(attrs['unit_of_measurement'])
            value=scalar(row.get('s',row.get('state')))
            if stamp<start:
                # HA start-state sentinel is a held state, not a sample at window start.
                points[start]=value
            else: points[stamp]=value
        all_points=sorted(points.items());numeric=bool(all_points) and all(type(v) in (int,float) for _,v in all_points if v is not None)
        valid=[v for _,v in all_points if type(v) in (int,float)]
        mixed=len(units)>1
        if mixed: valid=[];numeric=False
        # No change/event count is derived from a decimated chart.
        transitions=sum(a[1]!=b[1] for a,b in zip(all_points,all_points[1:]) if a[1] is not None and b[1] is not None)
        decimated=len(all_points)>limit
        if decimated:
            # Keep min/max of numeric buckets and unknown gaps; bound to <=4*limit.
            stride=max(1,len(all_points)//(limit//4 or 1));shown=[]
            for i in range(0,len(all_points),stride):
                bucket=all_points[i:i+stride];chosen=[bucket[0],bucket[-1]]
                if numeric:
                    nums=[p for p in bucket if p[1] is not None]
                    if nums:chosen += [min(nums,key=lambda p:p[1]),max(nums,key=lambda p:p[1])]
                else:
                    if len(bucket)>2:chosen.append((bucket[1][0],None)) # no invented duration across omitted discrete transitions
                gaps=[p for p in bucket if p[1] is None]
                if gaps:chosen.append(gaps[0])
                shown.extend(sorted(set(chosen)))
        else:shown=all_points
        result.append({'entity_id':eid,'name':by_id.get(eid,{}).get('name',eid),'unit':next(iter(units)) if len(units)==1 else unit,
            'kind':'numeric' if numeric else 'state','unit_conflict':mixed,'points':shown,'record_count':len(all_points),
            'decimated':decimated,'changes':transitions,'minimum':min(valid) if valid else None,
            'maximum':max(valid) if valid else None,'sample_mean':mean(valid) if valid else None,
            'coverage':'no_records' if not all_points else 'recorded_states_not_continuous_monitoring'})
    return result
