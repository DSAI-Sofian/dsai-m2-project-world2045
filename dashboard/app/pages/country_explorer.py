from __future__ import annotations

import streamlit as st

from lib.loaders import get_country_list, load_all
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

    if scores.empty:
        show_empty_data_warning("Country Explorer")
        return

    countries = get_country_list(scores)
    default_country = "Singapore" if "Singapore" in countries else countries[0]
    country = st.selectbox("Select country", countries, index=countries.index(default_country))

    score_df = scores[scores["country_name"] == country].copy()
    comp_df = components[components["country_name"] == country].copy() if not components.empty else components

    latest = score_df.sort_values("year").tail(1).iloc[0]
    metric_row([
        ("2045 trajectory score", f"{latest.get('trajectory_score_2045', latest.get('trajectory_score', 0)):.2f}", None),
        ("Momentum score", f"{latest.get('momentum_score', 0):.2f}", None),
        ("Rise potential", f"{latest.get('rise_potential_score', 0):.2f}", None),
        ("Quadrant", str(latest.get('quadrant', '-')), None),
    ])

    c1, c2 = st.columns((2, 1))
    with c1:
        st.plotly_chart(
            line_chart(score_df, x="year", y="trajectory_score", title=f"Trajectory path: {country}"),
            width='stretch',
        )
    with c2:
        summary_cols = [c for c in ["region_name", "forecast_completeness", "scenario_id"] if c in latest.index]
        if summary_cols:
            st.dataframe(latest[summary_cols].to_frame("value"), width='stretch')

    if not comp_df.empty and {"component", "component_score"}.issubset(comp_df.columns):
        latest_component_year = comp_df["year"].max()
        st.plotly_chart(
            bar_chart(
                comp_df[comp_df["year"] == latest_component_year],
                x="component",
                y="component_score",
                color="component",
                title=f"Component decomposition ({latest_component_year})",
            ),
            width='stretch',
        )

    st.dataframe(score_df.sort_values("year", ascending=False).head(15), width='stretch')


main()
