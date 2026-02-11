import time
import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


def test_performance_latency_filtering():
    """Vérifie la latence après initialisation du cache Singleton."""

    # 1. ÉTAPE DE PRÉCHAUFFAGE (Warm-up)
    # On charge le cache une fois, ce temps n'est pas chronométré
    client.get("/api/transactions/?limit=1")

    # 2. MESURE DE LA PERFORMANCE RÉELLE
    start_time = time.time()

    # On demande 100 transactions (limit=100)
    response = client.get("/api/transactions/?limit=100")

    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000

    # 3. ASSERTIONS
    assert response.status_code == 200
    # Maintenant que le cache est plein, cela prendra entre 5ms et 50ms
    assert latency_ms < 500, f"L'API est trop lente : {latency_ms:.2f}ms"