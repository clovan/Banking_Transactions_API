from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from banking_transaction_api.services.transaction_service import TransactionService
from banking_transaction_api.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["Statistiques"])

# Injection des dépendances
tx_service = TransactionService()
stats_service = StatsService(tx_service)


# =================================================================
# ROUTE 9 : VUE D'ENSEMBLE DES STATISTIQUES
# =================================================================
@router.get("/overview")
def get_stats_overview():
    """
    Retourne les indicateurs globaux du dataset :
    Total, Taux de fraude, Montant moyen et Type fréquent.
    """
    stats = stats_service.get_global_stats()
    if not stats:
        raise HTTPException(status_code=404, detail="Données indisponibles")
    return stats


# =================================================================
# ROUTE 10 : DISTRIBUTION DES MONTANTS (HISTOGRAMME)
# =================================================================
@router.get("/amount-distribution")
def get_amount_distribution(
        bins: Optional[List[int]] = Query(
            None,
            description="Paliers pour créer les intervalles. Exemple: 0, 100, 500"
        )
):
    """
    Retourne la distribution des montants sous forme d'histogramme.
    Les labels sont générés automatiquement comme des intervalles dynamiques.
    """
    dist = stats_service.get_amount_distribution(custom_bins=bins)

    if not dist:
        raise HTTPException(
            status_code=404,
            detail="Impossible de générer la distribution. Vérifiez les paliers saisis."
        )

    return dist


# =================================================================
# ROUTE 11 : STATISTIQUES PAR TYPE (ALIGNÉ SUR LE JSON PROF)
# =================================================================
@router.get("/by-type")
def get_stats_by_type():
    """
    Retourne le nombre total de transactions et le montant moyen par type.
    Conforme au format JSON de l'image : [{"type": str, "count": int, "avg_amount": float}].
    """
    data = stats_service.get_stats_by_type()

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Données insuffisantes pour calculer les statistiques par type."
        )

    return data