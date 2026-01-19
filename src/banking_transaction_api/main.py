from fastapi import FastAPI
from banking_transaction_api.routers.transactions import router as trans_router

app = FastAPI(title="Banking API")

app.include_router(trans_router)

@app.get("/")
def health_check():
    return {"status": "online"}