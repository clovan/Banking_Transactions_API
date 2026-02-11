import pytest
import pandas as pd
import numpy as np

@pytest.fixture(autouse=True)
def mock_all_services(monkeypatch):
    """
    Mock global optimisé pour GitHub Actions.
    Nettoie les colonnes en double et assure la présence de fraudes.
    """
    # 1. Dataset de transactions simulé
    # On évite d'avoir à la fois 'type' et 'transaction_type' s'ils font doublon
    mock_transactions = pd.DataFrame([
        {
            "id": 7475327,
            "date": "2010-01-01 00:01:00",
            "client_id": 825,
            "card_id": 2972,
            "amount": -77.0,
            "use_chip": "Swipe Transaction",
            "merchant_id": 59935,
            "merchant_city": "Beulah",
            "merchant_state": "ND",
            "zip": 58523,
            "mcc": 5499,
            "errors": 0,
            "isFraud": 0,
            "type": "PAYMENT" # On garde une seule colonne de type
        },
        {
            "id": 1,
            "client_id": 825,
            "amount": 9999.0, # Montant élevé pour déclencher les alertes
            "use_chip": "Online Transaction",
            "merchant_id": 12345,
            "merchant_city": "Online",
            "merchant_state": "CA",
            "zip": 90001,
            "mcc": 1234,
            "errors": 0,
            "isFraud": 1, # FORCER UNE FRAUDE ICI
            "type": "TRANSFER",
            "oldbalanceOrg": 10000.0,
            "newbalanceOrig": 1.0
        }
    ])

    # 2. Dataset d'utilisateurs simulé
    mock_users = pd.DataFrame([
        {
            "id": 825,
            "current_age": 53,
            "retirement_age": 66,
            "birth_year": 1966,
            "birth_month": 11,
            "gender": "Female",
            "address": "462 Rose Lane",
            "City": "Paris",
            "State": "France",
            "latitude": 34.15,
            "longitude": -117.76,
            "per_capita_income": 29278,
            "yearly_income": 59696,
            "total_debt": 127613,
            "credit_score": 787,
            "num_credit_cards": 5
        }
    ])

    # 3. Injection des Mocks dans les services
    paths = [
        "banking_transaction_api.services.transaction_service.load_full_dataset",
        "banking_transaction_api.services.fraud_detection_service.load_full_dataset",
        "banking_transaction_api.services.customer_service.load_full_dataset"
    ]

    for path in paths:
        monkeypatch.setattr(path, lambda: mock_transactions)

    monkeypatch.setattr(
        "banking_transaction_api.services.customer_service.load_user_data",
        lambda: mock_users
    )

    return mock_transactions