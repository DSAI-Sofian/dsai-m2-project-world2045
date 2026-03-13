from __future__ import annotations

from pathlib import Path
import pandas as pd


RAW_PATH = Path("data/raw/wpp2024/wpp2024_population_standard.csv")
OUT_PATH = Path("data/processed/wpp/wpp_projection_long.csv")


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    usecols = [
        "Variant",
        "Region, subregion, country or area *",
        "Location code",
        "ISO3 Alpha-code",
        "Type",
        "Year",
        "Total Population, as of 1 July (thousands)",
        "Total Fertility Rate (live births per woman)",
        "Life Expectancy at Birth, both sexes (years)",
        "Net Number of Migrants (thousands)",
    ]

    df = pd.read_csv(
        RAW_PATH,
        skiprows=16,
        usecols=usecols,
        encoding="utf-8-sig",
        low_memory=False,
    )

    df = df.rename(
        columns={
            "Variant": "projection_variant",
            "Region, subregion, country or area *": "country_name",
            "Location code": "location_code",
            "ISO3 Alpha-code": "country_iso3",
            "Type": "location_type",
            "Year": "year",
            "Total Population, as of 1 July (thousands)": "population_total_thousands",
            "Total Fertility Rate (live births per woman)": "fertility_rate",
            "Life Expectancy at Birth, both sexes (years)": "life_expectancy_birth_both",
            "Net Number of Migrants (thousands)": "net_migrants_thousands",
        }
    )

    print(f"Initial rows read: {len(df):,}")

    df["location_type"] = df["location_type"].astype(str).str.strip()
    df["country_iso3"] = df["country_iso3"].astype(str).str.strip().str.upper()

    print("\nUnique location_type values:")
    print(df["location_type"].value_counts(dropna=False).head(20).to_string())

    # Keep likely country rows
    country_type_mask = df["location_type"].str.lower().isin(
        ["country/area", "country", "area", "country or area"]
    )

    # Fallback: rows with valid ISO3 are generally country-level
    iso3_mask = df["country_iso3"].str.len() == 3

    df = df[country_type_mask | iso3_mask].copy()
    print(f"\nRows after country-level filter: {len(df):,}")

    numeric_cols = [
        "year",
        "population_total_thousands",
        "fertility_rate",
        "life_expectancy_birth_both",
        "net_migrants_thousands",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["year"].between(2024, 2045)].copy()
    print(f"Rows after 2024-2045 filter: {len(df):,}")

    df["projection_variant"] = df["projection_variant"].astype(str).str.strip()

    df["projection_source"] = "UN_WPP_2024"
    df["scenario_family"] = "WPP"
    df["scenario_id"] = "baseline"

    df = df.sort_values(["country_iso3", "year"]).reset_index(drop=True)

    df.to_csv(OUT_PATH, index=False)

    print(f"\nWrote {len(df):,} rows to {OUT_PATH}")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()