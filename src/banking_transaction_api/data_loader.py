import pandas as pd
import json
import os
import numpy as np

def load_full_dataset():
    csv_path = os.path.join("data", "transactions_data.csv")
    json_path = os.path.join("data", "train_fraud_labels.json")

    if not os.path.exists(csv_path):
        return pd.DataFrame()

    # 1. FIX MEMOIRE : nrows doit être ici, pas dans os.path.exists
    # Augmenté à 100 000 pour avoir des stats significatives sur l'histogramme
    df = pd.read_csv(csv_path, nrows=10000)

    # 2. NETTOYAGE MONTANT : Crucial pour la Route 10
    df["amount"] = df["amount"].replace(r'[\$,]', '', regex=True)
    df["amount"] = pd.to_numeric(df["amount"], errors='coerce').fillna(0.0)

    # 3. FUSION FRAUDE : Correction de la syntaxe os.path.exists
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            fraud_data = json.load(f).get("target", {})
        fraud_series = pd.Series(fraud_data)
        df['isFraud'] = df['id'].astype(str).map(fraud_series).map({'Yes': 1, 'No': 0})

    df['isFraud'] = df['isFraud'].fillna(0).astype(int)

    # 4. SÉCURITÉ STATS : Nettoyage des valeurs infinies
    if "use_chip" not in df.columns and "type" in df.columns:
        df["use_chip"] = df["type"]

    df = df.replace([np.inf, -np.inf], 0).fillna(0)

    return df