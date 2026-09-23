from __future__ import annotations

import unittest

from pilotsuite.core.attribution import EventAttribution


class EventAttributionTests(unittest.TestCase):
    def test_direct_user_context_needs_no_service_correlation(self):
        attribution = EventAttribution()
        self.assertEqual(
            "user_context",
            attribution.classify_state(
                {"context": {"id": "state", "user_id": "private-user"}}, now=10
            ),
        )

    def test_parented_service_call_is_correlated_without_exposing_ids(self):
        attribution = EventAttribution()
        self.assertTrue(
            attribution.observe_service_event(
                {
                    "context": {
                        "id": "private-context",
                        "parent_id": "private-parent",
                        "user_id": None,
                    },
                    "data": {"domain": "light", "service": "turn_on"},
                },
                now=10,
            )
        )
        self.assertEqual(
            "parented_service_context",
            attribution.classify_state(
                {"context": {"id": "private-context"}}, now=11
            ),
        )

    def test_unparented_service_and_uncorrelated_derived_context_stay_distinct(self):
        attribution = EventAttribution()
        attribution.observe_service_event(
            {"context": {"id": "service", "parent_id": None}}, now=10
        )
        self.assertEqual(
            "service_context",
            attribution.classify_state({"context": {"parent_id": "service"}}, now=11),
        )
        self.assertEqual(
            "derived_context",
            attribution.classify_state({"context": {"parent_id": "missing"}}, now=11),
        )

    def test_ttl_limit_clear_and_invalid_context(self):
        attribution = EventAttribution(ttl_seconds=5, limit=1)
        self.assertFalse(attribution.observe_service_event({"context": {}}, now=0))
        attribution.observe_service_event({"context": {"id": "old"}}, now=0)
        attribution.observe_service_event({"context": {"id": "new"}}, now=1)
        self.assertEqual(
            "unknown", attribution.classify_state({"context": {"id": "old"}}, now=1)
        )
        self.assertEqual(
            "unknown", attribution.classify_state({"context": {"id": "new"}}, now=7)
        )
        attribution.observe_service_event({"context": {"id": "again"}}, now=8)
        attribution.clear()
        self.assertEqual(
            "unknown", attribution.classify_state({"context": {"id": "again"}}, now=8)
        )


if __name__ == "__main__":
    unittest.main()
