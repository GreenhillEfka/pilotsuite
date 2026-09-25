"""Synthetic contracts; compatible with unittest discovery and pytest.

No HA access, additional collection or new evidence owner. Fixtures follow the
previously retrieved review_brief / _context_payload shape, not live house data.
"""
import copy
import json
import math
import unittest

from pilotsuite.core.daily_brief import build_daily_brief


def fixture():
    items = [
        {"entity_id": "binary_sensor.synthetic", "decision": "relevant",
         "suggested_role": "motion", "state": "off"},
        {"entity_id": "light.synthetic", "decision": "relevant",
         "suggested_role": "light", "state": "off"},
    ]
    inventory = {"zone_id": "z", "revision": 4, "enabled": True, "items": items}
    review = {
        "schema": "pilotsuite-review-v1", "zone_id": "z", "revision": 4,
        "pattern_id": "p1", "title": "Synthetische Abendroutine",
        "state": "unreviewed", "preference": None, "risk": "read_only",
        "sources": ["binary_sensor.synthetic"],
        "statistics": {"activation_count": 6, "distinct_day_count": 4,
            "day_group": "all", "timezone": "UTC",
            "window_local": {"start_hour": 12, "end_hour": 14}},
        "temporal_check": {"start": 100, "split_at": 170, "end": 200,
            "timezone": "UTC", "basis": "retained", "day_group": "all",
            "start_hour": 12, "state": "reobserved",
            "training_events": 5, "training_days": 3,
            "later_events": 1, "later_days": 1},
        "execution": {"allowed": False, "actions": []},
    }
    report = {"revision": 4, "enabled": True, "eligible": True,
        "collection_state": "collecting", "collecting_sources": ["binary_sensor.synthetic"],
        "config": {"learning": True, "roles": {"presence": ["binary_sensor.synthetic"]}},
        "candidates": copy.deepcopy(items),
        "coverage": {"sampled_slots": 12, "impaired_slots": 0,
                     "unobserved_slots_between_checks": 0},
        "reviews": [review]}
    return inventory, report


class DailyBriefTests(unittest.TestCase):
    def setUp(self):
        self.inventory, self.report = fixture()

    def build(self):
        return build_daily_brief(self.inventory, self.report)

    def withheld(self):
        result = self.build()
        self.assertIsNone(result["candidate"])
        self.assertTrue(result["withheld_reasons"])
        self.assertEqual({"allowed": False, "actions": []}, result["execution"])
        return result

    def test_current_existing_review_has_one_non_executing_candidate(self):
        result = self.build()
        self.assertEqual("p1", result["candidate"]["pattern_id"])
        self.assertEqual({"allowed": False, "actions": []}, result["candidate"]["execution"])
        self.assertEqual([], result["withheld_reasons"])

    def test_no_coverage_never_promotes_candidate(self):
        self.report["coverage"] = {}
        self.withheld()

    def test_invalid_coverage_counts_are_unknown_not_zero(self):
        for key in ("sampled_slots", "impaired_slots", "unobserved_slots_between_checks"):
            for value in (None, True, False, -1, 2**54, math.nan, math.inf, "12"):
                with self.subTest(key=key, value=value):
                    self.inventory, self.report = fixture()
                    self.report["coverage"][key] = value
                    self.withheld()

    def test_no_ready_samples_or_inconsistent_counts_withhold(self):
        for sampled, impaired in ((0, 0), (12, 12), (12, 13)):
            with self.subTest(sampled=sampled, impaired=impaired):
                self.report["coverage"].update(sampled_slots=sampled, impaired_slots=impaired)
                self.withheld()

    def test_partial_coverage_is_caution_not_claimed_complete(self):
        self.report["coverage"].update(impaired_slots=2, unobserved_slots_between_checks=3)
        result = self.build()
        self.assertIsNotNone(result["candidate"])
        self.assertEqual([], result["withheld_reasons"])
        self.assertTrue(result["cautions"])
        self.assertEqual("partial", result["coverage_state"])

    def test_only_literal_true_can_enable_promotion(self):
        for key in ("enabled", "eligible"):
            for value in (False, None, 0, 1, "true", "false", [], {}):
                with self.subTest(key=key, value=value):
                    self.inventory, self.report = fixture()
                    self.report[key] = value
                    self.withheld()
        for value in (False, None, 1, "true"):
            with self.subTest(learning=value):
                self.inventory, self.report = fixture()
                self.report["config"]["learning"] = value
                self.withheld()

    def test_inventory_enablement_must_agree(self):
        self.inventory["enabled"] = False
        self.withheld()

    def test_collection_states_fail_closed_including_malformed(self):
        for state in ("paused", "off", "disconnected", "no_source", "unknown", None, {}, []):
            with self.subTest(state=state):
                self.report["collection_state"] = state
                self.withheld()

    def test_foreign_and_stale_reviews_are_not_candidates(self):
        for changes in ({"zone_id": "other"}, {"revision": 3}, {"revision": True}, {"revision": 4.0}):
            with self.subTest(changes=changes):
                self.inventory, self.report = fixture()
                self.report["reviews"][0].update(changes)
                self.withheld()

    def test_foreign_dismissals_do_not_leak_into_zone_counts(self):
        self.report["reviews"] = [dict(self.report["reviews"][0], zone_id="foreign", state="dismissed")]
        self.assertEqual({"dismissed": 0, "deferred": 0}, self.withheld()["excluded"])

    def test_report_revision_must_match_current_inventory(self):
        for value in (None, True, 3, 4.0):
            with self.subTest(value=value):
                self.report["revision"] = value
                self.withheld()

    def test_review_sources_must_still_be_in_inventory_roles_and_collection(self):
        cases = ("inventory", "roles", "collecting", "foreign")
        for case in cases:
            with self.subTest(case=case):
                self.inventory, self.report = fixture()
                if case == "inventory": self.inventory["items"] = []
                elif case == "roles": self.report["config"]["roles"]["presence"] = []
                elif case == "collecting": self.report["collecting_sources"] = []
                else: self.report["reviews"][0]["sources"] = ["binary_sensor.foreign"]
                self.withheld()

    def test_unreviewed_ignored_and_unavailable_sources_are_not_current(self):
        for change in ({"decision": "unreviewed"}, {"decision": "ignored"},
                       {"state": None}, {"state": "unknown"}, {"state": "unavailable"}, {"state": "23"}):
            with self.subTest(change=change):
                self.inventory, self.report = fixture()
                self.inventory["items"][0].update(change)
                self.withheld()

    def test_unchanged_old_binary_state_is_not_declared_physically_stale(self):
        self.inventory["items"][0]["last_updated"] = "1990-01-01T00:00:00Z"
        self.assertIsNotNone(self.build()["candidate"])

    def test_invalid_or_duplicate_source_ids_are_rejected(self):
        for sources in (None, "binary_sensor.synthetic", [], [None], [1],
                        ["binary_sensor.synthetic"] * 2, ["binary_sensor.synthetic"] * 21):
            with self.subTest(sources=sources):
                self.report["reviews"][0]["sources"] = sources
                self.withheld()

    def test_duplicate_inventory_identity_is_ambiguous(self):
        self.inventory["items"].append(dict(self.inventory["items"][0], decision="ignored"))
        self.withheld()

    def test_rejected_and_deferred_stay_out_even_with_inconsistent_state(self):
        for preference, count in (("rejected", "dismissed"), ("later", "deferred")):
            with self.subTest(preference=preference):
                self.inventory, self.report = fixture()
                self.report["reviews"][0]["preference"] = preference
                self.assertEqual(1, self.withheld()["excluded"][count])

    def test_unknown_preference_and_unmatched_accepted_state_fail_closed(self):
        for changes in ({"preference": "new_status"}, {"preference": []},
                        {"preference": "accepted", "state": "unreviewed"}):
            with self.subTest(changes=changes):
                self.inventory, self.report = fixture()
                self.report["reviews"][0].update(changes)
                self.withheld()

    def test_accepted_review_remains_review_not_permission(self):
        self.report["reviews"][0].update(preference="accepted", state="review_requested")
        self.assertFalse(self.build()["candidate"]["execution"]["allowed"])

    def test_duplicate_pattern_identity_cannot_choose_arbitrary_record(self):
        self.report["reviews"].append(dict(self.report["reviews"][0], title="Different"))
        self.withheld()

    def test_duplicate_rejection_wins_without_double_counting(self):
        self.report["reviews"].append(dict(self.report["reviews"][0], preference="rejected"))
        self.assertEqual(1, self.withheld()["excluded"]["dismissed"])

    def test_missing_or_invalid_identity_schema_or_execution_withholds(self):
        for change in ({"pattern_id": ""}, {"pattern_id": None}, {"pattern_id": "x"*129},
                       {"pattern_id": "p\n1"}, {"schema": "other"},
                       {"execution": {"allowed": True, "actions": []}},
                       {"execution": {"allowed": False, "actions": ["light.turn_on"]}},
                       {"risk": "actuate"}):
            with self.subTest(change=change):
                self.inventory, self.report = fixture()
                self.report["reviews"][0].update(change)
                self.withheld()

    def test_invalid_statistics_never_become_evidence(self):
        for key in ("activation_count", "distinct_day_count"):
            for value in (None, True, 0, -1, 2**54, math.nan, math.inf, "6"):
                with self.subTest(key=key, value=value):
                    self.inventory, self.report = fixture()
                    self.report["reviews"][0]["statistics"][key] = value
                    self.withheld()
        self.inventory, self.report = fixture()
        self.report["reviews"][0]["statistics"]["distinct_day_count"] = 7
        self.withheld()

    def test_no_temporal_or_insufficient_later_evidence_is_not_absence(self):
        for temporal in (None, {}, {"state": "insufficient_later_evidence"}):
            with self.subTest(temporal=temporal):
                self.inventory, self.report = fixture()
                self.report["reviews"][0]["temporal_check"] = temporal
                result = self.withheld()
                self.assertNotIn("keine Aktivität", " ".join(result["withheld_reasons"]))

    def test_temporal_window_timezone_counts_and_bounds_must_match(self):
        for change in ({"timezone": "Europe/Berlin"}, {"day_group": "weekend"},
                       {"start_hour": 10}, {"training_events": True}, {"later_days": 0},
                       {"later_events": math.nan}, {"split_at": 300}, {"start": -1},
                       {"end": math.inf}, {"state": "insufficient_earlier_evidence"}):
            with self.subTest(change=change):
                self.inventory, self.report = fixture()
                self.report["reviews"][0]["temporal_check"].update(change)
                self.withheld()

    def test_invalid_local_window_or_timezone_withholds(self):
        for changes in ({"timezone": "Invalid/Nowhere"}, {"day_group": []},
                        {"window_local": {"start_hour": True, "end_hour": 14}},
                        {"window_local": {"start_hour": 14, "end_hour": 12}}):
            with self.subTest(changes=changes):
                self.inventory, self.report = fixture()
                self.report["reviews"][0]["statistics"].update(changes)
                self.withheld()

    def test_candidates_are_stable_under_input_order_and_title_changes(self):
        self.report["reviews"].append(dict(self.report["reviews"][0], pattern_id="p2", title="A first"))
        one = self.build()["candidate"]["pattern_id"]
        self.report["reviews"].reverse()
        self.report["reviews"][0]["title"] = "Z last"
        self.assertEqual(one, self.build()["candidate"]["pattern_id"])
        self.assertEqual("p1", one)

    def test_observation_counts_use_confirmed_inventory_not_first_forty(self):
        self.inventory["items"] = [dict(self.inventory["items"][0], entity_id=f"binary_sensor.x{i}") for i in range(45)]
        self.inventory["items"].append(dict(self.inventory["items"][0], entity_id="binary_sensor.hidden", decision="unreviewed"))
        obs = self.build()["observations"][0]
        self.assertEqual(45, obs["confirmed_entities"])
        self.assertFalse(obs["truncated"])

    def test_large_inputs_are_explicitly_bounded(self):
        self.report["reviews"] = [dict(self.report["reviews"][0], pattern_id=f"p{i}") for i in range(201)]
        self.assertTrue(self.withheld()["truncated"])
        self.inventory, self.report = fixture()
        self.inventory["items"] *= 1001
        self.assertTrue(self.withheld()["truncated"])

    def test_malformed_optional_members_do_not_crash_projection(self):
        for key, value in (("reviews", [None, 1, "x", []]), ("config", None),
                           ("coverage", None), ("collecting_sources", "bad")):
            with self.subTest(key=key):
                self.inventory, self.report = fixture()
                self.report[key] = value
                self.withheld()
        self.inventory, self.report = fixture()
        self.inventory["items"] = [None, 1, [], "x"]
        self.withheld()

    def test_top_level_zone_and_safe_integer_revision_are_strict(self):
        for changes in ({"zone_id": None}, {"zone_id": ""}, {"zone_id": "\nz"},
                        {"revision": True}, {"revision": -1}, {"revision": 2**54}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                build_daily_brief(dict(self.inventory, **changes), self.report)

    def test_pure_deterministic_detached_and_strict_json(self):
        before = copy.deepcopy((self.inventory, self.report))
        result = self.build()
        self.assertEqual(result, self.build())
        self.assertEqual(before, (self.inventory, self.report))
        result["candidate"]["statistics"]["activation_count"] = 999
        self.assertEqual(before, (self.inventory, self.report))
        self.assertEqual(self.build(), json.loads(json.dumps(self.build(), allow_nan=False)))

    def test_titles_are_bounded_and_controls_not_propagated(self):
        self.report["reviews"][0]["title"] = "X\x00" * 10000
        title = self.build()["candidate"]["title"]
        self.assertLessEqual(len(title), 240)
        self.assertNotIn("\x00", title)

    def test_unknown_private_payloads_and_context_do_not_escape(self):
        self.report["raw_private_config"] = "PRIVATE_CANARY"
        self.report["reviews"][0]["context"] = {"raw": "PRIVATE_CANARY"}
        result = self.build()
        self.assertNotIn("PRIVATE_CANARY", json.dumps(result))
        self.assertNotIn("confidence", result["candidate"])
        self.assertNotIn("score", result)

    def test_candidate_is_historical_review_not_today_prediction(self):
        result = self.build()
        self.assertEqual("retained_review", result["candidate"]["basis_kind"])
        self.assertIn("keine Tagesprognose", " ".join(result["limits"]))


    def test_explicit_ready_only_samples_cannot_contradict_coverage(self):
        for value in (0, 11, 13, True, None, '12', -1, 12.0):
            with self.subTest(ready_only_slots=value):
                self.inventory, self.report = fixture()
                self.report['coverage']['ready_only_slots'] = value
                self.withheld()

    def test_optional_ready_only_sample_count_preserves_old_contract(self):
        self.assertIsNotNone(self.build()['candidate'])
        self.report['coverage']['ready_only_slots'] = 12
        self.assertIsNotNone(self.build()['candidate'])
        self.report['coverage'].update(impaired_slots=2, ready_only_slots=10)
        self.assertIsNotNone(self.build()['candidate'])
        self.assertEqual('partial', self.build()['coverage_state'])

    def test_section_days_cannot_exceed_all_retained_days(self):
        self.report['reviews'][0]['temporal_check']['training_days'] = 5
        self.withheld()

    def test_equal_event_totals_require_consistent_union_of_observed_days(self):
        self.report['reviews'][0]['statistics']['distinct_day_count'] = 5
        self.withheld()

    def test_a_day_crossing_the_split_is_not_double_counted(self):
        review = self.report['reviews'][0]
        review['temporal_check'].update(training_events=4, training_days=3,
                                        later_events=2, later_days=2)
        self.assertEqual(4, self.build()['candidate']['statistics']['distinct_day_count'])
        self.assertIsNotNone(self.build()['candidate'])

    def test_partial_temporal_totals_do_not_invent_equal_coverage(self):
        # Some retained observations may not belong to the compared subwindows.
        self.report['reviews'][0]['statistics'].update(activation_count=8, distinct_day_count=5)
        self.assertIsNotNone(self.build()['candidate'])


if __name__ == "__main__":
    unittest.main()
