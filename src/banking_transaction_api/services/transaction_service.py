import pandas as pd
from banking_transaction_api.data_loader import load_full_dataset

class TransactionService:
    """Service de gestion des transactions bancaires"""
    
    def __init__(self):
        """Initialise le service avec un DataFrame vide"""
        self._df = None

    def get_all(self):
        """
        Récupère toutes les transactions du dataset.
        Charge le dataset en mémoire lors du premier appel (lazy loading).
        
        Returns:
            DataFrame: Toutes les transactions chargées
        """
        if self._df is None:
            self._df = load_full_dataset(nrows=10000)
        return self._df

    def get_customer_flow(self, customer_id: int, flow_type: str):
        """
        Récupère les flux financiers d'un client (débit ou crédit).
        
        Args:
            customer_id: L'identifiant du client
            flow_type: Type de flux - "debit" pour argent sortant, "credit" pour argent entrant
            
        Returns:
            DataFrame: Transactions filtrées selon le type de flux
        """
        df = self.get_all().copy()
        
        # Conversion des colonnes en entiers pour assurer la cohérence des types
        df['client_id'] = pd.to_numeric(df['client_id'], errors='coerce').fillna(0).astype(int)
        df['merchant_id'] = pd.to_numeric(df['merchant_id'], errors='coerce').fillna(0).astype(int)
        
        # Conversion du montant en numérique pour détecter les valeurs positives/négatives
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        if flow_type == "debit":
            # DÉBIT : Argent sortant du compte du client (montant négatif)
            # Le client est l'émetteur de la transaction (client_id)
            return df[(df['client_id'] == customer_id) & (df['amount'] < 0)]
        else:  # "credit"
            # CRÉDIT : Argent entrant sur le compte du client (montant positif)
            # Le client est l'émetteur de la transaction (client_id)
            return df[(df['client_id'] == customer_id) & (df['amount'] > 0)]

    def filter_transactions(self, df, type=None, is_fraud=None, min_amount=None, max_amount=None):
        """
        Applique des filtres sur un DataFrame de transactions.
        
        Args:
            df: DataFrame à filtrer
            type: Type de transaction (ex: "Swipe Transaction")
            is_fraud: Filtrer par fraude (True/False)
            min_amount: Montant minimum
            max_amount: Montant maximum
            
        Returns:
            DataFrame: Transactions filtrées selon les critères
        """
        if df.empty: 
            return df
        
        filtered_df = df.copy()
        
        # Filtre par type de transaction
        if type:
            col = "use_chip" if "use_chip" in filtered_df.columns else "type"
            filtered_df = filtered_df[filtered_df[col] == type]
        
        # Filtre par fraude (0 = non frauduleux, 1 = frauduleux)
        if is_fraud is not None:
            filtered_df = filtered_df[filtered_df["isFraud"] == int(is_fraud)]
        
        # Filtre par montant minimum
        if min_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] >= float(min_amount)]
        
        # Filtre par montant maximum
        if max_amount is not None:
            filtered_df = filtered_df[filtered_df["amount"] <= float(max_amount)]
            
        return filtered_df

    def get_recent(self, n=10):
        """
        Récupère les N dernières transactions du dataset.
        
        Args:
            n: Nombre de transactions à retourner (défaut: 10)
            
        Returns:
            DataFrame: Les N dernières transactions
        """
        return self.get_all().tail(n)

    def delete_transaction(self, transaction_id):
        """
        Supprime une transaction du dataset (en mémoire uniquement).
        
        Args:
            transaction_id: L'identifiant de la transaction à supprimer
            
        Returns:
            bool: True si la transaction a été supprimée, False sinon
        """
        df = self.get_all()
        initial_len = len(df)
        # Supprime la ligne correspondant à l'ID
        self._df = df[df["id"].astype(str) != str(transaction_id)]
        # Retourne True si une ligne a été supprimée
        return len(self._df) < initial_len
    
    def is_dataset_loaded(self):
        """
        Vérifie si le dataset a été chargé en mémoire.
        
        Returns:
            bool: True si le dataset est chargé, False sinon
        """
        return self._df is not None