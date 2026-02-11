import pandas as pd
from banking_transaction_api.data_loader import load_full_dataset


class TransactionService:
    # Cache au niveau de la CLASSE (Singleton pour performance < 500ms)
    _cached_df = None

    def __init__(self):
        # Désactive les warnings de downcasting pour Pandas
        pd.set_option('future.no_silent_downcasting', True)

    # --- CORE & UTILS : Chargement et formatage ---
    def get_all(self):
        """Source de vérité unique chargée une seule fois en RAM."""
        if TransactionService._cached_df is None:
            TransactionService._cached_df = load_full_dataset()
        return TransactionService._cached_df

    def _prepare_output(self, df: pd.DataFrame) -> list:
        """Formatage vectorisé pour transformer use_chip en transaction_type."""
        if df.empty:
            return []
        data = df.copy()
        if "use_chip" in data.columns:
            data.rename(columns={"use_chip": "transaction_type"}, inplace=True)
        # Nettoyage final pour éviter les erreurs de sérialisation JSON
        return data.fillna(0).infer_objects(copy=False).to_dict(orient="records")

    # --- ROUTE 1 : LOGIQUE DE FILTRAGE ET LISTE GLOBALE ---
    def filter_transactions(self, transaction_type=None, is_fraud=None, min_amount=None, max_amount=None):
        """
        Cœur de la Route 1 : Filtre les transactions selon les paramètres GET.
        """
        df = self.get_all()
        if df.empty:
            return df

        # Création d'un masque booléen pour un filtrage ultra-rapide
        mask = pd.Series([True] * len(df), index=df.index)

        if transaction_type:
            type_col = "use_chip" if "use_chip" in df.columns else "transaction_type"
            mask &= (df[type_col] == transaction_type)

        if is_fraud is not None:
            mask &= (df["isFraud"] == int(is_fraud))

        if min_amount is not None or max_amount is not None:
            amounts = pd.to_numeric(df["amount"], errors='coerce')
            if min_amount is not None:
                mask &= (amounts >= float(min_amount))
            if max_amount is not None:
                mask &= (amounts <= float(max_amount))

        return df[mask]

    # --- ROUTE 2 : DÉTAIL TRANSACTION ---
    def get_transaction_by_id(self, transaction_id: int):
        """Récupère une transaction unique par son identifiant numérique."""
        df = self.get_all()
        result = df[df["id"] == int(transaction_id)]
        return self._prepare_output(result)[0] if not result.empty else None

    # --- ROUTE 3 : RECHERCHE MULTICRITÈRE ---
    def search_advanced(self, filters: dict):
        """
        Recherche optimisée pour la Route 3 (POST).
        Défauts : 'Online Transaction' et montant entre 0 et 50.
        """
        # Type par défaut : Online Transaction
        transaction_type = filters.get("type") or "Online Transaction"

        # Filtre fraude (optionnel)
        is_fraud = filters.get("isFraud")

        # Plage de montant : 0.0 à 50.0 par défaut si non spécifiée
        amount_range = filters.get("amount_range") or [0.0, 50.0]
        min_amt = amount_range[0]
        max_amt = amount_range[1]

        # Utilisation de la logique de filtrage commune
        df_filtered = self.filter_transactions(transaction_type, is_fraud, min_amt, max_amt)
        return self._prepare_output(df_filtered)

    # --- ROUTE 4 : LISTE DES TYPES ---
    def get_types(self):
        """Récupère la liste triée de tous les types 'use_chip' disponibles."""
        df = self.get_all()
        if df.empty: return []
        col = "use_chip" if "use_chip" in df.columns else "transaction_type"
        return sorted(df[col].dropna().unique().tolist())

    # --- ROUTE 5 : TRANSACTIONS RÉCENTES ---
    def get_recent(self, n: int = 10):
        """Récupère les N dernières transactions ajoutées au système."""
        df = self.get_all()
        if df.empty: return []
        # .tail() est immédiat, .iloc[::-1] inverse pour avoir la plus récente en haut
        recent = df.tail(int(n)).iloc[::-1]
        return self._prepare_output(recent)

    # --- ROUTE 6 : SUPPRESSION TRANSACTION ---
    def delete_transaction(self, transaction_id: int) -> bool:
        """Supprime une transaction de la mémoire vive."""
        df = self.get_all()
        if int(transaction_id) not in df["id"].values:
            return False
        # Mise à jour du cache partagé
        TransactionService._cached_df = df[df["id"] != int(transaction_id)].copy()
        return True

    # --- ROUTES 7 & 8 : FLUX CLIENT (PAR client_id) ---
    def get_customer_flow(self, client_id: int, flow_type: str):
        """
        Filtre les débits (<0) ou les crédits (>0) pour un client donné.
        """
        df = self.get_all()
        if df.empty: return []

        amounts = pd.to_numeric(df["amount"], errors='coerce')
        # Masque combiné : ID client + Signe du montant
        if flow_type == "debit":
            mask = (df["client_id"] == float(client_id)) & (amounts < 0)
        else:
            mask = (df["client_id"] == float(client_id)) & (amounts > 0)

        return self._prepare_output(df[mask])