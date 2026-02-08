from fastapi.testclient import TestClient
from banking_transaction_api.main import app
from banking_transaction_api.services.stats_service import StatistiquesService
from banking_transaction_api.services.transactions_service import TransactionService

client = TestClient(app)

# ============================================================
# TESTS DES ROUTES STATISTIQUES
# ============================================================

def test_stats_overview_route():
    response = client.get("/api/stats/overview")
    assert response.status_code == 200

    data = response.json()
    assert "total_transactions" in data
    assert "fraud_rate" in data
    assert "avg_amount" in data
    assert "most_common_type" in data
    assert data["total_transactions"] > 0


def test_stats_by_type_route():
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    for item in data:
        assert "type" in item
        assert "count" in item
        assert "avg_amount" in item


def test_stats_daily_route():
    response = client.get("/api/stats/daily")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if len(data) > 0:
        for item in data:
            assert "date" in item
            assert "count" in item
            assert "avg_amount" in item


# ============================================================
# TESTS DU SERVICE STATISTIQUESERVICE
# ============================================================

def test_get_overview_stats_service():
    ts = TransactionService()
    service = StatistiquesService(ts)

    stats = service.get_overview_stats()

    assert stats["total_transactions"] > 0
    assert stats["avg_amount"] is not None
    assert stats["most_common_type"] is not None
    assert 0 <= stats["fraud_rate"] <= 1


def test_get_stats_by_type_service():
    ts = TransactionService()
    service = StatistiquesService(ts)

    stats = service.get_stats_by_type()

    assert isinstance(stats, list)
    assert len(stats) > 0

    for item in stats:
        assert "type" in item
        assert "count" in item
        assert "avg_amount" in item


def test_get_daily_stats_service():
    ts = TransactionService()
    service = StatistiquesService(ts)

    stats = service.get_daily_stats()

    assert isinstance(stats, list)

    if len(stats) > 0:
        for item in stats:
            assert "date" in item
            assert "count" in item
            assert "avg_amount" in item
