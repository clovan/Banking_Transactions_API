from fastapi import FastAPI
# L'import doit être relatif à la racine configurée dans PYTHONPATH
from banking_transaction_api.routers.transactions import router as trans_router

app = FastAPI(title="Banking API")

# Inclusion unique et propre
app.include_router(trans_router)

@app.get("/")
def health_check():
    return {"status": "online", "message": "API de Transaction Bancaire prête"}