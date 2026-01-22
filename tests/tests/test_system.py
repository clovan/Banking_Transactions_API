from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime" in data
    assert "dataset_loaded" in data

def test_metadata_endpoint():
    response = client.get("/api/system/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert "last_update" in data