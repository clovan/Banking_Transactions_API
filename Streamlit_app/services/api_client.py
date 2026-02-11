import requests
from config.settings import API_BASE_URL

class APIClient:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
