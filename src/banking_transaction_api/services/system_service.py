import time
from datetime import datetime

class SystemService:
    def __init__(self):
        self.start_time = time.time()
        self.version = "1.0.0"
        self.last_update = "2025-12-20T22:00:00Z"

    def get_uptime(self):
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}min"

    def get_status(self, dataset_loaded: bool):
        return {
            "status": "ok",
            "uptime": self.get_uptime(),
            "dataset_loaded": dataset_loaded
        }