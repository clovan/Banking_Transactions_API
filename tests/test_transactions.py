from fastapi import APIRouter, Query, HTTPException
from banking_transaction_api.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
service = TransactionService()

@router.get("/")
def list_transactions(
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100),
    type: str = Query(None),
    isFraud: int = Query(None)
):
    df = service.get_all()
    # On applique le filtre AVANT la pagination
    df_filtered = service.filter_transactions(df, type=type, is_fraud=isFraud)
    
    start = (page - 1) * limit
    results = df_filtered.iloc[start: start + limit].to_dict(orient="records")
    return {"page": page, "total_results": len(df_filtered), "transactions": results}

@router.get("/recent")
def get_recent(n: int = 10):
    return service.get_recent(n).to_dict(orient="records")

@router.delete("/{transaction_id}")
def delete_trans(transaction_id: str):
    if service.delete_transaction(transaction_id):
        return {"message": "Supprimé"}
    raise HTTPException(status_code=404, detail="Transaction non trouvée")

@router.get("/by-customer/{customer_id}")
def get_customer_debits(customer_id: int):
    df_debits = service.get_customer_flow(customer_id, flow_type="debit")
    return {"customer_id": customer_id, "type": "debit", "transactions": df_debits.to_dict(orient="records")}

@router.get("/to-customer/{customer_id}")
def get_customer_credits(customer_id: int):
    df_credits = service.get_customer_flow(customer_id, flow_type="credit")
    return {"customer_id": customer_id, "type": "credit", "transactions": df_credits.to_dict(orient="records")}