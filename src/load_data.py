"""Retail Sales Dashboard — data loading (clean read only)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import DATASETS

ROOT = Path(__file__).resolve().parent.parent

def load_raw(dataset: str = "retail") -> pd.DataFrame:
    spec = DATASETS[dataset]
    path = ROOT / spec["raw_path"]
    df = pd.read_csv(path)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df



def load_data(dataset: str = "retail") -> pd.DataFrame:
    """Return the CLEAN (retail-ready) frame for the dataset."""
    return load_raw(dataset)
