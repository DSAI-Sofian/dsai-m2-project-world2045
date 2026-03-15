from __future__ import annotations

import streamlit as st

from lib.loaders import get_region_list, load_all
from lib.charts import bar_chart, line_chart
from lib.ui import page_header, show_empty_data_warning


def main():
    page_header(
        "Regional View",
        "Compare regional trajectory trends, quadrant mix, and leading countries within each region.",
    )
    data = load_all()
    region_year = data["region_year"]
    rankings = data["rankings"]

    if region_year.empty:
        show_empty_data_warning("Regional View")
        return

    regions = get_region_list(region_year)
    region = st.selectbox("Select region", regions)

    region_df = region_year[region_year["region_name"] == region].copy()
    st.plotly_chart(
        line_chart(region_df, x="year", y="trajectory_score", title=f"Regional trajectory: {region}"),
        width='stretch',
    )

    if not rankings.empty:
        region_rankings = rankings[rankings["region_name"] == region].copy()
        if {"country_name", "rise_potential_score"}.issubset(region_rankings.columns):
            st.plotly_chart(
                bar_chart(
                    region_rankings.sort_values("rise_potential_score", ascending=False).head(10),
                    x="country_name",
                    y="rise_potential_score",
                    title=f"Top rise-potential countries in {region}",
                ),
                width='stretch',
            )
        st.dataframe(region_rankings.head(20), width='stretch')


main()
