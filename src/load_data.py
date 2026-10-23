"""Retail Sales Dashboard — data loading (clean + profile)."""
from __future__ import annotations

import pandas as pd

from pathlib import Path

from .config import DATASETS, FIGURES_DIR

ROOT = Path(__file__).resolve().parent.parent
PROFILE_DIR = ROOT / "reports" / "profiles"


def load_raw(dataset: str = "retail") -> pd.DataFrame:
    spec = DATASETS[dataset]
    path = ROOT / spec["raw_path"]
    df = pd.read_csv(path)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df


def profile(df: pd.DataFrame, dataset: str = "retail") -> pd.DataFrame:
    """One-line facts about the dataset used across reports/README."""
    prof = pd.DataFrame([{
        "dataset": dataset,
        "rows": len(df),
        "customers": df["Customer ID"].nunique(),
        "countries": df["Country"].nunique(),
        "date_min": df["InvoiceDate"].min().date(),
        "date_max": df["InvoiceDate"].max().date(),
        "total_revenue": round(df["Revenue"].sum(), 2),
    }])
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    prof.to_csv(PROFILE_DIR / "retail_profile.json", index=False)
    return prof


def load_data(dataset: str = "retail") -> pd.DataFrame:
    """Return the CLEAN (retail-ready) frame for the dataset."""
    return load_raw(dataset)
