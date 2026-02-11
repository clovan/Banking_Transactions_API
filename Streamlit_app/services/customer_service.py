import requests
from config.settings import API_BASE_URL


class CustomerAPI:
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/customers"

    def list_customers(self, page=1, size=10):
        return requests.get(f"{self.base_url}/", params={"page": page,
                                                         "size": size}).json()

    def top_customers(self, n=10):
        return requests.get(f"{self.base_url}/top", params={"n": n}).json()

    def profile(self, customer_id: int):
        return requests.get(f"{self.base_url}/{customer_id}").json()
