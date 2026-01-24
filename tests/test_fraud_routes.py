"""
Unit tests for fraud routes (Routes 13-15).

Estructura:
- Route 13: GET /api/fraud/summary
- Route 14: GET /api/fraud/by-type
- Route 15: POST /api/fraud/predict
"""

import pytest
from fastapi.testclient import TestClient

# IMPORTANTE: Importamos 'app' desde tu estructura src/banking_transaction_api/main.py
from banking_transaction_api.main import app

@pytest.fixture
def client():
    """Fixture para inicializar el cliente de pruebas de FastAPI."""
    return TestClient(app)


class TestFraudSummary:
    """Tests for Route 13: GET /api/fraud/summary"""

    def test_fraud_summary_returns_200(self, client: TestClient):
        response = client.get("/api/fraud/summary")
        assert response.status_code == 200

    def test_fraud_summary_contains_required_fields(self, client: TestClient):
        response = client.get("/api/fraud/summary")
        data = response.json()
        assert all(k in data for k in ["total_frauds", "flagged", "precision", "recall"])

    def test_fraud_summary_values_are_valid(self, client: TestClient):
        response = client.get("/api/fraud/summary")
        data = response.json()
        assert isinstance(data["total_frauds"], int)
        assert 0.0 <= data["precision"] <= 1.0


class TestFraudByType:
    """Tests for Route 14: GET /api/fraud/by-type"""

    def test_fraud_by_type_returns_200(self, client: TestClient):
        response = client.get("/api/fraud/by-type")
        assert response.status_code == 200

    def test_fraud_by_type_returns_list(self, client: TestClient):
        response = client.get("/api/fraud/by-type")
        assert isinstance(response.json(), list)

    def test_fraud_by_type_items_valid(self, client: TestClient):
        response = client.get("/api/fraud/by-type")
        data = response.json()
        if data:
            item = data[0]
            assert all(k in item for k in ["type", "total", "fraud_count", "fraud_rate"])


class TestFraudPredict:
    """Tests for Route 15: POST /api/fraud/predict"""

    def test_fraud_predict_returns_200(self, client: TestClient):
        payload = {
            "type": "TRANSFER",
            "amount": 3500.0,
            "oldbalanceOrg": 15000.0,
            "newbalanceOrig": 11500.0
        }
        response = client.post("/api/fraud/predict", json=payload)
        assert response.status_code == 200

    def test_fraud_predict_logic_response(self, client: TestClient):
        payload = {"type": "TRANSFER", "amount": 100.0}
        response = client.post("/api/fraud/predict", json=payload)
        data = response.json()
        assert "isFraud" in data
        assert "probability" in data
        assert isinstance(data["isFraud"], bool)

    def test_fraud_predict_missing_fields_returns_422(self, client: TestClient):
        # Payload sin 'type'
        payload = {"amount": 3500.0}
        response = client.post("/api/fraud/predict", json=payload)
        assert response.status_code == 422