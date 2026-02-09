from banking_transaction_api.data_loader import load_full_dataset

class TransactionService:
    def __init__(self):
        self._df = None

    def get_all(self):
        """Source de vérité unique pour toute l'API (Lazy loading)."""
        if self._df is None:
            self._df = load_full_dataset()
        return self._df

    def _rename_columns(self, data_list: list) -> list:
        """Substitue 'use_chip' par 'transaction_type' dans une liste de dictionnaires."""
        for item in data_list:
            if "use_chip" in item:
                item["transaction_type"] = item.pop("use_chip")
            elif "type" in item:
                item["transaction_type"] = item.pop("type")
        return data_list

    # =================================================================
    # ROUTE 2 : DÉTAILS D'UNE TRANSACTION
    # =================================================================
    def get_transaction_by_id(self, transaction_id: int):
        """Récupère une transaction unique par son ID."""
        df = self.get_all()
        if df.empty: return None

        result = df[df['id'] == transaction_id]
        if result.empty: return None

        transaction_dict_list = result.to_dict(orient="records")
        return self._rename_columns(transaction_dict_list)[0]

    # =================================================================
    # ROUTE 3 : RECHERCHE MULTICRITÈRE (POST)
    # =================================================================
    def search_advanced(self, filters: dict):
        """
        Effectue une recherche via corps JSON.
        Utilise 'use_chip' pour le filtrage du champ 'type'.
        """
        transaction_type = filters.get("type")
        is_fraud = filters.get("isFraud")
        amount_range = filters.get("amount_range")

        min_amt = amount_range[0] if amount_range and len(amount_range) >= 1 else None
        max_amt = amount_range[1] if amount_range and len(amount_range) >= 2 else None

        # Le filtrage utilise la colonne use_chip en interne
        df_filtered = self.filter_transactions(
            transaction_type=transaction_type,
            is_fraud=is_fraud,
            min_amount=min_amt,
            max_amount=max_amt
        )

        results = df_filtered.to_dict(orient="records")
        return self._rename_columns(results)

    def filter_transactions(self, transaction_type=None, is_fraud=None, min_amount=None, max_amount=None):
        """Logique de recherche commune (Route 1 et 3)."""
        df = self.get_all()
        if df.empty: return df

        filtered_df = df.copy()

        if transaction_type:
            # On utilise use_chip pour filtrer le type demandé en JSON
            col = "use_chip" if "use_chip" in filtered_df.columns else "type"
            filtered_df = filtered_df[filtered_df[col] == transaction_type]

        if is_fraud is not None:
            filtered_df = filtered_df[filtered_df["isFraud"] == int(is_fraud)]

        if min_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] >= float(min_amount)]

        if max_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] <= float(max_amount)]

        return filtered_df

    # ... (Autres méthodes existantes : delete_transaction, get_customer_flow)