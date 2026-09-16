#!/usr/bin/env python3
"""Toy script for Swanlaab Code teaser — fake portfolio numbers only."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "sample_portfolio.csv"


def main() -> None:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    total_arr = sum(float(r["arr_keur"]) for r in rows)
    watch = [r["company"] for r in rows if r["status"] == "watch"]
    avg_growth = sum(float(r["mom_growth_pct"]) for r in rows) / len(rows)

    print(f"Participadas en muestra: {len(rows)}")
    print(f"ARR agregado (k€, inventado): {total_arr:.0f}")
    print(f"Crecimiento MoM medio: {avg_growth:.1f}%")
    print(f"En watch: {', '.join(watch) if watch else 'ninguna'}")


if __name__ == "__main__":
    main()
