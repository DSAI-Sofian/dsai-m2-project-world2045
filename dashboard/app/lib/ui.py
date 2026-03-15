from __future__ import annotations

import streamlit as st


def page_header(title: str, subtitle: str):
    st.title(title)
    st.caption(subtitle)


def show_empty_data_warning(page_name: str):
    st.warning(
        f"No data detected for {page_name}. Add the required parquet/CSV extracts to the data/ folder and rerun the app."
    )


def metric_row(metrics: list[tuple[str, str, str | None]]):
    cols = st.columns(len(metrics))
    for col, (label, value, delta) in zip(cols, metrics):
        col.metric(label=label, value=value, delta=delta)
