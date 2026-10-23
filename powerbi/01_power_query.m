// Power Query (Power BI Desktop)
// Load the retail dataset and the sibling dimensional tables.
// Place the repo root at powerbi/data/retail/ before running.
let
    Source = Folder.Files("data/retail"),
    // ----- fact -----
    factRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "fact_sales.csv")[Content]{0},
        [Delimiter=",", Columns=7, Encoding=65001]
    ),
    #"Fact renames" = Table.RenameColumns(factRaw, {
        {"Column1","Invoice"},{"Column2","StockCode"},{"Column3","Customer ID"},
        {"Column4","InvoiceDate"},{"Column5","Quantity"},{"Column6","Price"},
        {"Column7","Revenue"}
    }),
    #"Fact change types" = Table.TransformColumnTypes(#"Fact renames", {
        {"Invoice", type text}, {"StockCode", type text}, {"Customer ID", type text},
        {"InvoiceDate", type date}, {"Quantity", Int64.Type}, {"Price", type number},
        {"Revenue", type number}
    }),
    #"Fact remove headers" = Table.RemoveHeaders(#"Fact change types"),

    // ----- dim_product -----
    prodRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "dim_product.csv")[Content]{0},
        [Delimiter=",", Columns=4, Encoding=65001]
    ),
    #"Product renames" = Table.RenameColumns(prodRaw, {
        {"Column1","StockCode"},{"Column2","Description"},{"Column3","ProductName"},
        {"Column4","total_revenue"},{"Column5","total_qty"}
    }),
    #"Product change types" = Table.TransformColumnTypes(#"Product renames", {
        {"StockCode", type text}, {"Description", type text}, {"ProductName", type text},
        {"total_revenue", type number}, {"total_qty", Int64.Type}
    }),
    #"Product remove headers" = Table.RemoveHeaders(#"Product change types"),

    // ----- dim_country -----
    ctryRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "dim_country.csv")[Content]{0},
        [Delimiter=",", Columns=3, Encoding=65001]
    ),
    #"Country renames" = Table.RenameColumns(ctryRaw, {
        {"Column1","CountryName"},{"Column2","revenue"}
    }),
    #"Country change types" = Table.TransformColumnTypes(ctryRaw, {
        {"CountryName", type text}, {"revenue", type number}
    }),

    // ----- dim_date -----
    dateRaw = Csv.Document(
        Table.SelectRows(Source, each [Name] = "dim_date.csv")[Content]{0},
        [Delimiter=",", Columns=2, Encoding=65001]
    ),
    #"Date renames" = Table.RenameColumns(dateRaw, {{"Column1","Month"},{"Column2","Revenue"}}),
    #"Date change types" = Table.TransformColumnTypes(#"Date renames", {
        {"Month", type date}, {"Revenue", type number}
    }),

    // ----- combine facts -----
    Combined = Table.Combine({"Fact", "Product", "Country", "Date"}),

    // ----- promote headers on the fact table -----
    #"Promoted headers" = Table.PromoteHeaders(factRaw, [DotStyle=None]),
    #"Fact typed" = Table.TransformColumnTypes(#"Promoted headers", {
        {"Invoice", type text}, {"StockCode", type text}, {"Customer ID", type text},
        {"InvoiceDate", type date}, {"Quantity", Int64.Type}, {"Price", type number},
        {"Revenue", type number}
    })
in
    #"Fact typed"
