import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="NOC Outage Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme
st.markdown("""
    <style>
    :root {
        --primary-color: #ff6b6b;
        --background-color: #0f0f0f;
        --secondary-background-color: #1a1a1a;
    }
    body {
        color: white;
        background-color: #0f0f0f;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚨 NOC Outage Impact Dashboard")
st.markdown("**Telecom Outage Impact Prioritization System**")

st.info("📊 Dashboard initialization complete - Phase 1")

# Placeholder content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Outages", "—", help="Loading data...")

with col2:
    st.metric("Avg Impact Score", "—", help="Loading data...")

with col3:
    st.metric("Regions Affected", "—", help="Loading data...")

st.divider()

st.subheader("Ranked Incidents")
st.info("No incident data available yet. Data pipeline coming in Phase 2.")

st.divider()

st.subheader("System Status")
st.json({
    "phase": "1 - Project Initialization",
    "backend": "Not connected",
    "data_pipeline": "Not implemented",
    "impact_scoring": "Not implemented",
    "anomaly_detection": "Not implemented"
})
