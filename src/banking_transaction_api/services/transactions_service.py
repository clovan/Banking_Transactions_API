from banking_transaction_api.data_loader import load_dataset, load_fraud_labels_dict
#from pydantic import BaseModel
#from typing import Optional, List
#import pandas as pd

class TransactionService:
    def __init__(self):
        self._df = None
        self._fraud_dict = load_fraud_labels_dict("train_fraud_labels.json")

    def get_all(self):
        if self._df is None:
            self._df = load_dataset("transactions_data.csv")

            if not self._df.empty:

                # Nettoyage du montant (gère $-77.00 sans planter)
                if "amount" in self._df.columns:
                    self._df["amount"] = (
                        self._df["amount"]
                        .astype(str)
                        .str.replace(r'[\$,]', '', regex=True)
                        .str.replace('(', '-', regex=False)
                        .str.replace(')', '', regex=False)
                        .astype(float)
                    )

                # Ajout de isFraud depuis le JSON
                if "id" in self._df.columns:
                    self._df["isFraud"] = self._df["id"].apply(
                        lambda tx_id: self._fraud_dict.get(int(tx_id), 0)
                    )

                # Création de la colonne type = use_chip
                if "use_chip" in self._df.columns:
                    self._df["transaction_type"] = self._df["use_chip"]
                else:
                    self._df["transaction_type"] = None

        return self._df

    def filter_transactions(self, df, transaction_type=None, isFraud=None, min_amount=None, max_amount=None):

        df_filtered = df.copy()

        # Filtre type (équivalent use_chip)
        if transaction_type and "transaction_type" in df_filtered.columns:
            df_filtered["transaction_type"] = df_filtered["transaction_type"].astype(str).str.upper()
            df_filtered = df_filtered[df_filtered["transaction_type"] == type.upper()]

        # Filtre isFraud
        if isFraud is not None and "isFraud" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["isFraud"] == isFraud]

        # Filtre montant min
        if min_amount is not None:
            df_filtered = df_filtered[df_filtered["amount"] >= min_amount]

        # Filtre montant max
        if max_amount is not None:
            df_filtered = df_filtered[df_filtered["amount"] <= max_amount]

        return df_filtered

    def get_transaction_by_id(self, id: int):
        df = self.get_all()
        if df.empty:
            return None

        transaction = df[df["id"] == id]
        if transaction.empty:
            return None

        return transaction.iloc[0].to_dict()

    def get_transaction_types(self):
        df = self.get_all()
        if df.empty:
            return []

        # La colonne réelle dans ton dataset est "use_chip"
        col_type = "use_chip" if "use_chip" in df.columns else "type"

        return df[col_type].dropna().unique().tolist()



