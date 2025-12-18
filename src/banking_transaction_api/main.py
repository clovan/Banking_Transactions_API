from fastapi import FastAPI
from src.banking_transaction_api.database import get_all_transactions
app = FastAPI(
    title="Banking Transactions API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenue sur l'API Bancaire",
        "team": ["Clovis", "Irmeline", "Milaine", "Amina"],
        "documentation": "/docs"
    }

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

@app.get("/transactions")
def read_transactions():
    return get_all_transactions()