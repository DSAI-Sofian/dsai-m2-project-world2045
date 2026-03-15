from __future__ import annotations

import streamlit as st

from lib.loaders import load_all
from lib.charts import bar_chart, gauge_clock, line_chart
from lib.ui import metric_row, page_header, show_empty_data_warning


def main():
    page_header(
        "Global Overview",
        "High-level view of global trajectory, 2045 quadrant distribution, and symbolic systemic-risk framing.",
    )

    data = load_all()
    global_year = data["global_year"]
    quadrants = data["quadrants"]
    clock = data["doomsday_clock"]

    if global_year.empty and quadrants.empty:
        show_empty_data_warning("Global Overview")
        return

    latest_year = None
    latest_score = None
    if not global_year.empty and {"year", "trajectory_score"}.issubset(global_year.columns):
        latest = global_year.sort_values("year").tail(1).iloc[0]
        latest_year = int(latest["year"])
        latest_score = f"{latest['trajectory_score']:.2f}"

    rankable_countries = "-"
    if not quadrants.empty and "country_name" in quadrants.columns:
        rankable_countries = str(quadrants["country_name"].nunique())

    clock_value = "70 sec"
    if not clock.empty and "seconds_to_midnight" in clock.columns:
        clock_value = f"{float(clock['seconds_to_midnight'].iloc[0]):.0f} sec"

    metric_row([
        ("Latest global year", str(latest_year or "-"), None),
        ("Latest global score", latest_score or "-", None),
        ("Rankable forecast countries", rankable_countries, None),
        ("Estimated 2045 clock", clock_value, None),
    ])

    c1, c2 = st.columns((2, 1))
    with c1:
        if not global_year.empty:
            st.plotly_chart(
                line_chart(global_year, x="year", y="trajectory_score", title="Global trajectory trend"),
                width='stretch',
            )
    with c2:
        seconds = 70
        if not clock.empty and "seconds_to_midnight" in clock.columns:
            seconds = float(clock["seconds_to_midnight"].iloc[0])
        st.plotly_chart(gauge_clock(seconds), width='stretch')

    if not quadrants.empty and {"quadrant", "country_count"}.issubset(quadrants.columns):
        st.plotly_chart(
            bar_chart(quadrants, x="quadrant", y="country_count", color="quadrant", title="2045 quadrant counts"),
            width='stretch',
        )

    with st.expander("Narrative findings", expanded=True):
        st.markdown(
            """
            - Global development improves by 2045, but convergence remains limited.
            - Europe retains the strongest structural position, while Africa contains the largest concentration of structural-risk countries.
            - Asia remains the most heterogeneous region, spanning all strategic quadrants.
            - The symbolic Doomsday Clock framing suggests improvement without true systemic safety.
            """
        )


main()
