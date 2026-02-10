import requests

BASE_URL = "http://localhost:8000/api"

def get_transactions(page=1, limit=20, transaction_type=None, isFraud=None, min_amount=None, max_amount=None):
    params = {
        "page": page,
        "limit": limit,
        "transaction_type": transaction_type,
        "isFraud": isFraud,
        "min_amount": min_amount,
        "max_amount": max_amount
    }
    params = {k: v for k, v in params.items() if v is not None}
    return requests.get(f"{BASE_URL}/transactions/", params=params).json()

def search_transactions(transaction_type=None, isFraud=None, min_amount=None, max_amount=None):
    params = {
        "transaction_type": transaction_type,
        "isFraud": isFraud,
        "min_amount": min_amount,
        "max_amount": max_amount
    }
    params = {k: v for k, v in params.items() if v is not None}
    return requests.post(f"{BASE_URL}/transactions/search", params=params).json()

def get_transaction_by_id(id):
    return requests.get(f"{BASE_URL}/transactions/{id}").json()

def get_transaction_types():
    return requests.get(f"{BASE_URL}/transactions/types").json()
