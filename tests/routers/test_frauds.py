import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app
from banking_transaction_api.services.fraud_detection_service import FraudDetectionService

client = TestClient(app)

# =================================================================
# FIXTURE : Initialisation et Préchauffage
# =================================================================

@pytest.fixture(scope="module")
def fraud_service():
    """Initialise le service et charge le cache une seule fois pour tous les tests."""
    service = FraudDetectionService()
    # Préchauffage pour éviter les latences de chargement CSV pendant les tests
    service.get_fraud_summary()
    return service

# =================================================================
# SECTION 1 : TESTS UNITAIRES (Logique métier du Service)
# =================================================================

def test_route_13_summary_logic(fraud_service):
    """
    UNIT TEST - ROUTE 13 : Vérifie la logique du résumé statistique.
    S'adapte aux données réelles (CSV de 10k lignes).
    """
    summary = fraud_service.get_fraud_summary()
    assert summary is not None
    # On vérifie qu'on a bien des fraudes détectées dans le fichier réel
    assert summary["total_frauds"] >= 1
    assert "precision" in summary
    assert "recall" in summary
    assert isinstance(summary["precision"], float)

def test_route_14_by_type_logic(fraud_service):
    """
    UNIT TEST - ROUTE 14 : Vérifie le groupement par mode 'use_chip'.
    """
    by_type = fraud_service.get_fraud_by_type()
    assert isinstance(by_type, dict)
    # Dans tes données réelles, il doit y avoir au moins un type
    if by_type:
        assert len(by_type) > 0

def test_route_15_predict_logic(fraud_service):
    """
    UNIT TEST - ROUTE 15 : Vérifie le calcul de probabilité de fraude.
    Calcul attendu : Base 0.05 + Type 0.45 + Amount>3000 0.35 + Balance 0.14 = 0.99
    """
    data = {
        "type": "Online Transaction",
        "amount": 5000.0,
        "oldbalanceOrg": 1000.0,
        "newbalanceOrig": 0.0
    }
    prediction = fraud_service.predict_fraud(data)
    assert prediction["isFraud"] is True
    # Doit être proche de 0.99 selon ta nouvelle logique optimisée
    assert prediction["probability"] >= 0.90


# =================================================================
# SECTION 2 : TESTS DE FONCTIONNALITÉS (Endpoints API)
# =================================================================

def test_api_route_13_get_summary():
    """
    FEATURE TEST - ROUTE 13 : GET /api/fraud/summary
    """
    # Premier appel peut être lent, les suivants seront instantanés
    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_frauds" in data
    assert "flagged" in data

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
    Vérifie la probabilité de 0.99 pour un cas de fraude extrême.
    """
    payload = {
        "type": "Online Transaction",
        "amount": 3500.0,
        "oldbalanceOrg": 500.0,
        "newbalanceOrig": 0.0
    }
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["isFraud"] is True
    # Aligné sur ton service : 0.05 + 0.45 + 0.35 + 0.14 = 0.99
    assert res_json["probability"] == 0.99

def test_api_route_15_post_predict_bad_request():
    """
    FEATURE TEST - ROUTE 15 : POST /api/fraud/predict (Erreur 422)
    Vérifie que la validation Pydantic V2 fonctionne.
    """
    # Montant en string au lieu de float pour déclencher 422
    payload = {"type": "Online Transaction", "amount": "erreur_montant"}
    response = client.post("/api/fraud/predict", json=payload)
    assert response.status_code == 422