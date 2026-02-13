import streamlit as st

st.set_page_config(
    page_title="Banking Transactions Dashboard",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Banking Transactions Dashboard")

st.markdown("""
Bienvenue dans le tableau de bord interactif de l’API bancaire.

Utilisez le menu de gauche pour naviguer entre :
- **Transactions**
- **Statistiques**
- **Fraudes**
- **Analyse Clients**
""")
