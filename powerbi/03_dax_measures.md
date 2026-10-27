// DAX measures (retail analytics)
// Place in the report on the `fact_sales` table (create a calculated table if
// you prefer; these read the `fact_sales` table directly).

// Monthly revenue
// NOTE: Revenue MTD/YoY filter fact_sales by dim_date[Month]. The current data
// model has NO relationship between fact_sales and dim_date (see
// powerbi/README.md §Relationship), so these measures currently sum the entire
// fact_sales table for every month. Add the relationship before relying on them.
Revenue MTD :=
    CALCULATE(
        SUM(fact_sales[Revenue]),
        DATESMTD('dim_date'[Month])
    )

Revenue YoY :=
    VAR Curr = [Revenue MTD]
    VAR Prev = CALCULATE([Revenue MTD], SAMEPERIODLASTYEAR('dim_date'[Month]))
    RETURN
        DIVIDE(Curr - Prev, Prev, BLANK())

// Recurring revenue ratio (repeat-purchase propensity, approximation).
// NOTE: BROKEN in the current data model. This measure requires a genuine
// one-to-many relationship between `fact_sales[InvoiceDate]` and
// `dim_date[Month]` (see powerbi/README.md §Relationship). Without that
// relationship, both variables below resolve to the total customer base, so the
// ratio is always 100%. Until the relationship exists, remove this measure or
// re-enable it after adding the relationship.
//
// TODO: add fact_sales[InvoiceDate] -> dim_date[Month] relationship in Power BI,
// then restore ActiveCustomerShare.
ActiveCustomerShare := BLANK()

// Average order value
AvgOrderValue :=
    DIVIDE(
        SUM(fact_sales[Revenue]),
        DISTINCTCOUNT(fact_sales[Invoice])
    )

// Total active customers
// NOTE: requires a genuine one-to-many relationship between
// `fact_sales[InvoiceDate]` and `dim_date[Month]` (see powerbi/README.md
// §Relationship). Without that relationship this resolves to the total customer
// base. TODO: add the relationship, then restore.
ActiveCustomers := BLANK()
