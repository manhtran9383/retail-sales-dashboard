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
| Repeat-purchase rate (30-day window) | **63.1%** |
| Median customer lifetime | ~12 active days |
| Best model | gradient boosting (revenue magnitude, hold-out 25%) |
| Top product | `85123A` — WHITE HANGING HEART T-LIGHT HOLDER (£10 857) |
| Top country | United Kingdom (£251 954) |

### Monthly revenue trend (£)
`2010-12: 20 105 → 2011-12: 8 950` (decline driven by fewer December orders)
Peak month `2011-11 (£33 297)`; trough `2010-12 (£20 105)`.

---

## 2 · Project structure

```
retail-sales-dashboard/
├── data/
│   └── raw/REtail_Sales.csv        # clean, sampled sales frame
├── src/
│   ├── config.py       # dataset registry + semantics
│   ├── load_data.py    # CSV loader + profile
│   ├── clean.py        # cleaning: no Anon, no cancel, positive qty/price
│   ├── analysis.py     # monthly revenue, top products, country, seasonality
│   ├── survival.py     # Kaplan-Meier-style repeat-purchase retention
│   ├── impact.py       # top products + retention by country
│   ├── report.py       # figures + Excel + Power BI pack
│   ├── dashboard_preview.py  # self-contained KPI + figure HTML
│   ├── powerbi_export.py   # Power BI pack builder
│   └── run_retail_analysis.py
├── powerbi/
│   ├── README.md
│   ├── 01_power_query.m
│   ├── 02_data_model.md
│   ├── 03_dax_measures.md
│   ├── 04_report_layout.md
│   ├── data/retail/      # generated data pack
│   └── dashboard_preview.html  # generated preview
├── tests/
│   └── test_streamlit_app.py
├── .github/workflows/ci.yml
├── streamlit_app.py
├── requirements.txt
└── README.md
```

---

## 3 · Analysis highlights

* **Monthly revenue** — 13 months of history; seasonality peaks in Q4 (Nov–Dec)
  and dips in June/July.
* **Top products** — the top 10 drive ~£52k of £254k (20% of revenue).
* **Customer retention** — repeat-purchase rate is `63.1%` within 30 days;
  the Kaplan-Meier curve shows declining reactivation the longer the window.
* **Regional mix** — 33 countries; `United Kingdom 99.2%` of revenue.

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
`https://github.com/<owner>/retail-sales-dashboard/releases`

Package the full portfolio (source + outputs + data):
```bat
python powerbi_build.py
```
(The `powerbi_build.py` script regenerates the Power BI data pack and the preview HTML.)
The zip includes source, figures, the Excel workbook, the Power BI data pack and
the preview HTML.
