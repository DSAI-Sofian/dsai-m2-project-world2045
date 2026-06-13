from __future__ import annotations

import streamlit as st

from lib.loaders import (
    combine_historical_with_forecast,
    get_scenario_label,
    load_all,
    render_forecast_scenario_selector,
)
from lib.charts import bar_chart, gauge_clock, line_chart
from lib.ui import metric_row, page_header, show_empty_data_warning


def main():
    page_header(
        "Global Overview",
        "High-level view of global trajectory, 2045 quadrant distribution, and symbolic systemic-risk framing.",
    )

    data = load_all()
    global_year = data["global_year"]
    country_scores = data["country_scores"]
    quadrants = data["quadrants"]
    clock = data["doomsday_clock"]
    scenario_delta_country = data["scenario_delta_country_2045"]
    scenario_delta_summary = data["scenario_delta_summary"]

    if global_year.empty and quadrants.empty:
        show_empty_data_warning("Global Overview")
        return

    scenario_id = render_forecast_scenario_selector(global_year, key="global_overview_scenario")
    st.caption(get_scenario_label(scenario_id))

    global_year_display = combine_historical_with_forecast(global_year, scenario_id)

    latest_year = None
    latest_score = None
    if not global_year_display.empty and {"year", "trajectory_score"}.issubset(global_year_display.columns):
        latest = global_year_display.sort_values("year").tail(1).iloc[0]
        latest_year = int(latest["year"])
        latest_score = f"{latest['trajectory_score']:.2f}"

    rankable_countries = "-"
    if not country_scores.empty and {"country_iso3", "year", "scenario_id"}.issubset(country_scores.columns):
        rankable_countries = str(
            country_scores[
                (country_scores["year"] == 2045)
                & (country_scores["scenario_id"] == scenario_id)
            ]["country_iso3"].nunique()
        )

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
        if not global_year_display.empty:
            st.plotly_chart(
                line_chart(global_year_display, x="year", y="trajectory_score", title="Global trajectory trend"),
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

    st.subheader("Scenario Comparison (2045)")
    if scenario_delta_summary.empty and scenario_delta_country.empty:
        st.info(
            "Scenario comparison extracts are not available. Export "
            "`scenario_delta_summary` and `scenario_delta_country_2045` to view deltas."
        )
    else:
        st.caption(
            "Interpretation guide: positive score delta means the ML dynamic scenario scores "
            "higher than the static baseline; negative means lower. Rank movement can look "
            "larger than score movement when many countries are clustered close together."
        )
        if not scenario_delta_summary.empty:
            summary_view = scenario_delta_summary.copy()
            if "scope_name" in summary_view.columns:
                summary_view["scope_name"] = summary_view["scope_name"].fillna("global")
            st.markdown("**Score/Rank delta summary (ML dynamic risk vs static baseline)**")
            st.dataframe(summary_view, width="stretch")
        if not scenario_delta_country.empty:
            st.markdown("**Most affected countries by absolute 2045 score delta**")
            country_view = scenario_delta_country.copy()
            if "trajectory_score_delta_ml_minus_static" in country_view.columns:
                country_view = country_view.assign(
                    abs_score_delta=country_view["trajectory_score_delta_ml_minus_static"].abs()
                ).sort_values("abs_score_delta", ascending=False)
            st.dataframe(country_view.head(15), width="stretch")

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
