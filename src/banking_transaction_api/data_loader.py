import pandas as pd
import json
import os
import numpy as np

# =================================================================
# ARTICULATION 1 : CHARGEMENT ET FUSION DES TRANSACTIONS (FRAUDE)
# =================================================================
def load_full_dataset():
    """
    Charge les transactions (CSV) et les fusionne avec les labels (JSON).
    Cible les Routes 13, 14 et 15.
    """
    csv_path = os.path.join("data", "transactions_data.csv")
    json_path = os.path.join("data", "train_fraud_labels.json")

    if not os.path.exists(csv_path):
        return pd.DataFrame()

    # --- Étape A : Lecture du CSV avec limite mémoire ---
    df = pd.read_csv(csv_path, nrows=5000)

    # --- Étape B : Nettoyage et conversion des montants ---
    df["amount"] = df["amount"].replace(r'[\$,]', '', regex=True)
    df["amount"] = pd.to_numeric(df["amount"], errors='coerce').fillna(0.0)

    # --- Étape C : Intégration des labels de fraude (JSON) ---
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            fraud_data = json.load(f).get("target", {})
        fraud_series = pd.Series(fraud_data)
        # Mapping id -> label ('Yes'/'No') -> numérique (1/0)
        df['isFraud'] = df['id'].astype(str).map(fraud_series).map({'Yes': 1, 'No': 0})

    df['isFraud'] = df['isFraud'].fillna(0).astype(int)

    # --- Étape D : Normalisation des colonnes et gestion des types ---
    if "use_chip" not in df.columns and "type" in df.columns:
        df["use_chip"] = df["type"]

    df = df.replace([np.inf, -np.inf], 0).fillna(0)
    return df


# =================================================================
# ARTICULATION 2 : CHARGEMENT DES DONNÉES CLIENTS (DÉMOGRAPHIE)
# =================================================================
def load_user_data():
    """
    Charge les informations des utilisateurs pour l'analyse géographique.
    Cible les Routes 16 et 17.
    """
    user_csv_path = os.path.join("data", "users_data.csv")

    if not os.path.exists(user_csv_path):
        print(f"ALERTE : Fichier {user_csv_path} manquant.")
        return pd.DataFrame()

    # --- Étape A : Chargement brut ---
    df_users = pd.read_csv(user_csv_path)

    # --- Étape B : Nettoyage des chaînes de caractères (City/State) ---
    for col in ['City', 'State']:
        if col in df_users.columns:
            # Enlève les espaces inutiles en début/fin de nom
            df_users[col] = df_users[col].astype(str).str.strip()

    return df_users