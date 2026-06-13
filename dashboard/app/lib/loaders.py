from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

DEFAULT_FORECAST_SCENARIO = "baseline_static_risk"
FORECAST_SCENARIOS = [
    "baseline_static_risk",
    "baseline_ml_dynamic_risk",
]
SCENARIO_LABELS = {
    "baseline_static_risk": (
        "Static baseline: governance, climate, adaptation, and conflict are carried "
        "forward where no external projection exists."
    ),
    "baseline_ml_dynamic_risk": (
        "ML dynamic risk: climate vulnerability uses validated ML projection where "
        "available; governance, adaptation, and conflict remain carried forward."
    ),
}

EXPECTED_FILES = {
    "global_year": ["global_year.parquet", "global_year.csv"],
    "region_year": ["region_year.parquet", "region_year.csv"],
    "country_scores": ["country_scores.parquet", "country_scores.csv"],
    "country_components": ["country_components.parquet", "country_components.csv"],
    "quadrants": ["quadrants.parquet", "quadrants.csv"],
    "rankings": ["rankings.parquet", "rankings.csv"],
    "doomsday_clock": ["doomsday_clock.csv"],
    "scenario_delta_country_2045": [
        "scenario_delta_country_2045.parquet",
        "scenario_delta_country_2045.csv",
    ],
    "scenario_delta_summary": [
        "scenario_delta_summary.parquet",
        "scenario_delta_summary.csv",
    ],
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


def get_scenario_label(scenario_id: str) -> str:
    return SCENARIO_LABELS.get(scenario_id, scenario_id)


def get_available_forecast_scenarios(df: pd.DataFrame) -> list[str]:
    if df.empty or "scenario_id" not in df.columns:
        return [DEFAULT_FORECAST_SCENARIO]

    available = (
        df.loc[df["scenario_id"].isin(FORECAST_SCENARIOS), "scenario_id"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )
    if DEFAULT_FORECAST_SCENARIO in available:
        available = [DEFAULT_FORECAST_SCENARIO] + [s for s in available if s != DEFAULT_FORECAST_SCENARIO]
    return available or [DEFAULT_FORECAST_SCENARIO]


def render_forecast_scenario_selector(df: pd.DataFrame, key: str) -> str:
    available = get_available_forecast_scenarios(df)

    options: list[tuple[str, str]] = [(sid, get_scenario_label(sid)) for sid in available]
    selected = st.selectbox(
        "Forecast scenario",
        options=options,
        index=0,
        format_func=lambda option: option[1],
        key=key,
    )
    return selected[0]


def combine_historical_with_forecast(df: pd.DataFrame, scenario_id: str) -> pd.DataFrame:
    if df.empty or "scenario_id" not in df.columns:
        return df

    historical = df[df["scenario_id"] == "historical_observed"]
    forecast = df[df["scenario_id"] == scenario_id]
    if forecast.empty and scenario_id != DEFAULT_FORECAST_SCENARIO:
        forecast = df[df["scenario_id"] == DEFAULT_FORECAST_SCENARIO]

    combined = pd.concat([historical, forecast], ignore_index=True)
    combined = combined.drop_duplicates()

    sort_cols = [c for c in ["country_iso3", "region_name", "year"] if c in combined.columns]
    if sort_cols:
        combined = combined.sort_values(sort_cols)
    return combined
