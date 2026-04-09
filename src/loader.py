# loader.py
# Responsibility: read input CSV files and return validated, clean Python data.
# Nothing here calculates risk — it only loads and checks the raw data.

import csv
from datetime import datetime
from pathlib import Path

import config

# The date format we expect in both CSV files.
DATE_FORMAT = "%Y-%m-%d"

# Valid values for the severity and status fields.
VALID_SEVERITIES = set(config.SEVERITY_WEIGHTS.keys())
VALID_STATUSES   = {"open", "closed"}


def load_bugs(filepath: str) -> list[dict]:
    """
    Read bugs.csv and return a list of bug records.

    Each record is a plain dict with these keys:
        bug_id        (str)
        module        (str)
        severity      (str)  — validated against VALID_SEVERITIES
        reported_date (datetime)
        status        (str)  — validated against VALID_STATUSES

    Raises:
        FileNotFoundError  — if the file does not exist
        ValueError         — if a row has missing or invalid data
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Bugs file not found: {filepath}")

    bugs = []
    required_columns = {"bug_id", "module", "severity", "reported_date", "status"}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Check that the file has all the columns we need.
        _validate_columns(reader.fieldnames, required_columns, filepath)

        for line_number, row in enumerate(reader, start=2):  # start=2 because row 1 is the header
            bug = _parse_bug_row(row, line_number)
            bugs.append(bug)

    return bugs


def load_changes(filepath: str) -> list[dict]:
    """
    Read changes.csv and return a list of change records.

    Each record is a plain dict with these keys:
        change_id    (str)
        module       (str)
        lines_changed (int)  — must be a positive integer
        change_date  (datetime)
        author       (str)

    Raises:
        FileNotFoundError  — if the file does not exist
        ValueError         — if a row has missing or invalid data
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Changes file not found: {filepath}")

    changes = []
    required_columns = {"change_id", "module", "lines_changed", "change_date", "author"}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        _validate_columns(reader.fieldnames, required_columns, filepath)

        for line_number, row in enumerate(reader, start=2):
            change = _parse_change_row(row, line_number)
            changes.append(change)

    return changes


# ---------------------------------------------------------------------------
# Private helpers — prefixed with _ to signal "internal use only"
# ---------------------------------------------------------------------------

def _validate_columns(
    actual_columns: list[str] | None,
    required_columns: set[str],
    filepath: str,
) -> None:
    """Raise ValueError if any required column is missing from the CSV header."""
    if actual_columns is None:
        raise ValueError(f"File appears to be empty: {filepath}")

    actual = set(actual_columns)
    missing = required_columns - actual
    if missing:
        raise ValueError(
            f"Missing columns in {filepath}: {sorted(missing)}"
        )


def _parse_bug_row(row: dict, line_number: int) -> dict:
    """Parse and validate one row from bugs.csv."""
    bug_id   = _require_field(row, "bug_id",   line_number)
    module   = _require_field(row, "module",   line_number)
    severity = _require_field(row, "severity", line_number).lower()
    status   = _require_field(row, "status",   line_number).lower()
    date_str = _require_field(row, "reported_date", line_number)

    if severity not in VALID_SEVERITIES:
        raise ValueError(
            f"Line {line_number}: unknown severity '{severity}'. "
            f"Expected one of {sorted(VALID_SEVERITIES)}."
        )

    if status not in VALID_STATUSES:
        raise ValueError(
            f"Line {line_number}: unknown status '{status}'. "
            f"Expected one of {sorted(VALID_STATUSES)}."
        )

    reported_date = _parse_date(date_str, line_number, "reported_date")

    return {
        "bug_id":        bug_id,
        "module":        module,
        "severity":      severity,
        "reported_date": reported_date,
        "status":        status,
    }


def _parse_change_row(row: dict, line_number: int) -> dict:
    """Parse and validate one row from changes.csv."""
    change_id = _require_field(row, "change_id",    line_number)
    module    = _require_field(row, "module",        line_number)
    author    = _require_field(row, "author",        line_number)
    date_str  = _require_field(row, "change_date",   line_number)
    lines_str = _require_field(row, "lines_changed", line_number)

    lines_changed = _parse_positive_int(lines_str, line_number, "lines_changed")
    change_date   = _parse_date(date_str, line_number, "change_date")

    return {
        "change_id":    change_id,
        "module":       module,
        "lines_changed": lines_changed,
        "change_date":  change_date,
        "author":       author,
    }


def _require_field(row: dict, field: str, line_number: int) -> str:
    """Return the field value stripped of whitespace, or raise if it is empty."""
    value = row.get(field, "").strip()
    if not value:
        raise ValueError(f"Line {line_number}: field '{field}' is missing or empty.")
    return value


def _parse_date(value: str, line_number: int, field_name: str) -> datetime:
    """Parse a date string into a datetime object."""
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValueError(
            f"Line {line_number}: field '{field_name}' has invalid date '{value}'. "
            f"Expected format: YYYY-MM-DD."
        )


def _parse_positive_int(value: str, line_number: int, field_name: str) -> int:
    """Parse a string into a positive integer."""
    try:
        number = int(value)
    except ValueError:
        raise ValueError(
            f"Line {line_number}: field '{field_name}' must be an integer, got '{value}'."
        )
    if number <= 0:
        raise ValueError(
            f"Line {line_number}: field '{field_name}' must be a positive number, got {number}."
        )
    return number
