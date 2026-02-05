import pandas as pd

class StatsService:
    def __init__(self, transaction_service):
        """Injecte le service de transaction pour accéder au DataFrame partagé."""
        self.transaction_service = transaction_service

    def _get_cleaned_df(self):
        """Récupère le DF et applique la valeur absolue sur les montants."""
        df = self.transaction_service.get_all()
        if df is not None and not df.empty:
            # On transforme les montants en valeur absolue (ex: -50 devient 50)
            # Cela évite que les retraits n'annulent les dépôts dans les moyennes
            df['amount'] = df['amount'].abs()
        return df

    def get_global_stats(self):
        """Route 9 : Statistiques globales."""
        df = self._get_cleaned_df()
        if df is None or df.empty:
            return None

        return {
            "total_transactions": int(len(df)),
            "fraud_rate": float(round(df["isFraud"].mean(), 5)),
            "avg_amount": float(round(df["amount"].mean(), 2)),
            "most_common_type": df["use_chip"].mode()[0] if "use_chip" in df.columns else "N/A"
        }

    def get_amount_distribution(self, custom_bins: list = None):
        """Route 10 : Distribution variable des montants."""
        df = self._get_cleaned_df()
        if df is None or df.empty:
            return None

        if not custom_bins or len(custom_bins) < 2:
            bins = [0, 100, 500, 1000, 5000]
        else:
            bins = sorted(list(set(custom_bins)))

        labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]
        dist = pd.cut(df['amount'], bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()

        return {
            "bins": [str(label) for label in dist.index],
            "counts": [int(x) for x in dist.values]
        }

    def get_stats_by_type(self):
        """Route 11 : Stats par type conforme au JSON prof."""
        df = self._get_cleaned_df()
        if df is None or df.empty:
            return None

        # Utilise count et mean sur les valeurs absolues
        stats_type = df.groupby('use_chip')['amount'].agg(['count', 'mean']).reset_index()

        result = []
        for _, row in stats_type.iterrows():
            result.append({
                "type": str(row['use_chip']),
                "count": int(row['count']),
                "avg_amount": float(round(row['mean'], 2))
            })
        return result