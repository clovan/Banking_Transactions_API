from banking_transaction_api.data_loader import load_dataset, load_fraud_labels_dict

import pandas as pd
from pydantic import BaseModel
from typing import Optional, List


class TransactionService:
    def __init__(self):
        self._df = None
        self._fraud_dict = load_fraud_labels_dict("train_fraud_labels.json")

    def get_all(self):
        if self._df is None:
            self._df = load_dataset("transactions_data.csv")
            if not self._df.empty and "amount" in self._df.columns:
                self._df["amount"] = self._df["amount"].replace(r'[\$,]', '', regex=True).astype(float)
        return self._df

    def filter_transactions(self, df, transaction_type=None, is_fraud=None, min_amount=None, max_amount=None):
        if df.empty:
            return df

        filtered_df = df.copy()

        # -----------------------------
        # 1. Nettoyage du montant
        # -----------------------------
        if "amount" not in filtered_df.columns:
            raise HTTPException(status_code=500, detail="Colonne 'amount' absente du dataset")

        # Nettoyage systématique (évite les erreurs si df est déjà en cache)
        filtered_df["amount"] = (
            filtered_df["amount"]
            .replace(r'[\$,]', '', regex=True)
            .astype(float)
        )

        # -----------------------------
        # 2. Filtrage par type
        # -----------------------------
        col_type = "use_chip" if "use_chip" in filtered_df.columns else "type"

        if transaction_type and col_type in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[col_type] == transaction_type]

        # -----------------------------
        # 3. Filtrage par fraude via JSON
        # -----------------------------
        if is_fraud is not None:
            filtered_df = filtered_df[
                filtered_df["id"].apply(lambda tx_id: self._fraud_dict.get(int(tx_id), 0) == is_fraud)
            ]

        # -----------------------------
        # 4. Filtrage par montant
        # -----------------------------
        if min_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] >= float(min_amount)]

        if max_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] <= float(max_amount)]

        return filtered_df

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


class TransactionSearch(BaseModel):
    type: Optional[str] = None
    isFraud: Optional[int] = None
    amount_range: Optional[List[float]] = None

