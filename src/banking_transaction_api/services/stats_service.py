import pandas as pd
from banking_transaction_api.services.transactions_service import TransactionService

class StatistiquesService:
    def __init__(self):
        self.transaction_service = TransactionService()

    def get_overview_stats(self):
        df = self.transaction_service.get_all()
        fraud_dict = self.transaction_service._fraud_dict  # JSON chargé dans le service

        if df.empty:
            return {
                "total_transactions": 0,
                "fraud_rate": None,
                "avg_amount": None,
                "most_common_type": None
            }

        # -----------------------------
        # 1. Total des transactions
        # -----------------------------
        total_transactions = len(df)

        # -----------------------------
        # 2. Nettoyage du montant
        # -----------------------------
        df["amount"] = (
            df["amount"]
            .replace(r'[\$,]', '', regex=True)
            .astype(float)
        )
        avg_amount = df["amount"].mean()

        # -----------------------------
        # 3. Type le plus fréquent
        # -----------------------------
        col_type = "use_chip" if "use_chip" in df.columns else "type"
        most_common_type = df[col_type].mode()[0]

        # -----------------------------
        # 4. Fraud rate via JSON
        # -----------------------------
        fraud_count = sum(fraud_dict.get(int(tx_id), 0) for tx_id in df["id"])
        fraud_rate = fraud_count / total_transactions if total_transactions > 0 else None

        return {
            "total_transactions": total_transactions,
            "fraud_rate": fraud_rate,
            "avg_amount": avg_amount,
            "most_common_type": most_common_type
        }

    def get_amount_distribution(self):
        df = self.transaction_service.get_all()

        if df.empty:
            return {"bins": [], "counts": []}

        # Nettoyage montant
        df["amount"] = (
            df["amount"]
            .replace(r'[\$,]', '', regex=True)
            .astype(float)
        )

        bins = [0, 100, 500, 1000, 5000]
        labels = ["0-100", "100-500", "500-1000", "1000-5000"]

        df["bin"] = pd.cut(df["amount"], bins=bins, labels=labels, right=False)

        counts = df["bin"].value_counts().sort_index().tolist()

        return {
            "bins": labels,
            "counts": counts
        }

    def get_stats_by_type(self):
        df = self.transaction_service.get_all()

        if df.empty:
            return []

        # Nettoyage montant
        df["amount"] = (
            df["amount"]
            .replace(r'[\$,]', '', regex=True)
            .astype(float)
        )

        col_type = "use_chip" if "use_chip" in df.columns else "type"

        results = []

        for t in df[col_type].unique():
            subset = df[df[col_type] == t]

            results.append({
                "type": t,
                "count": len(subset),
                "avg_amount": subset["amount"].mean()
            })

        return results

    def get_daily_stats(self):
        df = self.transaction_service.get_all()

        if df.empty or "date" not in df.columns:
            return []

        # Convertir la date
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Nettoyage montant
        df["amount"] = (
            df["amount"]
            .replace(r'[\$,]', '', regex=True)
            .astype(float)
        )

        daily = (
            df.groupby(df["date"].dt.date)["amount"]
            .agg(["count", "mean"])
            .reset_index()
            .rename(columns={"date": "date", "count": "count", "mean": "avg_amount"})
        )

        return [
            {
                "date": str(row["date"]),
                "count": int(row["count"]),
                "avg_amount": float(row["avg_amount"])
            }
            for _, row in daily.iterrows()
        ]
