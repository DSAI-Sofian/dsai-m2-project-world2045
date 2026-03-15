from __future__ import annotations

import streamlit as st

from lib.loaders import load_all
from lib.charts import bar_chart, gauge_clock
from lib.ui import page_header


def main():
    page_header(
        "2045 Doomsday Clock",
        "A symbolic interpretation of systemic global risk using World2045 findings.",
    )
    data = load_all()
    clock = data["doomsday_clock"]

    if clock.empty:
        seconds = 70
        risk_df = None
    else:
        seconds = float(clock["seconds_to_midnight"].iloc[0])
        risk_df = clock[[c for c in clock.columns if c in ["risk_factor", "risk_score"]]].dropna() if {"risk_factor", "risk_score"}.issubset(clock.columns) else None

    c1, c2 = st.columns((1, 2))
    with c1:
        st.plotly_chart(gauge_clock(seconds), width='stretch')
    with c2:
        st.markdown(
            """
            ### Interpretation
            World2045 suggests improvement in development conditions by 2045, but not a transition to systemic safety.
            Climate stress, geopolitical fragmentation, governance divergence, AI governance gaps, and conflict persistence keep the implied clock close to midnight.
            """
        )
        st.info("Project estimate: approximately 70 seconds to midnight in 2045.")

    if risk_df is not None and not risk_df.empty:
        st.plotly_chart(bar_chart(risk_df, x="risk_factor", y="risk_score", title="Risk-factor contribution"), width='stretch')


main()
