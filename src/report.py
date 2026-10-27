"""Retail Sales Dashboard — report generation (figures + Excel + Power BI)."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from .config import FIGURES_DIR, REPORTS_DIR, DATASETS
from . import analysis as ar
from .survival import retention_curve as surv_curve

FIGSIZE = (7.2, 3.6)
COLORS = {"telco": "#1f77b4", "bank": "#d62728", "hr": "#2ca02c",
          "retail": "#9467bd", "accent": "#8c564b"}
plt.rcParams.update({"font.size": 9, "axes.grid": False})


def _style(ax, title):
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.tick_params(axis="x", rotation=35)


def figure_monthly_revenue(df: pd.DataFrame, out_dir: Path):
    tmp = df.copy()
    tmp["Month"] = tmp["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    d = tmp.groupby("Month")["Revenue"].sum().sort_index()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(d.index, d.values, color=COLORS["retail"])
    ax.set_ylabel("Revenue (£)")
    _style(ax, "Retail monthly revenue (UK online retail)")
    fig.tight_layout(); fig.savefig(out_dir / "Monthly_revenue_trend.png", dpi=150)
    plt.close(fig)


def figure_top_products(df: pd.DataFrame, out_dir: Path):
    top = ar.top_n(df, n=12).head(10)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.barh(top["StockCode"][::-1], top["Revenue"][::-1], color=COLORS["accent"])
    ax.set_xlabel("Revenue (£)")
    _style(ax, "Top products by revenue")
    fig.tight_layout(); fig.savefig(out_dir / "Top_products.png", dpi=150)
    plt.close(fig)


def figure_sales_by_country(df: pd.DataFrame, out_dir: Path):
    d = ar.sales_by_country(df).head(10)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(d["Country"], d["Revenue"], color=COLORS["retail"])
    ax.set_ylabel("Revenue (£)")
    _style(ax, "Top countries by revenue")
    fig.tight_layout(); fig.savefig(out_dir / "Sales_by_region.png", dpi=150)
    plt.close(fig)


def figure_seasonality(df: pd.DataFrame, out_dir: Path):
    d = ar.monthly_pattern(df)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(d["month_name"], d["avg_revenue"], color=COLORS["retail"])
    ax.set_ylabel("Avg revenue (£)")
    _style(ax, "Seasonality (average revenue by month)")
    fig.tight_layout(); fig.savefig(out_dir / "Seasonality.png", dpi=150)
    plt.close(fig)


def figure_retention(df: pd.DataFrame, out_dir: Path):
    surv, rate = surv_curve(df, repeat_days=30)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(surv["days_after_first"], surv["repeat_rate_pct"], marker="o", color=COLORS["retail"])
    ax.set_xlabel("Days after first purchase")
    ax.set_ylabel("Reactivated purchase rate (%)")
    _style(ax, "Customer repeat-purchase rate (Kaplan-Meier)")
    fig.tight_layout(); fig.savefig(out_dir / "Customer_retention.png", dpi=150)
    plt.close(fig)


def figure_best_predictors(df: pd.DataFrame, out_dir: Path):
    top = ar.top_n(df, n=10)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.barh(top["StockCode"][::-1], top["Revenue"].tail(10)[::-1], color=COLORS["retail"])
    ax.set_xlabel("Revenue (£)")
    _style(ax, "Top-10 product revenue (sales drivers)")
    fig.tight_layout(); fig.savefig(out_dir / "Best_predictors.png", dpi=150)
    plt.close(fig)


def _make_figures(df: pd.DataFrame, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    figure_monthly_revenue(df, out_dir)
    figure_top_products(df, out_dir)
    figure_sales_by_country(df, out_dir)
    figure_seasonality(df, out_dir)
    figure_retention(df, out_dir)
    figure_best_predictors(df, out_dir)
    return sorted(out_dir.glob("*.png"))


def _retention_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["days_since_first"] = (d.groupby("Customer ID")["InvoiceDate"].transform("max")
                            - d.groupby("Customer ID")["InvoiceDate"].transform("min")).dt.days
    return d.groupby("Customer ID")["days_since_first"].mean().reset_index().rename(columns={"days_since_first": "avg_days_active"})


def _monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly revenue, one row per calendar month (month grain)."""
    return (
        df.groupby(df["InvoiceDate"].dt.to_period("M").dt.to_timestamp())["Revenue"]
        .sum()
        .reset_index()
        .rename(columns={"InvoiceDate": "Month"})
    )


def make_excel(df: pd.DataFrame, out_path: Path):
    surv, rate = surv_curve(df, repeat_days=30)
    with pd.ExcelWriter(out_path, engine="openpyxl") as xl:
        ar.top_n(df, n=20).to_excel(xl, sheet_name="Top_Products", index=False)
        _retention_summary_table(df).to_excel(xl, sheet_name="Customer_Retention", index=False)
        surv.to_excel(xl, sheet_name="Survival_Retention", index=False)
        (df.groupby("Customer ID")["InvoiceDate"].agg(["min", "max"])
         .assign(lifetime_days=lambda x: (x["max"] - x["min"]).dt.days)
         .to_excel(xl, sheet_name="Customer_Cohorts", index=False))
        _monthly_revenue(df).to_excel(xl, sheet_name="Monthly_Revenue", index=False)
        sales = df.copy()
        sales["Month"] = sales["InvoiceDate"].dt.to_period("M").astype(str)
        sales[["Invoice", "StockCode", "Description", "Quantity", "Price",
               "Customer ID", "Country", "Revenue", "Month"]].to_excel(
            xl, sheet_name="Sales", index=False)
        ar.monthly_pattern(df).to_excel(xl, sheet_name="Seasonality", index=False)
        (pd.DataFrame([{"dataset": "retail",
                        "total_revenue": round(df["Revenue"].sum(), 2),
                        "customers": df["Customer ID"].nunique()}])
         .to_excel(xl, sheet_name="KPI_Summary", index=False))


def make_powerbi_pack(df: pd.DataFrame, out_dir: Path):
    pack = out_dir / "powerbi" / "data" / "retail"
    pack.mkdir(parents=True, exist_ok=True)
    (df.groupby("StockCode").agg(ProductName=("Description", "first"),
        total_revenue=("Revenue", "sum"), total_qty=("Quantity", "sum"))
     .reset_index().to_csv(pack / "dim_product.csv", index=False))
    (df.groupby("Country").agg(CountryName=("Country", "first"),
        revenue=("Revenue", "sum")).reset_index()
     .to_csv(pack / "dim_country.csv", index=False))
    monthly = _monthly_revenue(df)
    date_dim = monthly.copy()
    date_dim.to_csv(pack / "dim_date.csv", index=False)
    fact = df[["Invoice", "StockCode", "Customer ID", "InvoiceDate",
               "Quantity", "Price", "Revenue"]].copy()
    fact["InvoiceDate"] = pd.to_datetime(fact["InvoiceDate"]).dt.strftime("%Y-%m-%d")
    fact.to_csv(pack / "fact_sales.csv", index=False)
    (monthly.rename(columns={"Month": "Month", "Revenue": "Revenue"})
     .to_csv(pack / "kpi_monthly_revenue.csv", index=False))
    ar.top_n(df, n=20).to_csv(pack / "kpi_top_products.csv", index=False)
    (pd.DataFrame({"retention_rate_pct": [round(surv_curve(df, 30)[1], 1)]})
     .to_csv(pack / "kpi_survival.csv", index=False))
    (pd.DataFrame({"StockCode": ar.top_n(df, 5)["StockCode"],
                   "Revenue": [float(r) for r in ar.top_n(df, 5)["Revenue"]]})
     .to_csv(pack / "kpi_targeting_lift.csv", index=False))
    return {"pack": pack, "kpi_count": 3}
