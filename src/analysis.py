"""Retail Sales Dashboard — analysis modules."""
from __future__ import annotations

import pandas as pd

from .config import DATASETS


def load(df_raw: pd.DataFrame) -> pd.DataFrame:
    return df_raw.copy()


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly revenue trend."""
    tmp = df.copy()
    tmp["Month"] = tmp["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    out = (
        tmp.groupby("Month", as_index=False)["Revenue"]
        .sum()
        .rename(columns={"Revenue": "monthly_revenue"})
    )
    out["monthly_revenue"] = out["monthly_revenue"].round(2)
    out = out.sort_values("Month").reset_index(drop=True)
    out["MoM_pct"] = (out["monthly_revenue"].pct_change() * 100).round(1)
    return out


def top_n(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Top-N products by revenue, with description."""
    top = (
        df.groupby("StockCode")["Revenue"].sum()
        .sort_values(ascending=False).head(n).reset_index()
    )
    top = top.rename(columns={"StockCode": "StockCode", "Revenue": "revenue"})
    top["Revenue"] = top["revenue"].round(2)
    desc = df.groupby("StockCode")["Description"].first().to_dict()
    top["Description"] = top["StockCode"].map(desc)
    return top[["StockCode", "Description", "Revenue"]]


def top_n_by(df: pd.DataFrame, n: int, col: str) -> pd.DataFrame:
    return (
        df.groupby(col).agg(Revenue=("Revenue", "sum"))
        .sort_values("Revenue", ascending=False).head(n).reset_index()
    )


def sales_by_country(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby("Country")["Revenue"].sum().reset_index()
        .rename(columns={"Revenue": "revenue"})
    )
    out["Revenue"] = out["revenue"].round(2)
    return out.sort_values("Revenue", ascending=False).reset_index(drop=True)


def top_categories(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    # group by product description (proxy for category)
    return (
        df.groupby("Description")["Revenue"].sum()
        .sort_values(ascending=False).head(n).reset_index()
        .rename(columns={"Description": "Category", "Revenue": "Revenue"})
    )


def monthly_pattern(df: pd.DataFrame) -> pd.DataFrame:
    """Average revenue share per month-of-year (seasonality)."""
    tmp = df.copy()
    tmp["month_name"] = tmp["InvoiceDate"].dt.month_name()
    out = tmp.groupby("month_name", observed=True)["Revenue"].mean().reset_index().rename(columns={"Revenue": "avg_revenue"})
    out["avg_revenue"] = out["avg_revenue"].round(2)
    order = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
    out["month_name"] = pd.Categorical(out["month_name"], categories=order, ordered=True)
    return out.sort_values("month_name").reset_index(drop=True)
