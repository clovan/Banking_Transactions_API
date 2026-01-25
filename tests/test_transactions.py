import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


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
        # On vérifie la présence de l'une ou l'autre des colonnes
        assert any(k in tx for k in ["type", "use_chip"])


def test_pagination_limit():
    limit = 5
    response = client.get(f"/api/transactions/?limit={limit}")
    assert response.status_code == 200
    # Vérifie que la liste n'est pas vide pour valider que le CSV est bien chargé
    res_list = response.json()["transactions"]
    assert len(res_list) > 0, "Le CSV semble vide sur Windows !"
    assert len(res_list) <= limit


def test_filter_by_type():
    """Vérifie le filtrage dynamique."""
    tx_type = "Swipe Transaction"
    response = client.get(f"/api/transactions/?type={tx_type}")
    assert response.status_code == 200

    transactions = response.json()["transactions"]
    for tx in transactions:
        # On cherche la valeur dans la colonne disponible (type ou use_chip)
        val = tx.get("use_chip") or tx.get("type")
        assert val == tx_type