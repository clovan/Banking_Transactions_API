from fastapi import APIRouter, Query, HTTPException, Path
from pydantic import BaseModel
from typing import List, Optional
from banking_transaction_api.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["01. Gestion des Transactions"])
service = TransactionService()


# --- Modèle Pydantic ---
class TransactionSearchCriteria(BaseModel):
    type: Optional[str] = None
    isFraud: Optional[int] = None
    amount_range: Optional[List[float]] = None


# =================================================================
# ROUTE 1 : LISTE ET FILTRAGE GLOBAL (GET)
# =================================================================
@router.get("/", summary="01. Liste paginée des transactions")
def list_transactions(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        transaction_type: str = Query(None, alias="type"),
        isFraud: int = Query(None, ge=0, le=1),
        min_amount: float = Query(None),
        max_amount: float = Query(None),
):
    # Appel de la logique de filtrage du service
    df_filtered = service.filter_transactions(transaction_type, isFraud, min_amount, max_amount)

    if df_filtered.empty:
        return {"page": page, "limit": limit, "total_results": 0, "transactions": []}

    # Pagination
    start = (page - 1) * limit
    subset = df_filtered.iloc[start: start + limit]

    # Utilisation de la méthode de formatage du service
    results = service._prepare_output(subset)

    return {
        "page": page,
        "limit": limit,
        "total_results": len(df_filtered),
        "transactions": results,
    }


# =================================================================
# ROUTE 3 : RECHERCHE AVANCÉE (POST JSON)
# =================================================================
@router.post("/search", summary="03. Recherche multicritère (JSON)")
def search_transactions(criteria: TransactionSearchCriteria):
    # Support pydantic v1 & v2
    filters = criteria.model_dump() if hasattr(criteria, "model_dump") else criteria.dict()
    results = service.search_advanced(filters)

    # Retourne une liste vide si rien n'est trouvé (attendu par les tests)
    return {
        "count": len(results),
        "results": results,
    }


# =================================================================
# ROUTE 4 : TYPES
# =================================================================
@router.get("/types", summary="04. Liste des types de transactions disponibles")
def get_transaction_types():
    types = service.get_types()
    return {"types": types}


# =================================================================
# ROUTE 5 : RECENT
# =================================================================
@router.get("/recent", summary="05. Dernières transactions")
def get_recent_transactions(n: int = Query(10, ge=1)):
    return service.get_recent(n)


# =================================================================
# ROUTE 2 : DÉTAILS D'UNE TRANSACTION (GET)
# =================================================================
# Placée après les routes statiques pour éviter les conflits d'URL
@router.get("/{transaction_id}", summary="02. Détails d'une transaction")
def get_transaction(transaction_id: int = Path(..., description="L'identifiant numérique de la transaction")):
    transaction = service.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} introuvable.")
    return transaction


# =================================================================
# ROUTE 6 : SUPPRESSION
# =================================================================
@router.delete("/{transaction_id}", summary="06. Suppression d'une transaction")
def delete_transaction(transaction_id: int = Path(...)):
    success = service.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return {"message": f"Transaction {transaction_id} supprimée avec succès"}


# =================================================================
# ROUTE 7 : FLUX SORTANTS (DÉBITS)
# =================================================================
@router.get("/by-customer/{customer_id}", summary="07. Transactions sortantes (Débits)")
def get_customer_debits(customer_id: int = Path(...)):
    results = service.get_customer_flow(customer_id, flow_type="debit")
    if not results:
        raise HTTPException(status_code=404, detail=f"Aucun débit trouvé pour le client {customer_id}")
    return {"customer_id": customer_id, "type": "debit/origine", "transactions": results}


# =================================================================
# ROUTE 8 : FLUX ENTRANTS (CRÉDITS)
# =================================================================
@router.get("/to-customer/{customer_id}", summary="08. Transactions entrantes (Crédits)")
def get_customer_credits(customer_id: int = Path(...)):
    results = service.get_customer_flow(customer_id, flow_type="credit")
    if not results:
        raise HTTPException(status_code=404, detail=f"Aucun crédit trouvé pour le client {customer_id}")
    return {"customer_id": customer_id, "type": "credit/destination", "transactions": results}