# reporter.py
# Responsibility: format and deliver the final results.
# Knows nothing about scoring or classification — only about presentation.

import json
from datetime import datetime
from pathlib import Path

from tabulate import tabulate

# Labels used to style the risk level column in the CLI output.
RISK_ICONS = {
    "HIGH":   "[HIGH]",
    "MEDIUM": "[MEDIUM]",
    "LOW":    "[LOW]",
}


def print_cli_report(results: list[dict]) -> None:
    """
    Print a formatted table to the terminal.

    Example output:
        ╒══════════════╤═════════════╤══════════════╤═════════════╤════════════╕
        │ Module       │  Bug Score  │ Change Score │ Risk Score  │ Risk Level │
        ╞══════════════╪═════════════╪══════════════╪═════════════╪════════════╡
        │ auth         │       38.40 │        24.10 │       62.50 │ 🔴 HIGH    │
        ...
    """
    if not results:
        print("No results to display.")
        return

    headers = ["Module", "Bug Score", "Change Score", "Risk Score", "Risk Level"]

    rows = [
        [
            r["module"],
            f"{r['bug_score']:>8.2f}",
            f"{r['change_score']:>8.2f}",
            f"{r['risk_score']:>8.2f}",
            RISK_ICONS.get(r["risk_level"], r["risk_level"]),
        ]
        for r in results
    ]

    print("\n" + "=" * 60)
    print("  DEFECT PREDICTION REPORT")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(_build_summary(results))


def write_json_report(results: list[dict], output_path: str) -> None:
    """
    Write results to a JSON file.

    The JSON includes a metadata block (generated_at, total modules,
    counts per risk level) plus the full result records.

    Args:
        results:     classified results from classifier.classify()
        output_path: path to the output JSON file (e.g. "output/report.json")
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    report = {
        "metadata": _build_metadata(results),
        "modules":  results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n  JSON report saved -> {output_path}")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_summary(results: list[dict]) -> str:
    """Return a one-line summary string showing counts per risk level."""
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        level = r.get("risk_level", "LOW")
        counts[level] = counts.get(level, 0) + 1

    return (
        f"\n  Summary: "
        f"{counts['HIGH']} HIGH  |  "
        f"{counts['MEDIUM']} MEDIUM  |  "
        f"{counts['LOW']} LOW\n"
    )


def _build_metadata(results: list[dict]) -> dict:
    """Build the metadata block for the JSON report."""
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        level = r.get("risk_level", "LOW")
        counts[level] = counts.get(level, 0) + 1

    return {
        "generated_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_modules":  len(results),
        "high_risk":      counts["HIGH"],
        "medium_risk":    counts["MEDIUM"],
        "low_risk":       counts["LOW"],
    }
