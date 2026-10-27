"""Retail Sales Dashboard — Power BI data pack builder.

Produces the per-dataset Power BI data pack: dimensional CSVs + fact table +
KPI Excel/CSV + embedded figures. Mirrors the churn-project powerbi_export.py
module so the powerbi folder stays dataset-aware.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path

from .clean import clean
from .config import DATASETS, REPORTS_DIR
from .import analysis as ar
from .load_data import load_data
from .survival import retention_curve


def _pack_dir() -> Path:
    out = REPORTS_DIR.parent / "powerbi" / "data" / "retail"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_pack(df: pd.DataFrame) -> dict[str, Path]:
    pack = _pack_dir()
    df = df.copy()
    df["InvoiceMonth"] = pd.to_datetime(df["InvoiceDate"]).dt.to_period("M").astype(str)

    (df.groupby("StockCode").agg(ProductName=("Description", "first"),
                                 total_revenue=("Revenue", "sum"),
                                 total_qty=("Quantity", "sum")).reset_index()
     .to_csv(pack / "dim_product.csv", index=False))

    (df.groupby("Country").agg(CountryName=("Country", "first"),
         revenue=("Revenue", "sum")).reset_index().to_csv(pack / "dim_country.csv", index=False))

    monthly = (df.groupby(df["InvoiceDate"].dt.to_period("M").dt.to_timestamp())
               .agg(Month=("InvoiceDate", "first"), Revenue=("Revenue", "sum"))
               .reset_index()
               .rename(columns={"Month": "Month", "Revenue": "Revenue"}))
    monthly.to_csv(pack / "kpi_monthly_revenue.csv", index=False)
    date_dim = pd.DataFrame({"Month": pd.date_range(
        start=monthly["Month"].min(), end=monthly["Month"].max(), freq="MS")})
    date_dim = (date_dim.merge(monthly, on="Month", how="left")
                .fillna(0).reset_index(drop=True))
    date_dim.to_csv(pack / "dim_date.csv", index=False)

    fact = df[["Invoice", "StockCode", "Customer ID", "InvoiceDate",
               "Quantity", "Price", "Revenue"]].copy()
    fact["InvoiceDate"] = pd.to_datetime(fact["InvoiceDate"]).dt.strftime("%Y-%m-%d")
    fact.to_csv(pack / "fact_sales.csv", index=False)

    (monthly.rename(columns={"Month": "Month", "Revenue": "Revenue"})
     .to_csv(pack / "kpi_monthly_revenue.csv", index=False))

    (ar.top_n(df, n=20).to_csv(pack / "kpi_top_products.csv", index=False))

    (pd.DataFrame({"retention_rate_pct": [round(retention_curve(df, 30)[1], 1)]})
     .to_csv(pack / "kpi_survival.csv", index=False))

    (pd.DataFrame({"StockCode": ar.top_n(df, 5)["StockCode"],
                   "Revenue": [float(r) for r in ar.top_n(df, 5)["Revenue"]]})
     .to_csv(pack / "kpi_targeting_lift.csv", index=False))

    return {"pack": pack,
            "kpi_count": 3,
            "dim_product": pack / "dim_product.csv",
            "fact_sales": pack / "fact_sales.csv"}


def main() -> None:
    df = load_data("retail")
    df = clean(df)
    pack = build_pack(df)
    print(f"Power BI pack: {pack['pack']} ({len(list(pack['pack'].iterdir()))} files)")


if __name__ == "__main__":
    main()
