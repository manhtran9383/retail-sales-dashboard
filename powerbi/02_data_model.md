# Data model (Power BI)

## Tables
| Table | Grain | Notes |
|---|---|---|
| `fact_sales` | transaction line | one row per invoice line |
| `dim_product` | product | denormalised with total revenue / qty |
| `dim_country` | country | sales mix |
| `dim_date` | month | monthly revenue grain |

## Relationships
- `fact_sales[StockCode]` → `dim_product[StockCode]`
- `fact_sales[Customer ID]` → `dim_customer[Customer ID]` (derived in report)
- `fact_sales[Month]` → `dim_date[Month]`

## Model notes
- Revenue is already computed (Quantity × Price) in the CSV; no DAX recompute.
- Cancellation filtering (`Invoice` not starting with "C") is done in `clean.py`
  before pack time, so the model stays revenue-accurate.
- Date table is marked as a date table in the report; Time Intelligence uses it.
