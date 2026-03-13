#!/usr/bin/env python3
"""Template ingestion script for country-year climate projection features.

This is intentionally conservative and lightweight.
Use it only after selecting a compact country-year climate scenario source.
Expected output columns:
    country_iso3, year, scenario_id, temperature_anomaly_c, precipitation_anomaly_pct
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-year", type=int, default=2024)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path, low_memory=True)
    required = {"country_iso3", "year", "scenario_id", "temperature_anomaly_c"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    keep = [c for c in [
        "country_iso3",
        "year",
        "scenario_id",
        "temperature_anomaly_c",
        "precipitation_anomaly_pct",
    ] if c in df.columns]

    out_df = df[keep].copy()
    out_df["year"] = pd.to_numeric(out_df["year"], errors="coerce").astype("Int64")
    out_df = out_df[out_df["year"].notna() & (out_df["year"] >= args.min_year)]
    out_df["country_iso3"] = out_df["country_iso3"].astype(str).str.upper().str.strip()
    out_df["scenario_id"] = out_df["scenario_id"].astype(str).str.upper().str.strip()

    for col in ["temperature_anomaly_c", "precipitation_anomaly_pct"]:
        if col in out_df.columns:
            out_df[col] = pd.to_numeric(out_df[col], errors="coerce")

    out_df = out_df.drop_duplicates()
    out_df.to_parquet(output_path, index=False)

    print(f"Wrote {len(out_df):,} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
