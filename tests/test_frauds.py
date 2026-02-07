import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app
from banking_transaction_api.services.fraud_detection_service import FraudDetectionService

client = TestClient(app)

# =================================================================
# SECTION 1 : TESTS UNITAIRES (Logique métier du Service)
# =================================================================

def test_route_13_summary_logic():
    """
    UNIT TEST - ROUTE 13 : Vérifie la logique du résumé statistique.
    """
    service = FraudDetectionService()
    summary = service.get_fraud_summary()
    assert "total_frauds" in summary
    assert "precision" in summary
    assert isinstance(summary["precision"], float)

def test_route_14_by_type_logic():
    """
    UNIT TEST - ROUTE 14 : Vérifie le groupement par mode 'use_chip'.
    """
    service = FraudDetectionService()
    by_type = service.get_fraud_by_type()
    assert isinstance(by_type, dict)
    # On s'assure que le dictionnaire contient des données si le dataset est chargé
    if by_type:
        assert any(k in by_type for k in ["Online Transaction", "Swipe Transaction"])

def test_route_15_predict_logic():
    """
    UNIT TEST - ROUTE 15 : Vérifie le calcul de probabilité de fraude.
    """
    service = FraudDetectionService()
    data = {
        "type": "Online Transaction",
        "amount": 5000.0,
        "oldbalanceOrg": 1000.0,
        "newbalanceOrig": 0.0
    }
    prediction = service.predict_fraud(data)
    assert "isFraud" in prediction
    assert prediction["probability"] > 0.5


# =================================================================
# SECTION 2 : TESTS DE FONCTIONNALITÉS (Endpoints API)
# =================================================================

def test_api_route_13_get_summary():
    """
    FEATURE TEST - ROUTE 13 : GET /api/fraud/summary
    """
    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    assert "flagged" in response.json()

def test_api_route_14_get_by_type():
    """
    FEATURE TEST - ROUTE 14 : GET /api/fraud/by-type
    """
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_api_route_15_post_predict_success():
    """
    FEATURE TEST - ROUTE 15 : POST /api/fraud/predict (Succès)
    """
    payload = {
        "type": "Online Transaction",
        "amount": 3500.0,
        "oldbalanceOrg": 500.0,
        "newbalanceOrig": 0.0
    }
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["isFraud"] is True

def test_api_route_15_post_predict_bad_request():
    """
    FEATURE TEST - ROUTE 15 : POST /api/fraud/predict (Erreur 422)
    """
    # Test avec un type de données incorrect (amount en string au lieu de float)
    payload = {"type": "Online Transaction", "amount": "beaucoup"}
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 422