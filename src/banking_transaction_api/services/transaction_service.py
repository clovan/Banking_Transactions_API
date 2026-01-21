import json
import pandas as pd
import numpy as np
from banking_transaction_api.data_loader import load_dataset

class TransactionService:
    def __init__(self):
        self._df = None

    def get_all(self):
        """Charge le CSV, fusionne les labels de fraude et nettoie les données NaN."""
        if self._df is None:
            # 1. Chargement du CSV principal
            df = load_dataset("transactions_data.csv")

            if not df.empty:
                # 2. Nettoyage des montants (retrait du $)
                df["amount"] = df["amount"].replace(r'[\$,]', '', regex=True).astype(float)

                # 3. Récupération des labels de fraude depuis le JSON
                try:
                    with open("data/train_fraud_labels.json", "r") as f:
                        fraud_data = json.load(f)
                        # Transformation du dictionnaire "target" pour la fusion
                        labels_df = pd.DataFrame.from_dict(fraud_data["target"], orient='index', columns=['isFraud'])
                        labels_df.index = labels_df.index.astype(int)
                        # Conversion 'Yes'/'No' en 1/0 pour les calculs
                        labels_df['isFraud'] = labels_df['isFraud'].map({'Yes': 1, 'No': 0})

                    # 4. Fusion des sources sur l'ID
                    df = df.join(labels_df, on='id')
                    # Remplissage des fraudes manquantes par 0
                    df["isFraud"] = df["isFraud"].fillna(0).astype(int)
                except Exception:
                    df["isFraud"] = 0

                # 5. --- CORRECTION CRUCIALE POUR LE JSON ---
                # On remplace les valeurs NaN (null) par des chaînes vides pour éviter l'erreur de conversion JSON
                # Les colonnes comme merchant_state ou zip contiennent des <null>
                df = df.replace({np.nan: ""})

            self._df = df
        return self._df

    def get_global_stats(self):
        """Calcule les stats globales (Route 9)."""
        df = self.get_all()
        if df.empty:
            return None

        total_tx = len(df)
        # On s'assure de ne calculer la moyenne que sur des valeurs numériques
        fraud_rate = df["isFraud"].mean()
        avg_amount = df["amount"].mean()

        # Identification du type le plus fréquent (colonne use_chip)
        col_type = "use_chip" if "use_chip" in df.columns else "type"
        # On ignore les valeurs vides pour le mode
        valid_types = df[df[col_type] != ""][col_type]
        most_common = valid_types.mode()[0] if not valid_types.empty else "N/A"

        return {
            "total_transactions": int(total_tx),
            "fraud_rate": float(round(fraud_rate, 5)), # Format 0.00129
            "avg_amount": float(round(avg_amount, 2)),
            "most_common_type": most_common
        }

    def get_customer_flow(self, customer_id: int, flow_type: str):
        """Filtre par client et signe du montant (Routes 7 et 8)."""
        df = self.get_all()
        if df.empty: return []

        mask_client = df["client_id"] == customer_id
        # Débit < 0 (Route 7) / Crédit > 0 (Route 8)
        mask_flow = (df["amount"] < 0) if flow_type == "debit" else (df["amount"] > 0)

        return df[mask_client & mask_flow].to_dict(orient="records")

    def filter_transactions(self, df, transaction_type=None, is_fraud=None, min_amount=None, max_amount=None):
        """Filtre dynamique (Route 1)."""
        filtered_df = df.copy()

        if transaction_type:
            col = "use_chip" if "use_chip" in filtered_df.columns else "type"
            filtered_df = filtered_df[filtered_df[col] == transaction_type]

        if is_fraud is not None:
            filtered_df = filtered_df[filtered_df["isFraud"] == int(is_fraud)]

        if min_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] >= float(min_amount)]
        if max_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] <= float(max_amount)]

        return filtered_df

    def delete_transaction(self, transaction_id: int):
        """Supprime une transaction (Route 6)."""
        df = self.get_all()
        if transaction_id in df['id'].values:
            self._df = df[df['id'] != transaction_id]
            return True
        return False