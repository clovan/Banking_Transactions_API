from fastapi import APIRouter, Query, HTTPException, Body
from banking_transaction_api.services.transactions_service import TransactionService, TransactionSearch

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
service = TransactionService()

"""Création de la route GET /api/transactions"""
@router.get("/")
def list_transactions(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        type: str = None,
        isFraud: int = Query(None, ge=0, le=1),
        min_amount: float = None,
        max_amount: float = None
):
    df = service.get_all()
    if df.empty:
        raise HTTPException(status_code=404, detail="Fichier de données introuvable ou vide")

    df_filtered = service.filter_transactions(df, type, isFraud, min_amount, max_amount)

    start = (page - 1) * limit
    results = df_filtered.iloc[start: start + limit].to_dict(orient="records")

    return {
        "page": page,
        "limit": limit,
        "total_results": len(df_filtered),
        "transactions": results
    }
"""Création de la route GET /api/transactions/{id}"""
@router.get("/{id:int}")
def get_transaction_by_id(id: int):
    transaction = service.get_transaction_by_id(id)
    if transaction is None:
        raise HTTPException(status_code=404, detail=f"Aucune transaction trouvée avec l'identifiant {id}")
    return transaction


"""Création de la route POST /api/transactions/search"""
@router.post("/search")
def search_transactions(filters: TransactionSearch = Body(...)):
    df = service.get_all()
    if df.empty:
        raise HTTPException(status_code=404, detail="Fichier de données introuvable ou vide")

    transaction_type = filters.type
    is_fraud = filters.isFraud  # 0 ou 1 venant du JSON

    min_amount = None
    max_amount = None
    if filters.amount_range and len(filters.amount_range) == 2:
        min_amount, max_amount = filters.amount_range

    df_filtered = service.filter_transactions(
        df,
        transaction_type=transaction_type,
        is_fraud=is_fraud,
        min_amount=min_amount,
        max_amount=max_amount
    )

    return {
        "total_results": len(df_filtered),
        "transactions": df_filtered.to_dict(orient="records")
    }

"""Création de la route GET /api/transactions/types"""
@router.get("/types")
def get_transaction_types():
    return service.get_transaction_types()

