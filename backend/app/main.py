from fastapi import FastAPI
from app.api.router import api_router
from app.db.session import init_db

app = FastAPI(title="Assistente de Atendimento Inteligente", version="1.0.0")

app.include_router(api_router)
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    init_db()

@app.get("/")
async def root():
    return {"message": "Assistente de Atendimento Inteligente - POC"}