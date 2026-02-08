from fastapi import FastAPI
from banking_transaction_api.routers.transactions import router as trans_router
from banking_transaction_api.routers import statistiques

app = FastAPI(title="Banking API")

# Ajout du préfixe attendu par les tests
app.include_router(trans_router)
app.include_router(statistiques.router)

@app.get("/")
def health_check():
    return {"status": "online"}


