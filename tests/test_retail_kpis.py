"""Golden tests for the retail portfolio.

Every headline number is asserted against a value computed independently from
the source CSV. If the analysis code drifts, `python -m pytest tests -q` fails.
"""
from __future__ import annotations

import pandas as pd
import pytest

from src.clean import clean
from src.load_data import load_data

# Independently computed from data/raw/REtail_Sales.csv (12 000 rows).
EXPECTED = {
    "rows": 12000,
    "customers": 2836,
    "countries": 32,
    "total_revenue": 253814.99,
    "repeat_rate_30d_pct": 42.5,
}


def _compute() -> dict:
    df = clean(load_data("retail"))
    g = df.groupby("Customer ID")["InvoiceDate"]
    first = g.min().rename("first_purchase")
    second = g.agg(lambda s: s.iloc[1] if len(s) > 1 else pd.NaT).rename("second_purchase")
    joined = pd.concat([first, second], axis=1).reset_index()
    joined = joined[joined["second_purchase"].notna()].copy()
    joined["repeat_days"] = (joined["second_purchase"] - joined["first_purchase"]).dt.days
    return {
        "rows": len(df),
        "customers": df["Customer ID"].nunique(),
        "countries": df["Country"].nunique(),
        "total_revenue": round(float(df["Revenue"].sum()), 2),
        "repeat_rate_30d_pct": round(
            float(joined["repeat_days"].le(30).sum() / df["Customer ID"].nunique()) * 100, 1
        ),
    }


@pytest.mark.parametrize("key,expected", [(k, v) for k, v in EXPECTED.items()])
def test_goldens_match(key, expected):
    actual = _compute()[key]
    assert actual == expected, f"{key}: expected {expected}, got {actual}"
