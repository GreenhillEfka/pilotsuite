"""Display suggestions are metadata defaults, never occupancy/control decisions."""
import unittest
from pilotsuite.core.zone_ontology import display_role_suggestion


class DisplayRoleSuggestionTests(unittest.TestCase):
    def row(self, eid='light.demo', **fields):
        return dict(entity_id=eid, unique_id='demo', platform='synthetic', in_registry=True, **fields)

    def test_type_defaults_explain_their_origin(self):
        for eid, fields, expected in [
            ('light.demo', {}, 'Habitus Bedienung'),
            ('switch.demo', {}, 'Habitus Bedienung'),
            ('climate.demo', {}, 'Habitus Bedienung'),
            ('cover.demo', {}, 'Habitus Bedienung'),
            ('media_player.demo', {}, 'Habitus Bedienung'),
            ('sensor.demo', {'device_class':'temperature'}, 'Habitus Übersicht'),
            ('sensor.demo', {'device_class':'humidity'}, 'Habitus Übersicht'),
            ('sensor.demo', {'device_class':'power'}, 'Habitus Status'),
            ('binary_sensor.demo', {'device_class':'occupancy'}, 'Habitus Status'),
            ('binary_sensor.demo', {'device_class':'motion'}, 'Habitus Status'),
            ('sensor.demo', {'device_class':'battery'}, 'Habitus Diagnose'),
            ('binary_sensor.demo', {'device_class':'connectivity'}, 'Habitus Diagnose'),
            ('number.demo', {}, 'Habitus Konfiguration'),
            ('timer.demo', {}, 'Habitus Status'),
            ('update.demo', {}, 'Habitus Diagnose'),
        ]:
            with self.subTest(eid=eid, fields=fields):
                result=display_role_suggestion(self.row(eid, **fields))
                self.assertEqual([expected], result['suggested_habitus_roles'])
                self.assertTrue(result['habitus_role_reason'])
                self.assertNotIn('Habitus Zone', result['suggested_habitus_roles'])

    def test_registry_category_precedes_generic_type(self):
        for category, expected in [('diagnostic','Habitus Diagnose'),('config','Habitus Konfiguration')]:
            result=display_role_suggestion(self.row(entity_category=category))
            self.assertEqual([expected], result['suggested_habitus_roles'])
            self.assertIn('HA-Kategorie', result['habitus_role_reason'])

    def test_unknown_types_do_not_guess_from_name(self):
        result=display_role_suggestion(self.row('custom.demo', name='Wohnzimmer Licht'))
        self.assertEqual([], result['suggested_habitus_roles'])

    def test_missing_or_disabled_identity_never_suggests(self):
        for field, value in [('disabled',True),('in_registry',False),('unique_id',None),('platform',None)]:
            row=self.row();row[field]=value
            self.assertEqual([], display_role_suggestion(row)['suggested_habitus_roles'])

    def test_unavailable_measurement_is_not_a_vacancy_decision(self):
        result=display_role_suggestion(self.row('binary_sensor.demo', device_class='occupancy', state='unavailable'))
        self.assertEqual(['Habitus Status'], result['suggested_habitus_roles'])
        self.assertEqual({'suggested_habitus_roles','habitus_role_reason'},set(result))
