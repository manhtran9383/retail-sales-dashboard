"""Retail Sales Dashboard — Power BI data pack builder + dashboard preview."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
from pathlib import Path

from .config import DATASETS, FIGURES_DIR
from . import analysis as ar
from .survival import retention_curve

FIGSIZE = (7.2, 3.6)
COLORS = {"retail": "#9467bd", "accent": "#8c564b"}
plt.rcParams.update({"font.size": 9, "axes.grid": False})


def _style(ax, title):
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.tick_params(axis="x", rotation=35)


def make_dashboard_preview(df: pd.DataFrame, out_html: Path):
    out_html.parent.mkdir(parents=True, exist_ok=True)
    tmp = df.copy()
    tmp["Month"] = tmp["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    monthly = tmp.groupby("Month")["Revenue"].sum().sort_index()
    top_p = ar.top_n(df, n=20).head(12)
    country = ar.sales_by_country(df).head(15)
    surv, rate = retention_curve(df, repeat_days=30)

    kpi = [
        ("Total Revenue (£)", f"£{df['Revenue'].sum():,.2f}"),
        ("Customers", f"{df['Customer ID'].nunique():,}"),
        ("Months (coverage)", f"{monthly.shape[0]}"),
        ("Repeat-purchase rate", f"{rate:.1f}%"),
        ("Months covered", f"{len(monthly)}"),
    ]
    kpi_rows = ""
    for k, v in kpi:
        kpi_rows += f"<tr><td style='text-align:left'>{k}</td><td style='text-align:right'>{v}</td></tr>\n"

    monthly_rows = "".join(
        f"<tr><td>{m.strftime('%Y-%m')}</td><td style='text-align:right'>£{v:,.2f}</td></tr>" for m, v in monthly.items())
    top_rows = "".join(
        f"<tr><td>{r['StockCode']}</td><td style='text-align:right'>£{r['Revenue']:,.2f}</td></tr>"
        for _, r in top_p.head(12).iterrows())
    country_rows = "".join(
        f"<tr><td>{c}</td><td style='text-align:right'>£{v:,.2f}</td></tr>"
        for c, v in country["Revenue"].items())
    surv_rows = "".join(
        f"<tr><td>{d}</td><td style='text-align:right'>{p:.1f}%</td></tr>"
        for d, p in zip(surv["days_after_first"], surv["repeat_rate_pct"]))

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Retail Sales Dashboard | {DATASETS['retail']['display_name']}</title>
<style>
:root {{ --bg:#0f1115; --card:#16191f; --fg:#e6e6e6; --muted:#8b8f98; --accent:#9467bd; --border:#2a2f3a; }}
*{{box-sizing:border-box}} body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:var(--bg); color:var(--fg); }}
.header {{ padding:18px 20px; background:var(--card); border-bottom:1px solid var(--border); }}
.header h1 {{ margin:0 0 4px; font-size:18px; }} .sub {{ color:var(--muted); font-size:12px; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:10px; padding:14px; }}
.kpi {{ background:var(--card); border:1px solid var(--border); border-radius:8px; padding:12px; }}
.kpi .v {{ font-size:15px; font-weight:600; color:var(--accent); }}
.kpi .l {{ font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:12px; padding:12px; }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:8px; padding:12px; }}
.card h2 {{ margin:0 0 8px; font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; }}
.card img {{ width:100%; border-radius:4px; display:block; }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th, td {{ border-bottom:1px solid var(--border); padding:6px 8px; text-align:left; }}
th {{ color:var(--muted); font-weight:600; }}
tr:last-child td {{ border-bottom:none; }}
</style></head><body>
<div class="header"><h1>Retail Sales Dashboard</h1><div class="sub">{DATASETS['retail']['display_name']} · UK online giftware · {df['Customer ID'].nunique():,} customers</div></div>
<div class="kpis">
{kpi_rows}
</div>
<div class="grid">
  <div class="card"><h2>Monthly Revenue</h2><img src="{_b64(_monthly_chart(monthly))}"></div>
  <div class="card"><h2>Sales by Country</h2><img src="{_b64(_country_chart(country))}"></div>
  <div class="card"><h2>Seasonality</h2><img src="{_b64(_season_chart(df))}"></div>
  <div class="card"><h2>Retention (KM)</h2><img src="{_b64(_retention_chart(surv, rate))}"></div>
  <div class="card"><h2>Top Products</h2><img src="{_b64(_top_chart(top_p))}"></div>
  <div class="card"><h2>Price Drivers</h2><img src="{_b64(_predictor_chart(df))}"></div>
</div>
<div class="card" style="margin:12px;"><h2>Monthly Revenue Detail</h2><table><thead><tr><th>Month</th><th>Revenue (£)</th></tr></thead><tbody>{monthly_rows}</tbody></table></div>
<div class="card" style="margin:12px;"><h2>Top Products</h2><table><thead><tr><th>StockCode</th><th>Revenue (£)</th></tr></thead><tbody>{top_rows}</tbody></table></div>
<div class="card" style="margin:12px;"><h2>Retention Curve (Kaplan-Meier)</h2><table><thead><tr><th>Days after 1st purchase</th><th>Reactivated rate (%)</th></tr></thead><tbody>{surv_rows}</tbody></table></div>
</body></html>"""
    out_html.write_text(html, encoding="utf-8")
    print(f"Preview    : {out_html} ({len(kpi)} KPIs)")


def _monthly_chart(monthly):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(monthly.index, monthly.values, color=COLORS["retail"])
    ax.set_ylabel("Revenue (£)")
    _style(ax, "Retail monthly revenue")
    return fig


def _country_chart(country):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(country["Country"], country["Revenue"], color=COLORS["retail"])
    ax.set_ylabel("Revenue (£)")
    _style(ax, "Top countries by revenue")
    return fig


def _season_chart(df):
    tmp = df.copy()
    tmp["month_name"] = tmp["InvoiceDate"].dt.month_name()
    order = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
    tmp["month_name"] = pd.Categorical(tmp["month_name"], categories=order, ordered=True)
    d = tmp.groupby("month_name")["Revenue"].mean().reindex(order)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(d.index, d.values, color=COLORS["retail"])
    ax.set_ylabel("Avg revenue (£)")
    _style(ax, "Seasonality")
    return fig


def _retention_chart(surv, rate):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(surv["days_after_first"], surv["repeat_rate_pct"], marker="o", color=COLORS["retail"])
    ax.set_xlabel("Days after first purchase")
    ax.set_ylabel("Reactivated purchase rate (%)")
    _style(ax, "Customer repeat-purchase rate")
    return fig


def _top_chart(top):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.barh(top["StockCode"][::-1], top["Revenue"][::-1], color=COLORS["accent"])
    ax.set_xlabel("Revenue (£)")
    _style(ax, "Top products by revenue")
    return fig


def _predictor_chart(df):
    top = ar.top_n(df, n=10)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.barh(top["StockCode"][::-1], top["Revenue"].tail(10)[::-1], color=COLORS["retail"])
    ax.set_xlabel("Revenue (£)")
    _style(ax, "Top-10 product revenue")
    return fig


def _b64(fig):
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
