import streamlit as st
import pandas as pd
from services.stats_service import StatsAPI

api = StatsAPI()

st.title("📊 Statistiques et Analyses")

# Onglets
tab1, tab2, tab3, tab4 = st.tabs([
    "Vue d'ensemble",
    "Distribution des montants",
    "Statistiques par type",
    "Transactions par jour"
])

# ============================================================
# TAB 1 : STATISTIQUES GLOBALES
# ============================================================
with tab1:
    st.subheader("📌 Vue d'ensemble des statistiques")

    data = api.overview()

    if "detail" in data:
        st.error(data["detail"])
    else:
        st.markdown("""
        <style>
        div[data-testid="metric-container"] {
            width: 100% !important;
            min-width: 180px;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total transactions", data["total_transactions"])
        col2.metric("Taux de fraude", f"{data['fraud_rate'] * 100:.2f}%")
        col3.metric("Montant moyen", f"{data['avg_amount']} €")
        col4.metric("Type le plus fréquent", data["most_common_type"])


# ============================================================
# TAB 2 : DISTRIBUTION DES MONTANTS
# ============================================================
with tab2:
    st.subheader("📦 Distribution des montants")

    bins_input = st.text_input(
        "Paliers personnalisés (séparés par des virgules)",
        "0,100,500,1000,5000"
    )

    if st.button("Générer l'histogramme", key="generate_histogram"):
        try:
            bins = [float(x.strip()) for x in bins_input.split(",")]
        except Exception:
            st.error("Format invalide. Exemple : 0, 100, 500, 1000")
            bins = None

        dist = api.amount_distribution(bins=bins)

        if "detail" in dist:
            st.error(dist["detail"])
        else:
            df = pd.DataFrame({
                "bins": dist["bins"],
                "count": dist["counts"]
            })

            # 🔥 Fix Arrow : conversion locale
            if "merchant_state" in df.columns:
                df["merchant_state"] = df["merchant_state"].astype(str)

            st.bar_chart(df, x="bins", y="count")
            st.dataframe(df)


# ============================================================
# TAB 3 : STATISTIQUES PAR TYPE
# ============================================================
with tab3:
    st.subheader("🧩 Statistiques par type de transaction")

    data = api.stats_by_type()

    if "detail" in data:
        st.error(data["detail"])
    else:
        df = pd.DataFrame(data)

        # 🔥 Fix Arrow
        if "merchant_state" in df.columns:
            df["merchant_state"] = df["merchant_state"].astype(str)

        st.dataframe(df)

        st.write("### Nombre de transactions par type")
        st.bar_chart(df, x="type", y="count")

        st.write("### Montant moyen par type")
        st.bar_chart(df, x="type", y="avg_amount")


# ============================================================
# TAB 4 : TRANSACTIONS PAR JOUR
# ============================================================
with tab4:
    st.subheader("📅 Transactions par jour")

    data = api.daily_stats()

    if "detail" in data:
        st.error(data["detail"])
    else:
        df = pd.DataFrame(data)

        # Conversion date
        df["date"] = pd.to_datetime(df["date"])

        st.line_chart(df, x="date", y="count")
        st.dataframe(df)
