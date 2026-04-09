# main.py
# Entry point — orchestrates the full pipeline in four steps:
#   1. Load   → read and validate CSV files
#   2. Analyze → calculate risk scores per module
#   3. Classify → assign LOW / MEDIUM / HIGH labels
#   4. Report  → print CLI table + write JSON + write HTML

import argparse
import sys
from pathlib import Path

# Allow imports from src/ without installing the package
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.loader     import load_bugs, load_changes
from src.analyzer   import calculate_risk_scores
from src.classifier import classify
from src.reporter   import print_cli_report, write_json_report, write_html_report


def parse_args() -> argparse.Namespace:
    """
    Define and parse command-line arguments.

    All arguments are optional — sensible defaults are provided so the tool
    works out of the box with just: python main.py
    """
    parser = argparse.ArgumentParser(
        prog="defect_predictor",
        description=(
            "Analyse historical bug reports and code changes to calculate "
            "a risk score per module and classify it as LOW, MEDIUM, or HIGH."
        ),
    )

    parser.add_argument(
        "--bugs",
        default="data/bugs.csv",
        metavar="FILE",
        help="Path to the bugs CSV file (default: data/bugs.csv)",
    )

    parser.add_argument(
        "--changes",
        default="data/changes.csv",
        metavar="FILE",
        help="Path to the code changes CSV file (default: data/changes.csv)",
    )

    parser.add_argument(
        "--output",
        default="output",
        metavar="DIR",
        help="Directory where reports will be saved (default: output/)",
    )

    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip generating the HTML report",
    )

    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Skip generating the JSON report",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    output_dir  = Path(args.output)
    json_output = str(output_dir / "report.json")
    html_output = str(output_dir / "report.html")

    print("Loading data...")
    bugs    = load_bugs(args.bugs)
    changes = load_changes(args.changes)
    print(f"  Loaded {len(bugs)} bugs and {len(changes)} changes.")

    print("Analysing risk scores...")
    scored = calculate_risk_scores(bugs, changes)

    print("Classifying risk levels...")
    classified = classify(scored)

    print_cli_report(classified)

    if not args.no_json:
        write_json_report(classified, json_output)

    if not args.no_html:
        write_html_report(classified, html_output)


if __name__ == "__main__":
    main()
