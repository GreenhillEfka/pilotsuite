"""Synthetic contracts for the read-only zone daily brief."""
import copy
from pilotsuite.core.daily_brief import build_daily_brief


def base():
    inv={"zone_id":"z","revision":4,"enabled":True,"items":[]}
    report={"enabled":True,"collection_state":"collecting",
            "candidates":[{"entity_id":"binary_sensor.p","suggested_role":"motion"}],
            "coverage":{"sampled_slots":12,"impaired_slots":0},
            "reviews":[{"zone_id":"z","revision":4,"pattern_id":"p1","title":"Abendroutine",
                        "state":"unreviewed","sources":["binary_sensor.p"]}]}
    return inv,report


def test_daily_brief_selects_one_current_candidate_without_execution():
    inv,report=base(); result=build_daily_brief(inv,report)
    assert result["candidate"]["pattern_id"]=="p1"
    assert result["candidate"]["execution"]=={"allowed":False,"actions":[]}
    assert result["execution"]=={"allowed":False,"actions":[]}


def test_daily_brief_is_pure_and_deterministic():
    inv,report=base(); before=copy.deepcopy((inv,report))
    assert build_daily_brief(inv,report)==build_daily_brief(inv,report)
    assert (inv,report)==before


def test_paused_or_disconnected_withholds_candidate():
    for state in ("paused","disconnected","no_source","off"):
        inv,report=base(); report["collection_state"]=state
        result=build_daily_brief(inv,report)
        assert result["candidate"] is None
        assert result["withheld_reasons"]


def test_rejected_deferred_and_stale_are_not_promoted():
    inv,report=base()
    report["reviews"]=[
      dict(report["reviews"][0],state="dismissed"),
      dict(report["reviews"][0],pattern_id="p2",state="deferred"),
      dict(report["reviews"][0],pattern_id="p3",revision=3),
    ]
    result=build_daily_brief(inv,report)
    assert result["candidate"] is None
    assert result["excluded"]=={"dismissed":1,"deferred":1}


def test_missing_coverage_is_explicit_not_zero_evidence():
    inv,report=base(); report["coverage"]={}
    result=build_daily_brief(inv,report)
    assert any("Beobachtbarkeit" in x for x in result["withheld_reasons"])
