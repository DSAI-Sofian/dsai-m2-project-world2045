from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

EXPECTED_FILES = {
    "global_year": ["global_year.parquet", "global_year.csv"],
    "region_year": ["region_year.parquet", "region_year.csv"],
    "country_scores": ["country_scores.parquet", "country_scores.csv"],
    "country_components": ["country_components.parquet", "country_components.csv"],
    "quadrants": ["quadrants.parquet", "quadrants.csv"],
    "rankings": ["rankings.parquet", "rankings.csv"],
    "doomsday_clock": ["doomsday_clock.csv"],
}


@st.cache_data(show_spinner=False)
def load_table(name: str) -> pd.DataFrame:
    for filename in EXPECTED_FILES[name]:
        path = DATA_DIR / filename
        if path.exists():
            if path.suffix == ".parquet":
                return pd.read_parquet(path)
            return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_all() -> dict[str, pd.DataFrame]:
    return {name: load_table(name) for name in EXPECTED_FILES}


@st.cache_data(show_spinner=False)
def get_country_list(country_scores: pd.DataFrame) -> list[str]:
    if country_scores.empty or "country_name" not in country_scores.columns:
        return []
    return sorted(country_scores["country_name"].dropna().unique().tolist())


@st.cache_data(show_spinner=False)
def get_region_list(region_year: pd.DataFrame) -> list[str]:
    if region_year.empty or "region_name" not in region_year.columns:
        return []
    return sorted(region_year["region_name"].dropna().unique().tolist())
