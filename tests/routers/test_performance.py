import time
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


def test_performance_latency_filtering():
    """Vérifie que la recherche de 100 transactions prend moins de 500ms."""
    start_time = time.time()

    # On demande 100 transactions (limit=100)
    response = client.get("/api/transactions/?limit=100")

    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000

    assert response.status_code == 200
    assert len(response.json()["transactions"]) <= 100
    # On vérifie la contrainte des 500ms
    assert latency_ms < 500, f"L'API est trop lente : {latency_ms:.2f}ms"

    print(f"\nTemps de réponse mesuré : {latency_ms:.2f}ms")