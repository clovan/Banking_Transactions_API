from fastapi import APIRouter, HTTPException, Query
from fastapi.openapi.models import Example  # Correction pour les exemples OpenAPI
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Vérifie bien que l'import correspond au nom exact de tes fichiers services
from banking_transaction_api.services.transaction_service import TransactionService
from banking_transaction_api.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["02. Statistiques et Analyses"])

# Injection des dépendances
tx_service = TransactionService()
stats_service = StatsService(tx_service)

# --- Modèles de réponse pour la documentation ---
class GlobalStatsResponse(BaseModel):
    total_transactions: int
    fraud_rate: float
    avg_amount: float
    most_common_type: str

class DistributionResponse(BaseModel):
    bins: List[str]
    counts: List[int]
    applied_bins: List[float]

class TypeStatsResponse(BaseModel):
    type: str
    count: int
    avg_amount: float

# =================================================================
# ROUTE 9 : VUE D'ENSEMBLE DES STATISTIQUES
# =================================================================
@router.get("/overview",
            summary="09. Vue d'ensemble des statistiques",
            response_model=GlobalStatsResponse)
def get_stats_overview():
    """
    Indicateurs globaux : Volume total, Fraude (JSON), Montant (ABS), Mode (use_chip).
    """
    stats = stats_service.get_global_stats()
    if not stats:
        raise HTTPException(status_code=404, detail="Données statistiques indisponibles")
    return stats

# =================================================================
# ROUTE 10 : DISTRIBUTION DES MONTANTS (HISTOGRAMME)
# =================================================================
@router.get("/amount-distribution",
            summary="10. Distribution des montants",
            response_model=DistributionResponse)
def get_amount_distribution(
    bins: Optional[List[float]] = Query(
        None,
        alias="bins",
        description="Paliers personnalisés pour l'histogramme.",
        openapi_examples={
            "default_paliers": Example(
                summary="Paliers standard",
                value=[0, 100, 500, 1000, 5000]
            ),
            "petits_montants": Example(
                summary="Focus transactions < 100",
                value=[0, 10, 25, 50, 100]
            )
        }
    )
):
    """
    Distribution des montants par paliers.
    Par défaut : [0, 100, 500, 1000, 5000].
    """
    dist = stats_service.get_amount_distribution(custom_bins=bins)
    if not dist:
        raise HTTPException(status_code=404, detail="Calcul de distribution impossible")
    return dist



# =================================================================
# ROUTE 11 : STATISTIQUES PAR TYPE
# =================================================================
@router.get("/by-type",
            summary="11. Statistiques par type de transaction",
            response_model=List[TypeStatsResponse])
def get_stats_by_type():
    """
    Agrégations par type de transaction (use_chip) : volume et moyenne.
    """
    data = stats_service.get_stats_by_type()
    if data is None:
        raise HTTPException(status_code=404, detail="Agrégation par type impossible")
    return data

# =================================================================
# ROUTE 12 : ANALYSE TEMPORELLE (JOURNALIÈRE)
# =================================================================
@router.get("/daily", summary="12. Nombre de transactions par jour")
def get_daily_stats():
    """
    Analyse de tendance temporelle basée sur le champ 'date'.
    """
    result = stats_service.get_daily_stats()
    if not result:
        raise HTTPException(status_code=404, detail="Statistiques temporelles indisponibles")
    return result