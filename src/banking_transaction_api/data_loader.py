import pandas as pd
import json
import os
import numpy as np

def load_full_dataset():
    csv_path = os.path.join("data", "transactions_data.csv")
    json_path = os.path.join("data", "train_fraud_labels.json")

    # Fallback dataset mock pour GitHub / CI
    if not os.path.exists(csv_path):
        return pd.DataFrame({
            "id": [7475327, 7475328, 7475329, 7480000],
            "client_id": [1556, 1556, 2001, 1556],
            "amount": [-120.5, 250.0, -50.0, 99.99],
            "use_chip": [True, False, True, True],
            "isFraud": [0, 0, 1, 0]
        })

    # Limite mémoire
    df = pd.read_csv(csv_path, nrows=10000)

    # Normalisation colonnes
    df.columns = df.columns.str.strip().str.lower()

    # Sécurité colonnes minimales
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)
    if "client_id" not in df.columns:
        df["client_id"] = df.get("customer_id", 0)

    # Nettoyage amount
    df["amount"] = df["amount"].astype(str).replace(r'[\$,]', '', regex=True)
    df["amount"] = pd.to_numeric(df["amount"], errors='coerce').fillna(0.0)

    # Fusion fraude
    if os.path.exists(json_path) and "id" in df.columns:
        with open(json_path, "r") as f:
            fraud_data = json.load(f).get("target", {})
        fraud_series = pd.Series(fraud_data)
        df["isFraud"] = df["id"].astype(str).map(fraud_series).map({"Yes": 1, "No": 0})

    # Valeur par défaut fraude
    df["isFraud"] = df.get("isFraud", 0).fillna(0).astype(int)

    # use_chip fallback
    if "use_chip" not in df.columns:
        df["use_chip"] = df.get("type", False)

    # Nettoyage final
    df = df.replace([np.inf, -np.inf], 0).fillna(0)

    return df
