# api/main.py
import sys
import os
import logging
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from config.settings import settings, logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ CORREGIDO: imports con try/except explícito
try:
    from core.agent import run_agent
    from api.doctor import router as doctor_router
    from api.wake import router as wake_router
except ImportError as e:
    logger.critical(f"Error crítico de importación: {e}")
    run_agent = None
    doctor_router = None
    wake_router = None

app = FastAPI(title="🌟 SuperNova API", version="1.1.0")

# 🌐 CORS Estricto con fallback seguro
allowed_origins = settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else ["http://127.0.0.1:8000", "http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CORREGIDO: verificar que el directorio static existe antes de montar
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/dashboard", StaticFiles(directory=str(static_dir), html=True), name="dashboard")
else:
    logger.warning(f"Directorio static no encontrado: {static_dir}")

# 🔐 Validación de API Key (solo si está configurada)
async def verify_api_key(x_api_key: str = Header(None)):
    if settings.API_KEY and x_api_key != settings.API_KEY:
        logger.warning("Intento de acceso no autorizado a API")
        raise HTTPException(status_code=401, detail="API Key inválida o faltante")

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# ✅ CORREGIDO: routers solo se montan si existen
if doctor_router:
    app.include_router(doctor_router, prefix="/doctor", dependencies=[Depends(verify_api_key)])
if wake_router:
    app.include_router(wake_router, prefix="/wake", dependencies=[Depends(verify_api_key)])

@app.get("/health")
def health_check():
    return {"status": "online", "service": "SuperNova API", "version": "1.1.0"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, x_api_key: str = Header(None)):
    # ✅ CORREGIDO: validar API Key solo si está configurada
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")
    
    logger.info(f"Petición chat: {request.query[:50]}...")
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Consulta vacía")
    if run_agent is None:
        raise HTTPException(status_code=503, detail="Agente no disponible")
    try:
        response = run_agent(request.query, request.history)
        return ChatResponse(response=str(response))
    except Exception as e:
        logger.error(f"Error procesando chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando API en {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
