from banking_transaction_api.data_loader import load_full_dataset

class TransactionService:
    def __init__(self):
        self._df = None

    def get_all(self):
        """Source de vérité unique pour toute l'API."""
        if self._df is None:
            self._df = load_full_dataset()
        return self._df

    def get_customer_flow(self, customer_id: int, flow_type: str):
        """Gestion des débits/crédits (Routes 7 et 8)."""
        df = self.get_all()
        if df.empty: return []
        mask_client = df["client_id"] == customer_id
        mask_flow = (df["amount"] < 0) if flow_type == "debit" else (df["amount"] > 0)
        return df[mask_client & mask_flow].to_dict(orient="records")

    def filter_transactions(self, df, transaction_type=None, is_fraud=None, min_amount=None, max_amount=None):
        """Logique de recherche (Route 1 et 3)."""
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
        """Suppression (Route 6)."""
        df = self.get_all()
        if transaction_id in df['id'].values:
            self._df = df[df['id'] != transaction_id]
            return True
        return False