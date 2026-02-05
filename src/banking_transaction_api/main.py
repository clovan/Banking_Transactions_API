from fastapi import FastAPI
from banking_transaction_api.routers.transactions import router as trans_router
from banking_transaction_api.routers.stats import router as stats_router


app = FastAPI(title="Banking API")

app.include_router(trans_router)
app.include_router(stats_router)

@app.get("/")
def health_check():
    return {"status": "online"}