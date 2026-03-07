from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd


VDEM_CANDIDATE_FILES = (
    "V-Dem-CY-Full+Others-v15.csv",
    "V-Dem-CY-Full+Others-v14.csv",
    "V-Dem-CY-Full+Others-v13.csv",
    "V-Dem-CY-Core-v15.csv",
    "V-Dem-CY-Core-v14.csv",
    "V-Dem-CY-Core-v13.csv",
)

# Candidate source columns by warehouse target name.
# The first matching source column found will be used.
COLUMN_CANDIDATES = {
    "country_name": ["country_name"],
    "country_text_id": ["country_text_id"],
    "country_iso3": ["country_text_id", "COWcode_text_id"],
    "year": ["year"],
    "vdem_liberal_democracy_index": ["v2x_libdem"],
    "vdem_electoral_democracy_index": ["v2x_polyarchy"],
    "vdem_judicial_constraints_index": ["v2x_jucon"],
    "vdem_civil_liberties_index": ["v2xcl_libs"],
}

REQUIRED_TARGET_COLUMNS = {
    "country_iso3",
    "year",
    "vdem_liberal_democracy_index",
    "vdem_electoral_democracy_index",
    "vdem_judicial_constraints_index",
    "vdem_civil_liberties_index",
}


def _find_vdem_csv_name(zip_file: zipfile.ZipFile) -> str:
    names = zip_file.namelist()

    for candidate in VDEM_CANDIDATE_FILES:
        for name in names:
            if name.endswith(candidate):
                return name

    csv_names = [name for name in names if name.lower().endswith(".csv")]
    if len(csv_names) == 1:
        return csv_names[0]

    raise FileNotFoundError(
        "Could not locate a V-Dem CSV inside the ZIP. "
        f"Available files: {names}"
    )


def _pick_source_columns(df: pd.DataFrame) -> dict[str, str]:
    selected: dict[str, str] = {}

    for target_col, candidates in COLUMN_CANDIDATES.items():
        for source_col in candidates:
            if source_col in df.columns:
                selected[target_col] = source_col
                break

    missing = REQUIRED_TARGET_COLUMNS - set(selected.keys())
    if missing:
        raise KeyError(
            "Missing required V-Dem columns after candidate matching: "
            f"{sorted(missing)}. Available columns: {list(df.columns)}"
        )

    return selected


def _normalize_iso3(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.upper()
        .replace(
            {
                "XKX": "XKX",  # keep as-is if present; downstream dim join will decide inclusion
                "PSE": "PSE",
            }
        )
    )


def ingest_vdem_from_zip(local_zip_path: str, bronze_root: str = "data/raw") -> str:
    """
    Read a V-Dem ZIP file, extract selected governance indicators,
    and write a conformed country-year CSV.

    Returns the output CSV path as a string.
    """
    zip_path = Path(local_zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"V-Dem ZIP not found: {local_zip_path}")

    bronze_dir = Path(bronze_root) / "vdem"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    output_path = bronze_dir / "vdem_country_year.csv"

    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_name = _find_vdem_csv_name(zf)
        with zf.open(csv_name) as f:
            raw_bytes = f.read()
            df = pd.read_csv(io.BytesIO(raw_bytes), low_memory=False)

    selected_map = _pick_source_columns(df)

    out = pd.DataFrame(
        {
            target_col: df[source_col]
            for target_col, source_col in selected_map.items()
        }
    )

    # Normalize keys
    out["country_iso3"] = _normalize_iso3(out["country_iso3"])
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")

    # Numeric indicators
    numeric_cols = [
        "vdem_liberal_democracy_index",
        "vdem_electoral_democracy_index",
        "vdem_judicial_constraints_index",
        "vdem_civil_liberties_index",
    ]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    # Optional metadata
    out["source_name"] = "V-Dem"
    out["source_version"] = zip_path.stem

    # Basic cleanup
    out = out[out["country_iso3"].notna()]
    out = out[out["year"].notna()]
    out = out.drop_duplicates(subset=["country_iso3", "year"], keep="last")
    out = out.sort_values(["country_iso3", "year"]).reset_index(drop=True)

    out.to_csv(output_path, index=False)

    return str(output_path)


if __name__ == "__main__":
    path = ingest_vdem_from_zip("data/raw/vdem/vdem.zip")
    print(f"V-Dem bronze extract written to: {path}")