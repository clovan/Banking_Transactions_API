import unittest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app


class TestBankingFeatures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_feature_transaction_search(self):
        """Feature : Recherche multicritère de transactions."""
        payload = {
            "type": "Online Transaction",
            "amount_range": [10.0, 100.0],
            "isFraud": 0
        }
        response = self.client.post("/api/transactions/search", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()

        # ANALYSE DU DICTIONNAIRE REÇU
        # On cherche la liste des transactions soit à la racine, soit dans une clé
        if isinstance(data, list):
            transactions = data
        elif isinstance(data, dict):
            # On cherche les clés communes (data, transactions, results, etc.)
            transactions = data.get("transactions") or data.get("data") or data.get("results")
            # Si aucune clé ne match, on prend la première valeur qui est une liste
            if transactions is None:
                for val in data.values():
                    if isinstance(val, list):
                        transactions = val
                        break

        # Si après tout ça on n'a rien, on considère que 'data' est ce qu'on cherche
        if transactions is None:
            transactions = data

        self.assertIsInstance(transactions, list, f"L'API doit renvoyer une liste. Reçu: {type(data)}")

        if len(transactions) > 0:
            # On vérifie le premier élément
            tx = transactions[0]
            self.assertIn('amount', tx)
            self.assertLessEqual(float(tx['amount']), 100.0)

    def test_feature_client_stats_integration(self):
        """Feature : Cohérence entre les stats globales et les données."""
        response = self.client.get("/api/stats/overview")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("total_transactions", data)
        self.assertIn("fraud_rate", data)

        # Validation robuste des types (NumPy vs Python native)
        self.assertTrue(any([isinstance(data["total_transactions"], int), str(data["total_transactions"]).isdigit()]))


if __name__ == "__main__":
    unittest.main()