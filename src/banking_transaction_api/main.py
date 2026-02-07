from fastapi import FastAPI
from banking_transaction_api.routers.transactions import router as trans_router
from banking_transaction_api.routers.system import router as system_router 
from banking_transaction_api.services.transaction_service import TransactionService

app = FastAPI(title="Banking API")

# ⬇️ CHANGEZ CETTE LIGNE : utilisez app.state au lieu d'une variable globale
app.state.transaction_service = TransactionService()

@app.on_event("startup")
async def startup_event():
    """Précharge le dataset au démarrage de l'API"""
    try:
        print("🔄 Chargement du dataset...")
        # ⬇️ CHANGEZ ICI AUSSI : utilisez app.state
        df = app.state.transaction_service.get_all()
        
        if df is not None and not df.empty:
            print(f"✅ Dataset chargé avec succès : {len(df)} transactions")
        else:
            print("⚠️ Dataset vide")
            
    except Exception as e:
        print(f"❌ Erreur lors du chargement du dataset: {e}")

# Inclusion des routers
app.include_router(trans_router)
app.include_router(system_router) 

@app.get("/")
def health_check():
    return {"status": "online", "message": "API de Transaction Bancaire prête"}