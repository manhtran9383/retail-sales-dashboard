"""Unit tests for report.make_powerbi_pack output schema (P2)."""
from pathlib import Path
import pandas as pd

from src.report import make_powerbi_pack

RAW = Path(__file__).parent.parent / "data" / "raw" / "REtail_Sales.csv"

EXPECTED_FILES = {
    "dim_product.csv": ["StockCode", "ProductName", "total_revenue", "total_qty"],
    "dim_country.csv": ["Country", "CountryName", "revenue"],
    "dim_date.csv": ["Month", "Revenue"],
    "fact_sales.csv": ["Invoice", "StockCode", "Customer ID", "InvoiceDate", "Quantity", "Price", "Revenue"],
    "kpi_monthly_revenue.csv": ["Month", "Revenue"],
    "kpi_top_products.csv": ["StockCode", "Description", "Revenue"],
    "kpi_survival.csv": ["retention_rate_pct"],
    "kpi_targeting_lift.csv": ["StockCode", "Revenue"],
}


def _read_raw():
    return pd.read_csv(RAW, parse_dates=["InvoiceDate"])


def test_make_powerbi_pack_schema(tmp_path):
    df = _read_raw()
    out = make_powerbi_pack(df, tmp_path)
    pack = out["pack"]
    assert pack.exists(), "pack directory was not created"

    files = sorted(p.name for p in pack.iterdir())
    expected = sorted(EXPECTED_FILES.keys())
    assert files == expected, f"files mismatch: {files} != {expected}"

    for name, cols in EXPECTED_FILES.items():
        frame = pd.read_csv(pack / name)
        assert list(frame.columns) == cols, (
            f"{name}: expected {cols}, got {list(frame.columns)}"
        )


def test_make_powerbi_pack_retention_kpi_positive():
    from src.survival import retention_curve

    df = _read_raw()
    _, rate = retention_curve(df, repeat_days=30)
    assert rate > 0, "retention rate must be positive after the index fix"
