"""Retail Sales Dashboard — Power BI packaging builder.

One-shot call (used by CI / run script):
    python -m src.powerbi_export

Produces the per-dataset data pack under powerbi/data/retail/.
"""
from __future__ import annotations

from pathlib import Path

from src import load_data, clean
from src import powerbi_export as pbe

ROOT = Path(__file__).resolve().parent.parent


def main():
    for key in ["retail"]:
        spec = {"key": key, "display_name": "Online Retail II"}
        # lazily import to avoid heavy deps at module import
        import pandas as pd
        df = load_data(key)
        df = clean(df)
        pbe.build_pack(df)
        print(f"Power BI pack: powerbi/data/retail/ ({len(list((pbe._pack_dir()).iterdir()))} files)")


if __name__ == "__main__":
    main()
