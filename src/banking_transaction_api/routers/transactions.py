from fastapi import APIRouter, Query, HTTPException, Body
from banking_transaction_api.services.transactions_service import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
service = TransactionService()

@router.get("/")
def list_transactions(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        transaction_type: str = None,          # correspond à use_chip
        isFraud: int = Query(None, ge=0, le=1),
        min_amount: float = None,
        max_amount: float = None
):
    df = service.get_all()

    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset vide ou introuvable")

    df_filtered = service.filter_transactions(df, transaction_type, isFraud, min_amount, max_amount)

    start = (page - 1) * limit
    results = df_filtered.iloc[start: start + limit].to_dict(orient="records")

    # Renommer use_chip → type dans la réponse
    for tx in results:
        if "use_chip" in tx:
            tx["transaction_type"] = tx.pop("use_chip")

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
def search_transactions(
    transaction_type: str = Query(None),
    isFraud: int = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None)
):
    df = service.get_all()

    df_filtered = service.filter_transactions(
        df,
        transaction_type=transaction_type,
        isFraud=isFraud,
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

