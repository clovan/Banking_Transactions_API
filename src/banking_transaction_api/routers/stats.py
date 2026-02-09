from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from banking_transaction_api.services.transaction_service import TransactionService
from banking_transaction_api.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["06. Statistiques et Analyses"])

# Injection des dépendances
# Note : on réutilise le TransactionService pour partager le même cache de données
tx_service = TransactionService()
stats_service = StatsService(tx_service)


# =================================================================
# ROUTE 9 : VUE D'ENSEMBLE DES STATISTIQUES
# =================================================================
@router.get("/overview", summary="09. Vue d'ensemble des statistiques")
def get_stats_overview():
    """
    Retourne les indicateurs globaux du dataset :
    - Nombre total de transactions
    - Taux de fraude moyen
    - Montant moyen (en valeur absolue)
    - Type de transaction le plus fréquent
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
        alias="bins",
        description="Paliers personnalisés. Exemple: ?bins=0&bins=100&bins=500",
        example=[0, 100, 500, 1000, 5000]
    )
):
    """
    Retourne la distribution des montants sous forme d'histogramme.
    - Si aucun palier n'est fourni, utilise par défaut : [0, 100, 500, 1000, 5000].
    - Les montants sont traités en valeur absolue.
    """
    dist = stats_service.get_amount_distribution(custom_bins=bins)

    if not dist:
        raise HTTPException(
            status_code=404,
            detail="Impossible de générer la distribution. Vérifiez les données ou les paliers."
        )

    return dist


# =================================================================
# ROUTE 11 : STATISTIQUES PAR TYPE
# =================================================================
@router.get("/by-type", summary="11. Statistiques par type de transaction")
def get_stats_by_type():
    """
    Retourne les agrégations par type de puce/entrée (use_chip) :
    - Le nom du type
    - Le nombre de transactions (count)
    - Le montant moyen (avg_amount)
    """
    data = stats_service.get_stats_by_type()

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Données insuffisantes pour calculer les statistiques par type."
        )

    return data