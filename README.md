# Defect Prediction Tool

A rule-based tool that analyses historical bug reports and code change data to calculate a **risk score per module** and classify each one as `LOW`, `MEDIUM`, or `HIGH` risk.

Built with pure Python — no machine learning libraries required.

---

## Why This Tool?

In software teams, not all modules are equally risky. Some areas of a codebase break repeatedly; others are rarely touched and remain stable. This tool surfaces that signal by combining two data sources:

- **Bug history** — how many defects a module had, how severe, and whether they are resolved
- **Code churn** — how frequently a module is changed and how large those changes are

The output helps QA teams prioritise test effort on the modules most likely to cause problems.

---

## How the Risk Score Works

```
risk_score = bug_score + change_score
```

**Bug score** — each bug contributes:
```
severity_weight  x  recency_multiplier  x  status_multiplier
```

| Factor | Detail |
|---|---|
| Severity weight | `low=1`, `medium=2`, `high=3`, `critical=5` |
| Recency multiplier | Linear decay over 180 days — recent bugs count more |
| Status multiplier | Open bugs (`1.5x`) weigh more than closed ones (`1.0x`) |

**Change score** — each code change contributes:
```
log(lines_changed + 1)  x  recency_multiplier
```
`log()` is used so large changes contribute more, but not linearly.

**Classification thresholds** (tunable in `config.py`):

| Score | Risk Level |
|---|---|
| >= 14 | HIGH |
| >= 8  | MEDIUM |
| < 8   | LOW |

---

## Project Structure

```
defect_predictor/
├── data/
│   ├── bugs.csv          # Historical bug records
│   └── changes.csv       # Code change records
├── src/
│   ├── loader.py         # Reads and validates CSV input files
│   ├── analyzer.py       # Calculates risk scores per module
│   ├── classifier.py     # Maps scores to LOW / MEDIUM / HIGH
│   └── reporter.py       # Formats CLI table and JSON output
├── tests/
│   ├── test_loader.py
│   ├── test_analyzer.py
│   ├── test_classifier.py
│   └── test_reporter.py
├── output/               # Generated reports (git-ignored)
├── config.py             # All weights and thresholds in one place
├── main.py               # Entry point
└── requirements.txt
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/alinsibu93-hub/defect_predictor.git
cd defect_predictor
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the tool

```bash
python main.py
```

### 4. Expected output

```
Loading data...
  Loaded 15 bugs and 17 changes.
Analysing risk scores...
Classifying risk levels...

============================================================
  DEFECT PREDICTION REPORT
  Generated: 2026-04-09 14:14
============================================================
+---------------+-------------+----------------+--------------+--------------+
| Module        |   Bug Score |   Change Score |   Risk Score | Risk Level   |
+===============+=============+================+==============+==============+
| auth          |        5.31 |          10.83 |        16.14 | [HIGH]       |
+---------------+-------------+----------------+--------------+--------------+
| payment       |        6.15 |           7.82 |        13.97 | [MEDIUM]     |
+---------------+-------------+----------------+--------------+--------------+
| cart          |        4.36 |           5.34 |         9.70 | [MEDIUM]     |
+---------------+-------------+----------------+--------------+--------------+
| notifications |        1.93 |           2.93 |         4.86 | [LOW]        |
+---------------+-------------+----------------+--------------+--------------+
| reporting     |        0.78 |           1.01 |         1.79 | [LOW]        |
+---------------+-------------+----------------+--------------+--------------+

  Summary: 1 HIGH  |  2 MEDIUM  |  2 LOW

  JSON report saved -> output/report.json
```

A machine-readable report is also written to `output/report.json`.

---

## Input File Format

### `data/bugs.csv`

| Column | Type | Valid values |
|---|---|---|
| `bug_id` | string | any unique identifier |
| `module` | string | name of the system module |
| `severity` | string | `low`, `medium`, `high`, `critical` |
| `reported_date` | date | `YYYY-MM-DD` |
| `status` | string | `open`, `closed` |

### `data/changes.csv`

| Column | Type | Valid values |
|---|---|---|
| `change_id` | string | any unique identifier |
| `module` | string | name of the system module |
| `lines_changed` | integer | positive integer |
| `change_date` | date | `YYYY-MM-DD` |
| `author` | string | contributor name |

---

## Tuning the Tool

All scoring weights and classification thresholds are in `config.py`:

```python
SEVERITY_WEIGHTS       = {"low": 1, "medium": 2, "high": 3, "critical": 5}
OPEN_BUG_MULTIPLIER    = 1.5
RECENCY_DECAY_WINDOW_DAYS = 180
HIGH_THRESHOLD         = 14
MEDIUM_THRESHOLD       = 8
```

Change these values to calibrate the tool to your team's data — no logic files need to be touched.

---

## Running the Tests

```bash
python -m pytest tests/ -v
```

```
41 passed in 0.19s
```

Tests cover:
- CSV validation (missing columns, bad dates, unknown severity values)
- Scoring logic (recency decay, severity weighting, open vs closed bugs)
- Classification boundary conditions
- CLI output content and JSON file structure

---

## Dependencies

| Package | Purpose |
|---|---|
| `tabulate` | Formats the CLI report table |
| `pytest` | Test runner |

No machine learning libraries. No external data sources. Runs anywhere Python 3.10+ is installed.

---

## Author

Built by Alin Sibu as a portfolio project demonstrating rule-based data analysis, clean Python architecture, and QA-oriented thinking.
