"""
Retail Sales Dashboard — packaging script.
Package the full portfolio (source + outputs + data) into a ZIP for delivery.

Usage:
    python _pack_retail.py            # build + zip
    python _pack_retail.py --zip only # zip only (assumes outputs already generated)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "_dist"
ZIP_NAME = "retail-sales-dashboard-portfolio"


def build_outputs() -> None:
    """Regenerate every artifact the portfolio ships (figures, xlsx, powerbi pack, preview)."""
    import subprocess
    import sys

    print(">>> Running pipeline (stage powerbi + preview)...")
    subprocess.run(
        [sys.executable, "-m", "src.run_retail_analysis", "--dataset", "retail", "--stage", "powerbi", "--stage", "preview"],
        cwd=ROOT,
        check=True,
    )
    print(">>> Done.")


def _copy_tree(src: Path, dst: Path) -> None:
    """Copy a directory tree (recursively), skipping __pycache__ and .git."""
    if src.is_file():
        shutil.copy2(src, dst)
    else:
        dst.mkdir(parents=True, exist_ok=True)
        for child in src.iterdir():
            if child.name in {".git", "__pycache__"}:
                continue
            _copy_tree(child, dst / child.name)


def build_zip() -> Path:
    """Create the delivery ZIP and return its path."""
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    # Top-level folders the user will see when unzipped
    root_items = ["src", "streamlit_app.py", "requirements.txt", "README.md", "reports", "powerbi", "data", "tests", ".github"]
    for name in root_items:
        _copy_tree(ROOT / name, DIST / name)

    zip_path = ROOT / f"{ZIP_NAME}.zip"
    # Archive the contents of DIST so every file sits at the archive root
    shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", root_dir=DIST, base_dir=".")
    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Package the Retail Sales Dashboard portfolio.")
    parser.add_argument("--zip", action="store_true", help="Only create the ZIP (skip rebuilding outputs)")
    args = parser.parse_args()

    if not args.zip:
        build_outputs()
    zip_path = build_zip()
    print(f"ZIP written: {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
