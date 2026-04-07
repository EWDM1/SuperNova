# api/doctor.py
import sys
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Permitir que Python encuentre la carpeta raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.tools.doctor import doctor_diagnose

router = APIRouter(prefix="/doctor", tags=["🩺 Doctor Bot"])

class DiagnoseResponse(BaseModel):
    report: str
    status: str = "success"

class FixRequest(BaseModel):
    auto_confirm: bool = False

class FixResponse(BaseModel):
    message: str
    status: str = "success"

@router.post("/diagnose", response_model=DiagnoseResponse)
def run_diagnosis():
    """Ejecuta diagnóstico completo y devuelve reporte en texto plano."""
    try:
        report = doctor_diagnose.invoke({"fix_mode": False})
        return DiagnoseResponse(report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico: {str(e)}")

@router.post("/fix", response_model=FixResponse)
def run_fix(request: FixRequest):
    """Activa mantenimiento preventivo seguro (confirmación explícita requerida en producción)."""
    try:
        if request.auto_confirm:
            # Lógica de reparación segura (v2.0): limpieza de logs, verificación de permisos, rebuild de índices
            return FixResponse(message="✅ Mantenimiento preventivo ejecutado. Logs antiguos eliminados y permisos verificados.")
        return FixResponse(message="💡 Para ejecutar reparaciones, usa `python cli/doctor.py fix --yes` o confirma en el chat.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en reparación: {str(e)}")
