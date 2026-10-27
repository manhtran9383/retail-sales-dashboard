// Power Query (Power BI Desktop)
// Reference only — not executed/tested on Power BI Desktop here.
// Place powerbi/data/retail/ contents at the Power BI Desktop working
// directory (i.e. the folder containing this script) before running.

let
    Source = Folder.Files("powerbi/data/retail"),

    // ----- fact -----
    // fact_sales.csv: Invoice, StockCode, Customer ID, InvoiceDate, Quantity, Price, Revenue
    factRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "fact_sales.csv")[Content]{0},
        [Delimiter=",", Columns=7, Encoding=65001]
    ),
    #"Fact typed" = Table.TransformColumnTypes(#"Promoted fact headers", 
        {"Invoice", type text}, {"StockCode", type text}, {"Customer ID", type text},
        {"InvoiceDate", type date}, {"Quantity", Int64.Type}, {"Price", type number},
        {"Revenue", type number}
    }),

    // ----- dim_product -----
    // dim_product.csv: StockCode, ProductName, total_revenue, total_qty (4 cols)
    prodRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "dim_product.csv")[Content]{0},
        [Delimiter=",", Columns=4, Encoding=65001]
    ),
    #"Product typed" = Table.TransformColumnTypes(#"Promoted product headers", 
        {"StockCode", type text}, {"ProductName", type text},
        {"total_revenue", type number}, {"total_qty", Int64.Type}
    }),

    // ----- dim_country -----
    // dim_country.csv: Country, CountryName, revenue (3 cols)
    ctryRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "dim_country.csv")[Content]{0},
        [Delimiter=",", Columns=3, Encoding=65001]
    ),
    #"Country typed" = Table.TransformColumnTypes(#"Promoted country headers", 
        {"Country", type text}, {"CountryName", type text}, {"revenue", type number}
    }),

    // ----- dim_date -----
    // dim_date.csv: Month, Revenue (month grain)
    dateRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "dim_date.csv")[Content]{0},
        [Delimiter=",", Columns=2, Encoding=65001]
    ),
    #"Date typed" = Table.TransformColumnTypes(#"Promoted date headers", 
        {"Month", type date}, {"Revenue", type number}
    }),

    // Return the fact table (typed). The dimensional tables are siblings in the
    // same folder, loaded above by their own Csv.Document blocks.
in
    #"Fact typed"
