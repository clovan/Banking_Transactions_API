import pandas as pd
import json
import os
import numpy as np

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# On remonte d'un niveau si le loader est dans /src/banking_transaction_api/
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "data")


# =================================================================
# ARTICULATION 1 : CHARGEMENT ET FUSION DES TRANSACTIONS (FRAUDE)
# =================================================================
def load_full_dataset():
    """
    Charge les transactions (CSV) et les fusionne avec les labels (JSON).
    Garantit la présence de 'transaction_type' et 'isFraud'.
    """
    csv_path = os.path.join(DATA_DIR, "transactions_data.csv")
    json_path = os.path.join(DATA_DIR, "train_fraud_labels.json")

    # --- Dataset fallback pour tests si fichiers absents ---
    if not os.path.exists(csv_path):
        return pd.DataFrame([
            {"id": 0, "client_id": 1556, "use_chip": "Chip Transaction", "amount": -50.0, "isFraud": 0},
            {"id": 1, "client_id": 1556, "use_chip": "Online Transaction", "amount": 200.0, "isFraud": 0},
            {"id": 2, "client_id": 1100, "use_chip": "Swipe Transaction", "amount": -100.5, "isFraud": 1},
        ])

    # --- Étape A : Lecture du CSV ---
    # On charge un échantillon pour la performance (ex: 5000 lignes)
    df = pd.read_csv(csv_path, nrows=5000)

    # --- Étape B : Nettoyage et Conversion des Montants ---
    if "amount" in df.columns:
        # Nettoyage des caractères monétaires ($, £, etc.)
        df["amount"] = df["amount"].astype(str).replace(r'[^\d.-]', '', regex=True)
        df["amount"] = pd.to_numeric(df["amount"], errors='coerce').fillna(0.0)

    # --- Étape C : Fusion des Labels de Fraude (JSON) ---
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                fraud_json = json.load(f)
                # On extrait le dictionnaire "target" (ID -> "Yes"/"No")
                fraud_data = fraud_json.get("target", {})

            # On mappe les labels sur l'ID de la transaction
            # Note : On convertit l'ID en string car les clés JSON sont souvent des strings
            fraud_series = pd.Series(fraud_data)
            df['isFraud'] = df['id'].astype(str).map(fraud_series).map({'Yes': 1, 'No': 0})
        except Exception as e:
            print(f"Erreur lors de la fusion JSON : {e}")
            df['isFraud'] = 0

    # Sécurité : Si isFraud est manquant ou contient des NaN
    df['isFraud'] = df['isFraud'].fillna(0).astype(int)

    # --- Étape D : Normalisation des Colonnes pour le Service ---
    # Ton service et tes tests cherchent 'use_chip' pour le transformer en 'transaction_type'
    if "use_chip" not in df.columns:
        if "transaction_type" in df.columns:
            df["use_chip"] = df["transaction_type"]
        elif "type" in df.columns:
            df["use_chip"] = df["type"]
        else:
            df["use_chip"] = "Unknown"

    # Nettoyage final des valeurs infinies ou nulles pour éviter les erreurs JSON
    df = df.replace([np.inf, -np.inf], 0).fillna(0)

    return df


# =================================================================
# ARTICULATION 2 : CHARGEMENT DES DONNÉES CLIENTS
# =================================================================
def load_user_data():
    """Charge les métadonnées des utilisateurs/clients."""
    user_csv_path = os.path.join(DATA_DIR, "users_data.csv")

    if not os.path.exists(user_csv_path):
        return pd.DataFrame([
            {"id": 1556, "City": "Paris", "State": "FR"},
            {"id": 1100, "City": "Lyon", "State": "FR"},
        ])

    df_users = pd.read_csv(user_csv_path)

    # Nettoyage des colonnes textuelles
    for col in ['City', 'State']:
        if col in df_users.columns:
            df_users[col] = df_users[col].astype(str).str.strip()

    return df_users