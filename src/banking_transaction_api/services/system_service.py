import time


class SystemService:
    """ """

    def __init__(self, transaction_service):
        self.transaction_service = transaction_service
        # Enregistré une seule fois au lancement du serveur
        self.start_time = time.time()
        # Métadonnées statiques pour la route 20
        self.version = "1.0.0"
        self.last_update = "2025-12-20T22:00:00Z"

    def get_health_status(self):
        """Route 19 : État de santé et uptime avec secondes."""
        uptime_seconds = int(time.time() - self.start_time)

        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60

        # Format avec espaces : "0h 0min 32s"
        uptime_formatted = f"{hours}h {minutes}min {seconds}s"

        df = self.transaction_service.get_all()
        is_loaded = not df.empty if df is not None else False

        return {
            "status": "ok",
            "uptime": uptime_formatted,
            "dataset_loaded": is_loaded
        }

    def get_metadata(self):
        """Route 20 : Informations sur la version."""
        return {
            "version": self.version,
            "last_update": self.last_update
        }
