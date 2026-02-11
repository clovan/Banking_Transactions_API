import streamlit as st
import pandas as pd
from services.fraud_service import FraudAPI

api = FraudAPI()

st.title("🚨 Analyse des Fraudes")

tab1, tab2, tab3 = st.tabs([
    "Résumé global",
    "Fraudes par type",
    "Prédiction de fraude"
])

# ============================================================
# TAB 1 : RÉSUMÉ GLOBAL DES FRAUDES
# ============================================================
with tab1:
    st.subheader("📌 Résumé global des fraudes")

    data = api.summary()

    if "detail" in data:
        st.error(data["detail"])
    else:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1.3])

        col1.metric("Total fraudes", data["total_frauds"])
        col2.metric("Transactions flaggées", data["flagged"])
        col3.metric("Précision", f"{data['precision'] * 100:.1f}%")
        col4.metric("Rappel", f"{data['recall'] * 100:.1f}%")


# ============================================================
# TAB 2 : FRAUDES PAR TYPE
# ============================================================
with tab2:
    st.subheader("🧩 Répartition des fraudes par type")

    data = api.by_type()

    if not data:
        st.warning("Aucune donnée disponible.")
    else:
        df = pd.DataFrame(list(data.items()), columns=["type", "count"])

        st.bar_chart(df, x="type", y="count")
        st.dataframe(df)


# ============================================================
# TAB 3 : PRÉDICTION DE FRAUDE
# ============================================================
with tab3:
    st.subheader("🔮 Prédire une fraude")

    type_choice = st.selectbox(
        "Type de transaction",
        ["Online Transaction", "Swipe Transaction", "TRANSFER"]
    )

    amount = st.number_input("Montant", min_value=0.0, step=10.0)
    oldbalance = st.number_input("Ancien solde (oldbalanceOrg)", min_value=0.0)
    newbalance = st.number_input("Nouveau solde (newbalanceOrig)", min_value=0.0)

    if st.button("Prédire", key="predict_fraud"):
        payload = {
            "type": type_choice,
            "amount": amount,
            "oldbalanceOrg": oldbalance,
            "newbalanceOrig": newbalance
        }

        result = api.predict(payload)

        if "detail" in result:
            st.error(result["detail"])
        else:
            st.success(
                f"Fraude probable : {'Oui' if result['isFraud'] else 'Non'} "
                f"(probabilité : {result['probability'] * 100:.1f}%)"
            )
