from __future__ import annotations

import streamlit as st

from lib.loaders import load_all
from lib.ui import page_header


def main():
    page_header(
        "Methodology",
        "Model framing, forecast filters, data sources, and limitations for academic review.",
    )
    data = load_all()
    metrics = data["model_evidence_metrics_summary"]
    decisions = data["model_selection_decision"]

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

    st.subheader("How We Tested ML (Plain Language)")
    st.markdown(
        """
        - We compared each ML method against the existing carry-forward baseline.
        - We trained on earlier years and tested on later unseen years (rolling-origin validation).
        - Main accuracy metric: **MAE** (Mean Absolute Error).
        - Simple interpretation of MAE: the average forecast miss size.
        - Lower MAE is better.
        - This project uses classical tabular ML. No foundation model fine-tuning was performed.
        """
    )

    st.subheader("Model Evidence")
    if metrics.empty and decisions.empty:
        st.info(
            "Model evidence extracts are not available. Add "
            "`model_evidence_metrics_summary` and `model_selection_decision` "
            "to the dashboard data folder to display this section."
        )
    else:
        if not metrics.empty:
            st.markdown("**Model comparison by indicator (lower MAE is better)**")
            st.dataframe(metrics, width="stretch")
        if not decisions.empty:
            st.markdown("**Final decision by indicator**")
            st.dataframe(decisions, width="stretch")

    st.subheader("Why Only Climate Is ML-Integrated")
    st.markdown(
        """
        - `climate_vulnerability`: integrated because it showed stable improvement over carry-forward.
        - `adaptation_readiness`: not integrated because improvement was too small.
        - `vdem_liberal_democracy_index`: not integrated because ML underperformed carry-forward.
        - `conflict_severity`: deferred due volatility and higher instability risk.
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
        - ML scenario is comparative and sensitivity-oriented, not definitive forecast truth.
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
