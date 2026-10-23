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


def retention_curve(df: pd.DataFrame, repeat_days: int = 30) -> tuple[pd.DataFrame, float]:
    """Repeat-purchase retention: fraction with >=2 purchases in >=repeat_days.

    Returns (curve_df, retention_rate).
    """
    tmp = df.copy()
    first = tmp.groupby("Customer ID")["InvoiceDate"].min().rename("first_purchase")
    second = tmp.groupby("Customer ID")["InvoiceDate"].nth(1).rename("second_purchase")
    joined = pd.concat([first, second], axis=1).reset_index()
    joined["repeat_days"] = (joined["second_purchase"] - joined["first_purchase"]).dt.days
    joined = joined[joined["second_purchase"].notna()].copy()
    joined["repeat"] = joined["repeat_days"] <= repeat_days
    rate = float(joined["repeat"].mean())
    curve = joined[["repeat_days", "repeat"]].sort_values("repeat_days").reset_index(drop=True)
    return curve, rate


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
