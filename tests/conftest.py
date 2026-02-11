import pytest
import pandas as pd
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_settings_env(monkeypatch):
    """
    Intercepte le chargement des données pour injecter un DataFrame de test.
    Cela évite d'avoir besoin des fichiers CSV sur GitHub.
    """
    # 1. Création d'un mini dataset de test (Mock)
    mock_data = pd.DataFrame([
        {
            "id": 0, "client_id": 825, "amount": -50.0,
            "use_chip": "Online Transaction", "type": "PAYMENT",
            "isFraud": 0, "oldbalanceOrg": 1000.0, "newbalanceOrig": 950.0
        },
        {
            "id": 1, "client_id": 825, "amount": 5000.0,
            "use_chip": "Online Transaction", "type": "TRANSFER",
            "isFraud": 1, "oldbalanceOrg": 5000.0, "newbalanceOrig": 0.0
        }
    ])

    # 2. On force TransactionService et FraudDetectionService à utiliser ce Mock
    # On remplace la fonction 'load_full_dataset' par une fonction qui renvoie notre mock_data
    monkeypatch.setattr(
        "banking_transaction_api.services.transaction_service.load_full_dataset",
        lambda: mock_data
    )
    monkeypatch.setattr(
        "banking_transaction_api.services.fraud_detection_service.load_full_dataset",
        lambda: mock_data
    )

    # On fait pareil pour les données users
    mock_users = pd.DataFrame([{"id": 825, "City": "Paris", "State": "France"}])
    monkeypatch.setattr(
        "banking_transaction_api.services.customer_service.load_user_data",
        lambda: mock_users
    )