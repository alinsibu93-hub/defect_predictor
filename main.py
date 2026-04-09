# main.py
# Entry point — orchestrates the full pipeline in four steps:
#   1. Load   → read and validate CSV files
#   2. Analyze → calculate risk scores per module
#   3. Classify → assign LOW / MEDIUM / HIGH labels
#   4. Report  → print CLI table + write JSON + write HTML

import sys
from pathlib import Path

# Allow imports from src/ without installing the package
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.loader     import load_bugs, load_changes
from src.analyzer   import calculate_risk_scores
from src.classifier import classify
from src.reporter   import print_cli_report, write_json_report, write_html_report

BUGS_FILE    = "data/bugs.csv"
CHANGES_FILE = "data/changes.csv"
JSON_OUTPUT  = "output/report.json"
HTML_OUTPUT  = "output/report.html"


def main() -> None:
    print("Loading data...")
    bugs    = load_bugs(BUGS_FILE)
    changes = load_changes(CHANGES_FILE)
    print(f"  Loaded {len(bugs)} bugs and {len(changes)} changes.")

    print("Analysing risk scores...")
    scored = calculate_risk_scores(bugs, changes)

    print("Classifying risk levels...")
    classified = classify(scored)

    print_cli_report(classified)
    write_json_report(classified, JSON_OUTPUT)
    write_html_report(classified, HTML_OUTPUT)


if __name__ == "__main__":
    main()
