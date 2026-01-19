from fastapi import APIRouter, Query, HTTPException
from banking_transaction_api.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
service = TransactionService()


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