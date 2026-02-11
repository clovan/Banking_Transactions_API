import streamlit as st
import pandas as pd
from services.transactions_service import TransactionsAPI

api = TransactionsAPI()

st.title("💳 Transactions bancaires")

# Onglets
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Liste des transactions",
    "Recherche par ID",
    "Débits client",
    "Crédits client",
    "Filtrage avancé"
])

# ============================================================
# TAB 1 : LISTE DES TRANSACTIONS
# ============================================================
with tab1:
    st.subheader("📄 Liste des transactions")
    limit = st.slider("Nombre de transactions à afficher", 10, 200, 50)

    if st.button("Charger les transactions", key="load_transactions"):
        data = api.list_transactions(limit=limit)

        if "transactions" not in data:
            st.error("Erreur lors du chargement des transactions.")
        else:
            df = pd.DataFrame(data["transactions"])

            # 🔥 Fix Arrow : conversion locale uniquement
            if "merchant_state" in df.columns:
                df["merchant_state"] = df["merchant_state"].astype(str)

            st.write(f"Total : {data['total_results']} transactions")
            st.dataframe(df)


# ============================================================
# TAB 2 : RECHERCHE PAR ID
# ============================================================
with tab2:
    st.subheader("🔍 Recherche par ID")
    transaction_id = st.number_input("ID de la transaction", min_value=1, step=1)

    if st.button("Rechercher", key="search_by_id"):
        result = api.get_by_id(transaction_id)

        if "detail" in result:
            st.error(result["detail"])
        else:
            df = pd.DataFrame([result])

            if "merchant_state" in df.columns:
                df["merchant_state"] = df["merchant_state"].astype(str)

            st.dataframe(df)


# ============================================================
# TAB 3 : DÉBITS CLIENT
# ============================================================
with tab3:
    st.subheader("💸 Débits client")
    customer_id = st.number_input("ID client", min_value=1, step=1)

    if st.button("Afficher les débits", key="show_debits"):
        result = api.get_debits(customer_id)

        if "detail" in result:
            st.error(result["detail"])
        else:
            df = pd.DataFrame(result["transactions"])

            if "merchant_state" in df.columns:
                df["merchant_state"] = df["merchant_state"].astype(str)

            st.dataframe(df)


# ============================================================
# TAB 4 : CRÉDITS CLIENT
# ============================================================
with tab4:
    st.subheader("💰 Crédits client")
    customer_id = st.number_input("ID client (crédits)", min_value=1, step=1)

    if st.button("Afficher les crédits", key="show_credits"):
        result = api.get_credits(customer_id)

        if "detail" in result:
            st.error(result["detail"])
        else:
            df = pd.DataFrame(result["transactions"])

            if "merchant_state" in df.columns:
                df["merchant_state"] = df["merchant_state"].astype(str)

            st.dataframe(df)


# ============================================================
# TAB 5 : FILTRAGE AVANCÉ
# ============================================================
with tab5:
    st.subheader("🎯 Recherche multicritère")

    types = api.get_types().get("types", [])
    selected_type = st.selectbox("Type de transaction", [""] + types)

    is_fraud = st.selectbox("Fraude ?", ["", 0, 1])

    min_amount = st.number_input("Montant minimum", value=0.0)
    max_amount = st.number_input("Montant maximum", value=0.0)

    if st.button("Rechercher", key="advanced_search"):
        payload = {
            "type": selected_type or None,
            "isFraud": is_fraud if is_fraud != "" else None,
            "amount_range": [min_amount, max_amount]
        }

        result = api.search_advanced(payload)

        if "detail" in result:
            st.error(result["detail"])
        else:
            df = pd.DataFrame(result["results"])

            if "merchant_state" in df.columns:
                df["merchant_state"] = df["merchant_state"].astype(str)

            st.dataframe(df)
