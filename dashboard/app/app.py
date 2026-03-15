from __future__ import annotations

from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="World2045 Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent

pages = [
    st.Page(str(ROOT / "pages" / "global_overview.py"), title="Global Overview", icon="🌐"),
    st.Page(str(ROOT / "pages" / "country_explorer.py"), title="Country Explorer", icon="🏳️"),
    st.Page(str(ROOT / "pages" / "regional_view.py"), title="Regional View", icon="🗺️"),
    st.Page(str(ROOT / "pages" / "strategic_rankings.py"), title="Strategic Rankings", icon="📈"),
    st.Page(str(ROOT / "pages" / "doomsday_clock.py"), title="2045 Doomsday Clock", icon="⏰"),
    st.Page(str(ROOT / "pages" / "methodology.py"), title="Methodology", icon="📘"),
]

with st.sidebar:
    st.markdown("## World2045")
    st.markdown("Final academic visualization product")
    st.divider()
    st.markdown(
        "Use precomputed extracts from dbt gold models. Keep app logic presentation-only."
    )

pg = st.navigation(pages, position="sidebar")
pg.run()
