import sys
import os
import logging
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# Logger centralizado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("supernova.api")

# Añadir el directorio raíz al sys.path para importaciones relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Importaciones críticas con manejo de errores ---
try:
    from core.agent import run_agent
    from api.doctor import router as doctor_router
    from api.wake import router as wake_router
    from config.settings import settings
except ImportError as e:
    logger.error(f"No se pudieron importar módulos esenciales: {e}")
    # FIX: closure bug — capturar 'e' como default arg para evitar NameError en Python 3
    _import_error_msg = str(e)
    run_agent = lambda q, h, _msg=_import_error_msg: f"⚠️ Error crítico de importación: {_msg}. Verifique la instalación."
    doctor_router = None
    wake_router = None
    settings = None

# --- Inicialización de FastAPI ---
app = FastAPI(
    title="🌟 SuperNova API",
    description="Interfaz REST para tu asistente IA personal (Modo COO)",
    version="1.0.0",
)

# --- CORS ---
# FIX: Aplicar CORS siempre con defaults seguros, incluso si settings falla
_allowed_origins = (
    settings.ALLOWED_ORIGINS
    if settings and getattr(settings, "ALLOWED_ORIGINS", None)
    else ["http://localhost:8000", "http://localhost:3000"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# --- Autenticación por API Key ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    # FIX: Si no hay API_KEY configurada en settings, se opera en modo abierto (dev/local)
    # Si hay API_KEY configurada, se exige y valida
    configured_key = settings.API_KEY if settings and getattr(settings, "API_KEY", None) else None
    if configured_key is None:
        return None  # Modo sin autenticación (uso local)
    if api_key == configured_key:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Acceso no autorizado: API Key inválida o faltante",
        headers={"WWW-Authenticate": "X-API-Key"},
    )

# --- Dashboard estático ---
# FIX: Verificar que el directorio 'static/' exista antes de montarlo
_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(_static_dir):
    app.mount("/dashboard", StaticFiles(directory=_static_dir, html=True), name="dashboard")
    logger.info(f"Dashboard montado desde: {_static_dir}")
else:
    logger.warning(f"Directorio 'static/' no encontrado en {_static_dir}. Dashboard no disponible.")

# --- Modelos Pydantic ---
class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# --- Routers opcionales ---
if doctor_router:
    app.include_router(doctor_router, dependencies=[Depends(get_api_key)])
if wake_router:
    app.include_router(wake_router, dependencies=[Depends(get_api_key)])

# --- Endpoints ---

@app.get("/health")
def health_check():
    """Health check público — sin autenticación requerida."""
    return {
        "status": "online",
        "service": "SuperNova API",
        "version": "1.0.0",
        "model": settings.MODEL_NAME if settings else "unknown",
    }

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(get_api_key)])
def chat_endpoint(request: ChatRequest):
    """Endpoint principal de chat con el agente IA."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")
    try:
        response_text = run_agent(request.query, request.history)
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error en chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")

# --- Entry point directo ---
if __name__ == "__main__":
    import uvicorn
    host = settings.API_HOST if settings else "0.0.0.0"
    port = settings.API_PORT if settings else 8000
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
