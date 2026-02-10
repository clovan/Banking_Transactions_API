import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


# =================================================================
# TESTS DE VALIDATION DES ENTRÉES JSON (Pydantic & FastAPI)
# =================================================================

def test_search_invalid_json_types():
    """Vérifie que l'API rejette un JSON avec des types de données incorrects."""
    # On envoie une chaîne au lieu d'une liste pour amount_range
    invalid_payload = {
        "type": "CASH_OUT",
        "amount_range": "de 0 à 100"  # Erreur : attend List[float]
    }
    response = client.post("/api/transactions/search", json=invalid_payload)

    # FastAPI renvoie 422 (Unprocessable Entity) pour les erreurs de validation
    assert response.status_code == 422
    assert "amount_range" in response.text


def test_search_invalid_fraud_value():
    """Vérifie que isFraud n'accepte que des entiers valides (0 ou 1)."""
    invalid_payload = {
        "isFraud": "vrai"  # Erreur : attend un entier (0 ou 1)
    }
    response = client.post("/api/transactions/search", json=invalid_payload)

    assert response.status_code == 422


def test_predict_fraud_missing_fields():
    """Vérifie que la prédiction rejette les JSON incomplets si des champs sont requis."""
    # Si ton modèle Pydantic exige 'amount', l'envoi d'un dictionnaire vide doit échouer
    response = client.post("/api/fraud/predict", json={})

    # Si ton API est strictement typée, elle doit répondre 422
    assert response.status_code == 422




def test_search_malformed_json_syntax():
    """Vérifie le comportement face à une erreur de syntaxe JSON pure (ex: virgule manquante)."""
    headers = {"Content-Type": "application/json"}
    bad_syntax_data = '{"type": "TRANSFER" "amount": 100}'  # Manque la virgule

    response = client.post("/api/transactions/search", content=bad_syntax_data, headers=headers)

    # CORRECTION : Selon la version de FastAPI/Starlette, une erreur de parsing
    # peut renvoyer 400 ou 422. On accepte les deux pour valider le rejet.
    assert response.status_code in [400, 422]