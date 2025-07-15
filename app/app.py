
import streamlit as st

st.set_page_config(
    page_title="Public API Dashboards",
    page_icon="🔮",
    layout="wide",
)

st.title("Public API Dashboards")

st.sidebar.success("Select a dashboard above.")

st.markdown(
    """
    This app provides dashboards for visualizing data from three public APIs:
    - FBI Wanted API
    - ArbeitNow Job Board API
    - Spaceflight News API

    **← Select a dashboard from the sidebar** to see the visualizations.
    """
)
