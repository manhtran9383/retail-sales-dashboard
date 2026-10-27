"""Retail Sales Dashboard — Streamlit demo app.

Tabs:
  Overview       — KPIs + KPI tables (monthly revenue, top products, top country)
  Sales Trend    — monthly revenue + seasonality chart
  Customer Retention — repeat-purchase Kaplan-Meier curve
  Top Products   — ranked product revenue table
  Targeting      — revenue concentration (top-50 lift) + retention by country

Run:  streamlit run streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src import config as cfg
from src import impact as im
from src import survival as surv_mod
from src.clean import clean
from src.load_data import load_data

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide", page_icon="📊")

# ---------------- chart helper (mirrors src/dashboard_preview.py) ----------------
def _monthly_chart(monthly):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.bar(monthly.index, monthly.values, color="#9467bd")
    ax.set_ylabel("Revenue (£)")
    ax.set_title("Monthly Revenue", fontsize=11, fontweight="bold")
    return fig


def _season_chart(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tmp = df.copy()
    tmp["month_name"] = tmp["InvoiceDate"].dt.month_name()
    order = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    tmp["month_name"] = pd.Categorical(tmp["month_name"], categories=order, ordered=True)
    d = tmp.groupby("month_name", observed=True)["Revenue"].mean().reindex(order)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.bar(d.index, d.values, color="#9467bd")
    ax.set_ylabel("Avg revenue (£)")
    ax.set_title("Seasonality", fontsize=11, fontweight="bold")
    return fig


def _retention_chart(curve, rate):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(curve["days_after_first"], curve["repeat_rate_pct"], marker="o", color="#9467bd")
    ax.set_xlabel("Days after first purchase")
    ax.set_ylabel("Reactivated purchase rate (%)")
    ax.set_title(f"Repeat-purchase rate (overall {rate:.1f}%)", fontsize=11, fontweight="bold")
    return fig

DATASETS = cfg.DATASETS
DATASET_KEY = st.sidebar.selectbox("Dataset", list(cfg.DATASETS.keys()),
                                   format_func=lambda k: cfg.DATASETS[k]["display_name"])

# ---- load ----
df = clean(load_data(DATASET_KEY))
tabs = st.tabs(["Overview", "Sales Trend", "Customer Retention", "Top Products", "Targeting"])


def _tabs_if(cond, body):
    if cond:
        body()


# ---- Overview ----
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Revenue", f"£{df['Revenue'].sum():,.2f}")
        st.metric("Customers", f"{df['Customer ID'].nunique():,}")
        st.metric("Countries", f"{df['Country'].nunique()}")
    with col2:
        monthly = df.groupby(df["InvoiceDate"].dt.to_period("M").dt.to_timestamp())["Revenue"].sum()
        st.metric("Months covered", f"{monthly.shape[0]}")
        first, last = df["InvoiceDate"].min().date(), df["InvoiceDate"].max().date()
        st.metric("Date range", f"{first} → {last}")
        st.metric("Avg revenue / month", f"£{df['Revenue'].mean():,.2f}")

# ---- Sales Trend ----
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Monthly Revenue")
        monthly_rev = df.groupby(df["InvoiceDate"].dt.to_period("M").dt.to_timestamp())["Revenue"].sum()
        fig = _monthly_chart(monthly_rev)
        st.pyplot(fig, use_container_width=True)
    with c2:
        st.subheader("Seasonality")
        fig = _season_chart(df)
        st.pyplot(fig, use_container_width=True)

# ---- Customer Retention ----
with tabs[2]:
    st.subheader("Customer Repeat-Purchase (Kaplan-Meier)")
    curve, rate = surv_mod.retention_curve(df, repeat_days=30)
    fig = _retention_chart(curve, rate)
    st.pyplot(fig, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Repeat-purchase rate", f"{rate:.1f}%")
    with c2:
        st.metric("Customers", f"{df['Customer ID'].nunique():,}")

# ---- Top Products ----
with tabs[3]:
    st.subheader("Top Products by Revenue")
    top = im.trending_revenue(df, n=20)
    st.dataframe(top, use_container_width=True)


# ---- Targeting ----
with tabs[4]:
    st.subheader("Revenue Concentration (Top-50 Revenue %)")
    top50 = im.trending_revenue(df, n=50)
    top50_rev = float(top50["revenue"].sum())
    total_rev = float(df["Revenue"].sum())
    st.metric("Top-50 Revenue Share", f"{top50_rev/total_rev*100:.1f}% of £{total_rev:,.2f}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Retention by Country")
        ret = im.retention_table(df, repeat_days=30)
        st.dataframe(ret, use_container_width=True)
    with c2:
        st.subheader("Top Products (rank, revenue)")
        top10 = im.trending_revenue(df, n=10)
        st.dataframe(top10, use_container_width=True)
