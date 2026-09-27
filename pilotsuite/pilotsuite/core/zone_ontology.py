"""Habituszonen dashboard ontology: physical location and logical membership separate."""
import re
import unicodedata
from .organization import identity
from .selections import InvalidSelection

ROLES=('Habitus Zone','Habitus Übersicht','Habitus Bedienung','Habitus Status','Habitus Konfiguration','Habitus Diagnose')
ROLE_DESCRIPTIONS=('Ein öffentlicher Zonenanker','Essentielle Alltagsinformationen','Direkte Bedienung',
                   'Zustand und Verlauf','Parameter und Verhaltenslogik','Technik, Wartung und Fehler')


def slug(text):
    text=text.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    text=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','_',text).strip('_')[:90]


def metadata_operation(row,labels,*,name,zone_label,roles):
    if not isinstance(name,str) or not 1<=len(name)<=120 or any(ord(c)<32 for c in name):
        raise InvalidSelection('Lesbarer Name bis 120 Zeichen erforderlich')
    if not isinstance(roles,list) or not roles or any(not isinstance(r,str) for r in roles) or len(roles)!=len(set(roles)) or not set(roles)<=set(ROLES):
        raise InvalidSelection('Mindestens eine gültige Habitusrolle erforderlich')
    ids={l['label_id']:l for l in labels if isinstance(l,dict) and isinstance(l.get('label_id'),str)}
    if not isinstance(zone_label,str) or zone_label not in ids:raise InvalidSelection('Ein bestehendes Zonenlabel auswählen')
    by_name={}
    for l in ids.values():by_name.setdefault(l['name'],[]).append(l['label_id'])
    if any(len(by_name.get(r,[]))!=1 for r in roles):
        raise InvalidSelection('Habitus-Rollenlabels fehlen oder sind mehrdeutig; keine geratenen Labels')
    old=row.get('labels') or []
    if not isinstance(old,list) or any(not isinstance(x,str) for x in old):raise InvalidSelection('Vorherige Labels nicht lesbar')
    # Replace ONLY known semantic role labels, preserve every unrelated label and location.
    role_ids={i for role in ROLES for i in by_name.get(role,[])}
    after=sorted((set(old)-role_ids)|{zone_label}|{by_name[r][0] for r in roles})
    return {'entity_id':row['entity_id'],'identity':identity(row),'before':{'name':row.get('name'),'labels':sorted(old)},
        'after':{'name':name,'labels':after},'effect':'display_name_and_semantic_labels',
        'entity_id_unchanged':True,'areas_unchanged':True}


def metadata_matches(row,operation,which):
    from .organization import same_identity
    return (same_identity(row,operation['identity']) and row.get('entity_id')==operation['entity_id'] and
            row.get('disabled_by') is None and row.get('name')==operation[which]['name'] and
            sorted(row.get('labels') or [])==operation[which]['labels'])
