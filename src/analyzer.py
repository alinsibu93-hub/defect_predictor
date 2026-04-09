# analyzer.py
# Responsibility: calculate a numeric risk score for each module.
# Input:  clean bug records and change records (from loader.py)
# Output: list of dicts, one per module, with bug_score, change_score, risk_score

import math
from datetime import datetime

import config


def calculate_risk_scores(
    bugs: list[dict],
    changes: list[dict],
    reference_date: datetime | None = None,
) -> list[dict]:
    """
    Calculate risk scores for every module found across bugs and changes.

    Args:
        bugs:           list of bug records returned by loader.load_bugs()
        changes:        list of change records returned by loader.load_changes()
        reference_date: the date to measure recency from (defaults to today).
                        Accepted as a parameter so tests can pass a fixed date.

    Returns:
        List of dicts sorted by risk_score descending, each containing:
            module        (str)
            bug_score     (float)
            change_score  (float)
            risk_score    (float)  — bug_score + change_score
    """
    if reference_date is None:
        reference_date = datetime.today()

    # Collect every module name that appears in either dataset.
    all_modules = _collect_modules(bugs, changes)

    results = []
    for module in all_modules:
        module_bugs    = [b for b in bugs    if b["module"] == module]
        module_changes = [c for c in changes if c["module"] == module]

        bug_score    = _calculate_bug_score(module_bugs, reference_date)
        change_score = _calculate_change_score(module_changes, reference_date)
        risk_score   = round(bug_score + change_score, 2)

        results.append({
            "module":       module,
            "bug_score":    round(bug_score, 2),
            "change_score": round(change_score, 2),
            "risk_score":   risk_score,
        })

    # Sort highest risk first so the report is immediately useful.
    results.sort(key=lambda r: r["risk_score"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Bug scoring
# ---------------------------------------------------------------------------

def _calculate_bug_score(bugs: list[dict], reference_date: datetime) -> float:
    """
    Score the bug history for one module.

    Each bug contributes:
        severity_weight * recency_multiplier * status_multiplier
    """
    total = 0.0
    for bug in bugs:
        severity_weight   = config.SEVERITY_WEIGHTS.get(bug["severity"], 1)
        recency           = _recency_multiplier(bug["reported_date"], reference_date)
        status_multiplier = (
            config.OPEN_BUG_MULTIPLIER
            if bug["status"] == "open"
            else config.CLOSED_BUG_MULTIPLIER
        )
        total += severity_weight * recency * status_multiplier

    return total


# ---------------------------------------------------------------------------
# Change scoring
# ---------------------------------------------------------------------------

def _calculate_change_score(changes: list[dict], reference_date: datetime) -> float:
    """
    Score the code churn for one module.

    Each change contributes:
        log(lines_changed + 1) * recency_multiplier

    We use log() so that large changes contribute more, but not linearly —
    a 400-line change is not 400x riskier than a 1-line change.
    """
    total = 0.0
    for change in changes:
        size_weight = math.log(change["lines_changed"] + 1)
        recency     = _recency_multiplier(change["change_date"], reference_date)
        total       += size_weight * recency

    return total


# ---------------------------------------------------------------------------
# Recency decay
# ---------------------------------------------------------------------------

def _recency_multiplier(event_date: datetime, reference_date: datetime) -> float:
    """
    Return a value between RECENCY_MIN_MULTIPLIER and 1.0 based on how
    recent the event is relative to the decay window.

    Formula:
        multiplier = max(min_value,  1.0 - (days_ago / decay_window))

    Examples (with a 180-day window):
        0 days ago   → 1.00  (full weight)
        90 days ago  → 0.50  (half weight)
        180 days ago → 0.10  (minimum weight, not zero)
        200 days ago → 0.10  (clamped to minimum)
    """
    days_ago      = (reference_date - event_date).days
    decay_window  = config.RECENCY_DECAY_WINDOW_DAYS
    raw           = 1.0 - (days_ago / decay_window)
    return max(config.RECENCY_MIN_MULTIPLIER, raw)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _collect_modules(bugs: list[dict], changes: list[dict]) -> list[str]:
    """Return a sorted list of unique module names from both datasets."""
    modules = set()
    for bug    in bugs:    modules.add(bug["module"])
    for change in changes: modules.add(change["module"])
    return sorted(modules)
