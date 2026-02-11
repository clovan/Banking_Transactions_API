import requests
from config.settings import API_BASE_URL


class TransactionsAPI:
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/transactions"

    def list_transactions(self, limit=50):
        url = f"{self.base_url}/?limit={limit}"
        return requests.get(url).json()

    def get_by_id(self, transaction_id):
        url = f"{self.base_url}/{transaction_id}"
        return requests.get(url).json()

    def search_advanced(self, payload: dict):
        url = f"{self.base_url}/search"
        return requests.post(url, json=payload).json()

    def get_debits(self, customer_id):
        url = f"{self.base_url}/by-customer/{customer_id}"
        return requests.get(url).json()

    def get_credits(self, customer_id):
        url = f"{self.base_url}/to-customer/{customer_id}"
        return requests.get(url).json()

    def get_types(self):
        url = f"{self.base_url}/types"
        return requests.get(url).json()

    def get_recent(self, n=10):
        url = f"{self.base_url}/recent?n={n}"
        return requests.get(url).json()
