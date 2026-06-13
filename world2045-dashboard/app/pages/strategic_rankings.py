from __future__ import annotations

import streamlit as st

from lib.loaders import load_all
from lib.charts import bar_chart, scatter_chart
from lib.ui import page_header, show_empty_data_warning


def main():
    page_header(
        "Strategic Rankings",
        "Filterable ranking tables for rise potential, momentum, and 2045 quadrant positioning.",
    )
    data = load_all()
    rankings = data["rankings"]

    if rankings.empty:
        show_empty_data_warning("Strategic Rankings")
        return

    only_rankable = st.toggle("Only rankable sovereign forecast cases", value=True)
    quadrant_filter = st.multiselect(
        "Quadrants",
        sorted(rankings["quadrant"].dropna().unique().tolist()) if "quadrant" in rankings.columns else [],
        default=sorted(rankings["quadrant"].dropna().unique().tolist()) if "quadrant" in rankings.columns else [],
    )

    df = rankings.copy()
    if only_rankable and "is_rankable_forecast_case" in df.columns:
        df = df[df["is_rankable_forecast_case"] == True]
    if only_rankable and "is_sovereign" in df.columns:
        df = df[df["is_sovereign"] == True]
    if quadrant_filter and "quadrant" in df.columns:
        df = df[df["quadrant"].isin(quadrant_filter)]

    c1, c2 = st.columns(2)
    with c1:
        if {"country_name", "rise_potential_score"}.issubset(df.columns):
            st.plotly_chart(
                bar_chart(df.sort_values("rise_potential_score", ascending=False).head(15), x="country_name", y="rise_potential_score", title="Top rise-potential countries"),
                width='stretch',
            )
    with c2:
        if {"country_name", "momentum_score"}.issubset(df.columns):
            st.plotly_chart(
                bar_chart(df.sort_values("momentum_score", ascending=False).head(15), x="country_name", y="momentum_score", title="Top momentum countries"),
                width='stretch',
            )

    if {"trajectory_score_2045", "momentum_score", "quadrant", "country_name"}.issubset(df.columns):
        st.plotly_chart(
            scatter_chart(df, x="trajectory_score_2045", y="momentum_score", color="quadrant", hover_name="country_name", title="2045 quadrant scatter"),
            width='stretch',
        )

    st.dataframe(df.sort_values(["rise_potential_score", "momentum_score"], ascending=False), width='stretch')


main()
