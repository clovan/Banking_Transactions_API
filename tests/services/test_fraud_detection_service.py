import pytest
import pandas as pd
from banking_transaction_api.services.fraud_detection_service import FraudDetectionService


# =================================================================
# FIXTURE : Simulation des données de fraude avec Reset du Cache
# =================================================================

class MockDataLoader:
    def __call__(self):
        # On crée un jeu de données contrôlé pour valider la logique mathématique
        return pd.DataFrame([
            {"id": 1, "use_chip": "Online Transaction", "amount": 100.0, "isFraud": 0},
            {"id": 2, "use_chip": "Online Transaction", "amount": 600.0, "isFraud": 0},  # Flagged (600 > 500)
            {"id": 3, "use_chip": "Swipe Transaction", "amount": 50.0, "isFraud": 1},  # Fraude réelle
            {"id": 4, "use_chip": "Online Transaction", "amount": 1000.0, "isFraud": 1},  # Flagged + Fraude
        ])


@pytest.fixture
def fraud_service(monkeypatch):
    """
    Fixture qui force le service à utiliser les données de test.
    Crucial : On doit vider le cache Singleton pour que le mock soit pris en compte.
    """
    # 1. On injecte le chargeur de données fictives
    monkeypatch.setattr(
        "banking_transaction_api.services.fraud_detection_service.load_full_dataset",
        MockDataLoader()
    )

    # 2. On FORCE la réinitialisation du cache de classe (Singleton)
    FraudDetectionService._cached_df = None

    return FraudDetectionService()


# =================================================================
# TESTS SECTION 1 : ANALYSE STATISTIQUE
# =================================================================

def test_fraud_summary_logic(fraud_service):
    """Vérifie le calcul de la précision et du rappel."""
    summary = fraud_service.get_fraud_summary()

    # Total fraudes réelles dans le mock = 2 (ID 3 et 4)
    assert summary["total_frauds"] == 2

    # Flagged (>500 et Online) = 2 (ID 2 et ID 4)
    assert summary["flagged"] == 2

    # True Positive (Flagged ET isFraud=1) = 1 (ID 4 uniquement)
    # Précision = TP / Flagged = 1 / 2 = 0.5
    assert summary["precision"] == 0.5

    # Rappel = TP / Total Frauds = 1 / 2 = 0.5
    assert summary["recall"] == 0.5


def test_fraud_by_type_logic(fraud_service):
    """Vérifie la répartition des fraudes par type."""
    fraud_types = fraud_service.get_fraud_by_type()

    # Dans le mock, il y a une fraude en 'Swipe Transaction' et une en 'Online Transaction'
    assert fraud_types["Swipe Transaction"] == 1
    assert fraud_types["Online Transaction"] == 1


# =================================================================
# TESTS SECTION 2 : PRÉDICTION TEMPS RÉEL
# =================================================================

def test_predict_fraud_high_risk(fraud_service):
    """Teste une transaction à haut risque (Montant élevé + Type TRANSFER)."""
    data = {
        "type": "TRANSFER",
        "amount": 4000,
        "oldbalanceOrg": 5000,
        "newbalanceOrig": 1000
    }
    prediction = fraud_service.predict_fraud(data)

    # Logique : Base(0.05) + TRANSFER(0.45) + Amount>3000(0.35) = 0.85
    assert prediction["probability"] == 0.85
    assert prediction["isFraud"] is True


def test_predict_fraud_balance_anomaly(fraud_service):
    """Teste la règle de l'anomalie de solde (compte vidé)."""
    data = {
        "type": "CASH_OUT",
        "amount": 200,
        "oldbalanceOrg": 200,
        "newbalanceOrig": 0  # Compte vidé
    }
    prediction = fraud_service.predict_fraud(data)

    # Logique : Base(0.05) + AutreType(0.05) + Amount<500(0) + BalanceZero(0.14) = 0.24
    assert prediction["probability"] == 0.24
    assert prediction["isFraud"] is False


def test_predict_fraud_low_risk(fraud_service):
    """Teste une transaction normale à faible risque."""
    data = {
        "type": "Unknown",
        "amount": 100,
        "oldbalanceOrg": 1000,
        "newbalanceOrig": 900
    }
    prediction = fraud_service.predict_fraud(data)

    # Logique : Base(0.05) + Autre(0.05) = 0.10
    assert prediction["probability"] == 0.10
    assert prediction["isFraud"] is False