import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


# =================================================================
# TEST ROUTE 19 : HEALTH & UPTIME
# =================================================================
def test_get_health():
    """Vérifie que la route health répond 200 et a le bon format d'uptime."""
    response = client.get("/api/system/health")

    assert response.status_code == 200
    data = response.json()

    # Vérification des clés
    assert "status" in data
    assert "uptime" in data
    assert "dataset_loaded" in data

    # Vérification du format de l'uptime (ex: "0h 0min 5s")
    uptime = data["uptime"]
    assert "h" in uptime
    assert "min" in uptime
    assert "s" in uptime
    # Vérifie qu'il y a bien des espaces (ex: "h " et "min ")
    assert "h " in uptime
    assert "min " in uptime


# =================================================================
# TEST ROUTE 20 : METADATA
# =================================================================
def test_get_metadata():
    """Vérifie la version et le format de la date de mise à jour."""
    response = client.get("/api/system/metadata")

    assert response.status_code == 200
    data = response.json()

    # Vérification des valeurs attendues
    assert data["version"] == "1.0.0"
    assert "last_update" in data

    # Vérification sommaire du format ISO de la date (contient 'T' et 'Z')
    assert "T" in data["last_update"]
    assert "Z" in data["last_update"]