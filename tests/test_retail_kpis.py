"""Golden tests for the retail portfolio.

Every headline number is asserted against a value computed independently from
the source CSV. If the analysis code drifts, `python -m pytest tests -q` fails.
"""
from __future__ import annotations

import pandas as pd
import pytest

from src.clean import clean
from src.load_data import load_data

# Independently computed from data/raw/retail_sales.csv (12 000 rows).
EXPECTED = {
    "rows": 12000,
    "customers": 2836,
    "countries": 32,
    "total_revenue": 253814.99,
    "repeat_rate_30d_pct": 42.5,
    "top10_revenue": 28118.91,
    "top_product_revenue": 4542.45,
    "uk_revenue": 206339.09,
    "lifetime_median_days": 2,
    "lifetime_mean_days": 94.4,
}


def _compute() -> dict:
    df = clean(load_data("retail"))
    g = df.groupby("Customer ID")["InvoiceDate"]
    first = g.min().rename("first_purchase")
    second = g.agg(lambda s: s.iloc[1] if len(s) > 1 else pd.NaT).rename("second_purchase")
    joined = pd.concat([first, second], axis=1).reset_index()
    joined = joined[joined["second_purchase"].notna()].copy()
    joined["repeat_days"] = (joined["second_purchase"] - joined["first_purchase"]).dt.days
    top10 = df.groupby("StockCode")["Revenue"].sum().nlargest(10).sum()
    top_product_rev = df.groupby("StockCode")["Revenue"].sum().idxmax()
    top_product_rev_value = df.groupby("StockCode")["Revenue"].sum().max()
    uk_rev = df.loc[df["Country"] == "United Kingdom", "Revenue"].sum()
    first_purchase = df.groupby("Customer ID")["InvoiceDate"].min()
    last_purchase = df.groupby("Customer ID")["InvoiceDate"].max()
    customer_lifetime = (last_purchase - first_purchase).dt.days
    return {
        "rows": len(df),
        "customers": df["Customer ID"].nunique(),
        "countries": df["Country"].nunique(),
        "total_revenue": round(float(df["Revenue"].sum()), 2),
        "repeat_rate_30d_pct": round(
            float(joined["repeat_days"].le(30).sum()) / df["Customer ID"].nunique() * 100, 1
        ),
        "top10_revenue": round(float(top10), 2),
        "top_product_revenue": round(float(top_product_rev_value), 2),
        "uk_revenue": round(float(uk_rev), 2),
        "lifetime_median_days": int(customer_lifetime.median()),
        "lifetime_mean_days": round(float(customer_lifetime.mean()), 1),
    }


@pytest.mark.parametrize("key,expected", [(k, v) for k, v in EXPECTED.items()])
def test_goldens_match(key, expected):
    actual = _compute()[key]
    assert actual == expected, f"{key}: expected {expected}, got {actual}"
