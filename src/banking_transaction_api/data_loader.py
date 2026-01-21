import pandas as pd
import os

def load_dataset(file_name: str, nrows: int = 5000):
    path = os.path.join("data", file_name)
    if os.path.exists(path):
        df = pd.read_csv(path, nrows=nrows)
        # Remplace les valeurs manquantes pour éviter les erreurs JSON
        return df.fillna(0)
    return pd.DataFrame()

import json
import os

def load_fraud_labels_dict(json_path: str) -> dict:
    path = os.path.join("data", json_path)
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        labels = json.load(f)["target"]

    # Convertir Yes/No en 1/0
    return {int(tx_id): 1 if label == "Yes" else 0 for tx_id, label in labels.items()}
