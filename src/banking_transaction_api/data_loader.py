import pandas as pd
import json
import os
import numpy as np

# Calcul automatique de la racine du projet (3 niveaux au-dessus de ce fichier)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =================================================================
# ARTICULATION 1 : CHARGEMENT ET FUSION DES TRANSACTIONS (FRAUDE)
# =================================================================
def load_full_dataset():
    """
    Charge les transactions (CSV) et les fusionne avec les labels (JSON).
    Sécurisé pour éviter les KeyError en cas d'absence de fichier.
    """
    csv_path = os.path.join(BASE_DIR, "data", "transactions_data.csv")
    json_path = os.path.join(BASE_DIR, "data", "train_fraud_labels.json")

    # Colonnes minimales pour éviter que TransactionService ou FraudService ne plantent
    default_cols = ["id", "client_id", "amount", "use_chip", "isFraud", "type"]

    if not os.path.exists(csv_path):
        # On retourne un DataFrame vide mais avec les colonnes pour éviter KeyError: 'id'
        return pd.DataFrame(columns=default_cols)

    # --- Étape A : Lecture du CSV ---
    df = pd.read_csv(csv_path, nrows=50000)

    # --- Étape B : Nettoyage et conversion des montants ---
    if "amount" in df.columns:
        df["amount"] = df["amount"].replace(r'[\$,]', '', regex=True)
        df["amount"] = pd.to_numeric(df["amount"], errors='coerce').fillna(0.0)

    # --- Étape C : Intégration des labels de fraude (JSON) ---
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                fraud_data = json.load(f).get("target", {})
            fraud_series = pd.Series(fraud_data)
            # Mapping id -> label ('Yes'/'No') -> numérique (1/0)
            df['isFraud'] = df['id'].astype(str).map(fraud_series).map({'Yes': 1, 'No': 0})
        except Exception:
            df['isFraud'] = 0
    else:
        df['isFraud'] = 0

    df['isFraud'] = df['isFraud'].fillna(0).astype(int)

    # --- Étape D : Normalisation des colonnes ---
    if "use_chip" not in df.columns and "type" in df.columns:
        df["use_chip"] = df["type"]

    # Sécurité si une colonne manque malgré tout
    for col in default_cols:
        if col not in df.columns:
            df[col] = 0

    df = df.replace([np.inf, -np.inf], 0).fillna(0)
    return df


# =================================================================
# ARTICULATION 2 : CHARGEMENT DES DONNÉES CLIENTS (DÉMOGRAPHIE)
# =================================================================
def load_user_data():
    """
    Charge les informations des utilisateurs.
    """
    user_csv_path = os.path.join(BASE_DIR, "data", "users_data.csv")

    if not os.path.exists(user_csv_path):
        # Colonnes par défaut pour les routes 16 et 17
        return pd.DataFrame(columns=["id", "City", "State"])

    # --- Étape A : Chargement brut ---
    df_users = pd.read_csv(user_csv_path)

    # --- Étape B : Nettoyage des chaînes de caractères ---
    for col in ['City', 'State']:
        if col in df_users.columns:
            df_users[col] = df_users[col].astype(str).str.strip()

    return df_users