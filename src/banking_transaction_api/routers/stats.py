from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from banking_transaction_api.services.transaction_service import TransactionService
from banking_transaction_api.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["06. Statistiques et Analyses"])

# Injection des dépendances
tx_service = TransactionService()
stats_service = StatsService(tx_service)


# =================================================================
# ROUTE 9 : VUE D'ENSEMBLE DES STATISTIQUES
# =================================================================
@router.get("/overview", summary="09. Vue d'ensemble des statistiques")
def get_stats_overview():
    """
    Retourne les indicateurs globaux : Total, Fraude, Moyenne et Type fréquent.
    """
    stats = stats_service.get_global_stats()
    if not stats:
        raise HTTPException(status_code=404, detail="Données indisponibles")
    return stats


# =================================================================
# ROUTE 10 : DISTRIBUTION DES MONTANTS (HISTOGRAMME)
# =================================================================
@router.get("/amount-distribution", summary="10. Distribution des montants")
def get_amount_distribution(
    bins: Optional[List[float]] = Query(
        None,
        description="Paliers personnalisés. Exemple: ?bins=0&bins=100&bins=500"
    )
):
    """
    Retourne l'histogramme des transactions par classes de valeurs.
    """
    dist = stats_service.get_amount_distribution(custom_bins=bins)
    if not dist:
        raise HTTPException(status_code=404, detail="Impossible de générer la distribution")
    return dist


# =================================================================
# ROUTE 11 : STATISTIQUES PAR TYPE
# =================================================================
@router.get("/by-type", summary="11. Statistiques par type de transaction")
def get_stats_by_type():
    """
    Retourne le volume et le montant moyen par type de puce (use_chip).
    """
    data = stats_service.get_stats_by_type()
    if data is None:
        raise HTTPException(status_code=404, detail="Données insuffisantes")
    return data


# =================================================================
# ROUTE 12 : STATISTIQUES JOURNALIÈRES (TEMPOREL)
# =================================================================
@router.get("/daily", summary="12. Statistiques journalières")
def get_daily_stats():
    """
    Retourne l'évolution quotidienne : volume (count) et montant moyen.
    """
    data = stats_service.get_daily_stats()
    if not data:
        raise HTTPException(
            status_code=404,
            detail="Données temporelles introuvables. Vérifiez les colonnes Year/Month/Day."
        )
    return data