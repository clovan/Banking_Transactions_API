import streamlit as st
from services.api_client import (
    get_stats_overview, get_stats_amount_distribution, get_stats_by_type
)

st.title("📊 Statistiques globales")

st.header("Vue d’ensemble")
st.json(get_stats_overview())

st.header("Distribution des montants")
st.json(get_stats_amount_distribution())

st.header("Stats par type")
st.json(get_stats_by_type())
