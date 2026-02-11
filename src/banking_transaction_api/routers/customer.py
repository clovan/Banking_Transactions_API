from fastapi import APIRouter, Query, Path
from banking_transaction_api.services.customer_service import CustomerService

# Initialisation du routeur
router = APIRouter(prefix="/api/customers", tags=["07. Analyse des Clients"])
service = CustomerService()

# =================================================================
# 1. ROUTE 16 : LISTE GÉNÉRALE (Racine)
# =================================================================
@router.get(
    "/",
    summary="16. Liste paginée des clients",
    response_description="Données complètes issues de users_data.csv"
)
def get_customers(
    page: int = Query(1, ge=1, description="Numéro de la page"),
    size: int = Query(10, ge=1, le=100, description="Clients par page")
):
    """Récupère la liste globale des clients avec pagination."""
    return service.get_paginated_customers(page, size)

# =================================================================
# 2. ROUTE 18 : CLASSEMENT (Chemin fixe /top)
# =================================================================
# IMPORTANT : Cette route doit être AVANT /{customer_id}

@router.get(
    "/top",
    summary="18. Top clients par volume",
    response_description="Classement des clients les plus actifs"
)
def get_top_customers(
    n: int = Query(10, ge=1, le=100, description="Nombre de clients (Top N)")
):
    """Identifie les clients ayant le plus grand nombre de transactions."""
    return service.get_top_customers(n)


# =================================================================
# 3. ROUTE 17 : DÉTAILS (Paramètre dynamique /{id})
# =================================================================
@router.get(
    "/{customer_id}",
    summary="17. Profil client synthétique"
)
def get_customer_profile(
    customer_id: int = Path(..., ge=0, description="ID numérique du client")
):
    """
    Croise les fichiers CSV et JSON pour générer un profil d'activité
    (volume, moyenne et statut de fraude).
    """
    return service.get_customer_profile(customer_id)


