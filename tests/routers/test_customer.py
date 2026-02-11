import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


# =================================================================
# TEST ROUTE 16 : LISTE PAGINÉE
# =================================================================
def test_get_customers_pagination():
    """Vérifie que la route 16 renvoie bien le format attendu et la pagination."""
    response = client.get("/api/customers/?page=1&size=5")
    assert response.status_code == 200
    data = response.json()

    assert "total" in data
    assert "data" in data
    assert len(data["data"]) <= 5  # Taille respectée
    assert isinstance(data["data"], list)


# =================================================================
# TEST ROUTE 18 : TOP CLIENTS (Avant la 17 pour tester l'ordre)
# =================================================================
def test_get_top_customers():
    """Vérifie que la route 18 renvoie un classement par volume."""
    response = client.get("/api/customers/top?n=3")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    if len(data) > 0:
        assert "transaction_volume" in data[0]
        assert "average_transaction_value" in data[0]
        # Vérifie l'ordre décroissant du volume
        if len(data) > 1:
            assert data[0]["transaction_volume"] >= data[1]["transaction_volume"]


# =================================================================
# TEST ROUTE 17 : PROFIL SYNTHÉTIQUE
# =================================================================
def test_get_customer_profile():
    """Vérifie le profil synthétique d'un client existant (ex: 825)."""
    customer_id = 825
    response = client.get(f"/api/customers/{customer_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(customer_id)
    assert "transactions_count" in data
    assert "avg_amount" in data
    assert "fraudulent" in data
    assert isinstance(data["fraudulent"], bool)


def test_get_customer_profile_not_found():
    """Vérifie le comportement avec un ID qui n'existe pas (0 ou négatif)."""
    response = client.get("/api/customers/999999")
    assert response.status_code == 200  # Ton service renvoie un objet avec count=0
    assert response.json()["transactions_count"] == 0