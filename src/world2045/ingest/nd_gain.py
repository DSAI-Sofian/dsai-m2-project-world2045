from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


ND_GAIN_YEAR_START = 1995
ND_GAIN_YEAR_END = 2023


def _year_columns(columns: Iterable[str]) -> list[str]:
    years: list[str] = []
    for col in columns:
        col_str = str(col).strip()
        if col_str.isdigit():
            year = int(col_str)
            if ND_GAIN_YEAR_START <= year <= ND_GAIN_YEAR_END:
                years.append(col_str)
    return years


def _load_nd_gain_wide(csv_path: str | Path, value_name: str) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"ND-GAIN file not found: {path}")

    df = pd.read_csv(path)

    required_base_cols = {"ISO3", "Name"}
    missing = required_base_cols - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} missing required columns: {sorted(missing)}")

    year_cols = _year_columns(df.columns)
    if not year_cols:
        raise ValueError(f"{path.name} has no year columns in {ND_GAIN_YEAR_START}-{ND_GAIN_YEAR_END}")

    long_df = df.melt(
        id_vars=["ISO3", "Name"],
        value_vars=year_cols,
        var_name="year",
        value_name=value_name,
    )

    long_df = long_df.rename(
        columns={
            "ISO3": "country_iso3",
            "Name": "country_name",
        }
    )

    long_df["country_iso3"] = long_df["country_iso3"].astype(str).str.strip().str.upper()
    long_df["country_name"] = long_df["country_name"].astype(str).str.strip()
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce").astype("Int64")
    long_df[value_name] = pd.to_numeric(long_df[value_name], errors="coerce")

    # Keep rows with valid grain only
    long_df = long_df[
        long_df["country_iso3"].notna()
        & (long_df["country_iso3"] != "")
        & long_df["year"].notna()
    ].copy()

    # Drop duplicate country-year rows if any appear
    long_df = long_df.drop_duplicates(subset=["country_iso3", "year"])

    return long_df


def ingest_nd_gain(raw_root: str | Path, bronze_root: str | Path) -> Path:
    raw_root = Path(raw_root)
    bronze_root = Path(bronze_root)
    bronze_root.mkdir(parents=True, exist_ok=True)

    gain_df = _load_nd_gain_wide(raw_root / "gain.csv", "ndgain_index")
    vulnerability_df = _load_nd_gain_wide(raw_root / "vulnerability.csv", "climate_vulnerability")
    readiness_df = _load_nd_gain_wide(raw_root / "readiness.csv", "adaptation_readiness")

    merged = (
        gain_df[["country_iso3", "country_name", "year", "ndgain_index"]]
        .merge(
            vulnerability_df[["country_iso3", "year", "climate_vulnerability"]],
            on=["country_iso3", "year"],
            how="outer",
        )
        .merge(
            readiness_df[["country_iso3", "year", "adaptation_readiness"]],
            on=["country_iso3", "year"],
            how="outer",
        )
        .sort_values(["country_iso3", "year"])
        .reset_index(drop=True)
    )

    # Reconstruct country_name where needed from gain_df only
    country_lookup = (
        gain_df[["country_iso3", "country_name"]]
        .dropna()
        .drop_duplicates(subset=["country_iso3"])
    )

    merged = merged.merge(country_lookup, on="country_iso3", how="left", suffixes=("", "_lookup"))
    merged["country_name"] = merged["country_name"].fillna(merged["country_name_lookup"])
    merged = merged.drop(columns=["country_name_lookup"], errors="ignore")

    # Canonical column order
    merged = merged[
        [
            "country_iso3",
            "country_name",
            "year",
            "ndgain_index",
            "climate_vulnerability",
            "adaptation_readiness",
        ]
    ]

    output_path = bronze_root / "nd_gain_country_year.parquet"
    merged.to_parquet(output_path, index=False)

    print(f"ND-GAIN bronze rows written: {len(merged)}")
    print(f"ND-GAIN bronze output: {output_path}")

    return output_path