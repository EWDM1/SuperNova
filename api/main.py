# api/main.py
import sys
import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Permitir que Python encuentre las carpetas `core/` y `config/` desde la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.agent import run_agent
except ImportError:
    run_agent = lambda q, h: "⚠️ Módulo 'core/agent.py' no encontrado. Ejecuta ./install.sh primero."

app = FastAPI(
    title="🌟 SuperNova API",
    description="Interfaz REST para tu asistente IA personal (Modo COO)",
    version="1.0.0"
)

# 📥 Modelos de entrada/salida (validación automática)
class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# 🏥 Endpoint de verificación
@app.get("/health")
def health_check():
    return {"status": "online", "service": "SuperNova API", "version": "1.0.0"}

# 💬 Endpoint principal de chat
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía")
    
    try:
        response_text = run_agent(request.query, request.history)
        return ChatResponse(response=response_text)
    except Exception as e:
        # En producción se loguea, aquí se devuelve mensaje claro
        raise HTTPException(status_code=500, detail=f"Error al procesar: {str(e)}")

# 🚀 Ejecución local (solo para pruebas manuales)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
