from fastapi import APIRouter, Query, HTTPException, Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from banking_transaction_api.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["01. Gestion des Transactions"])
service = TransactionService()


class TransactionSearchCriteria(BaseModel):
    """ """
    type: Optional[str] = Field(default="Online Transaction")
    isFraud: Optional[int] = Field(None, ge=0, le=1)
    amount_range: Optional[List[float]] = Field(
        default=[0.0, 100.0], min_length=2, max_length=2)
    model_config = ConfigDict(json_schema_extra={"example": {
                              "type": "Online Transaction", "isFraud": 0,
                              "amount_range": [0.0, 100.0]}})


@router.get("/", summary="01. Liste paginée des transactions")
def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    transaction_type: str = Query(None, alias="type"),
    isFraud: int = Query(None, ge=0, le=1),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
):
    """

    Parameters
    ----------
    page: int :
         (Default value = Query(1)
    ge :
         (Default value = 0)
    limit: int :
         (Default value = Query(20)
    le :
         (Default value = 1))
    transaction_type: str :
         (Default value = Query(None)
    alias :
         (Default value = "type"))
    isFraud: int :
         (Default value = Query(None)
    min_amount: float :
         (Default value = Query(None))
    max_amount: float :
         (Default value = Query(None))

    Returns
    -------

    """
    df_filtered = service.filter_transactions(
        transaction_type, isFraud, min_amount, max_amount)
    if df_filtered.empty:
        return {"page": page, "limit": limit, "total_results": 0, "transactions": []}
    start = (page - 1) * limit
    subset = df_filtered.iloc[start: start + limit]
    return {"page": page, "limit": limit, "total_results": len(df_filtered),
            "transactions": service._prepare_output(subset)}


@router.post("/search", summary="03. Recherche multicritère (JSON)")
def search_transactions(criteria: TransactionSearchCriteria):
    """

    Parameters
    ----------
    criteria: TransactionSearchCriteria :


    Returns
    -------

    """
    results = service.search_advanced(criteria.model_dump())
    return {"count": len(results), "results": results}


@router.get("/types", summary="04. Liste des types de transactions")
def get_transaction_types():
    """ """
    return {"types": service.get_types()}


@router.get("/recent", summary="05. Dernières transactions")
def get_recent_transactions(n: int = Query(10, ge=1, le=100)):
    """

    Parameters
    ----------
    n: int :
         (Default value = Query(10)
    ge :
         (Default value = 1)
    le :
         (Default value = 100))

    Returns
    -------

    """
    return service.get_recent(n)


@router.get("/{transaction_id}", summary="02. Détails d'une transaction")
def get_transaction(transaction_id: int = Path(..., ge=0)):
    """

    Parameters
    ----------
    transaction_id: int :
         (Default value = Path(...)
    ge :
         (Default value = 0))

    Returns
    -------

    """
    transaction = service.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=404, detail=f"Transaction {transaction_id} introuvable.")
    return transaction


@router.delete("/{transaction_id}", summary="06. Suppression d'une transaction")
def delete_transaction(transaction_id: int = Path(..., ge=0)):
    """

    Parameters
    ----------
    transaction_id: int :
         (Default value = Path(...)
    ge :
         (Default value = 0))

    Returns
    -------

    """
    if not service.delete_transaction(transaction_id):
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return {"status": "success", "message": f"Transaction {transaction_id} supprimée"}

# =================================================================
# ROUTES 7 & 8 : FLUX CLIENTS (MISES À JOUR)
# =================================================================


@router.get("/by-customer/{customer_id}", summary="07. Transactions sortantes (Débits)")
def get_customer_debits(
        customer_id: int = Path(
        ...,
            description="L'ID du client pour les débits")):
    """

    Parameters
    ----------
    customer_id: int :
         (Default value = Path(...)
    description :
         (Default value = "L'ID du client pour les débits"))

    Returns
    -------

    """
    results = service.get_customer_flow(customer_id, flow_type="debit")
    if not results:
        raise HTTPException(
            status_code=404, detail="ce client n'a pas de debit dans compte")
    return {"client_id": customer_id, "type": "debit", "transactions": results}


@router.get("/to-customer/{customer_id}",
            summary="08. Transactions entrantes (Crédits)")
def get_customer_credits(
        customer_id: int = Path(
        ...,
            description="L'ID du client pour les crédits")):
    """

    Parameters
    ----------
    customer_id: int :
         (Default value = Path(...)
    description :
         (Default value = "L'ID du client pour les crédits"))

    Returns
    -------

    """
    results = service.get_customer_flow(customer_id, flow_type="credit")
    if not results:
        raise HTTPException(
            status_code=404, detail="ce client n'a pas de credit sur son compte")
    return {"client_id": customer_id, "type": "credit", "transactions": results}
