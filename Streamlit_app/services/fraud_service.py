import requests
from config.settings import API_BASE_URL


class FraudAPI:
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/fraud"

    def summary(self):
        return requests.get(f"{self.base_url}/summary").json()

    def by_type(self):
        return requests.get(f"{self.base_url}/by-type").json()

    def predict(self, payload: dict):
        return requests.post(f"{self.base_url}/predict", json=payload).json()
