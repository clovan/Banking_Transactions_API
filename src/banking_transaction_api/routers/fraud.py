from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from banking_transaction_api.services.fraud_detection_service import (
    FraudDetectionService)

router = APIRouter(prefix="/api/fraud", tags=["03. Analyse des Fraudes"])
service = FraudDetectionService()


# --- Modèles Pydantic ---

class FraudPredictRequest(BaseModel):
    """ """

    type: str = Field(...,
                      description="Type de transaction (Online Transaction / "
                                  "Swipe Transaction)")
    amount: float = Field(..., ge=0, description="Montant de la transaction")
    oldbalanceOrg: float = Field(..., ge=0, description="Solde initial du compte")
    newbalanceOrig: float = Field(..., ge=0,
                                  description="Nouveau solde après transaction")

    # Correction: Utilisation de json_schema_extra au lieu de example dans Field
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "Online Transaction",
                "amount": 2500.0,
                "oldbalanceOrg": 5000.0,
                "newbalanceOrig": 0.0
            }
        }
    )


class FraudPredictResponse(BaseModel):
    """ """
    # Modèle représentant la réponse de la prédiction."
    isFraud: bool
    probability: float


# --- Routes ---

@router.get("/summary", summary="13. Résumé des fraudes")
def get_fraud_summary():
    """Endpoint pour obtenir le résumé global des fraudes (Précision/Rappel).
    Calcule les stats sur le dataset complet chargé en mémoire.

    Parameters
    ----------

    Returns
    -------


    """
    summary = service.get_fraud_summary()
    if not summary:
        raise HTTPException(
            status_code=404, detail="Données indisponibles ou dataset vide")
    return summary


@router.get("/by-type", summary="14. Fraudes par type de transaction")
def get_fraud_by_type():
    """ """
    # Répartition des fraudes réelles par mode (use_chip ou transaction_type).
    results = service.get_fraud_by_type()
    # On retourne un dictionnaire vide si aucune donnée
    if not results:
        return {}
    return results


@router.post("/predict", response_model=FraudPredictResponse,
             summary="15. Prédiction de fraude")
def predict_fraud(request: FraudPredictRequest):
    """Endpoint de scoring temps réel.
    Analyse les anomalies de solde et le type de transaction via le service.

    Parameters
    ----------
    request : FraudPredictRequest :

    request : FraudPredictRequest :

    request : FraudPredictRequest :

    request: FraudPredictRequest :


    Returns
    -------


    """
    # model_dump() est la méthode Pydantic V2 pour convertir en dict
    result = service.predict_fraud(request.model_dump())

    if result is None:
        raise HTTPException(
            status_code=500, detail="Erreur lors du calcul de prédiction")

    return result
