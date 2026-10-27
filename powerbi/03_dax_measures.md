// DAX measures (retail analytics)
// Place in the report on the `fact_sales` table (create a calculated table if
// you prefer; these read the `fact_sales` table directly).

// Monthly revenue
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
// NOTE: a fully accurate recurring-revenue measure requires a genuine date table
// (`dim_date` marked as the date table in Power BI) plus a customer-level
// relationship to `fact_sales`. This approximation instead reports the share of
// a month's revenue coming from customers active in that month (recurring vs
// one-off), derived from distinct customer counts.
ActiveCustomerShare :=
    VAR TotalCustomers =
        CALCULATE(
            DISTINCTCOUNT(fact_sales[Customer ID]),
            REMOVEFILTERS('dim_date'[Month])
        )
    VAR AllCustomers =
        CALCULATE(DISTINCTCOUNT(fact_sales[Customer ID]))
    RETURN DIVIDE(TotalCustomers, AllCustomers, BLANK())

// Average order value
AvgOrderValue :=
    DIVIDE(
        SUM(fact_sales[Revenue]),
        DISTINCTCOUNT(fact_sales[Invoice])
    )

// Total active customers
ActiveCustomers :=
    CALCULATE(
        DISTINCTCOUNT(fact_sales[Customer ID]),
        REMOVEFILTERS('dim_date'[Month])
    )
