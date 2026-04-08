import sys
import os
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# Añadir el directorio raíz del proyecto al sys.path para importaciones relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.agent import run_agent
    from api.doctor import router as doctor_router
    from api.wake import router as wake_router
    from config.settings import settings
except ImportError as e:
    # Manejo de errores más específico o al menos loguear el error
    print(f"ERROR: No se pudieron importar módulos esenciales: {e}", file=sys.stderr)
    run_agent = lambda q, h: f"⚠️ Error crítico de importación: {e}. Verifique la instalación y el entorno."
    doctor_router = None
    wake_router = None
    settings = None # Asegurarse de que settings sea None si falla la importación

app = FastAPI(
    title="🌟 SuperNova API",
    description="Interfaz REST para tu asistente IA personal (Modo COO)",
    version="1.0.0"
)

# Configuración de CORS usando settings
if settings and settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Configuración de seguridad con API Key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if settings and settings.API_KEY and api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Acceso no autorizado: API Key inválida o faltante",
        headers={"WWW-Authenticate": "X-API-Key"},
    )

# Montar el dashboard estático
app.mount("/dashboard", StaticFiles(directory="static", html=True), name="dashboard")

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# Incluir routers condicionalmente
if doctor_router: app.include_router(doctor_router, dependencies=[Depends(get_api_key)])
if wake_router: app.include_router(wake_router, dependencies=[Depends(get_api_key)])

@app.get("/health")
def health_check():
    return {"status": "online", "service": "SuperNova API", "version": "1.0.0"}

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(get_api_key)])
def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía")
    try:
        response_text = run_agent(request.query, request.history)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Usar la configuración centralizada para host y puerto
    host = settings.API_HOST if settings else "0.0.0.0"
    port = settings.API_PORT if settings else 8000
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
