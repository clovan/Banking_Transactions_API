from fastapi import FastAPI
from banking_transaction_api.routers.transactions import router as trans_router
from banking_transaction_api.routers.customers import router as customers_router
from banking_transaction_api.routers.fraud import router as fraud_router

app = FastAPI(title="Banking API")

app.include_router(customers_router)
app.include_router(fraud_router)

@app.get("/")
def health_check():
    return {"status": "online"}