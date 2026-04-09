# test_reporter.py
# Tests for reporter.py.
#
# Strategy:
#   - print_cli_report  → capture stdout and assert on its content
#   - write_json_report → write to a temp file, read it back, assert on structure
#   - write_html_report → write to a temp file, read raw HTML, assert on content

import sys
import os
import io
import json
import tempfile
import contextlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.reporter import print_cli_report, write_json_report, write_html_report


# ---------------------------------------------------------------------------
# Shared fixture — a small realistic result set used across multiple tests
# ---------------------------------------------------------------------------

SAMPLE_RESULTS = [
    {
        "module":       "auth",
        "bug_score":    8.0,
        "change_score": 10.0,
        "risk_score":   18.0,
        "risk_level":   "HIGH",
    },
    {
        "module":       "cart",
        "bug_score":    4.0,
        "change_score": 7.0,
        "risk_score":   11.0,
        "risk_level":   "MEDIUM",
    },
    {
        "module":       "reporting",
        "bug_score":    1.0,
        "change_score": 3.0,
        "risk_score":   4.0,
        "risk_level":   "LOW",
    },
]


def capture_cli_output(results: list[dict]) -> str:
    """Run print_cli_report and return everything it printed as a string."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        print_cli_report(results)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# print_cli_report — content checks
# ---------------------------------------------------------------------------

def test_cli_report_contains_all_module_names():
    output = capture_cli_output(SAMPLE_RESULTS)
    assert "auth"      in output
    assert "cart"      in output
    assert "reporting" in output


def test_cli_report_contains_risk_level_labels():
    output = capture_cli_output(SAMPLE_RESULTS)
    assert "HIGH"   in output
    assert "MEDIUM" in output
    assert "LOW"    in output


def test_cli_report_contains_header_row():
    output = capture_cli_output(SAMPLE_RESULTS)
    assert "Module"       in output
    assert "Bug Score"    in output
    assert "Change Score" in output
    assert "Risk Score"   in output
    assert "Risk Level"   in output


def test_cli_report_contains_summary_line():
    output = capture_cli_output(SAMPLE_RESULTS)
    # Summary line should show counts for each level.
    assert "Summary" in output
    assert "HIGH"    in output
    assert "MEDIUM"  in output
    assert "LOW"     in output


def test_cli_report_empty_input_does_not_crash():
    # Should print a graceful message, not raise an exception.
    output = capture_cli_output([])
    assert "No results" in output


# ---------------------------------------------------------------------------
# write_json_report — file structure checks
# ---------------------------------------------------------------------------

def _write_to_temp(results: list[dict]) -> dict:
    """Write a JSON report to a temp file and return the parsed contents."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = f.name

    # Redirect stdout so the "saved ->" message doesn't pollute test output.
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        write_json_report(results, temp_path)

    with open(temp_path, encoding="utf-8") as f:
        return json.load(f)


def test_json_report_has_metadata_and_modules_keys():
    data = _write_to_temp(SAMPLE_RESULTS)
    assert "metadata" in data
    assert "modules"  in data


def test_json_report_metadata_contains_expected_fields():
    metadata = _write_to_temp(SAMPLE_RESULTS)["metadata"]
    assert "generated_at"  in metadata
    assert "total_modules" in metadata
    assert "high_risk"     in metadata
    assert "medium_risk"   in metadata
    assert "low_risk"      in metadata


def test_json_report_metadata_counts_are_correct():
    metadata = _write_to_temp(SAMPLE_RESULTS)["metadata"]
    assert metadata["total_modules"] == 3
    assert metadata["high_risk"]     == 1
    assert metadata["medium_risk"]   == 1
    assert metadata["low_risk"]      == 1


def test_json_report_modules_list_length_matches_input():
    data = _write_to_temp(SAMPLE_RESULTS)
    assert len(data["modules"]) == len(SAMPLE_RESULTS)


def test_json_report_module_records_contain_all_fields():
    modules = _write_to_temp(SAMPLE_RESULTS)["modules"]
    for record in modules:
        assert "module"       in record
        assert "bug_score"    in record
        assert "change_score" in record
        assert "risk_score"   in record
        assert "risk_level"   in record


def test_json_report_creates_output_directory_if_missing():
    # write_json_report should create the parent directory automatically.
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_path = os.path.join(tmpdir, "nested", "subdir", "report.json")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            write_json_report(SAMPLE_RESULTS, nested_path)
        assert os.path.exists(nested_path)


def test_json_report_empty_input_writes_valid_json():
    data = _write_to_temp([])
    assert data["modules"] == []
    assert data["metadata"]["total_modules"] == 0


# ---------------------------------------------------------------------------
# write_html_report — content checks
# ---------------------------------------------------------------------------

def _write_html_to_temp(results: list[dict]) -> str:
    """Write an HTML report to a temp file and return the raw HTML string."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        temp_path = f.name

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        write_html_report(results, temp_path)

    with open(temp_path, encoding="utf-8") as f:
        return f.read()


def test_html_report_is_valid_html_document():
    html = _write_html_to_temp(SAMPLE_RESULTS)
    assert "<!DOCTYPE html>" in html
    assert "<html"           in html
    assert "</html>"         in html


def test_html_report_contains_all_module_names():
    html = _write_html_to_temp(SAMPLE_RESULTS)
    assert "auth"      in html
    assert "cart"      in html
    assert "reporting" in html


def test_html_report_contains_risk_level_labels():
    html = _write_html_to_temp(SAMPLE_RESULTS)
    assert "HIGH"   in html
    assert "MEDIUM" in html
    assert "LOW"    in html


def test_html_report_applies_colour_classes_per_risk_level():
    # Each risk level should have its own CSS row class and label class.
    html = _write_html_to_temp(SAMPLE_RESULTS)
    assert 'class="high"'        in html
    assert 'class="medium"'      in html
    assert 'class="low"'         in html
    assert 'risk-HIGH'           in html
    assert 'risk-MEDIUM'         in html
    assert 'risk-LOW'            in html


def test_html_report_contains_table_headers():
    html = _write_html_to_temp(SAMPLE_RESULTS)
    assert "Module"       in html
    assert "Bug Score"    in html
    assert "Change Score" in html
    assert "Risk Score"   in html
    assert "Risk Level"   in html


def test_html_report_empty_input_produces_valid_file():
    html = _write_html_to_temp([])
    assert "<!DOCTYPE html>" in html
    assert "<tbody>"         in html
