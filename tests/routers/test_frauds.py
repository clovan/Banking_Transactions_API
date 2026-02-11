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
# ===========================================================
