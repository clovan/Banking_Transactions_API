from fastapi import APIRouter, Query, HTTPException
from banking_transaction_api.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
service = TransactionService()

@router.get("/")
def list_transactions(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    """Liste globale paginée des transactions"""
    df = service.get_all()
    start = (page - 1) * limit
    results = df.iloc[start: start + limit].to_dict(orient="records")
    return {"page": page, "total": len(df), "transactions": results}

# 5. GET /api/transactions/recent
@router.get("/recent")
def get_recent(n: int = Query(10, ge=1, le=100, description="Nombre de transactions à retourner")):
    """Renvoie les N dernières transactions du dataset (défaut=10)"""
    df_recent = service.get_recent(n)
    if df_recent.empty:
        raise HTTPException(status_code=404, detail="Aucune transaction trouvée")
    return df_recent.to_dict(orient="records")

# 6. DELETE /api/transactions/{id}
@router.delete("/{transaction_id}")
def delete_trans(transaction_id: str):
    """Supprime une transaction fictive (mode test uniquement)"""
    if service.delete_transaction(transaction_id):
        return {"message": f"Transaction {transaction_id} supprimée avec succès", "id": transaction_id}
    raise HTTPException(status_code=404, detail="Transaction non trouvée")

# 7. GET /api/transactions/by-customer/{customer_id}
@router.get("/by-customer/{customer_id}")
def get_customer_debits(customer_id: int):
    """Listes des transactions associées à un client (origine - débits)"""
    df_debits = service.get_customer_flow(customer_id, flow_type="debit")
    if df_debits.empty:
        raise HTTPException(status_code=404, detail=f"Aucun débit trouvé pour le client {customer_id}")
    return {
        "customer_id": customer_id, 
        "type": "debit (origine)", 
        "count": len(df_debits), 
        "transactions": df_debits.to_dict(orient="records")
    }

# 8. GET /api/transactions/to-customer/{customer_id}
@router.get("/to-customer/{customer_id}")
def get_customer_credits(customer_id: int):
    """Liste des transactions reçues par un client (destination - crédits)"""
    df_credits = service.get_customer_flow(customer_id, flow_type="credit")
    if df_credits.empty:
        raise HTTPException(status_code=404, detail=f"Aucun crédit trouvé pour le client {customer_id}")
    return {
        "customer_id": customer_id, 
        "type": "credit (destination)", 
        "count": len(df_credits), 
        "transactions": df_credits.to_dict(orient="records")
    }