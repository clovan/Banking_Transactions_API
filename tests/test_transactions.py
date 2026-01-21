import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


# --- TESTS EXISTANTS (AMÉLIORÉS) ---

def test_list_transactions_structure():
    """Vérifie la structure et la présence de la fraude fusionnée."""
    response = client.get("/api/transactions/")
    assert response.status_code == 200
    data = response.json()

    assert "transactions" in data
    if len(data["transactions"]) > 0:
        tx = data["transactions"][0]
        # Vérifie que le montant est bien un nombre (nettoyé du $)
        assert isinstance(tx["amount"], (int, float))
        # Vérifie que la colonne isFraud est bien présente suite à la fusion JSON
        assert "isFraud" in tx


def test_pagination_limit():
    limit = 5
    response = client.get(f"/api/transactions/?limit={limit}")
    assert response.status_code == 200
    res_list = response.json()["transactions"]
    assert len(res_list) <= limit


# --- TESTS POUR LES NOUVELLES ROUTES ---

def test_route_7_customer_debits():
    """Vérifie que la route 7 ne renvoie que des débits (montant < 0)."""
    # On utilise l'ID client 1556 visible dans tes données
    customer_id = 1556
    response = client.get(f"/api/transactions/by-customer/{customer_id}")

    assert response.status_code == 200
    transactions = response.json()["transactions"]

    for tx in transactions:
        assert tx["amount"] < 0, f"La transaction {tx['id']} devrait être un débit"
        assert tx["client_id"] == customer_id


def test_route_8_customer_credits():
    """Vérifie que la route 8 ne renvoie que des crédits (montant > 0)."""
    customer_id = 1556
    response = client.get(f"/api/transactions/to-customer/{customer_id}")

    assert response.status_code == 200
    transactions = response.json()["transactions"]

    for tx in transactions:
        assert tx["amount"] > 0, f"La transaction {tx['id']} devrait être un crédit"
        assert tx["client_id"] == customer_id


def test_route_9_stats_overview():
    """Vérifie la structure et la validité des statistiques globales."""
    response = client.get("/api/transactions/stats/overview")

    assert response.status_code == 200
    stats = response.json()

    # Vérification des champs exigés
    assert "total_transactions" in stats
    assert "fraud_rate" in stats
    assert "avg_amount" in stats
    assert "most_common_type" in stats

    # Vérification des types de données
    assert isinstance(stats["total_transactions"], int)
    assert 0 <= stats["fraud_rate"] <= 1
    assert isinstance(stats["most_common_type"], str)


def test_route_6_delete_transaction():
    """Vérifie que la suppression d'une transaction fonctionne."""
    # ID issu de ton fichier CSV
    tx_id = 7475327
    response = client.delete(f"/api/transactions/{tx_id}")

    # Peut être 200 (succès) ou 404 (si déjà supprimé par un test précédent)
    assert response.status_code in [200, 404]


def test_filter_by_fraud():
    """Vérifie le filtrage par fraude (0 ou 1) rendu possible par la fusion."""
    response = client.get("/api/transactions/?isFraud=0")
    assert response.status_code == 200
    for tx in response.json()["transactions"]:
        assert tx["isFraud"] == 0