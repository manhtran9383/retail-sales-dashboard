"""Retail Sales Dashboard — configuration registry.

Mirrors the churn-analysis-portfolio registry style: each dataset is a
structured spec so the pipeline, Power BI pack and Streamlit app stay
dataset-aware (no hard-coded column names).
"""
from __future__ import annotations

from pathlib import Path

# Dataset registry (add a new key per dataset you want to run)
DATASETS = {
    "retail": {
        "key": "retail",
        "display_name": "Online Retail II — UK Giftwear",
        "short": "Retail",
        "raw_path": "data/raw/REtail_Sales.csv",
        "time_unit": "days",          # each row is a transaction on a date
        "time_col": "InvoiceDate",
        "customer_col": "Customer ID",
        "country_col": "Country",
        "category_col": "StockCode",
        "revenue_col": "Revenue",
        "powerbi_pack_name": "retail",
    },
}

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# ---- Survival / retention ----
#
# "Retention" = repeat-purchase. A customer is "retained" at month m if they
# bought again in month >= first_purchase_month + m. We treat months as lanes
# and build a Kaplan-Meier-style retention curve (no look-ahead).
SURVIVAL = {
    "method": "cohort_repeat_purchase",   # cohort_repeat_purchase | kaplan_meier
    "customer_col": "Customer ID",
    "month_col": "InvoiceMonth",
    "duration_col": "months_since_first",
    "event_col": "repeat_purchase",
    "censored": False,                    # every observed customer is real
}

# ---- Impact / targeting ----
#
# Retail has no monthly_revenue (that is a payroll concept), so impact is:
#   - revenue at risk   (revenue from customers who churn)
#   - targeting lift    (top-Revenue% of products vs full base) — n/a when a
#     column like monthly_revenue is absent (market-size unknown).
IMPACT = {
    "revenue_col": "Revenue",
    "customer_col": "Customer ID",
    "targeting": {
        "list_sizes_pct": [2, 5, 10, 20, 50],   # 2%..50% of customers
        "metric": "Revenue",                       # revenue (not "revenue")
        "unit_label": "£",
    },
    "retention": {
        # repeat purchase within N days after first purchase
        "repeat_days": 30,
    },
}

# ---- Model (best model for ranking) ----
MODEL = {
    "features": ["Quantity", "Price"],  # product-level regressors
    "model": "gradient_boosting",       # GB > RF > LR for sales magnitude
    "target": "Revenue",                # regression target (top sellers)
    "test_size": 0.25,                  # hold-out for honest impact
    "random_state": 42,
}

# ---- Power BI ----
POWERBI = {
    "data_dir": "powerbi/data/retail",
    "figures_dir": "powerbi/data/retail/figures",
    "preview_html": "powerbi/dashboard_preview_retail.html",
    "csv_files": [
        "dim_customer.csv", "dim_country.csv", "dim_date.csv",
        "dim_product.csv", "fact_sales.csv",
        "kpi_monthly_revenue.csv", "kpi_top_products.csv",
        "kpi_survival.csv", "kpi_targeting_lift.csv",
    ],
}
