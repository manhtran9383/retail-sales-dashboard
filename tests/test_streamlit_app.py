"""Retail Sales Dashboard — Smoke test for the Streamlit demo.

Headless test using streamlit.testing.v1.AppTest. Runs the app for the
retail dataset and asserts it executes end-to-end without exception.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _run_app(dataset: str = "retail"):
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=300)
    at.run()
    if at.exception:
        for e in at.exception:
            print(e.value)
    return at


def test_app_runs_without_exception():
    at = _run_app()
    assert not at.exception, "streamlit_app.py raised an exception"


def test_tabs_present():
    at = _run_app()
    labels = {t.label for t in at.tabs}
    for wanted in ("Overview", "Sales Trend", "Customer Retention", "Top Products", "Targeting"):
        assert any(wanted in l for l in labels), f"missing tab '{wanted}'"


def test_no_runtime_errors():
    at = _run_app()
    assert at.error == [], f"app raised {len(at.error)} errors"
