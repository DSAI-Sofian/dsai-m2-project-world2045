from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.loaders import (
    combine_historical_with_forecast,
    get_country_list,
    get_scenario_label,
    load_all,
    render_forecast_scenario_selector,
)
from lib.charts import bar_chart, line_chart
from lib.ui import metric_row, page_header, show_empty_data_warning


def main():
    page_header(
        "Country Explorer",
        "Inspect 1995–2045 country trajectory, component breakdown, rise potential, momentum, and quadrant assignment.",
    )

    data = load_all()
    scores = data["country_scores"]
    components = data["country_components"]
    rankings = data["rankings"]

    if scores.empty:
        show_empty_data_warning("Country Explorer")
        return

    required_score_cols = {"country_name", "country_iso3", "year", "trajectory_score"}
    if not required_score_cols.issubset(scores.columns):
        missing = sorted(required_score_cols - set(scores.columns))
        st.error(f"country_scores is missing required columns: {', '.join(missing)}")
        return

    scenario_id = render_forecast_scenario_selector(scores, key="country_explorer_scenario")
    st.caption(get_scenario_label(scenario_id))

    scores_display = combine_historical_with_forecast(scores, scenario_id)
    components_display = combine_historical_with_forecast(components, scenario_id)

    countries = get_country_list(scores_display)
    if not countries:
        st.warning("No countries available in the country dataset.")
        return

    default_country = "Singapore" if "Singapore" in countries else countries[0]
    country = st.selectbox("Select country", countries, index=countries.index(default_country))

    score_df = scores_display[scores_display["country_name"] == country].copy()
    if score_df.empty:
        st.warning(f"No score rows available for {country}.")
        return

    score_df = score_df.sort_values("year")
    country_iso3 = score_df["country_iso3"].dropna().iloc[0]

    comp_df = (
        components_display[components_display["country_name"] == country].copy()
        if not components_display.empty and "country_name" in components_display.columns
        else components_display
    )

    ranking_row = None
    if not rankings.empty and {"country_iso3", "country_name"}.issubset(rankings.columns):
        ranking_match = rankings[rankings["country_iso3"] == country_iso3].copy()
        if not ranking_match.empty:
            ranking_row = ranking_match.iloc[0]

    latest = score_df.iloc[-1]

    trajectory_2045 = None
    score_2045_df = score_df[score_df["year"] == 2045]
    if not score_2045_df.empty:
        trajectory_2045 = float(score_2045_df["trajectory_score"].iloc[0])
    else:
        trajectory_2045 = float(latest.get("trajectory_score", 0))

    momentum_score = float(ranking_row["momentum_score"]) if ranking_row is not None and "momentum_score" in ranking_row.index else 0.0
    rise_potential_score = float(ranking_row["rise_potential_score"]) if ranking_row is not None and "rise_potential_score" in ranking_row.index else 0.0
    quadrant = str(ranking_row["quadrant"]) if ranking_row is not None and "quadrant" in ranking_row.index else "-"

    metric_row(
        [
            ("2045 trajectory score", f"{trajectory_2045:.2f}", None),
            ("Momentum score", f"{momentum_score:.2f}", None),
            ("Rise potential", f"{rise_potential_score:.2f}", None),
            ("Quadrant", quadrant, None),
        ]
    )

    c1, c2 = st.columns((2, 1))

    with c1:
        st.plotly_chart(
            line_chart(
                score_df,
                x="year",
                y="trajectory_score",
                title=f"Trajectory path: {country}",
            ),
            width="stretch",
        )

    with c2:
        summary = {}
        if "region" in latest.index:
            summary["region"] = latest["region"]
        if "subregion" in latest.index:
            summary["subregion"] = latest["subregion"]
        if "income_group" in latest.index:
            summary["income_group"] = latest["income_group"]
        if "forecast_score_completeness" in latest.index:
            summary["forecast_score_completeness"] = latest["forecast_score_completeness"]
        if "scenario_id" in latest.index:
            summary["scenario_id"] = latest["scenario_id"]

        if ranking_row is not None:
            if "momentum_band" in ranking_row.index:
                summary["momentum_band"] = ranking_row["momentum_band"]
            if "quadrant" in ranking_row.index:
                summary["quadrant"] = ranking_row["quadrant"]

        if summary:
            st.dataframe(pd.DataFrame.from_dict(summary, orient="index", columns=["value"]), width="stretch")

        if score_2045_df.empty:
            st.info("2045 row is unavailable for this scenario in the current extract.")
        else:
            metadata_cols = [
                "climate_vulnerability_projection_source",
                "climate_vulnerability_forecast_method",
            ]
            available_metadata = [col for col in metadata_cols if col in score_2045_df.columns]
            if available_metadata:
                st.markdown("**Climate projection metadata (2045)**")
                st.dataframe(score_2045_df[available_metadata].head(1), width="stretch")

    if not comp_df.empty and {"component", "value"}.issubset(comp_df.columns):
        latest_component_year = int(comp_df["year"].max())
        comp_latest = comp_df[comp_df["year"] == latest_component_year].copy()

        if not comp_latest.empty:
            st.plotly_chart(
                bar_chart(
                    comp_latest,
                    x="component",
                    y="value",
                    color="component",
                    title=f"Component decomposition ({latest_component_year})",
                ),
                width="stretch",
            )

    st.dataframe(score_df.sort_values("year", ascending=False).head(15), width="stretch")


main()
