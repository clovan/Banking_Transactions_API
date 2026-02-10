import pandas as pd
from banking_transaction_api.data_loader import load_full_dataset


class TransactionService:
    def __init__(self):
        self._df = None

    # ===============================================================
    # CORE & UTILS
    # ===============================================================
    def get_all(self):
        """Source de vérité unique avec chargement paresseux."""
        if self._df is None:
            self._df = load_full_dataset()
        return self._df

    def _prepare_output(self, df: pd.DataFrame) -> list:
        """Méthode interne pour formater la sortie (renommage de colonnes)."""
        data = df.to_dict(orient="records")
        for item in data:
            # On remplace use_chip par transaction_type pour l'API
            if "use_chip" in item:
                item["transaction_type"] = item.pop("use_chip")
        return data

    # ===============================================================
    # ROUTE 2 : DÉTAIL TRANSACTION
    # ===============================================================
    def get_transaction_by_id(self, transaction_id: int):
        df = self.get_all()
        if df.empty:
            return None

        result = df[df["id"] == transaction_id]
        if result.empty:
            return None

        return self._prepare_output(result)[0]

    # ===============================================================
    # ROUTE 3 : RECHERCHE MULTICRITÈRE
    # ===============================================================
    def search_advanced(self, filters: dict):
        transaction_type = filters.get("type")
        is_fraud = filters.get("isFraud")
        amount_range = filters.get("amount_range") or []

        min_amt = amount_range[0] if len(amount_range) > 0 else None
        max_amt = amount_range[1] if len(amount_range) > 1 else None

        df_filtered = self.filter_transactions(
            transaction_type=transaction_type,
            is_fraud=is_fraud,
            min_amount=min_amt,
            max_amount=max_amt,
        )

        return self._prepare_output(df_filtered)

    # ===============================================================
    # LOGIQUE COMMUNE DE FILTRAGE (Routes 1 & 3)
    # ===============================================================
    def filter_transactions(self, transaction_type=None, is_fraud=None, min_amount=None, max_amount=None):
        df = self.get_all()
        if df.empty:
            return df

        filtered_df = df.copy()

        # Conversion du montant une seule fois pour la performance
        filtered_df["amount"] = pd.to_numeric(filtered_df["amount"], errors='coerce')

        if transaction_type:
            # Détecter la colonne de type (use_chip ou transaction_type)
            type_col = "use_chip" if "use_chip" in filtered_df.columns else "transaction_type"
            filtered_df = filtered_df[filtered_df[type_col] == transaction_type]

        if is_fraud is not None:
            filtered_df = filtered_df[filtered_df["isFraud"] == int(is_fraud)]

        if min_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] >= float(min_amount)]

        if max_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] <= float(max_amount)]

        return filtered_df

    # ===============================================================
    # ROUTE 4 : TYPES
    # ===============================================================
    def get_types(self):
        df = self.get_all()
        if df.empty: return []
        # Chercher dans use_chip (nom CSV original)
        col = "use_chip" if "use_chip" in df.columns else "transaction_type"
        return sorted(df[col].dropna().unique().tolist())

    # ===============================================================
    # ROUTE 5 : TRANSACTIONS RÉCENTES
    # ===============================================================
    def get_recent(self, n: int = 10):
        df = self.get_all()
        if df.empty: return []
        recent = df.sort_values(by="id", ascending=False).head(n)
        return self._prepare_output(recent)

    # ===============================================================
    # ROUTE 6 : SUPPRESSION
    # ===============================================================
    def delete_transaction(self, transaction_id: int) -> bool:
        df = self.get_all()
        if transaction_id not in df["id"].values:
            return False

        # Mise à jour du DataFrame principal
        self._df = df[df["id"] != transaction_id].copy()
        return True

    # ===============================================================
    # ROUTES 7 & 8 : FLUX CLIENT
    # ===============================================================
    def get_customer_flow(self, customer_id: int, flow_type: str):
        df = self.get_all()
        if df.empty:
            return []

        # Filtrer sur le client d'abord (plus rapide)
        df_client = df[df["client_id"] == customer_id].copy()
        if df_client.empty:
            return []

        df_client["amount"] = pd.to_numeric(df_client["amount"], errors='coerce')

        if flow_type == "debit":
            result = df_client[df_client["amount"] < 0]
        else:  # credit
            result = df_client[df_client["amount"] > 0]

        return self._prepare_output(result)