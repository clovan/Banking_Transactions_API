from fastapi import APIRouter
from banking_transaction_api.services.system_service import SystemService
from banking_transaction_api.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/system", tags=["08. Système"])

# Initialisation unique pour préserver l'uptime
tx_service = TransactionService()
system_service = SystemService(tx_service)

@router.get("/health", summary="19. État de santé de l'API")
def get_health():
    """Vérifie l'état de santé, le ping et l'uptime."""
    return system_service.get_health_status()

@router.get("/metadata", summary="20. Métadonnées du service")
def get_metadata():
    """Informations sur la version et la dernière mise à jour."""
    return system_service.get_metadata()