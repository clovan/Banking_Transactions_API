from fastapi.testclient import TestClient
from banking_transaction_api.main import app
from banking_transaction_api.services.transactions_service import TransactionService

client = TestClient(app)

# ============================================================
# TESTS DES ROUTES TRANSACTIONS
# ============================================================

def test_list_transactions_route():
    response = client.get("/api/transactions/?page=1&limit=5")
    assert response.status_code == 200

    data = response.json()

    assert "transactions" in data
    assert "total_results" in data
    assert data["page"] == 1
    assert data["limit"] == 5
    assert data["total_results"] > 0
    assert len(data["transactions"]) <= 5


def test_get_transaction_by_id_route():
    # On récupère un ID existant via la route principale
    first_page = client.get("/api/transactions/?limit=1").json()
    tx_id = first_page["transactions"][0]["id"]

    response = client.get(f"/api/transactions/{tx_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == tx_id
    assert "amount" in data


def test_search_transactions_route():
    response = client.post("/api/transactions/search?min_amount=10")
    assert response.status_code == 200

    data = response.json()
    assert "transactions" in data
    assert "total_results" in data
    assert data["total_results"] >= 0

    for tx in data["transactions"]:
        assert tx["amount"] >= 10


# ============================================================
# TESTS DU SERVICE TRANSACTIONSERVICE
# ============================================================

def test_get_all_service():
    service = TransactionService()
    df = service.get_all()

    assert df is not None
    assert not df.empty
    assert "id" in df.columns
    assert "amount" in df.columns
    assert "transaction_type" in df.columns
    assert "isFraud" in df.columns


def test_get_transaction_by_id_service():
    service = TransactionService()
    df = service.get_all()

    # On prend un ID réel
    tx_id = int(df.iloc[0]["id"])

    tx = service.get_transaction_by_id(tx_id)
    assert tx is not None
    assert tx["id"] == tx_id


def test_filter_transactions_service():
    service = TransactionService()
    df = service.get_all()

    # Filtre simple : montant minimum
    filtered = service.filter_transactions(df, min_amount=100)

    assert not filtered.empty
    for _, row in filtered.iterrows():
        assert row["amount"] >= 100
