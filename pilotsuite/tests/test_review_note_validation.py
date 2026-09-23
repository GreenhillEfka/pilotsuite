"""Pure synthetic contract checks; no HA access or household data."""
import copy
import json
import sqlite3
import unittest

from pilotsuite.core.review_notes import validate_note_request, notes_view, scope_fingerprint
from pilotsuite.core.selections import InvalidSelection


class ReviewNoteValidationTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'revision': 2, 'zone_revision': 3, 'review_revision': 0,
                        'automation_id': 'automation.synthetic', 'config_fingerprint': 'a'*64,
                        'disposition': 'reviewed', 'text': '  A synthetic note  '}
        self.draft = {'id': 'draft', 'zone_id': 'zone', 'pattern_id': 'pattern', 'revision': 2,
                      'source_status': 'current', 'unavailable_targets': [],
                      'fields': {'target_ids': ['light.synthetic']},
                      'current_pattern': {'sources': ['binary_sensor.synthetic']}}

    def test_normalizes_text_without_mutating_request(self):
        self.assertEqual('A synthetic note', validate_note_request(self.payload)['text'])
        self.assertEqual('  A synthetic note  ', self.payload['text'])

    def test_rejects_unknown_permissions_and_malformed_fields(self):
        cases = [dict(self.payload, allowed=True), dict(self.payload, text='x'*2001),
                 dict(self.payload, text='\x00'), dict(self.payload, text='\ud800'),
                 dict(self.payload, text=[]), dict(self.payload, disposition='approved'),
                 dict(self.payload, disposition=[]), dict(self.payload, automation_id='light.other'),
                 dict(self.payload, config_fingerprint='bad'), None, [], {}]
        for value in cases:
            with self.subTest(value=repr(value)[:100]), self.assertRaises(InvalidSelection):
                validate_note_request(value)

    def test_revision_numbers_are_strict_and_safe_for_javascript(self):
        for key in ('revision', 'zone_revision', 'review_revision'):
            for bad in (True, False, -1, 1.2, '1', None, 2**53):
                with self.subTest(key=key, bad=bad), self.assertRaises(InvalidSelection):
                    validate_note_request(dict(self.payload, **{key: bad}))
        with self.assertRaises(InvalidSelection):
            validate_note_request(dict(self.payload, revision=0))

    def test_delete_accepts_only_its_explicit_contract(self):
        payload = {k: self.payload[k] for k in ('revision','zone_revision','review_revision','automation_id')}
        self.assertEqual(payload, validate_note_request(payload, deleting=True))
        with self.assertRaises(InvalidSelection): validate_note_request(self.payload, deleting=True)

    def test_reference_binding_ignores_statistics_but_detects_changed_sources(self):
        other = copy.deepcopy(self.draft)
        other['current_pattern']['statistics'] = {'activation_count': 999}
        self.assertEqual(scope_fingerprint(self.draft), scope_fingerprint(other))
        other['current_pattern']['sources'].append('binary_sensor.second')
        self.assertNotEqual(scope_fingerprint(self.draft), scope_fingerprint(other))

    def test_stored_hash_never_claims_current_config_and_stale_notes_survive(self):
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE TABLE routine_review_notes (draft_id TEXT, revision INTEGER, records TEXT)')
            note = {'automation_id':'automation.synthetic', 'draft_revision':2, 'zone_revision':3,
                    'scope_fingerprint':scope_fingerprint(self.draft), 'config_fingerprint':'a'*64,
                    'text':'retained', 'disposition':'reviewed'}
            db.execute('INSERT INTO routine_review_notes VALUES (?,?,?)', ('draft',1,json.dumps({'automation.synthetic':note})))
            view = notes_view(db,self.draft,3)
            self.assertEqual('not_rechecked',view['items'][0]['config_status'])
            self.assertFalse(view['items'][0]['stale']); self.assertFalse(view['execution']['allowed'])
            self.draft['revision'] += 1
            self.assertIn('draft_changed',notes_view(db,self.draft,3)['items'][0]['stale_reasons'])
            self.draft.update(source_status='pattern_missing',current_pattern=None)
            changed = notes_view(db,self.draft,4)['items'][0]
            self.assertTrue(changed['stale']); self.assertEqual('retained',changed['text'])
            self.assertIn('pattern_missing',changed['stale_reasons']); self.assertIn('zone_changed',changed['stale_reasons'])
