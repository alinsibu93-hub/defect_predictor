# test_loader.py
# Tests for loader.py — we test the happy path and the most important error cases.

import sys
import os
import tempfile
import pytest
from datetime import datetime

# Allow imports from the project root and src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.loader import load_bugs, load_changes


# ---------------------------------------------------------------------------
# Helpers — write a temporary CSV file for each test
# ---------------------------------------------------------------------------

def write_temp_csv(content: str) -> str:
    """Write content to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# load_bugs — happy path
# ---------------------------------------------------------------------------

def test_load_bugs_returns_correct_number_of_records():
    csv_content = (
        "bug_id,module,severity,reported_date,status\n"
        "BUG-001,auth,high,2024-01-05,closed\n"
        "BUG-002,payment,critical,2024-02-10,open\n"
    )
    path = write_temp_csv(csv_content)
    bugs = load_bugs(path)
    assert len(bugs) == 2


def test_load_bugs_parses_fields_correctly():
    csv_content = (
        "bug_id,module,severity,reported_date,status\n"
        "BUG-001,auth,high,2024-01-05,closed\n"
    )
    path = write_temp_csv(csv_content)
    bug = load_bugs(path)[0]

    assert bug["bug_id"]        == "BUG-001"
    assert bug["module"]        == "auth"
    assert bug["severity"]      == "high"
    assert bug["status"]        == "closed"
    assert bug["reported_date"] == datetime(2024, 1, 5)


# ---------------------------------------------------------------------------
# load_bugs — error cases
# ---------------------------------------------------------------------------

def test_load_bugs_raises_if_file_missing():
    with pytest.raises(FileNotFoundError):
        load_bugs("/nonexistent/path/bugs.csv")


def test_load_bugs_raises_on_unknown_severity():
    csv_content = (
        "bug_id,module,severity,reported_date,status\n"
        "BUG-001,auth,extreme,2024-01-05,closed\n"  # 'extreme' is not valid
    )
    path = write_temp_csv(csv_content)
    with pytest.raises(ValueError, match="unknown severity"):
        load_bugs(path)


def test_load_bugs_raises_on_bad_date_format():
    csv_content = (
        "bug_id,module,severity,reported_date,status\n"
        "BUG-001,auth,high,05-01-2024,closed\n"  # wrong format
    )
    path = write_temp_csv(csv_content)
    with pytest.raises(ValueError, match="invalid date"):
        load_bugs(path)


def test_load_bugs_raises_on_missing_column():
    csv_content = (
        "bug_id,module,severity,reported_date\n"  # 'status' column missing
        "BUG-001,auth,high,2024-01-05\n"
    )
    path = write_temp_csv(csv_content)
    with pytest.raises(ValueError, match="Missing columns"):
        load_bugs(path)


# ---------------------------------------------------------------------------
# load_changes — happy path
# ---------------------------------------------------------------------------

def test_load_changes_returns_correct_number_of_records():
    csv_content = (
        "change_id,module,lines_changed,change_date,author\n"
        "CHG-001,auth,120,2024-01-03,alice\n"
        "CHG-002,payment,45,2024-01-10,bob\n"
        "CHG-003,cart,300,2024-02-01,carol\n"
    )
    path = write_temp_csv(csv_content)
    changes = load_changes(path)
    assert len(changes) == 3


def test_load_changes_parses_lines_changed_as_int():
    csv_content = (
        "change_id,module,lines_changed,change_date,author\n"
        "CHG-001,auth,120,2024-01-03,alice\n"
    )
    path = write_temp_csv(csv_content)
    change = load_changes(path)[0]

    assert change["lines_changed"] == 120
    assert isinstance(change["lines_changed"], int)


def test_load_changes_raises_on_negative_lines():
    csv_content = (
        "change_id,module,lines_changed,change_date,author\n"
        "CHG-001,auth,-5,2024-01-03,alice\n"
    )
    path = write_temp_csv(csv_content)
    with pytest.raises(ValueError, match="positive number"):
        load_changes(path)
