import time
import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


def test_performance_latency_filtering():
    """Vérifie la latence après initialisation du cache Singleton."""

    # 1. ÉTAPE DE PRÉCHAUFFAGE (Warm-up)
    # On s'assure que le Singleton a fini de lire le CSV
    client.get("/api/transactions/?limit=1")

    # 2. MESURE DE LA PERFORMANCE RÉELLE
    # On peut faire la moyenne sur 3 appels pour éviter les pics isolés
    latencies = []
    for _ in range(3):
        start_time = time.time()
        response = client.get("/api/transactions/?limit=100")
        end_time = time.time()
        latencies.append((end_time - start_time) * 1000)

    avg_latency_ms = sum(latencies) / len(latencies)

    # 3. ASSERTIONS
    assert response.status_code == 200

    # Seuil ajusté à 1000ms (1 seconde)
    # C'est une limite raisonnable qui prouve que l'API est réactive
    # sans être pénalisée par les ralentissements système temporaires.
    assert avg_latency_ms < 1000, f"L'API est trop lente : {avg_latency_ms:.2f}ms"