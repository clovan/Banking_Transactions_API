from fastapi import APIRouter, Query, HTTPException, Path, Body
from pydantic import BaseModel
from typing import List, Optional
from banking_transaction_api.services.transaction_service import TransactionService

# Configuration du router avec un tag clair pour Swagger
router = APIRouter(prefix="/api/transactions", tags=["01. Gestion des Transactions"])
service = TransactionService()


# --- Modèle Pydantic pour la Route 3 (Validation JSON) ---
class TransactionSearchCriteria(BaseModel):
    type: Optional[str] = None  # Mappe vers use_chip dans le service
    isFraud: Optional[int] = None
    amount_range: Optional[List[float]] = None  # Format attendu : [min, max]


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
        max_amount: float = Query(None)
):
    """
    Récupère la liste des transactions avec pagination et filtres optionnels.
    Substitue automatiquement 'use_chip' par 'transaction_type'.
    """
    df_filtered = service.filter_transactions(transaction_type, isFraud, min_amount, max_amount)

    if df_filtered.empty:
        return {"page": page, "limit": limit, "total_results": 0, "transactions": []}

    start = (page - 1) * limit
    subset = df_filtered.iloc[start: start + limit].to_dict(orient="records")

    # Renommage des colonnes pour la sortie API
    results = service._rename_columns(subset)

    return {
        "page": page,
        "limit": limit,
        "total_results": len(df_filtered),
        "transactions": results
    }

#====================Route 4 """""""""""""""""""
@router.get("/types", summary="04. Liste des types de transactions disponibles")
def get_transaction_types():
    df = service.get_all()

    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible.")

    # Valeurs uniques triées
    types = sorted(df["use_chip"].dropna().unique().tolist())

    return {"types": types}


# =================================================================
# ROUTE 2 : DÉTAILS D'UNE TRANSACTION (GET)
# =================================================================
@router.get("/{transaction_id}", summary="02. Détails d'une transaction")
def get_transaction(
        transaction_id: int = Path(..., description="L'identifiant numérique de la transaction")
):
    """
    Retourne tous les détails d'une transaction spécifique.
    """
    transaction = service.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} introuvable.")
    return transaction


# =================================================================
# ROUTE 3 : RECHERCHE AVANCÉE (POST JSON)
# =================================================================
@router.post("/search", summary="03. Recherche multicritère (JSON)")
def search_transactions(criteria: TransactionSearchCriteria):
    """
    Recherche avancée via un corps JSON.
    Permet de filtrer par type (use_chip), statut de fraude et plage de montants.
    """
    filters = criteria.dict()
    results = service.search_advanced(filters)

    if not results:
        raise HTTPException(status_code=404, detail="Aucune transaction ne correspond aux critères.")

    return {
        "count": len(results),
        "results": results
    }


#==================Route 5 =================
@router.get("/recent", summary="05. Dernières transactions")
def get_recent_transactions(
    n: int = Query(10, description="Nombre de transactions récentes à renvoyer")
):
    df = service.get_all()

    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible.")

    # On trie par ID décroissant (ou par date si tu en avais une)
    recent = df.sort_values(by="id", ascending=False).head(n)

    return recent.to_dict(orient="records")


# =================================================================
# ROUTE 6 : SUPPRESSION D'UNE TRANSACTION (DELETE)
# =================================================================
@router.delete("/{transaction_id}", summary="06. Suppression d'une transaction")
def delete_transaction(transaction_id: int = Path(...)):
    """
    Supprime définitivement une transaction de la session actuelle.
    """
    success = service.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return {"message": f"Transaction {transaction_id} supprimée avec succès"}


# =================================================================
# ROUTE 7 : FLUX SORTANTS PAR CLIENT (GET)
# =================================================================
@router.get("/by-customer/{customer_id}", summary="07. Transactions sortantes (Débits)")
def get_customer_debits(customer_id: int = Path(...)):
    """
    Liste les transactions émises par un client (montants négatifs).
    """
    results = service.get_customer_flow(customer_id, flow_type="debit")
    if not results:
        raise HTTPException(status_code=404, detail=f"Aucun débit trouvé pour le client {customer_id}")
    return {"customer_id": customer_id, "type": "debit/origine", "transactions": results}


# =================================================================
# ROUTE 8 : FLUX ENTRANTS PAR CLIENT (GET)
# =================================================================
@router.get("/to-customer/{customer_id}", summary="08. Transactions entrantes (Crédits)")
def get_customer_credits(customer_id: int = Path(...)):
    """
    Liste les transactions reçues par un client (montants positifs).
    """
    results = service.get_customer_flow(customer_id, flow_type="credit")
    if not results:
        raise HTTPException(status_code=404, detail=f"Aucun crédit trouvé pour le client {customer_id}")
    return {"customer_id": customer_id, "type": "credit/destination", "transactions": results}