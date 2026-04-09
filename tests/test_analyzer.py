# test_analyzer.py
# We pass a fixed reference_date to every test so results are deterministic.

import sys
import os
import math
import pytest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.analyzer import (
    calculate_risk_scores,
    _recency_multiplier,
    _calculate_bug_score,
    _calculate_change_score,
)
import config

# Fixed reference date used in all tests — makes results predictable.
REF_DATE = datetime(2024, 4, 9)


# ---------------------------------------------------------------------------
# _recency_multiplier
# ---------------------------------------------------------------------------

def test_recency_multiplier_is_1_for_today():
    today = REF_DATE
    result = _recency_multiplier(today, today)
    assert result == 1.0


def test_recency_multiplier_is_half_at_halfway_point():
    # 90 days ago with a 180-day window → 1.0 - (90/180) = 0.5
    event = datetime(2024, 1, 10)   # ~90 days before REF_DATE
    result = _recency_multiplier(event, REF_DATE)
    assert abs(result - 0.5) < 0.02   # allow small rounding


def test_recency_multiplier_clamps_at_minimum():
    # A very old event should return the minimum, not a negative number.
    old_event = datetime(2020, 1, 1)
    result = _recency_multiplier(old_event, REF_DATE)
    assert result == config.RECENCY_MIN_MULTIPLIER


# ---------------------------------------------------------------------------
# _calculate_bug_score
# ---------------------------------------------------------------------------

def test_bug_score_is_zero_for_empty_list():
    assert _calculate_bug_score([], REF_DATE) == 0.0


def test_open_bug_scores_higher_than_closed():
    base_bug = {
        "bug_id": "X",
        "module": "auth",
        "severity": "high",
        "reported_date": REF_DATE,
    }
    open_bug   = {**base_bug, "status": "open"}
    closed_bug = {**base_bug, "status": "closed"}

    open_score   = _calculate_bug_score([open_bug],   REF_DATE)
    closed_score = _calculate_bug_score([closed_bug], REF_DATE)

    assert open_score > closed_score


def test_critical_bug_scores_higher_than_low():
    base_bug = {
        "bug_id": "X",
        "module": "auth",
        "status": "closed",
        "reported_date": REF_DATE,
    }
    critical_score = _calculate_bug_score([{**base_bug, "severity": "critical"}], REF_DATE)
    low_score      = _calculate_bug_score([{**base_bug, "severity": "low"}],      REF_DATE)

    assert critical_score > low_score


# ---------------------------------------------------------------------------
# _calculate_change_score
# ---------------------------------------------------------------------------

def test_change_score_is_zero_for_empty_list():
    assert _calculate_change_score([], REF_DATE) == 0.0


def test_larger_change_scores_higher():
    base = {"change_id": "C", "module": "auth", "change_date": REF_DATE, "author": "alice"}
    big_change   = _calculate_change_score([{**base, "lines_changed": 400}], REF_DATE)
    small_change = _calculate_change_score([{**base, "lines_changed": 5}],   REF_DATE)

    assert big_change > small_change


# ---------------------------------------------------------------------------
# calculate_risk_scores — integration
# ---------------------------------------------------------------------------

def test_results_sorted_highest_risk_first():
    bugs = [
        {"bug_id": "B1", "module": "risky",  "severity": "critical", "reported_date": REF_DATE, "status": "open"},
        {"bug_id": "B2", "module": "stable", "severity": "low",      "reported_date": REF_DATE, "status": "closed"},
    ]
    changes = [
        {"change_id": "C1", "module": "risky",  "lines_changed": 500, "change_date": REF_DATE, "author": "a"},
        {"change_id": "C2", "module": "stable", "lines_changed": 5,   "change_date": REF_DATE, "author": "b"},
    ]
    results = calculate_risk_scores(bugs, changes, reference_date=REF_DATE)

    assert results[0]["module"] == "risky"
    assert results[-1]["module"] == "stable"


def test_risk_score_equals_bug_plus_change_score():
    bugs = [
        {"bug_id": "B1", "module": "auth", "severity": "high", "reported_date": REF_DATE, "status": "closed"},
    ]
    changes = [
        {"change_id": "C1", "module": "auth", "lines_changed": 100, "change_date": REF_DATE, "author": "alice"},
    ]
    results = calculate_risk_scores(bugs, changes, reference_date=REF_DATE)
    r = results[0]

    assert r["risk_score"] == round(r["bug_score"] + r["change_score"], 2)


def test_module_appearing_only_in_changes_is_included():
    bugs    = []
    changes = [
        {"change_id": "C1", "module": "new_module", "lines_changed": 50, "change_date": REF_DATE, "author": "bob"},
    ]
    results = calculate_risk_scores(bugs, changes, reference_date=REF_DATE)
    modules = [r["module"] for r in results]

    assert "new_module" in modules
