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

    if "region_name" not in region_year.columns:
        st.error("region_year is missing required column: region_name")
        return

    regions = get_region_list(region_year)
    if not regions:
        st.warning("No regions available in the regional dataset.")
        return

    region = st.selectbox("Select region", regions)

    region_df = region_year[region_year["region_name"] == region].copy()
    st.plotly_chart(
        line_chart(
            region_df,
            x="year",
            y="trajectory_score",
            title=f"Regional trajectory: {region}",
        ),
        width="stretch",
    )

    if not rankings.empty:
        region_col = "region_name" if "region_name" in rankings.columns else "region"

        if region_col not in rankings.columns:
            st.warning("Rankings dataset is missing a region column.")
            return

        region_rankings = rankings[rankings[region_col] == region].copy()

        if region_rankings.empty:
            st.info(f"No ranking rows available for {region}.")
            return

        if {"country_name", "rise_potential_score"}.issubset(region_rankings.columns):
            top_rise = (
                region_rankings
                .dropna(subset=["rise_potential_score"])
                .sort_values("rise_potential_score", ascending=False)
                .head(10)
            )

            if not top_rise.empty:
                st.plotly_chart(
                    bar_chart(
                        top_rise,
                        x="country_name",
                        y="rise_potential_score",
                        title=f"Top rise-potential countries in {region}",
                    ),
                    width="stretch",
                )

        st.dataframe(region_rankings.head(20), width="stretch")


main()