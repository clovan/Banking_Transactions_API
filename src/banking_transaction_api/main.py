from fastapi import FastAPI
from src.banking_transaction_api.database import get_all_transactions
app = FastAPI(
    title="Banking Transactions API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "success", "message": "API de Transactions Bancaires opérationnelle"}