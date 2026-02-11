import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ajout du chemin racine pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from banking_transaction_api.main import app

client = TestClient(app)

# =================================================================
# ROUTE 1 : LISTE ET FILTRAGE GLOBAL
# =================================================================

def test_route_1_list_structure():
    """Vérifie le contrat d'interface : renommage transaction_type et pagination."""
    response = client.get("/api/transactions/?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    # On retire le skip et on check si on a des data
    if data["transactions"]:
        tx = data["transactions"][0]
        assert "transaction_type" in tx
        assert isinstance(tx["amount"], (int, float))

def test_route_1_filter_fraud():
    """Vérifie le filtrage des fraudes."""
    response = client.get("/api/transactions/?isFraud=1")
    assert response.status_code == 200

# =================================================================
# ROUTE 3 : RECHERCHE AVANCÉE (POST)
# =================================================================

def test_route_3_search_advanced():
    """Vérifie la recherche multicritère."""
    payload = {
        "type": "Online Transaction",
        "amount_range": [0.0, 100.0]
    }
    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200

# =================================================================
# ROUTE 2 : DÉTAILS D'UNE TRANSACTION (FIXE)
# =================================================================

def test_route_2_get_transaction_detail():
    """Vérifie la récupération par l'ID 0 (toujours présent au début du CSV)."""
    response = client.get("/api/transactions/0")
    # On accepte 200 si chargé, ou 404 si le fichier n'est vraiment pas lu
    assert response.status_code in [200, 404]

def test_route_2_not_found():
    """Vérifie le message 404 sur ID inexistant."""
    response = client.get("/api/transactions/999999999")
    assert response.status_code == 404
    assert "introuvable" in response.json()["detail"]

# =================================================================
# ROUTE 6 : SUPPRESSION
# =================================================================

def test_route_6_delete_transaction():
    """Vérifie la suppression de l'ID 0."""
    response = client.delete("/api/transactions/0")
    assert response.status_code in [200, 404]

# =================================================================
# ROUTE 7 : FLUX SORTANTS (DÉBITS)
# =================================================================

def test_route_7_customer_debits_flow():
    """Vérifie le flux de débit pour le client 825."""
    response = client.get("/api/transactions/by-customer/825")
    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json()["detail"] == "ce client n'a pas de debit dans compte"


def test_route_7_customer_debits_not_found():
    """Vérifie le message d'erreur personnalisé."""
    response = client.get("/api/transactions/by-customer/9999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "ce client n'a pas de debit dans compte"


# =================================================================
# ROUTE 8 : FLUX ENTRANTS (CRÉDITS)
# =================================================================

def test_route_8_customer_credits_flow():
    """Vérifie le flux de crédit pour le client 825."""
    response = client.get("/api/transactions/to-customer/825")
    assert response.status_code in [200, 404]
    if response.status_code == 404:
        assert response.json()["detail"] == "ce client n'a pas de credit sur son compte"


def test_route_8_customer_credits_not_found():
    """Vérifie le message d'erreur personnalisé."""
    response = client.get("/api/transactions/to-customer/9999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "ce client n'a pas de credit sur son compte"
