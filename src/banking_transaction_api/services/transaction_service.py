import pandas as pd
from banking_transaction_api.data_loader import load_full_dataset

class TransactionService:
    def __init__(self):
        self._df = None

    def get_all(self):
        if self._df is None:
            self._df = load_full_dataset(nrows=10000)
        return self._df

    def get_customer_flow(self, customer_id: int, flow_type: str):
        df = self.get_all().copy()
        df['client_id'] = pd.to_numeric(df['client_id'], errors='coerce').fillna(0).astype(int)
        df['merchant_id'] = pd.to_numeric(df['merchant_id'], errors='coerce').fillna(0).astype(int)

        if flow_type == "debit":
            # Argent sortant : le client est l'émetteur et le montant est négatif
            return df[(df['client_id'] == customer_id) & (df['amount'] < 0)]
        else:
            # Argent entrant : le client est le récepteur (merchant_id) et le montant est positif
            return df[(df['merchant_id'] == customer_id) & (df['amount'] > 0)]

    def filter_transactions(self, df, type=None, is_fraud=None, min_amount=None, max_amount=None):
        if df.empty: return df
        filtered_df = df.copy()
        
        if type:
            # On cherche dans use_chip car c'est là que se trouve "Swipe Transaction" dans ton CSV
            col = "use_chip" if "use_chip" in filtered_df.columns else "type"
            filtered_df = filtered_df[filtered_df[col] == type]
        
        if is_fraud is not None:
            filtered_df = filtered_df[filtered_df["isFraud"] == int(is_fraud)]
            
        if min_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] >= float(min_amount)]
        if max_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] <= float(max_amount)]
            
        return filtered_df

    def get_recent(self, n=10):
        return self.get_all().tail(n)

    def delete_transaction(self, transaction_id):
        df = self.get_all()
        initial_len = len(df)
        self._df = df[df["id"].astype(str) != str(transaction_id)]
        return len(self._df) < initial_len
    
    # DOIT ÊTRE ALIGNÉ ICI (DANS LA CLASSE)
    def is_dataset_loaded(self):
        """Vérifie si le DataFrame a été initialisé."""
        return self._df is not None