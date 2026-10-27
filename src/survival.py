"""Retail Sales Dashboard — survival / retention."""
from __future__ import annotations

import pandas as pd


def load(df_raw: pd.DataFrame) -> pd.DataFrame:
    return df_raw.copy()


def retention_curve(df: pd.DataFrame, repeat_days: int = 30) -> tuple[pd.DataFrame, float]:
    """Repeat-purchase retention (honest, all customers).

    A customer is "retained" at k days if they made a *first* purchase at least
    k days after their first. Customers with only one purchase are censored
    (they never repeat) and sit in the denominator, so the rate is reported over
    the full customer base (2 836) rather than only repeat buyers (1 910).
    This avoids the survivorship bias of reporting only among repeat buyers.
    """
    tmp = df.copy()
    g = tmp.groupby("Customer ID")["InvoiceDate"]
    # Align BOTH on the same index (Customer ID) so the join is lossless.
    first = g.min().rename("first_purchase")
    second = g.agg(lambda s: s.iloc[1] if len(s) > 1 else pd.NaT).rename("second_purchase")
    joined = pd.concat([first, second], axis=1).reset_index()
    joined["repeat_days"] = (joined["second_purchase"] - joined["first_purchase"]).dt.days
    joined = joined[joined["second_purchase"].notna()].copy()
    # Denominator = FULL customer base. Non-repeaters (one-off) are censored:
    # they never repeat, so they lower the rate.
    n_customers = df["Customer ID"].nunique()
    sizes = []
    for k in range(1, repeat_days + 1):
        sizes.append({"days_after_first": k,
                      "reactivated": int((joined["repeat_days"] >= k).sum())})
    out = pd.DataFrame(sizes)
    out["repeat_rate_pct"] = (out["reactivated"] / max(n_customers, 1) * 100).round(1)
    # Honest overall: customers with a repeat within 30 days / ALL customers
    overall = float(joined["repeat_days"].le(repeat_days).sum() / max(n_customers, 1) * 100)
    return out, overall
