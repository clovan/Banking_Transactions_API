import streamlit as st
from services.api_client import (
    get_transactions, search_transactions, get_transaction_by_id, get_transaction_types
)

st.title("📄 Transactions")

tab1, tab2, tab3, tab4 = st.tabs(["Liste", "Recherche", "Types", "Par ID"])

with tab1:
    st.subheader("Liste paginée")
    page = st.number_input("Page", min_value=1, value=1)
    limit = st.slider("Limite", 10, 100, 20)

    data = get_transactions(page=page, limit=limit)
    st.dataframe(data["transactions"])

with tab2:
    st.subheader("Recherche multicritère")

    type_ = st.text_input("Type de transaction (ex: chip, swipe, online)")
    is_fraud = st.selectbox("Fraude", ["", 0, 1])
    min_amount = st.number_input("Montant min", min_value=0.0)
    max_amount = st.number_input("Montant max", min_value=0.0)

    if st.button("Rechercher"):
        results = search_transactions(
            transaction_type=type_ or None,
            isFraud=is_fraud if is_fraud != "" else None,
            min_amount=min_amount if min_amount > 0 else None,
            max_amount=max_amount if max_amount > 0 else None
        )

        df = pd.DataFrame(results["transactions"])

        # 🔥 Fix PyArrow: convertir toutes les colonnes object en string
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str)

        st.dataframe(df)


with tab3:
    st.subheader("Types disponibles")
    st.json(get_transaction_types())



with tab4:
    st.subheader("Rechercher une transaction par ID")

    tx_id = st.number_input("ID de la transaction", min_value=1, step=1)

    if st.button("Chercher"):
        tx = get_transaction_by_id(int(tx_id))

        # On met le dict dans un DataFrame pour l’affichage
        df = pd.DataFrame([tx])

        # Fix PyArrow : convertir les colonnes object en string
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str)

        st.dataframe(df)

