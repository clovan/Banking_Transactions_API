import streamlit as st
from services.api_client import (
    get_fraud_summary, get_fraud_by_type, predict_fraud
)

st.title("🚨 Détection de fraude")

st.header("Résumé fraude")
st.json(get_fraud_summary())

st.header("Fraude par type")
st.json(get_fraud_by_type())

st.header("Prédiction")
amount = st.number_input("Montant", min_value=0.0)
type_ = st.text_input("Type")
old_balance = st.number_input("Ancien solde")
new_balance = st.number_input("Nouveau solde")

if st.button("Prédire"):
    payload = {
        "type": type_,
        "amount": amount,
        "oldbalanceOrg": old_balance,
        "newbalanceOrig": new_balance
    }
    st.json(predict_fraud(payload))
