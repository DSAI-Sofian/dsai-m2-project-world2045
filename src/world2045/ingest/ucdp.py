from __future__ import annotations

from pathlib import Path
import re

import pandas as pd


UCDP_COUNTRY_FIXES = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cambodia (Kampuchea)": "Cambodia",
    "Congo": "Congo",
    "DR Congo (Zaire)": "Democratic Republic of the Congo",
    "Ivory Coast": "Côte d'Ivoire",
    "Kyrgyzstan": "Kyrgyz Republic",
    "Laos": "Lao PDR",
    "Macedonia": "North Macedonia",
    "Russia (Soviet Union)": "Russian Federation",
    "Serbia (Yugoslavia)": "Serbia",
    "South Korea": "Korea, Rep.",
    "North Korea": "Korea, Dem. People's Rep.",
    "Syria": "Syrian Arab Republic",
    "Taiwan": "Taiwan, China",
    "United States of America": "United States",
    "Vietnam (North Vietnam)": "Vietnam",
    "Yemen (North Yemen)": "Yemen, Rep.",
    "Yemen (South Yemen)": "Yemen, Rep.",
}


def _clean_country_name(name: str) -> str:
    name = str(name).strip().strip('"').strip()
    name = re.sub(r"\s+", " ", name)
    return UCDP_COUNTRY_FIXES.get(name, name)


def _split_location_field(value: str) -> list[str]:
    if pd.isna(value):
        return []

    parts = [p.strip() for p in str(value).split(",")]
    cleaned = []
    for p in parts:
        p2 = _clean_country_name(p)
        if p2:
            cleaned.append(p2)
    return cleaned


def _explode_locations(df: pd.DataFrame, location_col: str) -> pd.DataFrame:
    out = df.copy()
    out["country_name"] = out[location_col].apply(_split_location_field)
    out = out.explode("country_name")
    out = out[out["country_name"].notna()].copy()
    out["country_name"] = out["country_name"].astype(str).str.strip()
    return out


def _build_country_lookup() -> pd.DataFrame:
    # 1) Try local project files first
    candidates = [
        Path("data/bronze/wdi/wdi_country_dim.csv"),
        Path("data/raw/wdi/country_dim.csv"),
        Path("dbt/seeds/country_overrides.csv"),
        Path("seeds/country_overrides.csv"),
    ]

    for path in candidates:
        if path.exists():
            df = pd.read_csv(path)
            cols_lower = {c.lower(): c for c in df.columns}

            name_candidates = [
                "country_name",
                "name",
                "country",
                "economy",
                "raw_country_name",
            ]
            iso_candidates = [
                "country_iso3",
                "iso3",
                "country_code",
                "id",
                "canonical_country_iso3",
            ]

            name_col = next((cols_lower[c] for c in name_candidates if c in cols_lower), None)
            iso_col = next((cols_lower[c] for c in iso_candidates if c in cols_lower), None)

            if name_col and iso_col:
                out = (
                    df[[name_col, iso_col]]
                    .rename(columns={name_col: "country_name", iso_col: "country_iso3"})
                    .dropna()
                    .copy()
                )
                out["country_name"] = out["country_name"].astype(str).str.strip()
                out["country_iso3"] = out["country_iso3"].astype(str).str.strip().str.upper()
                out = out[out["country_iso3"].str.len() == 3]
                out = out.drop_duplicates(subset=["country_name"])
                if not out.empty:
                    return out

    # 2) Fallback to pycountry if installed
    try:
        import pycountry

        rows = []
        for c in pycountry.countries:
            rows.append(
                {
                    "country_name": c.name.strip(),
                    "country_iso3": c.alpha_3.strip().upper(),
                }
            )

            # common alternative names
            if hasattr(c, "official_name"):
                rows.append(
                    {
                        "country_name": str(c.official_name).strip(),
                        "country_iso3": c.alpha_3.strip().upper(),
                    }
                )

        # add manual aliases commonly needed for UCDP/WDI harmonization
        manual_aliases = {
            "Bolivia": "BOL",
            "Bosnia-Herzegovina": "BIH",
            "Brunei": "BRN",
            "Cambodia (Kampuchea)": "KHM",
            "Cape Verde": "CPV",
            "Central African Republic": "CAF",
            "Congo": "COG",
            "DR Congo (Zaire)": "COD",
            "Egypt": "EGY",
            "Gambia": "GMB",
            "Iran": "IRN",
            "Ivory Coast": "CIV",
            "Kyrgyz Republic": "KGZ",
            "Laos": "LAO",
            "Micronesia": "FSM",
            "Moldova": "MDA",
            "North Korea": "PRK",
            "North Macedonia": "MKD",
            "Palestine": "PSE",
            "Russia": "RUS",
            "Russia (Soviet Union)": "RUS",
            "South Korea": "KOR",
            "Syria": "SYR",
            "Taiwan": "TWN",
            "Tanzania": "TZA",
            "Turkey": "TUR",
            "United Kingdom": "GBR",
            "United States": "USA",
            "United States of America": "USA",
            "Venezuela": "VEN",
            "Vietnam": "VNM",
            "Vietnam (North Vietnam)": "VNM",
            "Yemen": "YEM",
            "Yemen (North Yemen)": "YEM",
            "Yemen (South Yemen)": "YEM",
        }

        for name, iso3 in manual_aliases.items():
            rows.append({"country_name": name, "country_iso3": iso3})

        out = pd.DataFrame(rows).dropna().drop_duplicates(subset=["country_name"])
        return out

    except ImportError:
        raise FileNotFoundError(
            "Could not build a country lookup. Checked local files and pycountry is not installed. "
            "Expected one of: data/bronze/wdi/wdi_country_dim.csv, data/raw/wdi/country_dim.csv, "
            "dbt/seeds/country_overrides.csv, seeds/country_overrides.csv"
        )


def _load_prio(prio_path: Path) -> pd.DataFrame:
    df = pd.read_csv(prio_path)

    keep = [
        "location",
        "year",
        "type_of_conflict",
        "intensity_level",
    ]
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise ValueError(f"UCDP-PRIO missing required columns: {missing}")

    df = df[keep].copy()
    df = _explode_locations(df, "location")

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["type_of_conflict"] = pd.to_numeric(df["type_of_conflict"], errors="coerce")
    df["intensity_level"] = pd.to_numeric(df["intensity_level"], errors="coerce")

    agg = (
        df.groupby(["country_name", "year"], dropna=False)
        .agg(
            conflict_incidence=("intensity_level", lambda x: int((x >= 1).any())),
            interstate_conflict=("type_of_conflict", lambda x: int((x == 2).any())),
            civil_conflict=("type_of_conflict", lambda x: int((x == 3).any())),
            internationalized_conflict=("type_of_conflict", lambda x: int((x == 4).any())),
            war_intensity=("intensity_level", lambda x: int((x == 2).any())),
        )
        .reset_index()
    )

    return agg


def _load_brd(brd_path: Path) -> pd.DataFrame:
    df = pd.read_csv(brd_path)

    keep = [
        "location_inc",
        "year",
        "bd_best",
    ]
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise ValueError(f"UCDP BRD missing required columns: {missing}")

    df = df[keep].copy()
    df = _explode_locations(df, "location_inc")

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["bd_best"] = pd.to_numeric(df["bd_best"], errors="coerce").fillna(0)

    agg = (
        df.groupby(["country_name", "year"], dropna=False)
        .agg(
            battle_deaths=("bd_best", "sum"),
        )
        .reset_index()
    )

    return agg


def ingest_ucdp(raw_root: str | Path, bronze_root: str | Path) -> Path:
    raw_root = Path(raw_root)
    bronze_root = Path(bronze_root)
    bronze_root.mkdir(parents=True, exist_ok=True)

    prio_path = raw_root / "UCDP-PRIO.csv"
    brd_path = raw_root / "UCDP BRD.csv"

    if not prio_path.exists():
        raise FileNotFoundError(f"UCDP-PRIO file not found: {prio_path}")
    if not brd_path.exists():
        raise FileNotFoundError(f"UCDP BRD file not found: {brd_path}")

    prio_df = _load_prio(prio_path)
    brd_df = _load_brd(brd_path)

    merged = prio_df.merge(
        brd_df,
        on=["country_name", "year"],
        how="outer",
    )

    merged["battle_deaths"] = merged["battle_deaths"].fillna(0)

    for col in [
        "conflict_incidence",
        "interstate_conflict",
        "civil_conflict",
        "internationalized_conflict",
        "war_intensity",
    ]:
        merged[col] = merged[col].fillna(0).astype(int)

    country_lookup = _build_country_lookup()

    merged = merged.merge(country_lookup, on="country_name", how="left")

    unmatched = (
        merged[merged["country_iso3"].isna()]["country_name"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
    if unmatched:
        print("UCDP unmatched country names:")
        for name in unmatched[:50]:
            print(f"  - {name}")
        if len(unmatched) > 50:
            print(f"  ... and {len(unmatched) - 50} more")

    merged = merged[merged["country_iso3"].notna()].copy()
    merged["country_iso3"] = merged["country_iso3"].astype(str).str.upper()

    final_df = (
        merged[
            [
                "country_iso3",
                "year",
                "battle_deaths",
                "conflict_incidence",
                "interstate_conflict",
                "civil_conflict",
                "internationalized_conflict",
                "war_intensity",
            ]
        ]
        .drop_duplicates(subset=["country_iso3", "year"])
        .sort_values(["country_iso3", "year"])
        .reset_index(drop=True)
    )

    output_path = bronze_root / "ucdp_conflict_country_year.parquet"
    final_df.to_parquet(output_path, index=False)

    print(f"UCDP bronze rows written: {len(final_df)}")
    print(f"UCDP bronze output: {output_path}")

    return output_path