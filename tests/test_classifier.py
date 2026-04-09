# test_classifier.py

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.classifier import classify, _classify_score
import config


# ---------------------------------------------------------------------------
# _classify_score — boundary tests
# ---------------------------------------------------------------------------

def test_score_above_high_threshold_is_high():
    assert _classify_score(config.HIGH_THRESHOLD + 1) == config.RISK_HIGH


def test_score_exactly_at_high_threshold_is_high():
    assert _classify_score(config.HIGH_THRESHOLD) == config.RISK_HIGH


def test_score_just_below_high_threshold_is_medium():
    assert _classify_score(config.HIGH_THRESHOLD - 0.01) == config.RISK_MEDIUM


def test_score_exactly_at_medium_threshold_is_medium():
    assert _classify_score(config.MEDIUM_THRESHOLD) == config.RISK_MEDIUM


def test_score_just_below_medium_threshold_is_low():
    assert _classify_score(config.MEDIUM_THRESHOLD - 0.01) == config.RISK_LOW


def test_score_of_zero_is_low():
    assert _classify_score(0) == config.RISK_LOW


# ---------------------------------------------------------------------------
# classify — list behaviour
# ---------------------------------------------------------------------------

def test_classify_adds_risk_level_to_each_result():
    # Scores chosen to sit clearly inside each band given current thresholds.
    results = [
        {"module": "auth",    "bug_score":  8.0, "change_score": 10.0, "risk_score": 18.0},  # >= HIGH_THRESHOLD (14)
        {"module": "cart",    "bug_score":  4.0, "change_score":  7.0, "risk_score": 11.0},  # >= MEDIUM_THRESHOLD (8), < 14
        {"module": "reports", "bug_score":  1.0, "change_score":  3.0, "risk_score":  4.0},  # < MEDIUM_THRESHOLD
    ]
    classified = classify(results)

    assert classified[0]["risk_level"] == config.RISK_HIGH
    assert classified[1]["risk_level"] == config.RISK_MEDIUM
    assert classified[2]["risk_level"] == config.RISK_LOW


def test_classify_preserves_all_existing_keys():
    results = [
        {"module": "auth", "bug_score": 38.0, "change_score": 24.0, "risk_score": 62.0},
    ]
    classified = classify(results)
    record = classified[0]

    assert "module"       in record
    assert "bug_score"    in record
    assert "change_score" in record
    assert "risk_score"   in record
    assert "risk_level"   in record


def test_classify_returns_empty_list_for_empty_input():
    assert classify([]) == []
