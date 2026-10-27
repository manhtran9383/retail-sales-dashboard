// Power Query (Power BI Desktop)
// Load the retail dataset and the sibling dimensional tables.
// Place the repo root at powerbi/data/retail/ before running.
let
    Source = Folder.Files("data/retail"),

    // ----- fact -----
    // fact_sales.csv: Invoice, StockCode, Customer ID, InvoiceDate, Quantity, Price, Revenue
    factRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "fact_sales.csv")[Content]{0},
        [Delimiter=",", Columns=7, Encoding=65001]
    ),
    #"Fact renames" = Table.RenameColumns(factRaw, {
        {"Column1","Invoice"},{"Column2","StockCode"},{"Column3","Customer ID"},
        {"Column4","InvoiceDate"},{"Column5","Quantity"},{"Column6","Price"},
        {"Column7","Revenue"}
    }),
    #"Fact typed" = Table.TransformColumnTypes(#"Fact renames", {
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
    #"Product renames" = Table.RenameColumns(prodRaw, {
        {"Column1","StockCode"},{"Column2","ProductName"},
        {"Column3","total_revenue"},{"Column4","total_qty"}
    }),
    #"Product typed" = Table.TransformColumnTypes(#"Product renames", {
        {"StockCode", type text}, {"ProductName", type text},
        {"total_revenue", type number}, {"total_qty", Int64.Type}
    }),

    // ----- dim_country -----
    // dim_country.csv: Country, CountryName, revenue (3 cols)
    ctryRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "dim_country.csv")[Content]{0},
        [Delimiter=",", Columns=3, Encoding=65001]
    ),
    #"Country renames" = Table.RenameColumns(ctryRaw, {
        {"Column1","Country"},{"Column2","CountryName"},{"Column3","revenue"}
    }),
    #"Country typed" = Table.TransformColumnTypes(#"Country renames", {
        {"Country", type text}, {"CountryName", type text}, {"revenue", type number}
    }),

    // ----- dim_date -----
    // dim_date.csv: Month, Revenue (month grain)
    dateRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "dim_date.csv")[Content]{0},
        [Delimiter=",", Columns=2, Encoding=65001]
    ),
    #"Date renames" = Table.RenameColumns(dateRaw, {"Column1","Month"}, {"Column2","Revenue"}),
    #"Date typed" = Table.TransformColumnTypes(#"Date renames", {
        {"Month", type date}, {"Revenue", type number}
    }),

    // Return the fact table (typed). The dimensional tables are siblings in the
    // same folder, loaded above by their own Csv.Document blocks.
in
    #"Fact typed"
