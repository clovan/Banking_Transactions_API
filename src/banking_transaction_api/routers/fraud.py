from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from banking_transaction_api.services.fraud_detection_service import FraudDetectionService

router = APIRouter(prefix="/api/fraud", tags=["06. Analyse des Fraudes"])
service = FraudDetectionService()

# --- Modèles Pydantic pour la Route 15 ---

class FraudPredictRequest(BaseModel):
    """Modèle représentant le corps de la requête de prédiction."""
    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float

class FraudPredictResponse(BaseModel):
    """Modèle représentant la réponse de la prédiction."""
    isFraud: bool
    probability: float

# --- Routes existantes ---

@router.get("/summary", summary="13. Résumé des fraudes")
def get_fraud_summary():
    """
    Endpoint pour obtenir le résumé global des fraudes.

    Returns
    -------
    dict
        Statistiques de fraude (total, flagged, precision, recall).
    """
    summary = service.get_fraud_summary()
    if not summary:
        raise HTTPException(status_code=404, detail="Données indisponibles")
    return summary

@router.get("/by-type", summary="14. Fraudes par type de transaction")
def get_fraud_by_type():
    """
    Endpoint pour obtenir la répartition des fraudes par valeur de 'use_chip'.
    """
    return service.get_fraud_by_type()

# --- Nouvelle Route 15 ---

@router.post("/predict", response_model=FraudPredictResponse, summary="15. Prédiction de fraude")
def predict_fraud(request: FraudPredictRequest):
    """
    Endpoint de scoring pour prédire si une transaction est frauduleuse.

    Parameters
    ----------
    request : FraudPredictRequest
        Les données de la transaction à analyser.

    Returns
    -------
    FraudPredictResponse
        Le résultat de la prédiction (isFraud et probabilité).
    """
    # Appel de la logique de prédiction dans le service
    result = service.predict_fraud(request.model_dump())
    return result