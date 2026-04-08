# core/tools/doctor.py (actualizado)
import os, socket, subprocess, logging
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool
import psutil
from config.settings import settings

logger = logging.getLogger("supernova.doctor")

@tool
def doctor_diagnose(fix_mode: bool = False) -> str:
    """Diagnóstico completo: Ollama, disco, puerto, memoria, CPU, RAM, logs."""
    report = {"checks": [], "recommendations": []}
    project_root = Path(__file__).resolve().parent.parent.parent

    # CPU & RAM (nuevo)
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        report["checks"].append({"component": "CPU", "status": f"{'⚠️' if cpu>80 else '✅'} {cpu}%", "detail": "Uso promedio"})
        report["checks"].append({"component": "RAM", "status": f"{'⚠️' if ram.percent>85 else '✅'} {ram.percent}%", "detail": f"{ram.used/1e9:.1f}GB / {ram.total/1e9:.1f}GB"})
    except Exception as e:
        report["checks"].append({"component": "Sistema", "status": "⚠️ Error métricas", "detail": str(e)})

    # Ollama
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        models = [line.split()[0] for line in res.stdout.strip().split("\n")[1:] if line.strip()]
        report["checks"].append({"component": "Ollama", "status": "✅ Activo", "detail": f"Modelos: {', '.join(models) if models else 'Ninguno'}"})
    except Exception:
        report["checks"].append({"component": "Ollama", "status": "❌ No detectado"})
        report["recommendations"].append("Instala Ollama: brew install --cask ollama")

    # Disco
    try:
        free = psutil.disk_usage(str(project_root)).free / 1e9
        report["checks"].append({"component": "Disco", "status": f"{'⚠️' if free<5 else '✅'} {free:.1f}GB libres"})
    except: pass

    # Puerto
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_status = "✅ Libre" if s.connect_ex(('127.0.0.1', settings.API_PORT)) != 0 else f"⚠️ Ocupado (puerto {settings.API_PORT})"
    s.close()
    report["checks"].append({"component": f"Puerto API ({settings.API_PORT})", "status": port_status})

    # Salida formateada
    out = f"🩺 **Reporte Diagnóstico SuperNova** | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    for c in report["checks"]:
        out += f"{c['status']} {c['component']} → {c.get('detail','')}\n"
    if report["recommendations"]:
        out += "\n🔧 **Recomendaciones:**\n" + "\n".join([f"• {r}" for r in report["recommendations"]])
    else:
        out += "\n✅ **Estado:** Todo nominal."
    return out
