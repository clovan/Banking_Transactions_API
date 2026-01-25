import pandas as pd
from typing import Dict, Any, List
# Ajustamos el import según tu estructura en el VS Code
from src.banking_transaction_api.data_loader import DataLoader

class FraudDetectionService:
    """Service for fraud detection and analysis."""

    def __init__(self):
        # Se inicializa el cargador de datos
        self.data_loader = DataLoader()

    def get_fraud_summary(self) -> Dict[str, Any]:
        """
        Get an overview of fraud statistics.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing:
            - total_frauds: Total number of fraudulent transactions
            - flagged: Number of transactions flagged by the detection system
            - precision: TP / (TP + FP)
            - recall: TP / (TP + FN)
        """
        df = self.data_loader.transactions

        if 'is_fraud' not in df.columns:
            return {"error": "Fraud labels not loaded"}

        total_frauds = int(df['is_fraud'].sum())

        # Determinar la columna de tipo (mapeada en DataLoader)
        type_col = 'type' if 'type' in df.columns else 'use_chip'
        
        def predict_for_row(row):
            transaction_data = {
                'amount': row.get('amount', 0),
                'type': row.get(type_col, ''),
            }
            if 'oldbalanceOrg' in row:
                transaction_data['oldbalanceOrg'] = row['oldbalanceOrg']
            if 'newbalanceOrig' in row:
                transaction_data['newbalanceOrig'] = row['newbalanceOrig']
            
            prediction = self.predict_fraud(transaction_data)
            return 1 if prediction['isFraud'] else 0
        
        # Aplicamos la predicción a cada fila para calcular métricas
        df['is_flagged'] = df.apply(predict_for_row, axis=1)
        flagged = int(df['is_flagged'].sum())

        true_positives = int(((df['is_flagged'] == 1) & (df['is_fraud'] == 1)).sum())
        false_positives = int(((df['is_flagged'] == 1) & (df['is_fraud'] == 0)).sum())
        false_negatives = int(((df['is_flagged'] == 0) & (df['is_fraud'] == 1)).sum())

        precision = 0.0
        if (true_positives + false_positives) > 0:
            precision = round(true_positives / (true_positives + false_positives), 2)

        recall = 0.0
        if (true_positives + false_negatives) > 0:
            recall = round(true_positives / (true_positives + false_negatives), 2)

        return {
            "total_frauds": total_frauds,
            "flagged": flagged,
            "precision": precision,
            "recall": recall
        }

    def get_fraud_by_type(self) -> List[Dict[str, Any]]:
        """
        Get fraud rate distribution by transaction type.
        """
        df = self.data_loader.transactions

        if 'is_fraud' not in df.columns:
            return []

        type_col = 'type' if 'type' in df.columns else 'use_chip'

        stats = df.groupby(type_col)['is_fraud'].agg(['count', 'sum']).reset_index()
        stats.columns = ['type', 'total', 'fraud_count']
        stats['fraud_rate'] = round(stats['fraud_count'] / stats['total'], 4)

        stats = stats.fillna(0)
        stats['total'] = stats['total'].astype(int)
        stats['fraud_count'] = stats['fraud_count'].astype(int)

        return stats.to_dict(orient='records')

    def predict_fraud(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict if a given transaction is fraudulent using a simplified scoring model.
        """
        amount = abs(float(transaction_data.get('amount', 0)))
        tx_type = str(transaction_data.get('type', ''))
        old_balance = transaction_data.get('oldbalanceOrg')
        new_balance = transaction_data.get('newbalanceOrig')

        probability = 0.0

        # Lógica basada en tipos de transacción
        if tx_type == 'Online Transaction':
            probability += 0.45
        elif tx_type == 'Swipe Transaction':
            probability += 0.05

        # Lógica basada en montos
        if amount > 500:
            probability += 0.25
        elif amount > 200:
            probability += 0.15
        elif amount > 100:
            probability += 0.08

        # Discrepancia de saldo
        if old_balance is not None and new_balance is not None:
            expected_new_balance = old_balance - amount
            if abs(new_balance - expected_new_balance) > 0.01:
                probability += 0.2

        probability = min(round(probability, 2), 0.99)

        return {
            "isFraud": probability > 0.5,
            "probability": probability
        }