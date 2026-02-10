import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ajout du chemin racine pour les imports selon la structure du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from banking_transaction_api.main import app

client = TestClient(app)

# --- Fonctions utilitaires pour le dynamisme des tests ---

def get_first_valid_id():
    """Récupère dynamiquement un ID depuis le Data Loader via l'API."""
    response = client.get("/api/transactions/?limit=1")
    txs = response.json().get("transactions", [])
    return txs[0]["id"] if txs else None


def get_first_valid_customer_id():
    """Récupère un ID client existant pour tester les flux."""
    response = client.get("/api/transactions/?limit=1")
    txs = response.json().get("transactions", [])
    return txs[0].get("client_id") if txs else None


# =================================================================
# ROUTE 1 : LISTE ET FILTRAGE GLOBAL
# =================================================================

def test_route_1_list_structure():
    """Vérifie le contrat d'interface : renommage transaction_type et pagination."""
    response = client.get("/api/transactions/?limit=5")
    assert response.status_code == 200
    data = response.json()

    assert "transactions" in data
    assert "total_results" in data

    if data["transactions"]:
        tx = data["transactions"][0]
        # Vérifie que le Data Loader / Service a bien transformé use_chip
        assert "transaction_type" in tx
        assert "use_chip" not in tx
        # Vérifie que le montant est bien un flottant (nettoyage regex réussi)
        assert isinstance(tx["amount"], (int, float))


def test_route_1_filter_fraud():
    """Vérifie la fusion des labels JSON effectuée par le Data Loader."""
    response = client.get("/api/transactions/?isFraud=1")
    assert response.status_code == 200
    transactions = response.json().get("transactions", [])
    for tx in transactions:
        assert tx["isFraud"] == 1


# =================================================================
# ROUTE 3 : RECHERCHE AVANCÉE (POST)
# =================================================================

def test_route_3_search_advanced():
    """Vérifie que la recherche JSON renvoie les bons types (formatage _prepare_output)."""
    type_res = client.get("/api/transactions/types")
    types = type_res.json().get("types", [])

    if not types:
        pytest.skip("Pas de types disponibles dans le dataset actuel")

    target_type = types[0]
    payload = {
        "type": target_type,
        "amount_range": [-10000, 10000]
    }
    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200
    results = response.json().get("results", [])

    for tx in results:
        # Vérifie que le filtrage sur use_chip/transaction_type est cohérent
        assert tx["transaction_type"] == target_type


# =================================================================
# ROUTE 4 : LISTE DES TYPES
# =================================================================

def test_route_4_get_types():
    """Vérifie que la route statique répond correctement (priorité routeur)."""
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    assert isinstance(response.json().get("types"), list)


# =================================================================
# ROUTE 5 : RÉCENTS
# =================================================================

def test_route_5_get_recent():
    """Vérifie le tri décroissant (head du DataFrame)."""
    response = client.get("/api/transactions/recent?n=3")
    assert response.status_code == 200
    data = response.json()
    if len(data) >= 2:
        # Les IDs les plus récents (grands) doivent être en premier
        assert data[0]["id"] >= data[1]["id"]


# =================================================================
# ROUTE 2 : DÉTAILS D'UNE TRANSACTION
# =================================================================

def test_route_2_get_transaction_detail():
    """Vérifie la route dynamique après les routes statiques."""
    tx_id = get_first_valid_id()
    if tx_id is None:
        pytest.skip("Le dataset est vide")

    response = client.get(f"/api/transactions/{tx_id}")
    assert response.status_code == 200
    assert response.json()["id"] == tx_id
    assert "transaction_type" in response.json()


def test_route_2_not_found():
    """Vérifie le comportement sur un ID inexistant."""
    response = client.get("/api/transactions/999999999")
    assert response.status_code == 404


# =================================================================
# ROUTE 6 : SUPPRESSION
# =================================================================

def test_route_6_delete_transaction():
    """Vérifie que la suppression en mémoire (self._df) fonctionne."""
    tx_id = get_first_valid_id()
    if tx_id is None:
        pytest.skip("Aucune transaction à supprimer")

    # Suppression
    del_res = client.delete(f"/api/transactions/{tx_id}")
    assert del_res.status_code == 200

    # Vérification de la disparition immédiate
    check_res = client.get(f"/api/transactions/{tx_id}")
    assert check_res.status_code == 404


# =================================================================
# ROUTE 7 : FLUX SORTANTS (DÉBITS)
# =================================================================

def test_route_7_customer_debits():
    """Vérifie le filtrage amount < 0 du Service."""
    c_id = get_first_valid_customer_id()
    if c_id is None:
        pytest.skip("Aucun client trouvé dans le dataset")

    response = client.get(f"/api/transactions/by-customer/{c_id}")
    if response.status_code == 200:
        txs = response.json().get("transactions", [])
        for tx in txs:
            assert tx["amount"] < 0
            assert tx["client_id"] == c_id


# =================================================================
# ROUTE 8 : FLUX ENTRANTS (CRÉDITS)
# =================================================================

def test_route_8_customer_credits():
    """Vérifie le filtrage amount > 0 du Service."""
    c_id = get_first_valid_customer_id()
    if c_id is None:
        pytest.skip("Aucun client trouvé dans le dataset")

    response = client.get(f"/api/transactions/to-customer/{c_id}")
    if response.status_code == 200:
        txs = response.json().get("transactions", [])
        for tx in txs:
            assert tx["amount"] > 0
            assert tx["client_id"] == c_id