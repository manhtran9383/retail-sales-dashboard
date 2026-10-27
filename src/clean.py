"""Retail Sales Dashboard — cleaning."""
from __future__ import annotations

import pandas as pd

# Retail-specific: keep only sales with a known customer, non-cancelled invoice,
# positive quantity and positive unit price. Cancelled invoices are excluded so
# revenue reflects money actually received (matches churn "drop constant cols").
DROP_COLS = []


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # keep only rows with a known customer (anonymous transactions excluded)
    df = df[df["Customer ID"].notna()].copy()
    df["Customer ID"] = df["Customer ID"].astype(int)
    # exclude cancelled invoices (Invoice no starts with 'C')
    df["Invoice"] = df["Invoice"].astype(str)
    df = df[~df["Invoice"].str.startswith("C")].copy()
    # drop odd prices / returns (Quantity <= 0 or Price <= 0)
    df = df[(df["Quantity"] > 0) & (df["Price"] > 0)].copy()
    # Sales volume
    df["Revenue"] = (df["Quantity"] * df["Price"]).round(2)
    # Date helpers for cohort & monthly analysis
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["InvoiceYearMonth"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    df["customer_first_month"] = (
        df.groupby("Customer ID")["InvoiceDate"].transform("min").dt.to_period("M").astype(str)
    )
    cols = [
        "Invoice", "StockCode", "Description", "Quantity", "InvoiceDate",
        "Price", "Customer ID", "Country", "Revenue",
        "InvoiceMonth", "InvoiceYearMonth",
    ]
    df = df[cols].copy()
    df = df.sort_values("InvoiceDate", kind="mergesort").reset_index(drop=True)
    return df


def check(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "customers": int(df["Customer ID"].nunique()),
        "countries": int(df["Country"].nunique()),
        "date_min": str(df["InvoiceDate"].min().date()),
        "date_max": str(df["InvoiceDate"].max().date()),
        "total_revenue": round(float(df["Revenue"].sum()), 2),
    }
