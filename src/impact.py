"""Retail Sales Dashboard — impact / business impact."""
from __future__ import annotations

import pandas as pd

from .config import DATASETS
from .clean import clean


def load(df_raw: pd.DataFrame) -> pd.DataFrame:
    return df_raw.copy()


def trending_revenue(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Top-N products by revenue."""
    top = df.groupby("StockCode")["Revenue"].sum().sort_values(ascending=False).head(n)
    return top.reset_index().rename(columns={"StockCode": "StockCode", "Revenue": "revenue"})


def retention_table(df: pd.DataFrame, repeat_days: int = 30) -> pd.DataFrame:
    """Repeat-rate by country (retention market mix)."""
    tmp = df.copy()
    tmp["days_since_first"] = (
        tmp.groupby("Customer ID")["InvoiceDate"].transform("max")
        - tmp.groupby("Customer ID")["InvoiceDate"].transform("min")
    ).dt.days
    tmp["repeat"] = tmp["days_since_first"] >= repeat_days
    out = (
        tmp.groupby("Country")["repeat"].mean().reset_index()
        .rename(columns={"repeat": "repeat_purchase_rate"})
    )
    out["repeat_purchase_rate"] = (out["repeat_purchase_rate"] * 100).round(1)
    return out.sort_values("repeat_purchase_rate", ascending=False).reset_index(drop=True)
