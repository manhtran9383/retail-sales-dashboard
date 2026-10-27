"""Golden tests for the report generation (figures + Excel + Power BI pack).

Covers the report.py functions that were previously uncovered, raising the
overall test coverage above the 40% gate required by CI.
"""
from __future__ import annotations

import pathlib

import pandas as pd
import pytest

from src import report as rpt
from src.clean import clean
from src.load_data import load_data

REPO = pathlib.Path(__file__).resolve().parent.parent

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


def _df():
    return clean(load_data("retail"))


def test_figure_outputs_exist(tmp_path):
    df = _df()
    fig_fns = {
        "figure_monthly_revenue": "Monthly_revenue_trend.png",
        "figure_top_products": "Top_products.png",
        "figure_sales_by_country": "Sales_by_region.png",
        "figure_seasonality": "Seasonality.png",
        "figure_retention": "Customer_retention.png",
        "figure_best_predictors": "Best_predictors.png",
    }
    for name, png in fig_fns.items():
        getattr(rpt, name)(df, tmp_path)
        assert (tmp_path / png).exists()


@pytest.mark.parametrize(
    "key,expected", [(k, v) for k, v in EXPECTED.items()]
)
def test_goldens_match(key, expected):
    actual = _df()
    g = actual.groupby("Customer ID")["InvoiceDate"]
    first = g.min().rename("first_purchase")
    second = g.agg(lambda s: s.iloc[1] if len(s) > 1 else pd.NaT).rename("second_purchase")
    joined = pd.concat([first, second], axis=1).reset_index()
    joined = joined[joined["second_purchase"].notna()].copy()
    joined["repeat_days"] = (joined["second_purchase"] - joined["first_purchase"]).dt.days
    top10 = actual.groupby("StockCode")["Revenue"].sum().nlargest(10).sum()
    top_product_rev_value = actual.groupby("StockCode")["Revenue"].sum().max()
    uk_rev = actual.loc[actual["Country"] == "United Kingdom", "Revenue"].sum()
    first_purchase = actual.groupby("Customer ID")["InvoiceDate"].min()
    last_purchase = actual.groupby("Customer ID")["InvoiceDate"].max()
    customer_lifetime = (last_purchase - first_purchase).dt.days
    checks = {
        "rows": len(actual),
        "customers": actual["Customer ID"].nunique(),
        "countries": actual["Country"].nunique(),
        "total_revenue": round(float(actual["Revenue"].sum()), 2),
        "repeat_rate_30d_pct": round(
            float(joined["repeat_days"].le(30).sum()) / actual["Customer ID"].nunique() * 100, 1
        ),
        "top10_revenue": round(float(top10), 2),
        "top_product_revenue": round(float(top_product_rev_value), 2),
        "uk_revenue": round(float(uk_rev), 2),
        "lifetime_median_days": int(customer_lifetime.median()),
        "lifetime_mean_days": round(float(customer_lifetime.mean()), 1),
    }
    assert checks[key] == expected, f"{key}: expected {expected}, got {checks[key]}"


def test_make_excel_writes_sheets(tmp_path):
    from src import report as rpt

    df = _df()
    out = tmp_path / "Re_Sales_Analysis.xlsx"
    rpt.make_excel(df, out)
    assert out.exists()
    xl = pd.ExcelFile(out)
    assert {"Top_Products", "Customer_Retention", "Survival_Retention",
            "Customer_Cohorts", "Monthly_Revenue", "Seasonality", "KPI_Summary"} <= set(xl.sheet_names)


def test_make_powerbi_pack_creates_csvs(tmp_path):
    from src import report as rpt

    df = _df()
    out = rpt.make_powerbi_pack(df, tmp_path)
    pack = out["pack"]
    assert pack.exists()
    expected_files = {
        "dim_product.csv", "dim_country.csv", "dim_date.csv", "fact_sales.csv",
        "kpi_monthly_revenue.csv", "kpi_top_products.csv",
        "kpi_survival.csv", "kpi_targeting_lift.csv",
    }
    actual_files = {p.name for p in pack.iterdir()}
    assert expected_files <= actual_files
    # spot-check a column on one of the CSVs
    prod = pd.read_csv(pack / "dim_product.csv")
    assert "ProductName" in prod.columns
    assert "total_revenue" in prod.columns

class TestSmokeArtifacts:
    "Smoke tests for the two 0%-covered artifact modules."

    def test_make_dashboard_preview_writes_html(self, tmp_path):
        from src.dashboard_preview import make_dashboard_preview
        from src.load_data import load_data

        df = load_data("retail")
        out_html = tmp_path / "dashboard_preview.html"
        make_dashboard_preview(df, out_html)
        assert out_html.exists()
        html = out_html.read_text(encoding="utf-8")
        assert html.count("data:image/png;base64,") == 6

    def test_run_retail_analysis_builds_outputs(self, tmp_path):
        import sys

        import src.run_retail_analysis as rra
        from src import config as cfg

        # monkeypatch: redirect REPORTS_DIR / FIGURES_DIR to tmp_path
        cfg.REPORTS_DIR = tmp_path
        cfg.FIGURES_DIR = tmp_path / "figures"
        rra.REPORTS = tmp_path
        rra.FIGURES_DIR = tmp_path / "figures"
        sys.modules[cfg.__name__] = cfg
        sys.modules[rra.__name__] = rra

        rra.run("retail", stage="preview")

        figures = tmp_path / "figures"
        assert figures.is_dir()
        assert len(list(figures.glob("*.png"))) == 6
        assert (tmp_path / "Re_Sales_Analysis.xlsx").exists()
        assert (tmp_path.parent / "dashboard_preview.html").exists()
