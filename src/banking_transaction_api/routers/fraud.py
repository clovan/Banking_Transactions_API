from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Import adjustment based on your folder structure:
# From the services package, we import the class from the fraud_service.py file
from banking_transaction_api.services.fraud_service import FraudService

router = APIRouter(prefix="/api/fraud", tags=["Fraud"])

# Instantiate the service (ensure the class is named FraudService)
service = FraudService()

class FraudPredictionRequest(BaseModel):
    """
    Request model for fraud prediction.
    """
    type: str
    amount: float
    oldbalanceOrg: Optional[float] = None
    newbalanceOrig: Optional[float] = None

@router.get("/summary")
def get_fraud_summary() -> Dict[str, Any]:
    """Overview of fraud statistics."""
    return service.get_fraud_summary()

@router.get("/by-type")
def get_fraud_by_type() -> List[Dict[str, Any]]:
    """Fraud rate distribution by transaction type."""
    return service.get_fraud_by_type()

@router.post("/predict")
def predict_fraud(request: FraudPredictionRequest) -> Dict[str, Any]:
    """Scoring endpoint to predict if a transaction is fraudulent."""
    return service.predict_fraud(request.model_dump())