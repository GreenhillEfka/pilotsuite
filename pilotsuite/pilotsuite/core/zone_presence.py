"""Zone presence v2: typed evidence, bounded indirect holds and the existing kernel.

No HA writes, URLs or time-series storage. Historical data never enters evaluate().
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import replace
from math import isfinite
from .presence_kernel import advance_presence, checkpoint_dict, validate_checkpoint
from .presence_shadow import timestamp
from .organization import ENTITY, fingerprint, identity
from .selections import InvalidSelection

SCHEMA = 'pilotsuite-zone-presence-v2'
KINDS = ('continuous', 'pulse', 'support')
DEFAULTS = {'grace_seconds':300, 'clear_seconds':5, 'support_limit_seconds':1800,
            'sources':[], 'comparison_entity':None}
REASONS = {'not_observed':'Noch keine tragende Beobachtung.',
    'continuous_presence':'Gültige Dauerpräsenz.', 'activity_pulse':'Neuer Aktivitätsimpuls.',
    'all_clear_starts_grace':'Tragende Quellen frei; Nachlauf gestartet.',
    'grace_deadline_pending':'Ursprünglicher Nachlauf läuft.',
    'deadline_elapsed_all_clear':'Nachlauf beendet, benötigte Quellen frei.',
    'all_clear_remains_vacant':'Zone bleibt frei.',
    'no_recent_presence_basis':'Kaltstart ohne bestätigten Aufenthalt.',
    'required_source_unknown':'Direkte Raumabdeckung fehlt oder erforderliche Quelle unklar.',
    'support_hold':'Zeitlich begrenzte Stützung durch Nutzungsindiz.',
    'clear_stabilizing':'Freiphase wird stabil bestätigt.'}


def finite(value):
    return type(value) in (int,float) and isfinite(value)


def validate_spec(value, relevant, catalog):
    if not isinstance(value,dict) or set(value)!=set(DEFAULTS):
        raise InvalidSelection('Vollständige Zonen-Präsenzkonfiguration erforderlich')
    spec=deepcopy(value); by_id={r['entity_id']:r for r in catalog}
    for key,lo,hi in [('grace_seconds',1,86400),('clear_seconds',0,300),('support_limit_seconds',0,14400)]:
        if type(spec[key]) is not int or not lo<=spec[key]<=hi:
            raise InvalidSelection('Ungültige Zeitgrenze: '+key)
    if not isinstance(spec['sources'],list) or not 1<=len(spec['sources'])<=40:
        raise InvalidSelection('Eine bis 40 Präsenzquellen erforderlich')
    seen=set(); independent=set(); primary=False
    for row in spec['sources']:
        if not isinstance(row,dict) or set(row)!= {'entity_id','kind','required','max_age','group','can_start','active_states'}:
            raise InvalidSelection('Ungültige Quellendefinition')
        eid=row['entity_id']
        if not isinstance(eid,str): raise InvalidSelection('Ungültige Quellenkennung')
        entry=by_id.get(eid,{})
        if not isinstance(eid,str) or not ENTITY.fullmatch(eid) or eid in seen or eid not in relevant:
            raise InvalidSelection('Quelle muss eindeutig und relevant sein')
        if entry.get('disabled') or not entry.get('in_registry'):
            raise InvalidSelection('Quelle fehlt oder ist deaktiviert')
        if row['kind'] not in KINDS or type(row['required']) is not bool or type(row['can_start']) is not bool:
            raise InvalidSelection('Signaltyp und Wirkung müssen festgelegt sein')
        if type(row['max_age']) is not int or not 0<=row['max_age']<=86400:
            raise InvalidSelection('Meldealter: 0 = ereignisorientiert, sonst Sekunden bis 86400')
        if not isinstance(row['group'],str) or not 1<=len(row['group'])<=80 or any(ord(c)<32 for c in row['group']):
            raise InvalidSelection('Indizgruppe erforderlich')
        if (not isinstance(row['active_states'],list) or not 1<=len(row['active_states'])<=8 or
            any(not isinstance(s,str) or not s or len(s)>50 or s in ('unknown','unavailable') for s in row['active_states'])):
            raise InvalidSelection('Gültige Aktivzustände erforderlich')
        # Groups/templates are allowed as ONE derived observation, not independent duplicates.
        deps=set(entry.get('member_entity_ids') or [])
        if (entry.get('platform')=='group' and not deps):
            raise InvalidSelection('Gruppenmitglieder fehlen; Abhängigkeiten zuerst prüfen')
        if deps & {s['entity_id'] for s in spec['sources']}:
            raise InvalidSelection('Gruppe und Mitglieder nicht gleichzeitig als Quellen verwenden')
        if entry.get('derived') and row['kind']!='support':
            raise InvalidSelection('Abgeleitete Quelle vorerst als Zusatzindiz verwenden')
        if row['kind']!='support':
            if not eid.startswith('binary_sensor.'):
                raise InvalidSelection('Direkte Präsenz muss von einem Binärsensor stammen')
            if len(row['active_states'])!=1 or row['active_states'][0] not in ('on','off'):
                raise InvalidSelection('Direkte Binärquelle verwendet genau on oder off als Aktivzustand')
            primary=True
        elif row['required']:
            raise InvalidSelection('Zusatzindizien sind keine erforderliche Raumabdeckung')
        seen.add(eid)
        independent.add(row['group'])
    if not primary:
        raise InvalidSelection('Mindestens eine direkte Präsenz- oder Bewegungsquelle erforderlich')
    comparator=spec['comparison_entity']
    if comparator is not None and (not isinstance(comparator,str) or comparator not in relevant or comparator in seen
                                  or not comparator.startswith(('binary_sensor.','input_boolean.'))):
        raise InvalidSelection('Vergleichsstatus muss relevant und von den Eingängen getrennt sein')
    return spec


def suggested_sources(catalog,relevant):
    out=[]
    for item in catalog:
        eid=item['entity_id']; dc=item.get('device_class'); domain=eid.split('.')[0]
        if eid not in relevant or item.get('disabled'): continue
        if domain=='binary_sensor' and dc in ('motion','occupancy','presence') and not item.get('derived'):
            kind='pulse' if dc=='motion' else 'continuous'
            out.append({'entity_id':eid,'kind':kind,'required':True,'max_age':0,
                        'group':eid,'can_start':True,'active_states':['on']})
        elif domain=='media_player':
            out.append({'entity_id':eid,'kind':'support','required':False,'max_age':0,
                        'group':item.get('device_id') or eid,'can_start':False,'active_states':['playing']})
    return out


def source_basis(spec,catalog):
    by_id={r['entity_id']:r for r in catalog}
    ids=[s['entity_id'] for s in spec['sources']]+([spec['comparison_entity']] if spec['comparison_entity'] else [])
    return fingerprint({'spec':spec,'identities':[{**identity(by_id.get(e,{})),
        'disabled':by_id.get(e,{}).get('disabled'),'device_class':by_id.get(e,{}).get('device_class'),
        'members':by_id.get(e,{}).get('member_entity_ids',[])} for e in ids]})


def evaluate(spec, previous, states, *, now, fresh, event=None):
    if not finite(now): raise InvalidSelection('Ungültige Zeit')
    previous=deepcopy(previous or {})
    cp=validate_checkpoint(previous.get('kernel'))
    if (cp.last_activity_at is not None and cp.last_activity_at>now or
        previous.get('evaluated_at',now)>now):
        cp=validate_checkpoint(None); previous={}
    memory=deepcopy(previous.get('sources',{})); groups={}; rows=[]; new_pulse=None
    established=cp.state in ('occupied','grace') or (cp.deadline is not None and cp.deadline>now)
    for source in spec['sources']:
        eid=source['entity_id']; s=states.get(eid,{})
        value=s.get('state'); stamp=timestamp(s.get('last_reported',s.get('last_updated')))
        age=now-stamp if stamp is not None else None
        usable=fresh and value not in (None,'unknown','unavailable') and (source['max_age']==0 or
                        age is not None and 0<=age<=source['max_age'])
        if source['kind']!='support' and value not in ('on','off'): usable=False
        active=usable and value in source['active_states']; old=memory.get(eid,{})
        edge=False; at=None
        if event and event.get('entity_id')==eid:
            before,after=event.get('old_state'),event.get('new_state')
            at=timestamp(after.get('last_changed')) if isinstance(after,dict) else None
            edge=(isinstance(before,dict) and isinstance(after,dict) and
                  before.get('state') not in source['active_states']+['unknown','unavailable'] and
                  after.get('state') in source['active_states'] and at is not None and 0<=now-at<=120 and
                  at>old.get('last_edge',-1))
        if edge:
            old['last_edge']=at
            # Only actually observed edges can renew pulse or indirect evidence.
            if source['kind']=='pulse' and active and (source['can_start'] or established) and not event.get('self_generated',False):
                new_pulse=max(new_pulse or at,at)
            if source['kind']=='support' and active and not event.get('self_generated',False):
                old['support_until']=at+spec['support_limit_seconds']
                if source['can_start']:
                    new_pulse=max(new_pulse or at,at)
        # A support high level is bounded from the last DIRECT evidence. Do not slide
        # the deadline on repeated polling; no new pulse is manufactured by a restart.
        if source['kind']=='support' and active and cp.last_activity_at is not None:
            old['support_until']=max(old.get('support_until',0),cp.last_activity_at+spec['support_limit_seconds'])
        if not active: old.pop('support_until',None)
        if source['kind']=='continuous':
            level='on' if active and (source['can_start'] or established) else 'unknown' if active else 'off' if usable else 'unknown'
        elif source['kind']=='pulse':
            level=('off' if usable and (not active or edge or cp.deadline is not None and now<cp.deadline)
                   else 'unknown')
        else: level='off'  # handled as bounded support below, never as a direct source
        if source['kind']!='support':
            group=groups.setdefault(source['group'],{'states':[],'required_unknown':False})
            group['states'].append(level)
            group['required_unknown'] |= source['required'] and level=='unknown'
        memory[eid]=old
        rows.append({**source,'name':eid,'state':value if usable else 'unknown','usable':usable,
                     'age_seconds':round(age,1) if age is not None and age>=0 else None,
                     'active':active,'support_until':old.get('support_until')})
    levels=[]
    for g in groups.values():
        levels.append('on' if 'on' in g['states'] else
                      'unknown' if g['required_unknown'] else 'off')
    # Optional gaps may be ignored beside valid direct coverage, but an entirely
    # unobserved zone cannot prove absence merely because every source is optional.
    direct_observation=any(level in ('on','off') for g in groups.values() for level in g['states'])
    if not fresh or not direct_observation: levels=['unknown']
    # Strong positive evidence wins over unavailable unrelated coverage. Pulses
    # must also be able to establish occupied before unknown data blocks vacancy.
    if new_pulse is not None and 'on' not in levels and fresh:
        transition=advance_presence(cp,continuous=['off'],pulse=True,now=new_pulse,grace_seconds=spec['grace_seconds'])
        cp=transition.checkpoint
        if 'unknown' in levels:
            levels=['off']  # this frame's positive evidence; future ticks re-evaluate quality
    transition=advance_presence(cp,continuous=levels or ['unknown'],now=now,grace_seconds=spec['grace_seconds'])
    current=transition.checkpoint
    if current.state==cp.state=='occupied' and cp.last_activity_at is not None:
        current=replace(current,generation=cp.generation,last_activity_at=cp.last_activity_at)
    # A newly cleared continuous source anchors the optional support hold once.
    if cp.state=='occupied' and 'on' not in levels and 'unknown' not in levels:
        for row in rows:
            if row['kind']=='support' and row['active']:
                row['support_until']=now+spec['support_limit_seconds']
                memory[row['entity_id']]['support_until']=row['support_until']
    supports=[r['support_until'] for r in rows if r['kind']=='support' and r['active'] and
              finite(r['support_until']) and r['support_until']>now]
    if current.state in ('grace','vacant') and supports and 'unknown' not in levels:
        # Extension is anchored to direct evidence, not current wall time.
        deadline=max(current.deadline or 0,max(supports))
        current=replace(current,state='grace',deadline=deadline,reason='support_hold')
    clear_since=previous.get('clear_since')
    if current.state=='vacant' and cp.state!='vacant':
        clear_since=clear_since if finite(clear_since) and clear_since<=now else now
        if now-clear_since<spec['clear_seconds']:
            current=replace(current,state='grace',deadline=cp.deadline or now,reason='clear_stabilizing')
    elif current.state not in ('vacant','grace') or current.reason not in ('clear_stabilizing','deadline_elapsed_all_clear'):
        clear_since=None
    # Constant occupied observations must not mutate an inferred event timestamp.
    before=checkpoint_dict(cp);after=checkpoint_dict(current)
    if (before['state'],before['deadline'],before['reason'])!=(after['state'],after['deadline'],after['reason']):
        current=replace(current,generation=max(cp.generation+1,current.generation))
    value=True if current.state in ('occupied','grace') else False if current.state=='vacant' else None
    comparator=states.get(spec['comparison_entity'],{}).get('state') if spec['comparison_entity'] else None
    existing=True if comparator=='on' else False if comparator=='off' else None
    view={'state':current.state,'occupied':value,'valid':fresh and value is not None,
          'reason':current.reason,'explanation':REASONS.get(current.reason,transition.explanation),
          'deadline':current.deadline,'remaining_seconds':max(0,round(current.deadline-now)) if current.deadline else None,
          'generation':current.generation,'ha_state':comparator,
          'comparison':'unassessable' if existing is None or value is None else 'same' if value==existing else 'different',
          'sources':rows,'observed_at':now}
    checkpoint={'kernel':checkpoint_dict(current),'sources':memory,'clear_since':clear_since,'evaluated_at':now}
    return checkpoint,view
