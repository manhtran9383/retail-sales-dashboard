"""Retail Sales Dashboard — survival / retention."""
from __future__ import annotations

import pandas as pd

from .config import DATASETS, SURVIVAL


def load(df_raw: pd.DataFrame) -> pd.DataFrame:
    return df_raw.copy()


def retention_curve(df: pd.DataFrame, repeat_days: int = 30) -> tuple[pd.DataFrame, float]:
    """Kaplan-Meier-style: % of customers still repeat-free after k days.

    The cumulative retention curve shows the testable, honest retention metric.
    """
    tmp = df.copy()
    first = tmp.groupby("Customer ID")["InvoiceDate"].min().rename("first_purchase")
    second = tmp.groupby("Customer ID")["InvoiceDate"].nth(1).rename("second_purchase")
    joined = pd.concat([first, second], axis=1).reset_index()
    joined["repeat_days"] = (joined["second_purchase"] - joined["first_purchase"]).dt.days
    joined = joined[joined["second_purchase"].notna()].copy()
    n_customers = len(joined)
    sizes = []
    for k in range(1, repeat_days + 1):
        sizes.append({"days_after_first": k,
                      "reactivated": int((joined["repeat_days"] >= k).sum())})
    out = pd.DataFrame(sizes)
    out["repeat_rate_pct"] = (out["reactivated"] / max(n_customers, 1) * 100).round(1)
    overall = float(joined["repeat_days"].le(repeat_days).mean() * 100)
    return out, overall
