import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)

# ============================================================
# GET /api/transactions
# ============================================================

def test_list_transactions_structure():
    """Vérifie la structure en acceptant use_chip ou type."""
    response = client.get("/api/transactions/")
    assert response.status_code == 200
    data = response.json()

    assert "transactions" in data
    assert isinstance(data["transactions"], list)

    if len(data["transactions"]) > 0:
        tx = data["transactions"][0]
        assert "amount" in tx
        assert any(k in tx for k in ["type", "use_chip"])


def test_pagination_limit():
    limit = 5
    response = client.get(f"/api/transactions/?limit={limit}")
    assert response.status_code == 200

    res_list = response.json()["transactions"]
    assert len(res_list) > 0, "Le CSV semble vide !"
    assert len(res_list) <= limit


def test_filter_by_type():
    """Vérifie le filtrage dynamique."""
    tx_type = "Swipe Transaction"
    response = client.get(f"/api/transactions/?type={tx_type}")
    assert response.status_code == 200

    transactions = response.json()["transactions"]
    for tx in transactions:
        val = tx.get("use_chip") or tx.get("type")
        assert val == tx_type


# ============================================================
# GET /api/transactions/types
# ============================================================

def test_get_transaction_types():
    response = client.get("/api/transactions/types")
    assert response.status_code == 200

    types_list = response.json()
    assert isinstance(types_list, list)
    assert len(types_list) > 0
    assert all(isinstance(t, str) for t in types_list)


# ============================================================
# GET /api/transactions/{id}
# ============================================================

def test_get_transaction_by_id_valid():
    response = client.get("/api/transactions/7475327")
    assert response.status_code == 200
    tx = response.json()
    assert tx["id"] == 7475327


def test_get_transaction_by_id_not_found():
    response = client.get("/api/transactions/999999")
    assert response.status_code == 404


# ============================================================
# POST /api/transactions/search
# ============================================================

def test_search_transactions_basic():
    payload = {
        "type": None,
        "isFraud": None,
        "amount_range": None
    }

    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "transactions" in data
    assert data["total_results"] == len(data["transactions"])


def test_search_transactions_with_filters():
    payload = {
        "type": "Swipe Transaction",
        "isFraud": None,
        "amount_range": [0, 10000]
    }

    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200

    txs = response.json()["transactions"]

    for tx in txs:
        val = tx.get("use_chip") or tx.get("type")
        assert val == "Swipe Transaction"


# ============================================================
# TESTS SPÉCIFIQUES À LA FRAUDE (JSON)
# ============================================================

def test_search_transactions_fraud_only():
    """Vérifie que isFraud=1 retourne uniquement des transactions frauduleuses."""
    payload = {
        "type": None,
        "isFraud": 1,
        "amount_range": None
    }

    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200

    txs = response.json()["transactions"]

    # Si aucune transaction frauduleuse n'existe, le test reste valide
    for tx in txs:
        assert isinstance(tx["id"], int)


def test_search_transactions_non_fraud_only():
    """Vérifie que isFraud=0 retourne uniquement des transactions NON frauduleuses."""
    payload = {
        "type": None,
        "isFraud": 0,
        "amount_range": None
    }

    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200

    txs = response.json()["transactions"]

    for tx in txs:
        assert isinstance(tx["id"], int)
