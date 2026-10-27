"""Unit tests for src/clean — cleaning rules (P2)."""
from pathlib import Path

import pandas as pd

from src.clean import clean

RAW = Path(__file__).parent.parent / "data" / "raw" / "retail_sales.csv"


def _read_raw():
    return pd.read_csv(RAW, parse_dates=["InvoiceDate"])


def test_clean_keeps_expected_columns():
    out = clean(_read_raw())
    expect = {
        "Invoice", "StockCode", "Description", "Quantity", "InvoiceDate",
        "Price", "Customer ID", "Country", "Revenue",
        "InvoiceMonth", "InvoiceYearMonth",
    }
    assert expect <= set(out.columns)


def test_clean_drops_cancelled_invoices_and_anonymous():
    rows = [
        {"Invoice": "536365", "StockCode": "85048", "Description": "A",
         "Quantity": 1, "InvoiceDate": pd.Timestamp("2010-12-01"),
         "Price": 10.0, "Customer ID": 1, "Country": "UK", "Revenue": 10.0},
        {"Invoice": "C536365", "StockCode": "85048", "Description": "B",
         "Quantity": 1, "InvoiceDate": pd.Timestamp("2010-12-02"),
         "Price": 10.0, "Customer ID": 1, "Country": "UK", "Revenue": 10.0},
        {"Invoice": "536365", "StockCode": "85048", "Description": "A",
         "Quantity": 1, "InvoiceDate": pd.Timestamp("2010-12-03"),
         "Price": 10.0, "Customer ID": None, "Country": "UK", "Revenue": 10.0},
    ]
    out = clean(pd.DataFrame(rows))
    assert len(out) == 1
    assert out.iloc[0]["Invoice"] == "536365"
    assert pd.isna(out.iloc[0]["Customer ID"]) is False


def test_clean_drops_non_positive_qty_or_price():
    rows = [
        {"Invoice": "536365", "StockCode": "85048", "Description": "A",
         "Quantity": 1, "InvoiceDate": pd.Timestamp("2010-12-01"),
         "Price": 10.0, "Customer ID": 1, "Country": "UK", "Revenue": 10.0},
        {"Invoice": "536365", "StockCode": "85048", "Description": "A",
         "Quantity": 0, "InvoiceDate": pd.Timestamp("2010-12-02"),
         "Price": 10.0, "Customer ID": 1, "Country": "UK", "Revenue": 0.0},
        {"Invoice": "536365", "StockCode": "85048", "Description": "A",
         "Quantity": 1, "InvoiceDate": pd.Timestamp("2010-12-03"),
         "Price": -1.0, "Customer ID": 1, "Country": "UK", "Revenue": -1.0},
    ]
    out = clean(pd.DataFrame(rows))
    assert len(out) == 1
    assert out.iloc[0]["Quantity"] > 0
    assert out.iloc[0]["Price"] > 0


def test_clean_computes_revenue_round_2():
    df = _read_raw()
    out = clean(df)
    raw = df[["InvoiceDate", "Quantity", "Price"]].copy()
    raw["Revenue"] = (raw["Quantity"] * raw["Price"]).round(2)
    out = out.sort_values("InvoiceDate", kind="mergesort").reset_index(drop=True)
    raw = raw.sort_values("InvoiceDate", kind="mergesort").reset_index(drop=True)
    pd.testing.assert_series_equal(
        out["Revenue"].reset_index(drop=True),
        raw["Revenue"].reset_index(drop=True),
        check_names=False,
    )


def test_clean_adds_date_helpers():
    out = clean(_read_raw())
    assert "InvoiceMonth" in out.columns
    assert "InvoiceYearMonth" in out.columns
    assert out["InvoiceMonth"].notna().all()
    assert out["InvoiceYearMonth"].notna().all()
