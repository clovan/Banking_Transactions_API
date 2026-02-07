from fastapi import APIRouter, Request
from banking_transaction_api.services.system_service import SystemService

router = APIRouter(prefix="/api/system", tags=["System"])
system_service = SystemService()

@router.get("/health")
def health(request: Request):
    # Utilise l'instance partagée depuis app.state
    is_loaded = request.app.state.transaction_service.is_dataset_loaded()
    return system_service.get_status(is_loaded)

@router.get("/metadata")
def metadata():
    return {
        "version": system_service.version,
        "last_update": system_service.last_update
    }