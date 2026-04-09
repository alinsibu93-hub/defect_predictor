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


def write_html_report(results: list[dict], output_path: str) -> None:
    """
    Write a colour-coded HTML report to a file.

    Rows are highlighted by risk level:
        HIGH   → red background
        MEDIUM → yellow background
        LOW    → green background

    The file is self-contained — no external CSS or JS dependencies.

    Args:
        results:     classified results from classifier.classify()
        output_path: path to the output HTML file (e.g. "output/report.html")
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    metadata = _build_metadata(results)
    table_rows = _build_html_rows(results)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Defect Prediction Report</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      padding: 30px;
      color: #333;
    }}
    h1 {{
      font-size: 1.6rem;
      margin-bottom: 4px;
    }}
    .meta {{
      color: #666;
      font-size: 0.9rem;
      margin-bottom: 24px;
    }}
    .summary {{
      display: flex;
      gap: 16px;
      margin-bottom: 24px;
    }}
    .badge {{
      padding: 10px 20px;
      border-radius: 6px;
      font-weight: bold;
      font-size: 1rem;
      color: #fff;
    }}
    .badge-high   {{ background-color: #c0392b; }}
    .badge-medium {{ background-color: #d4a017; color: #333; }}
    .badge-low    {{ background-color: #27ae60; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      max-width: 800px;
      background: #fff;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
      border-radius: 6px;
      overflow: hidden;
    }}
    th {{
      background-color: #2c3e50;
      color: #fff;
      padding: 12px 16px;
      text-align: left;
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    td {{
      padding: 11px 16px;
      font-size: 0.95rem;
      border-bottom: 1px solid #e0e0e0;
    }}
    tr.high   {{ background-color: #fdecea; }}
    tr.medium {{ background-color: #fef9e7; }}
    tr.low    {{ background-color: #eafaf1; }}
    tr:last-child td {{ border-bottom: none; }}
    .risk-label {{
      font-weight: bold;
      padding: 3px 10px;
      border-radius: 4px;
      font-size: 0.85rem;
    }}
    .risk-HIGH   {{ background-color: #c0392b; color: #fff; }}
    .risk-MEDIUM {{ background-color: #d4a017; color: #333; }}
    .risk-LOW    {{ background-color: #27ae60; color: #fff; }}
  </style>
</head>
<body>
  <h1>Defect Prediction Report</h1>
  <p class="meta">Generated: {metadata['generated_at']} &nbsp;|&nbsp; {metadata['total_modules']} modules analysed</p>

  <div class="summary">
    <div class="badge badge-high">{metadata['high_risk']} HIGH</div>
    <div class="badge badge-medium">{metadata['medium_risk']} MEDIUM</div>
    <div class="badge badge-low">{metadata['low_risk']} LOW</div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Module</th>
        <th>Bug Score</th>
        <th>Change Score</th>
        <th>Risk Score</th>
        <th>Risk Level</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  HTML report saved -> {output_path}")


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


def _build_html_rows(results: list[dict]) -> str:
    """Build the HTML table rows, one per module."""
    rows = []
    for r in results:
        level = r["risk_level"]
        rows.append(f"""      <tr class="{level.lower()}">
        <td>{r['module']}</td>
        <td>{r['bug_score']:.2f}</td>
        <td>{r['change_score']:.2f}</td>
        <td>{r['risk_score']:.2f}</td>
        <td><span class="risk-label risk-{level}">{level}</span></td>
      </tr>""")
    return "\n".join(rows)


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
