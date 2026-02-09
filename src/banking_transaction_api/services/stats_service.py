import pandas as pd

class StatsService:
    def __init__(self, transaction_service):
        """Injecte le service de transaction pour accéder au DataFrame partagé."""
        self.transaction_service = transaction_service

    def _get_cleaned_df(self):
        """Récupère le DF et applique la valeur absolue sur les montants."""
        df = self.transaction_service.get_all()
        if df is not None and not df.empty:
            df = df.copy()
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
        df = self._get_cleaned_df()
        if df is None or df.empty:
            return None

        if not custom_bins or len(custom_bins) < 2:
            bins = [0.0, 100.0, 500.0, 1000.0, 5000.0]
        else:
            bins = sorted(list(set([float(b) for b in custom_bins])))

        labels = [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(len(bins)-1)]

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

        stats_type = df.groupby('use_chip')['amount'].agg(['count', 'mean']).reset_index()

        result = []
        for _, row in stats_type.iterrows():
            result.append({
                "type": str(row['use_chip']),
                "count": int(row['count']),
                "avg_amount": float(round(row['mean'], 2))
            })
        return result

    # =================================================================
    # ROUTE 12 : ANALYSE TEMPORELLE (PAR JOUR)
    # =================================================================
    def get_daily_stats(self):
        """Calcule le nombre de transactions et la moyenne par jour."""
        df = self._get_cleaned_df()
        if df is None or df.empty:
            return None

        # Tentative de reconstruction de la date si les colonnes Year/Month/Day existent
        if all(col in df.columns for col in ['Year', 'Month', 'Day']):
            df['temp_date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        elif 'date' in df.columns:
            df['temp_date'] = pd.to_datetime(df['date'])
        else:
            # Si aucune colonne temporelle n'est trouvée
            return []

        # Groupement par date
        daily_stats = df.groupby('temp_date')['amount'].agg(['count', 'mean']).sort_index()

        result = []
        for date, row in daily_stats.iterrows():
            result.append({
                "date": date.strftime('%Y-%m-%d'),
                "count": int(row['count']),
                "avg_amount": float(round(row['mean'], 2))
            })
        return result