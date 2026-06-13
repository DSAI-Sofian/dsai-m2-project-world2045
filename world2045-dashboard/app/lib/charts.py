from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def line_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str | None = None):
    if df.empty:
        return go.Figure()
    fig = px.line(df, x=x, y=y, color=color, markers=False, title=title)
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str | None = None):
    if df.empty:
        return go.Figure()
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, hover_name: str | None = None, title: str | None = None):
    if df.empty:
        return go.Figure()
    fig = px.scatter(df, x=x, y=y, color=color, hover_name=hover_name, title=title)
    fig.update_layout(height=500, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def gauge_clock(seconds_to_midnight: float, label: str = "Estimated 2045 Doomsday Clock"):
    value = max(0.0, min(120.0, seconds_to_midnight))
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": " sec"},
            title={"text": label},
            gauge={
                "axis": {"range": [0, 120]},
                "steps": [
                    {"range": [0, 30], "color": "#7f1d1d"},
                    {"range": [30, 60], "color": "#b45309"},
                    {"range": [60, 90], "color": "#1d4ed8"},
                    {"range": [90, 120], "color": "#065f46"},
                ],
            },
        )
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=70, b=20))
    return fig
