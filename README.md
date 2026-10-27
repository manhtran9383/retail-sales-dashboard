# Retail Sales Dashboard

A dataset-driven, end-to-end business-intelligence portfolio for a UK online
giftware retailer (**Online Retail II**, UCI). Every number is reproducible from
raw CSV → cleaning → analysis → Power BI → Streamlit → Excel, and the whole
pipeline runs as `python -m src.run_retail_analysis --dataset retail`.

---

## 0 · Quick start

```bat
cd retail-sales-dashboard
pip install -r requirements.txt
python -m src.run_retail_analysis --dataset retail
```

Equivalent streamlit: `streamlit run streamlit_app.py`

### What the default run produces
| Artifact | Path |
|---|---|
| 6 figures (monthly revenue, top products, regions, seasonality, retention, price drivers) | `reports/figures/` |
| 8-sheet Excel workbook | `reports/Re_Sales_Analysis.xlsx` |
| Power BI data pack | `powerbi/data/retail/` |
| Preview HTML (KPI + figures) | `dashboard_preview.html` |
| Streamlit app | `streamlit_app.py` |

### Stage flags (also accepted)
```bat
python -m src.run_retail_analysis --dataset retail --stage powerbi
python -m src.run_retail_analysis --dataset retail --stage preview
```

### Tests
```bat
python -m pytest tests -q
```

---

## 1 · Key results (data: online retail II, 2010-12 → 2011-12)

| Metric | Value |
|---|---|
| Dataset | Online Retail II (UK online giftware) |
| Rows | 12 000 |
| Customers | 2 836 |
| Countries | 32 |
| Total revenue | **£253 814.99** / mo est **£21 151.25** |
| Repeat-purchase rate (30-day window) | **42.5%** of 2 836 customers (63.1% of the 1 910 who returned) |
| Median customer lifetime | 2 days (mean 94 days) |
| Best model | None (no ML model is trained) |
| Top product | `22423` — REGENCY CAKESTAND 3 TIER (£4 542.45) |
| Top country | United Kingdom (£206 339, 81.3% of revenue) |

### Monthly revenue trend (£)
`2010-12: 20 106 → 2011-12: 8 950` — note **Dec-2011 is truncated** (the sample
ends 09/12/2011, 9 days), so the dip is a sampling artefact, not a true decline.
Peak month `2011-11 (£33 297)`; trough `2010-12 (£20 106)`.

---

## 2 · Project structure

```
retail-sales-dashboard/
├── data/
│   └── raw/retail_sales.csv        # clean, sampled sales frame
├── src/
│   ├── config.py       # dataset registry + semantics
│   ├── load_data.py    # CSV loader + profile
│   ├── clean.py        # cleaning: no Anon, no cancel, positive qty/price
│   ├── analysis.py     # monthly revenue, top products, country, seasonality
│   ├── survival.py     # Kaplan-Meier-style repeat-purchase retention
│   ├── impact.py       # top products + retention by country
│   ├── report.py       # figures + Excel + Power BI pack
│   ├── dashboard_preview.py  # self-contained KPI + figure HTML
│   └── run_retail_analysis.py
├── tests/
│   ├── test_retail_kpis.py
│   ├── test_clean.py
│   ├── test_analysis.py
│   ├── test_powerbi_pack.py
│   └── test_streamlit_app.py
├── powerbi/
│   ├── README.md
│   ├── 01_power_query.m
│   ├── 02_data_model.md
│   ├── 03_dax_measures.md
│   ├── 04_report_layout.md
│   └── data/retail/      # generated data pack
├── .github/workflows/ci.yml
├── streamlit_app.py
├── requirements.txt
└── README.md
```

### Data provenance

| Field | Value |
|---|---|
| Source | UCI Online Retail II (`online_retail_II.xlsx`, sheet `Year 2010-2011`) |
| Processed frame | `data/raw/retail_sales.csv` — 12 000 sampled transactions (pre-cleaned) |
| Cleaning rules | drop `Invoice` starting `C`; drop `Quantity <= 0` / `Price <= 0`; `Revenue = Quantity * Price`; add `InvoiceMonth` + `month_name` |
| Code license | MIT (`LICENSE`). Reference data: UCI Online Retail II is CC BY 4.0 — cite: Chen, J. D. (2015), "Online Retail II", UCI Machine Learning Repository, https://archive.ics.uci.edu/dataset/352/online+retail+ii |


---

## 3 · Analysis highlights

* **Monthly revenue** — 13 months of history; seasonality peaks in Q4 (Nov).
  Dec-2011 is truncated (data ends 09/12), so it is **not** a true decline.
* **Top products** — the top 10 drive £28 118,91 (11.1% of revenue).
* **Customer retention** — repeat-purchase rate is `42.5%` of all customers
  within 30 days (63.1% of the 1 910 who returned). One-off customers are
  censored in the denominator, so the rate is not inflated by survivorship.
* **Regional mix** — 32 countries; United Kingdom is `81.3%` of revenue.

---

## 4 · Power BI

1. `pip install -r requirements.txt`
2. Copy the repo root so that `powerbi/data/retail/` is populated:
   `python -m src.run_retail_analysis --stage powerbi`
3. Open the `powerbi` folder in Power BI Desktop and use `01_power_query.m` to
   import; then `03_dax_measures.md` for the measures on the canvas.
4. Run the preview (`--stage preview`) and open
   `dashboard_preview.html` in a browser for a quick look.

---

## 5 · CI

```yaml
# .github/workflows/ci.yml  →  windows-latest matrix (retail)
#   verify (pipeline run)  +  pytest  +  preview stage
```

---

## 6 · Release & packaging

View the release/tag at:
`https://github.com/manhtran9383/retail-sales-dashboard/releases/tag/2026.10.23-v1.0.4`

Package the full portfolio (source + outputs + data):
```bat
python _pack_retail.py
```
(The `_pack_retail.py` script rebuilds the pipeline outputs and then zips the repo for delivery.)

The ZIP delivery artifact is at:

`retail-sales-dashboard-portfolio.zip`

The zip includes source, figures, the Excel workbook, the Power BI data pack and
the preview HTML.

## 7 · Release notes (v1.0.4)

Nothing in this release is published while any GitHub Actions job is failing; the
tag only moves after CI is green.

- **CI gate:** 36 golden tests pass; coverage is **60 %** (above the 40 % gate);
  `ruff check src tests` is clean (0 errors).
- **Cross-platform:** tests reference `data/raw/retail_sales.csv` with a
  case-correct filename; the GitHub Actions CI (Ubuntu) now passes end to end.
- **Power Query M:** `01_power_query.m` uses `Table.PromoteHeaders` in all four
  import blocks, so the header-promotion claim is now accurate.
- **API / analysis:** `ActiveCustomerShare` / `ActiveCustomers` return `BLANK` (a
  genuine `fact_sales` ↔ `dim_date` relationship is absent); `POWERBI.figures_dir` and
  `preview_html` point at real output paths; dead code (`load_data.profile`,
  `streamlit._tabs_if`, unused imports) removed.
- **Docs:** `powerbi/README.md` documents `dim_product` columns correctly, fixes a
  stray backtick, and no longer lists `dashboard_preview.html` as a pack file.
- Versioning convention: the next breaking change is v2.0.

The ZIP delivery artifact is at:

`retail-sales-dashboard-portfolio.zip`

The zip includes source, figures, the Excel workbook, the Power BI data pack and
the preview HTML.
