# config.py
# Central place for all tunable constants.
# Changing behavior means changing values here — not hunting through logic files.

# --- Severity weights ---
# Maps bug severity labels to numeric risk weights.
# Critical is intentionally disproportionate (5 vs 3) because a single
# critical bug causes more damage than multiple high-severity ones.
SEVERITY_WEIGHTS = {
    "low":      1,
    "medium":   2,
    "high":     3,
    "critical": 5,
}

# --- Open bug multiplier ---
# An unresolved bug is still an active risk — weight it higher than a closed one.
OPEN_BUG_MULTIPLIER   = 1.5
CLOSED_BUG_MULTIPLIER = 1.0

# --- Recency decay ---
# How many days back we look. Anything older than this window gets the minimum weight.
RECENCY_DECAY_WINDOW_DAYS = 180   # 6 months

# Minimum multiplier so that old records still contribute a little.
RECENCY_MIN_MULTIPLIER = 0.1

# --- Risk classification thresholds ---
# risk_score >= HIGH_THRESHOLD   → HIGH
# risk_score >= MEDIUM_THRESHOLD → MEDIUM
# otherwise                      → LOW
HIGH_THRESHOLD   = 14
MEDIUM_THRESHOLD = 8

# --- Risk level labels ---
RISK_HIGH   = "HIGH"
RISK_MEDIUM = "MEDIUM"
RISK_LOW    = "LOW"
