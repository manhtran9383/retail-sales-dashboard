"""Unit tests for src/analysis — monthly / top-products / country."""
from pathlib import Path
import pandas as pd
import pytest

from src.analysis import monthly_revenue, sales_by_country, top_n

RAW = Path(__file__).parent.parent / "data" / "raw" / "REtail_Sales.csv"


def _read_raw():
    return pd.read_csv(RAW, parse_dates=["InvoiceDate"])


def test_monthly_revenue_shape_and_total():
    df = _read_raw()
    out = monthly_revenue(df)
    assert len(out) == 13  # Dec-2010 through Dec-2011 (truncated)
    assert list(out.columns) == ["Month", "monthly_revenue", "MoM_pct"]
    assert out["monthly_revenue"].sum() == pytest.approx(253814.99, abs=0.01)
    assert out["Month"].iloc[0] == pd.Timestamp("2010-12-01")


def test_top_n_returns_top_product():
    df = _read_raw()
    out = top_n(df, n=10)
    assert len(out) <= 10
    assert list(out.columns) == ["StockCode", "Description", "Revenue"]
    assert out.loc[out["Revenue"].idxmax(), "StockCode"] == "22423"


def test_sales_by_country_top_is_uk():
    df = _read_raw()
    out = sales_by_country(df)
    assert len(out) >= 32
    assert out.iloc[0]["Country"] == "United Kingdom"
    assert out.iloc[0]["Revenue"] == pytest.approx(206339.09, abs=0.01)
