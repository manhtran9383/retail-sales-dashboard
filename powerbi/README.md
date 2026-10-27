# Retail Sales Dashboard — Power BI

## Overview
One-Power-BI data pack scoped to a single dataset (`retail` = online retail II):

- `fact_sales.csv`       — transaction fact (Invoice, StockCode, Customer, date, qty, price, revenue)
- `dim_product.csv`      — product dimension (StockCode, Description, total revenue)
- `dim_country.csv`      — country dimension
`- dim_date.csv`         — date dimension (month grain, Month as a date)
- `kpi_monthly_revenue.csv` — monthly revenue
- `kpi_top_products.csv`   — top products
- `kpi_survival.csv`       — repeat-purchase retention rate
- `kpi_targeting_lift.csv` — revenue concentration (top-50 lift)
- `dashboard_preview.html` — self-contained KPI + figures preview

## Build the pack
```bat
cd retail-sales-dashboard
pip install -r requirements.txt
python -m src.run_retail_analysis --stage powerbi
```
The pack lands in `powerbi/data/retail/`.

## Power Query dataset
Run the `01_power_query.m` from Power BI Desktop (Data → Power Query) after
placing the repo root in `powerbi/data/retail/`.

## Relationship
`fact_sales.StockCode` → `dim_product.StockCode`.
`dim_date` is a standalone calendar dimension (month grain); `fact_sales`
stores `InvoiceDate` (not a month key), so no relationship is enforced between
them unless you add a month column to the fact table.

## DAX measures
See `03_dax_measures.md` for the calculated measures used on the report canvas
(monthly revenue, YoY growth, recurring-revenue ratio, avg order value).
