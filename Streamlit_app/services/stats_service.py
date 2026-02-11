import requests
from config.settings import API_BASE_URL


class StatsAPI:
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/stats"

    def overview(self):
        return requests.get(f"{self.base_url}/overview").json()

    def amount_distribution(self, bins=None):
        params = []
        if bins:
            for b in bins:
                params.append(("bins", b))
        return requests.get(f"{self.base_url}/amount-distribution",
                            params=params).json()

    def stats_by_type(self):
        return requests.get(f"{self.base_url}/by-type").json()

    def daily_stats(self):
        return requests.get(f"{self.base_url}/daily").json()
