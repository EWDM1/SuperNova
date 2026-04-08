# api/main.py
import sys, os
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config.settings import settings, logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.agent import run_agent
    from api.doctor import router as doctor_router
    from api.wake import router as wake_router
except ImportError as e:
    logger.error(f"Error de importación crítica: {e}")
    run_agent = lambda q, h: f"⚠️ Módulo no encontrado: {e}"
    doctor_router = wake_router = None

app = FastAPI(title="🌟 SuperNova API", version="1.1.0")

# 🌐 CORS Estricto
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/dashboard", StaticFiles(directory="static", html=True), name="dashboard")

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

if doctor_router: app.include_router(doctor_router, dependencies=[Depends(verify_api_key)])
if wake_router: app.include_router(wake_router, dependencies=[Depends(verify_api_key)])

@app.get("/health")
def health_check():
    return {"status": "online", "service": "SuperNova API", "version": "1.1.0"}

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
def chat_endpoint(request: ChatRequest):
    logger.info(f"Petición chat: {request.query[:50]}...")
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Consulta vacía")
    try:
        response = run_agent(request.query, request.history)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error procesando chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando API en {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
