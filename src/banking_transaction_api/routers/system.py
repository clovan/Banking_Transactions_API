from fastapi import APIRouter
from banking_transaction_api.services.system_service import SystemService
from banking_transaction_api.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/system", tags=["System"])
system_service = SystemService()
trans_service = TransactionService()

@router.get("/health")
def health():
    # On vérifie l'état via les deux services
    is_loaded = trans_service.is_dataset_loaded() # <--- Attention aux parenthèses ()
    return system_service.get_status(is_loaded)

@router.get("/metadata")
def metadata():
    return {
        "version": system_service.version,
        "last_update": system_service.last_update
    }