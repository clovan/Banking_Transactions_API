import pandas as pd
from banking_transaction_api.data_loader import load_user_data, load_full_dataset


class CustomerService:
    """ """
    def __init__(self):
        self._df_users = None
        self._df_trans = None

    @property
    def df_users(self):
        """Chargement et nettoyage des données clients (users_data.csv)."""
        if self._df_users is None:
            df = load_user_data()
            if df is not None and not df.empty:
                cols_to_fix = ['per_capita_income', 'yearly_income', 'total_debt']
                for col in cols_to_fix:
                    if col in df.columns:
                        df[col] = (
                            df[col]
                            .astype(str)
                            .replace(r'[\$,]', '', regex=True)
                        )
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            self._df_users = df
        return self._df_users

    @property
    def df_trans(self):
        """Chargement des transactions fusionnées avec la fraude."""
        if self._df_trans is None:
            self._df_trans = load_full_dataset()
        return self._df_trans

    # =================================================================
    # ROUTE 16 : LISTE PAGINÉE DES CLIENTS
    # =================================================================
    def get_paginated_customers(self, page: int = 1, size: int = 10):
        """

        Parameters
        ----------
        page : int :
            (Default value = 1)
        size : int :
            (Default value = 10)
        page: int :
             (Default value = 1)
        size: int :
             (Default value = 10)

        Returns
        -------

        
        """
        df = self.df_users
        if df is None or df.empty:
            return {"total": 0, "page": page, "size": size, "data": []}

        total = len(df)
        start = (page - 1) * size
        end = start + size

        subset = df.iloc[start:end]
        customers_list = subset.to_dict(orient="records")

        return {
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "data": customers_list
        }

    # =================================================================
    # ROUTE 18 : TOP CLIENTS PAR VOLUME DE TRANSACTIONS
    # =================================================================
    def get_top_customers(self, n: int = 10):
        """Classe les clients par nombre total de transactions.

        Parameters
        ----------
        n : int :
            (Default value = 10)
        n: int :
             (Default value = 10)

        Returns
        -------

        
        """
        df_t = self.df_trans
        if df_t is None or df_t.empty:
            return []

        # 1. On compte le nombre de transactions par client_id
        top_clients = df_t['client_id'].value_counts().head(n)

        # 2. On prépare la liste de sortie
        result = []
        for c_id, volume in top_clients.items():
            # Calcul du montant moyen pour ce client spécifique dans le top
            client_avg = df_t[df_t['client_id'] == c_id]['amount'].mean()

            result.append({
                "client_id": str(c_id),
                "transaction_volume": int(volume),
                "average_transaction_value": round(float(client_avg), 2)
            })

        return result

    # =================================================================
    # ROUTE 17 : PROFIL CLIENT SYNTHÉTIQUE
    # =================================================================
    def get_customer_profile(self, customer_id: int):
        """

        Parameters
        ----------
        customer_id : int :
            
        customer_id: int :
            

        Returns
        -------

        
        """
        df_t = self.df_trans
        if df_t is None or df_t.empty:
            return {"id": str(customer_id), "error": "Données transactions indisponibles"}

        user_transactions = df_t[df_t['client_id'].astype(str) == str(customer_id)]

        count = len(user_transactions)
        avg_amount = round(user_transactions['amount'].mean(), 2) if count > 0 else 0.0
        is_fraudulent = any(user_transactions['isFraud'] == 1) if count > 0 else False

        return {
            "id": str(customer_id),
            "transactions_count": count,
            "avg_amount": avg_amount,
            "fraudulent": is_fraudulent
        }

