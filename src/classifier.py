# classifier.py
# Responsibility: assign a human-readable risk level to each scored module.
# Thresholds are read from config.py — not hardcoded here.

import config


def classify(scored_results: list[dict]) -> list[dict]:
    """
    Add a 'risk_level' key to each result dict.

    Args:
        scored_results: list of dicts from analyzer.calculate_risk_scores()

    Returns:
        The same list with a 'risk_level' key added to every item.
        Order is preserved (highest risk first, as returned by the analyzer).
    """
    for result in scored_results:
        result["risk_level"] = _classify_score(result["risk_score"])
    return scored_results


def _classify_score(score: float) -> str:
    """
    Map a numeric risk score to a label.

    Thresholds (from config.py):
        score >= HIGH_THRESHOLD   → HIGH
        score >= MEDIUM_THRESHOLD → MEDIUM
        otherwise                 → LOW
    """
    if score >= config.HIGH_THRESHOLD:
        return config.RISK_HIGH
    if score >= config.MEDIUM_THRESHOLD:
        return config.RISK_MEDIUM
    return config.RISK_LOW
