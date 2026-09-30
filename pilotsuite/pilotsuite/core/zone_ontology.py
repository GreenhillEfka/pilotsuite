"""Habituszonen dashboard ontology: physical location and logical membership separate."""
import re
import unicodedata
from .organization import identity
from .selections import InvalidSelection

ROLES=('Habitus Zone','Habitus Übersicht','Habitus Bedienung','Habitus Status','Habitus Konfiguration','Habitus Diagnose')
ROLE_DESCRIPTIONS=('Ein öffentlicher Zonenanker','Essentielle Alltagsinformationen','Direkte Bedienung',
                   'Zustand und Verlauf','Parameter und Verhaltenslogik','Technik, Wartung und Fehler')


def display_role_suggestion(row):
    """Explain an editable display default from HA type metadata, never a grant.

    Existing labels and saved/manual drafts take precedence at the import boundary.
    A device can expose controls, configuration and diagnostics together: classify
    each entity, never propagate one guessed role to the whole device.
    """
    def result(role, reason):
        return {'suggested_habitus_roles': [role] if role else [], 'habitus_role_reason': reason}
    if (row.get('disabled') or row.get('in_registry') is False or
            not row.get('unique_id') or not row.get('platform')):
        return result(None, 'Keine eindeutige aktive Registerzuordnung.')
    category = row.get('entity_category')
    if category in ('diagnostic', 'config'):
        return result('Habitus Diagnose' if category == 'diagnostic' else 'Habitus Konfiguration',
                      'HA-Kategorie: Diagnose.' if category == 'diagnostic' else 'HA-Kategorie: Konfiguration.')
    domain = row.get('entity_id', '').split('.')[0]
    device_class = row.get('device_class')
    if domain in ('sensor', 'binary_sensor') and device_class in ('battery', 'signal_strength', 'connectivity', 'problem'):
        return result('Habitus Diagnose', 'Geräteklasse: Batterie, Verbindung oder Gerätestörung.')
    if domain == 'sensor' and device_class in ('temperature', 'humidity', 'illuminance', 'carbon_dioxide', 'pm25'):
        return result('Habitus Übersicht', 'Umgebungswert für die Zonenübersicht.')
    controls = {'light':'Leuchte', 'switch':'Schalter', 'fan':'Ventilator', 'cover':'Beschattung',
                'climate':'Thermostat', 'media_player':'Wiedergabegerät', 'vacuum':'Saug-/Wischroboter',
                'valve':'Ventil', 'lock':'Schloss', 'water_heater':'Warmwassergerät',
                'scene':'Szene', 'script':'Skript', 'button':'Taste', 'input_button':'Taste',
                'input_boolean':'Schalter'}
    if domain in controls:
        return result('Habitus Bedienung', 'Gerätetyp: ' + controls[domain] + '.')
    if domain in ('number', 'select', 'text', 'input_number', 'input_select', 'input_text', 'input_datetime', 'automation'):
        return result('Habitus Konfiguration', 'Einstellwert oder Verhaltenslogik.')
    if domain in ('sensor', 'binary_sensor', 'timer', 'counter', 'device_tracker', 'person', 'calendar'):
        return result('Habitus Status', 'Zustandsanzeige; daraus folgt keine Zonenanwesenheit.')
    if domain == 'weather':
        return result('Habitus Übersicht', 'Wetter für die Zonenübersicht.')
    if domain == 'update':
        return result('Habitus Diagnose', 'Wartung und verfügbare Aktualisierungen.')
    return result(None, 'Kein eindeutiger Darstellungsvorschlag; Rolle manuell wählen.')


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
