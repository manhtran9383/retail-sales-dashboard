# Report layout (Power BI)

## Canvas layout (one report page)
1. `KPI` section — total revenue, customers, countries, months, repeat rate
2. `Sales Trend` — line/bar of monthly revenue + YoY sparkline
3. `Top Products` — clustered column of top-10 products
4. `Regions` — country sales (bar)
5. `Seasonality` — average revenue by calendar month
6. `Customer Retention` — repeat-purchase curve (Kaplan-Meier)
7. `Detail` — fact_sales table + line chart

## Slicers
- `dim_date[Month]` (range slicer)
- `dim_country[CountryName]`
- `dim_product[ProductName]`
- `Customer ID` (optional)

## Number formats
- Revenue: `£#,##0.00`
- Percentages: `0.0%`
- Quantity: `#,##0`

## Custom visuals
- Use the "Power BI reputation chart" or native bar/line per above; no
  third-party visuals strictly required.
