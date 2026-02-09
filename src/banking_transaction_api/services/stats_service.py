import pandas as pd

class StatsService:
    def __init__(self, transaction_service):
        """Injecte le service de transaction pour accéder au DataFrame partagé."""
        self.transaction_service = transaction_service

    def _get_cleaned_df(self):
        """Récupère le DF et applique la valeur absolue sur les montants."""
        df = self.transaction_service.get_all()
        if df is not None and not df.empty:
            # Important : on crée une copie pour ne pas polluer le DF original
            df = df.copy()
            # On transforme les montants en valeur absolue (ex: -50 devient 50)
            df['amount'] = df['amount'].abs()
        return df

    # =================================================================
    # ROUTE 9 : STATISTIQUES GLOBALES
    # =================================================================
    def get_global_stats(self):
        df = self._get_cleaned_df()
        if df is None or df.empty:
            return None

        return {
            "total_transactions": int(len(df)),
            "fraud_rate": float(round(df["isFraud"].mean(), 5)),
            "avg_amount": float(round(df["amount"].mean(), 2)),
            "most_common_type": df["use_chip"].mode()[0] if "use_chip" in df.columns else "N/A"
        }

    # =================================================================
    # ROUTE 10 : DISTRIBUTION DES MONTANTS (BINS)
    # =================================================================
    def get_amount_distribution(self, custom_bins: list = None):
        """
        Génère la distribution des montants.
        Par défaut : [0, 100, 500, 1000, 5000]
        """
        df = self._get_cleaned_df()
        if df is None or df.empty:
            return None

        # 1. Définition des paliers (Default vs Custom)
        if not custom_bins or len(custom_bins) < 2:
            bins = [0.0, 100.0, 500.0, 1000.0, 5000.0]
        else:
            # Nettoyage : suppression doublons, tri et conversion en float
            bins = sorted(list(set([float(b) for b in custom_bins])))

        # 2. Création des labels dynamiques (ex: "0-100")
        labels = [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(len(bins)-1)]

        # 3. Calcul de la distribution
        # include_lowest=True permet d'inclure la valeur 0 dans le premier palier
        dist = pd.cut(
            df['amount'],
            bins=bins,
            labels=labels,
            include_lowest=True
        ).value_counts().sort_index()

        return {
            "bins": [str(label) for label in dist.index],
            "counts": [int(x) for x in dist.values],
            "applied_bins": bins
        }

    # =================================================================
    # ROUTE 11 : STATISTIQUES PAR TYPE
    # =================================================================
    def get_stats_by_type(self):
        df = self._get_cleaned_df()
        if df is None or df.empty:
            return None

        # Agrégation par type de transaction
        stats_type = df.groupby('use_chip')['amount'].agg(['count', 'mean']).reset_index()

        result = []
        for _, row in stats_type.iterrows():
            result.append({
                "type": str(row['use_chip']),
                "count": int(row['count']),
                "avg_amount": float(round(row['mean'], 2))
            })
        return result