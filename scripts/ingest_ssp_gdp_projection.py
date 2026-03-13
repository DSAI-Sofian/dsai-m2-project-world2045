#!/usr/bin/env python3
"""Ingest SSP GDP projections into a bronze-ready parquet file.

Assumptions:
- Input is a flat CSV extract from an SSP scenario source.
- Columns can vary by source version, so the script uses candidate mappings.
- This script keeps memory usage low with chunked reads.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_COLUMN_CANDIDATES = {
    "country_iso3": ["country_iso3", "ISO3", "iso3", "REGION"],
    "year": ["year", "Year", "TIME"],
    "scenario_id": ["scenario", "Scenario", "SCENARIO"],
    "gdp_ppp": ["gdp_ppp", "GDP|PPP", "GDP_PPP", "Value"],
    "gdp_per_capita": ["gdp_per_capita", "GDP_per_capita", "gdp_pc"],
}


def resolve_column(df: pd.DataFrame, candidates: list[str], required: bool = True) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    if required:
        raise KeyError(f"None of the candidate columns were found: {candidates}")
    return None



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-year", type=int, default=2024)
    parser.add_argument("--chunksize", type=int, default=50000)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(input_path, chunksize=args.chunksize, low_memory=True):
        country_col = resolve_column(chunk, DEFAULT_COLUMN_CANDIDATES["country_iso3"])
        year_col = resolve_column(chunk, DEFAULT_COLUMN_CANDIDATES["year"])
        scenario_col = resolve_column(chunk, DEFAULT_COLUMN_CANDIDATES["scenario_id"])
        gdp_col = resolve_column(chunk, DEFAULT_COLUMN_CANDIDATES["gdp_ppp"])
        gdp_pc_col = resolve_column(chunk, DEFAULT_COLUMN_CANDIDATES["gdp_per_capita"], required=False)

        use_cols = [country_col, year_col, scenario_col, gdp_col]
        if gdp_pc_col:
            use_cols.append(gdp_pc_col)

        projection = chunk[use_cols].copy()
        rename_map = {
            country_col: "country_iso3",
            year_col: "year",
            scenario_col: "scenario_id",
            gdp_col: "gdp_ppp",
        }
        if gdp_pc_col:
            rename_map[gdp_pc_col] = "gdp_per_capita"
        projection = projection.rename(columns=rename_map)

        projection["year"] = pd.to_numeric(projection["year"], errors="coerce").astype("Int64")
        projection["gdp_ppp"] = pd.to_numeric(projection["gdp_ppp"], errors="coerce")
        if "gdp_per_capita" in projection.columns:
            projection["gdp_per_capita"] = pd.to_numeric(projection["gdp_per_capita"], errors="coerce")
        projection = projection[projection["year"].notna() & (projection["year"] >= args.min_year)]
        projection["country_iso3"] = projection["country_iso3"].astype(str).str.upper().str.strip()
        projection["scenario_id"] = projection["scenario_id"].astype(str).str.strip().str.upper()
        chunks.append(projection)

    if not chunks:
        raise ValueError("No rows were ingested from the SSP GDP input.")

    out_df = pd.concat(chunks, ignore_index=True)
    out_df = out_df.drop_duplicates()
    out_df.to_parquet(output_path, index=False)

    print(f"Wrote {len(out_df):,} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
