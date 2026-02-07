from fastapi import APIRouter, HTTPException
from banking_transaction_api.services.stats_service import TransactionService,StatistiquesService

router = APIRouter(prefix="/api/stats", tags=["Statistiques"])
#service = StatistiquesService()

transaction_service = TransactionService()
service = StatistiquesService(transaction_service)

@router.get("/overview")
def get_overview_stats():
    stats = service.get_overview_stats()
    if stats["total_transactions"] == 0:
        raise HTTPException(status_code=404, detail="Dataset vide ou introuvable")
    return stats

"""from fastapi import APIRouter
from banking_transaction_api.services.transactions_service import TransactionService
from banking_transaction_api.services.stats_service import StatistiquesService



transaction_service = TransactionService()
service = StatistiquesService(transaction_service)"""


@router.get("/api/stats/amount-distribution")
def amount_distribution():
    return service.get_amount_distribution()


"""@router.get("/amount-distribution")
def get_amount_distribution():
    dist = service.get_amount_distribution()
    if not dist["bins"]:
        raise HTTPException(status_code=404, detail="Dataset vide ou introuvable")
    return dist
"""

@router.get("/by-type")
def get_stats_by_type():
    stats = service.get_stats_by_type()

    if not stats:
        raise HTTPException(status_code=404, detail="Dataset vide ou introuvable")

    return stats

@router.get("/daily")
def get_daily_stats():
    stats = service.get_daily_stats()

    if not stats:
        raise HTTPException(status_code=404, detail="Dataset vide ou introuvable")

    return stats
