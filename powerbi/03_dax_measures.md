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

// Recurring revenue ratio (repeat-purchase propensity)
RecurringRatio :=
    VAR Total = [Revenue MTD]
    VAR Recurring =
        CALCULATE(
            SUM(fact_sales[Revenue]),
            fact_sales[Customer ID] <> BLANK(),
            // customers purchasing in the current month also purchased in a
            // previous month — approximated by repeat purchases in the window
            DATEDIFF(MAX('dim_date'[Month]), TODAY(), MONTH) >= 1
        )
    RETURN DIVIDE(Recurring, Total, BLANK())

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
