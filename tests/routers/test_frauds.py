import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app
from banking_transaction_api.services.fraud_detection_service import (
    FraudDetectionService,
)

client = TestClient(app)

# =================================================================
# FIXTURE : Initialisation et Préchauffage
# =================================================================


@pytest.fixture(scope="module")
def fraud_service():
    """Initialise le service et charge le cache une seule fois pour tous les tests."""
    service = FraudDetectionService()
    # Préchauffage pour s'assurer que le cache est prêt
    service.get_fraud_summary()
    return service

# =================================================================
# SECTION 1 : TESTS UNITAIRES (Logique métier du Service)
# =================================================================


def test_service_fraud_summary_logic(fraud_service):
    """Vérifie le calcul des statistiques de fraude (Route 13)."""
    summary = fraud_service.get_fraud_summary()
    assert "total_frauds" in summary
    assert "precision" in summary
    assert "recall" in summary
    assert isinstance(summary["total_frauds"], int)


def test_service_predict_high_risk(fraud_service):
    """Vérifie qu'une transaction à haut risque (Online + >3000) est détectée."""
    data = {
        "type": "Online Transaction",
        "amount": 4000.0,
        "oldbalanceOrg": 5000.0,
        "newbalanceOrig": 1000.0
    }
    result = fraud_service.predict_fraud(data)
    # Calcul : 0.05 (base) + 0.45 (online) + 0.35 (>3000) = 0.85
    assert result["isFraud"] is True
    assert result["probability"] == 0.85


def test_service_predict_balance_anomaly(fraud_service):
    """Vérifie le bonus de probabilité quand le solde est vidé."""
    data = {
        "type": "Swipe Transaction",
        "amount": 600.0,
        "oldbalanceOrg": 600.0,
        "newbalanceOrig": 0.0
    }
    result = fraud_service.predict_fraud(data)
    # Calcul : 0.05 (base) + 0.05 (swipe) + 0.15 (>500) + 0.14 (vide) = 0.39
    assert result["isFraud"] is False
    assert result["probability"] == 0.39


def test_service_predict_low_risk(fraud_service):
    """Vérifie qu'un petit montant en Swipe reste très faible en probabilité."""
    data = {
        "type": "Swipe Transaction",
        "amount": 10.0,
        "oldbalanceOrg": 100.0,
        "newbalanceOrig": 90.0
    }
    result = fraud_service.predict_fraud(data)
    # Calcul : 0.05 (base) + 0.05 (swipe) = 0.10
    assert result["probability"] == 0.10

# =================================================================
# SECTION 2 : TESTS D'INTÉGRATION (Routes API)
# =================================================================


def test_api_route_13_summary():
    """Vérifie l'accès HTTP au résumé des fraudes."""
    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_frauds" in data


def test_api_route_14_by_type():
    """Vérifie l'accès HTTP à la répartition par type."""
    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_api_route_15_predict_success():
    """Vérifie le succès d'un POST de prédiction via l'API."""
    payload = {
        "type": "Online Transaction",
        "amount": 2500.0,
        "oldbalanceOrg": 5000.0,
        "newbalanceOrig": 0.0
    }
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "isFraud" in data
    assert "probability" in data


def test_api_route_15_predict_invalid_payload():
    """Vérifie la gestion d'erreur si des champs obligatoires manquent."""
    #  Pas de 'amount' et 'type'
    payload = {"oldbalanceOrg": 5000.0}
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (Erreur Pydantic)
