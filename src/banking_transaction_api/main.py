from fastapi import FastAPI
from banking_transaction_api.routers.transactions import router as trans_router
from banking_transaction_api.routers.stats import router as stats_router
from banking_transaction_api.routers.fraud import router as fraud_router
from banking_transaction_api.routers.customer import router as customer_router
from banking_transaction_api.routers.system import router as system_router



app = FastAPI(title="Banking API")

app.include_router(trans_router)
app.include_router(stats_router)
app.include_router(fraud_router)
app.include_router(customer_router)

app.include_router(system_router)

@app.get("/")
def health_check():
    return {"status": "online"}