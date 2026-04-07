# core/tools/doctor.py
import os
import shutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool

@tool
def doctor_diagnose(fix_mode: bool = False) -> str:
    """
    Ejecuta un diagnóstico completo del entorno SuperNova.
    Revisa Ollama, espacio en disco, puerto API, memoria y logs.
    Devuelve un reporte claro en español con recomendaciones seguras.
    """
    report = {"checks": [], "recommendations": []}
    project_root = Path(__file__).resolve().parent.parent.parent

    # 1. Verificar Ollama
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        models = [line.split()[0] for line in result.stdout.strip().split("\n")[1:] if line.strip()]
        if models:
            report["checks"].append({"component": "Ollama", "status": "✅ Activo", "detail": f"Modelos: {', '.join(models)}"})
        else:
            report["checks"].append({"component": "Ollama", "status": "⚠️ Sin modelos"})
            report["recommendations"].append("Ejecuta: `ollama pull qwen2.5:7b`")
    except FileNotFoundError:
        report["checks"].append({"component": "Ollama", "status": "❌ No encontrado"})
        report["recommendations"].append("Ejecuta: `brew install --cask ollama && brew services start ollama`")
    except Exception as e:
        report["checks"].append({"component": "Ollama", "status": "⚠️ Error", "detail": str(e)})

    # 2. Espacio en disco
    try:
        total, used, free = shutil.disk_usage(project_root)
        free_gb = free / (1024**3)
        if free_gb < 5:
            report["checks"].append({"component": "Disco", "status": "⚠️ Espacio bajo", "detail": f"{free_gb:.1f} GB libres"})
            report["recommendations"].append("Libera espacio. Se recomiendan >10 GB libres para IA.")
        else:
            report["checks"].append({"component": "Disco", "status": "✅ OK", "detail": f"{free_gb:.1f} GB libres"})
    except Exception as e:
        report["checks"].append({"component": "Disco", "status": "⚠️ Error al verificar", "detail": str(e)})

    # 3. Puerto API (8000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_status = "✅ Libre"
    if sock.connect_ex(('127.0.0.1', 8000)) == 0:
        port_status = "⚠️ Ocupado"
        report["recommendations"].append("Puerto 8000 en uso. Cierra la otra app o usa: `uvicorn api.main:app --port 8001`")
    sock.close()
    report["checks"].append({"component": "Puerto API (8000)", "status": port_status})

    # 4. Memoria Vectorial (ChromaDB)
    db_path = project_root / "memory" / "chroma_db"
    if db_path.exists():
        report["checks"].append({"component": "Memoria", "status": "✅ Activa", "detail": str(db_path)})
    else:
        report["checks"].append({"component": "Memoria", "status": "ℹ️ No creada aún", "detail": "Se generará en el primer uso"})

    # 5. Logs
    log_path = project_root / "logs"
    log_path.mkdir(exist_ok=True)
    report["checks"].append({"component": "Logs", "status": "✅ Listo", "detail": str(log_path)})

    # Construir reporte final
    output = "🩺 **Reporte de Diagnóstico SuperNova**\n"
    output += f"🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    for check in report["checks"]:
        output += f"{check['status']} {check['component']}"
        if "detail" in check:
            output += f" → {check['detail']}"
        output += "\n"

    if report["recommendations"]:
        output += "\n🔧 **Acciones recomendadas:**\n"
        for rec in report["recommendations"]:
            output += f"• {rec}\n"
    else:
        output += "\n✅ **Estado general:** Todo funciona correctamente. No se requieren acciones."

    return output
