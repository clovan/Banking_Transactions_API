import streamlit as st
import pandas as pd
from services.customer_service import CustomerAPI

api = CustomerAPI()

st.title("🧑‍💼 Analyse des Clients")

tab1, tab2, tab3 = st.tabs([
    "Liste des clients",
    "Top clients",
    "Profil client"
])

# ============================================================
# TAB 1 : LISTE PAGINÉE DES CLIENTS
# ============================================================
with tab1:
    st.subheader("📄 Liste paginée des clients")

    page = st.number_input("Page", min_value=1, value=1)
    size = st.slider("Clients par page", 5, 50, 10)

    if st.button("Charger", key="load_customers"):
        data = api.list_customers(page, size)

        if "data" not in data:
            st.error("Erreur lors du chargement des clients.")
        else:
            df = pd.DataFrame(data["data"])

            # 🔥 Fix Arrow si nécessaire
            for col in df.columns:
                if df[col].dtype == "object":
                    df[col] = df[col].astype(str)

            st.write(f"Total clients : {data['total']} — Page {data['page']} / {data['pages']}")
            st.dataframe(df)


# ============================================================
# TAB 2 : TOP CLIENTS PAR VOLUME
# ============================================================
with tab2:
    st.subheader("🏆 Top clients par volume de transactions")

    n = st.slider("Nombre de clients (Top N)", 5, 50, 10)

    if st.button("Afficher le classement", key="show_top_customers"):
        data = api.top_customers(n)

        if not data:
            st.warning("Aucune donnée disponible.")
        else:
            df = pd.DataFrame(data)

            # 🔥 Fix Arrow
            for col in df.columns:
                if df[col].dtype == "object":
                    df[col] = df[col].astype(str)

            st.bar_chart(df, x="client_id", y="transaction_volume")
            st.dataframe(df)


# ============================================================
# TAB 3 : PROFIL CLIENT
# ============================================================
with tab3:
    st.subheader("🧾 Profil client")

    customer_id = st.number_input("ID client", min_value=0, step=1)

    if st.button("Afficher le profil", key="show_customer_profile"):
        data = api.profile(customer_id)

        if "error" in data:
            st.error(data["error"])
        else:
            col1, col2, col3 = st.columns([1, 1, 1.3])

            col1.metric("Transactions", data["transactions_count"])
            col2.metric("Montant moyen", f"{data['avg_amount']} €")
            col3.metric("Fraude détectée", "Oui" if data["fraudulent"] else "Non")

            st.write("### Détails bruts")
            st.json(data)
