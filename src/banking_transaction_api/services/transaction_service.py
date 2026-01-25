from banking_transaction_api.data_loader import DataLoader
import pandas as pd

class TransactionService:
    def __init__(self):
        self.data_loader = DataLoader()
        

    def get_all(self):
        return self.data_loader.transactions

    def filter_transactions(self, df, transaction_type=None, is_fraud=None, min_amount=None, max_amount=None):
        if df.empty:
            print("DataFrame is empty, returning as is.")
            return df

        filtered_df = df.copy()

        # 1. Correction du nom de colonne : 'use_chip' au lieu de 'type'
        if transaction_type:
            # On vérifie dynamiquement quelle colonne existe
            col_type = "use_chip" if "use_chip" in filtered_df.columns else "type"
            if col_type in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[col_type] == transaction_type]

        # 2. Filtrage de la fraude (avec conversion en entier)
        if is_fraud is not None:
            if "isFraud" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["isFraud"].astype(int) == int(is_fraud)]

        # 3. Filtrage des montants (maintenant que c'est du float)
        if min_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] >= float(min_amount)]
        if max_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] <= float(max_amount)]

        return filtered_df