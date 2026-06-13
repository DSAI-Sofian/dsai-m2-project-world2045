from __future__ import annotations

import streamlit as st

from lib.ui import page_header


def main():
    page_header(
        "Methodology",
        "Model framing, forecast filters, data sources, and limitations for academic review.",
    )

    st.subheader("Analytical basis")
    st.markdown(
        """
        - Base data pipeline: Bronze → Silver → Gold on BigQuery and dbt.
        - Core visual layer should read precomputed extracts from gold models only.
        - Forecast rankings should be restricted to `is_rankable_forecast_case = true` and `is_sovereign = true`.
        - Scenario options for forecast years:
          - `baseline_static_risk`: governance, climate, adaptation, and conflict are carried forward.
          - `baseline_ml_dynamic_risk`: climate vulnerability uses validated ML projection where available, with explicit carry-forward fallback.
        - Governance, adaptation, and conflict remain carry-forward in both forecast scenarios for this release.
        """
    )

    st.subheader("Core gold models used in app")
    st.code(
        """
        gold__trajectory_global_year
        gold__region_trajectory_score_year
        gold__country_trajectory_score_year_scenario
        gold__country_rise_potential
        gold__country_trajectory_momentum
        gold__trajectory_country_quadrant
        gold__trajectory_component_breakdown
        """.strip(),
        language="text",
    )

    st.subheader("Limitations")
    st.markdown(
        """
        - Forecast completeness varies by country.
        - Climate ML coverage can be partial; fallback rows still use carry-forward assumptions.
        - Several structural risk dimensions remain held constant beyond the observed window.
        - The Doomsday Clock module is symbolic and not an official Bulletin estimate.
        - The app is an academic decision-support artifact, not a production forecasting system.
        """
    )

    st.subheader("Submission guidance")
    st.markdown(
        """
        For academic demonstration, prioritize speed, clarity, and narrative cohesion over excessive interactivity.
        A smaller, stable app is preferable to live warehouse connections.
        """
    )


main()
