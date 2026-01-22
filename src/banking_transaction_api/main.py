from fastapi import FastAPI
from banking_transaction_api.routers.transactions import router as trans_router
# On importe le futur router système
from banking_transaction_api.routers.system import router as system_router 

app = FastAPI(title="Banking API")

# Inclusion des deux routers
app.include_router(trans_router)
app.include_router(system_router) 

@app.get("/")
def health_check():
    return {"status": "online", "message": "API de Transaction Bancaire prête"}