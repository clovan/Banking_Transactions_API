import pytest
import pandas as pd
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_all_services(monkeypatch):
    """
    Mock global pour GitHub Actions.
    Injecte des données simulées dans tous les services pour éviter les erreurs de fichiers manquants.
    """
    # 1. Dataset de transactions simulé (Mock)
    # On ajoute plusieurs lignes pour le client 825 et au moins une fraude
    mock_transactions = pd.DataFrame([
        {
            "id": 0, "client_id": 825.0, "amount": -50.0,
            "use_chip": "Online Transaction", "type": "PAYMENT",
            "isFraud": 0, "oldbalanceOrg": 1000.0, "newbalanceOrig": 950.0,
            "transaction_type": "Online Transaction"
        },
        {
            "id": 1, "client_id": 825.0, "amount": 5000.0,
            "use_chip": "Online Transaction", "type": "TRANSFER",
            "isFraud": 1, "oldbalanceOrg": 5000.0, "newbalanceOrig": 0.0,
            "transaction_type": "Online Transaction"
        },
        {
            "id": 2, "client_id": 999.0, "amount": -20.0,
            "use_chip": "Swipe Transaction", "type": "PAYMENT",
            "isFraud": 0, "oldbalanceOrg": 100.0, "newbalanceOrig": 80.0,
            "transaction_type": "Swipe Transaction"
        }
    ])

    # 2. Dataset d'utilisateurs simulé
    mock_users = pd.DataFrame([
        {"id": 825, "City": "Paris", "State": "France"},
        {"id": 999, "City": "Lyon", "State": "France"}
    ])

    # 3. Injection des Mocks dans les différents services
    # On mocke load_full_dataset pour tous les services qui l'utilisent
    monkeypatch.setattr(
        "banking_transaction_api.services.transaction_service.load_full_dataset",
        lambda: mock_transactions
    )

    monkeypatch.setattr(
        "banking_transaction_api.services.fraud_detection_service.load_full_dataset",
        lambda: mock_transactions
    )

    monkeypatch.setattr(
        "banking_transaction_api.services.customer_service.load_full_dataset",
        lambda: mock_transactions
    )

    # On mocke load_user_data pour le service client
    monkeypatch.setattr(
        "banking_transaction_api.services.customer_service.load_user_data",
        lambda: mock_users
    )

    return mock_transactions