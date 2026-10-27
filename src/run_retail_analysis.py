"""Retail Sales Dashboard — CLI entry point.

Run as `python -m src.run_retail_analysis [--dataset retail] [--stage powerbi|preview]`.
Module mode is required (the repo root is exported as PYTHONPATH) so that
relative imports (`from . import ...`) resolve correctly.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from . import config as cfg
from . import report as rpt
from .dashboard_preview import make_dashboard_preview as make_preview
from .clean import clean, check
from .load_data import load_data

REPORTS = cfg.REPORTS_DIR
FIGURES_DIR = cfg.FIGURES_DIR


def run(dataset: str = "retail", stage: str | None = None) -> None:
    spec = cfg.DATASETS[dataset]
    print(f"--- {spec['display_name']} ({dataset}) ---")

    df = load_data(dataset)
    df = clean(df)
    facts = check(df)

    print(f"Date range : {facts['date_min']} -> {facts['date_max']}")
    print(f"Rows       : {facts['rows']}")
    print(f"Customers  : {facts['customers']}")
    print(f"Countries  : {facts['countries']}")
    print(f"Total rev  : £{facts['total_revenue']:,.2f} / mo est £{facts['total_revenue']/12:,.2f}")

    # ---- figures + Excel ----
    figures = rpt._make_figures(df, FIGURES_DIR)
    print(f"Figures    : {len(figures)} in {FIGURES_DIR}")
    out_xlsx = REPORTS / "Re_Sales_Analysis.xlsx"
    rpt.make_excel(df, out_xlsx)
    print(f"Excel      : {out_xlsx} ({len(list(FIGURES_DIR.glob('*.png')))} figures)")

    # ---- stage: powerbi ----
    if stage == "powerbi" or stage is None:
        pack = rpt.make_powerbi_pack(df, cfg.REPORTS_DIR.parent)
        print(f"Power BI   : {pack['pack']} ({pack['kpi_count']} kpi csvs)")

    # ---- stage: preview ----
    if stage == "preview" or stage is None:
        make_preview(df, cfg.REPORTS_DIR.parent / "dashboard_preview.html")
        print("Preview    : dashboard_preview.html (6 figs + KPI tables)")

    print(f"Outputs    : {FIGURES_DIR} | {REPORTS / 'Re_Sales_Analysis.xlsx'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="retail")
    ap.add_argument("--stage", choices=["powerbi", "preview"], default=None)
    args = ap.parse_args()
    run(args.dataset, args.stage)
