"""Retail Sales Dashboard — Power BI packaging builder.

One-shot call (used by CI / run script):

    python -m src.powerbi_export

Produces the per-dataset data pack under powerbi/data/retail/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.clean import clean as _clean  # noqa: E402
from src.load_data import load_data as _load_data  # noqa: E402
from src import powerbi_export as _pbe  # noqa: E402


def main() -> None:
    df = _load_data("retail")
    df = _clean(df)
    pack = _pbe.build_pack(df)
    print(f"Power BI pack: {pack['pack']} ({len(list(pack['pack'].iterdir()))} files)")


if __name__ == "__main__":
    main()
