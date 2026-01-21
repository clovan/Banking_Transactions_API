from fastapi import APIRouter, Query, HTTPException
from banking_transaction_api.services.transaction_service import TransactionService

# Le préfixe /api/transactions regroupe toutes les actions sur les données
router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
service = TransactionService()

@router.get("/")
def list_transactions(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        type: str = None,
        isFraud: int = Query(None, ge=0, le=1), # Filtrage basé sur la fusion JSON/CSV
        min_amount: float = None,
        max_amount: float = None
):
    """Route 1 : Consultation et filtrage global (inclut le statut de fraude)."""
    df = service.get_all()
    if df.empty:
        raise HTTPException(status_code=404, detail="Fichier de données vide")

    # On utilise le service pour filtrer dynamiquement
    df_filtered = service.filter_transactions(df, type, isFraud, min_amount, max_amount)

    start = (page - 1) * limit
    results = df_filtered.iloc[start: start + limit].to_dict(orient="records")

    return {
        "page": page,
        "limit": limit,
        "total_results": len(df_filtered),
        "transactions": results
    }

@router.get("/by-customer/{customer_id}")
def get_customer_debits(customer_id: int):
    """Route 7 : Liste les transactions sortantes (montant < 0)"""
    results = service.get_customer_flow(customer_id, flow_type="debit")
    if not results:
        raise HTTPException(status_code=404, detail="Aucun débit trouvé pour ce client")
    return {"customer_id": customer_id, "type": "debit/origine", "transactions": results}

@router.get("/to-customer/{customer_id}")
def get_customer_credits(customer_id: int):
    """Route 8 : Liste les transactions reçues (montant > 0)"""
    results = service.get_customer_flow(customer_id, flow_type="credit")
    if not results:
        raise HTTPException(status_code=404, detail="Aucun crédit trouvé pour ce client")
    return {"customer_id": customer_id, "type": "credit/destination", "transactions": results}

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int):
    """Route 6 : Supprime une transaction par son ID"""
    success = service.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return {"message": f"Transaction {transaction_id} supprimée avec succès"}

# --- ROUTE DE STATISTIQUES (Route 9) ---

@router.get("/stats/overview")
def get_stats_overview():
    """Route 9 : Statistiques globales (Total, Taux de fraude, Moyenne)"""
    stats = service.get_global_stats()
    if not stats:
        raise HTTPException(status_code=404, detail="Calcul des statistiques impossible")
    return stats