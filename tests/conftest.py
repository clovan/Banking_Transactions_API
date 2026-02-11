import pytest
import pandas as pd
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_all_services(monkeypatch):
    """
    Mock global pour GitHub Actions.
    Simule les fichiers CSV avec la structure réelle des données.
    """
    # 1. Dataset de transactions simulé (basé sur ton format réel)
    mock_transactions = pd.DataFrame([
        {
            "id": 7475327,
            "date": "2010-01-01 00:01:00",
            "client_id": 825, # On utilise 825 pour matcher avec le test du profil
            "card_id": 2972,
            "amount": -77.0,
            "transaction_type": "Swipe Transaction",
            "use_chip": "Swipe Transaction", # Pour la compatibilité des services
            "merchant_id": 59935,
            "merchant_city": "Beulah",
            "merchant_state": "ND",
            "zip": 58523,
            "mcc": 5499,
            "errors": 0,
            "isFraud": 0,
            "type": "PAYMENT"
        },
        {
            "id": 1,
            "client_id": 825,
            "amount": 5000.0,
            "use_chip": "Online Transaction",
            "type": "TRANSFER",
            "isFraud": 1, # On garde une fraude pour valider les stats
            "oldbalanceOrg": 5000.0,
            "newbalanceOrig": 0.0
        }
    ])

    # 2. Dataset d'utilisateurs simulé (basé sur ton format réel)
    mock_users = pd.DataFrame([
        {
            "id": 825,
            "current_age": 53,
            "retirement_age": 66,
            "birth_year": 1966,
            "birth_month": 11,
            "gender": "Female",
            "address": "462 Rose Lane",
            "City": "Paris", # On garde City/State car tes services les cherchent
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

    # 3. Injection des Mocks
    # On patche les fonctions de chargement pour que le CSV réel ne soit jamais appelé
    paths_to_patch = [
        "banking_transaction_api.services.transaction_service.load_full_dataset",
        "banking_transaction_api.services.fraud_detection_service.load_full_dataset",
        "banking_transaction_api.services.customer_service.load_full_dataset"
    ]

    for path in paths_to_patch:
        monkeypatch.setattr(path, lambda: mock_transactions)

    # Patch spécifique pour le fichier users_data.csv
    monkeypatch.setattr(
        "banking_transaction_api.services.customer_service.load_user_data",
        lambda: mock_users
    )

    return mock_transactions