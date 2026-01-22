import pandas as pd
import json
import os
import numpy as np

def load_full_dataset(nrows: int = 10000):
    """
    Charge le CSV, nettoie les montants et fusionne avec les labels de fraude.
    """
    csv_path = os.path.join("data", "transactions_data.csv")
    json_path = os.path.join("data", "train_fraud_labels.json")

    # 1. Vérification du fichier CSV
    if not os.path.exists(csv_path):
        print(f"Erreur : Le fichier {csv_path} est introuvable.")
        return pd.DataFrame()

    # 2. Lecture du CSV
    df = pd.read_csv(csv_path, nrows=nrows)
    
    # Nettoyage immédiat des noms de colonnes (supprime les espaces invisibles)
    df.columns = [c.strip() for c in df.columns]

    # 3. NETTOYAGE MONTANT : Transforme "$12.50" en 12.50 (float)
    if "amount" in df.columns:
        df["amount"] = df["amount"].replace(r'[\$,]', '', regex=True)
        df["amount"] = pd.to_numeric(df["amount"], errors='coerce').fillna(0.0)

    # 4. FUSION FRAUDE : Charge les "Yes"/"No" du JSON
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                fraud_dict = json.load(f)
                # On récupère le dictionnaire sous la clé "target"
                fraud_data = fraud_dict.get("target", {})
            
            fraud_series = pd.Series(fraud_data)
            # On mappe les ID (en string) vers les labels 1 ou 0
            df['isFraud'] = df['id'].astype(str).map(fraud_series).map({'Yes': 1, 'No': 0})
        except Exception as e:
            print(f"Erreur lors de la lecture du JSON : {e}")
            df['isFraud'] = 0
    else:
        df['isFraud'] = 0

    # 5. SÉCURITÉ FINALE : Remplissage des vides pour éviter les erreurs JSON dans l'API
    df['isFraud'] = df['isFraud'].fillna(0).astype(int)
    
    # Gestion des colonnes manquantes ou renommées (ex: use_chip / type)
    if "use_chip" not in df.columns and "type" in df.columns:
        df["use_chip"] = df["type"]

    # Remplace les valeurs infinies ou NaN par 0 pour que le navigateur ne plante pas
    df = df.replace([np.inf, -np.inf], 0).fillna(0)

    return df