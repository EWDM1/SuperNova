# api/wake.py
from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter(prefix="/wake", tags=["🎙️ Wake Word"])
TRIGGER_FILE = Path(__file__).parent.parent / "memory" / "wakeword_trigger.json"

@router.get("/status")
def get_status():
    """Devuelve y reinicia automáticamente el estado de activación"""
    if TRIGGER_FILE.exists():
        data = json.loads(TRIGGER_FILE.read_text())
        if data.get("triggered"):
            TRIGGER_FILE.write_text(json.dumps({"triggered": False, "timestamp": data["timestamp"]}))
            return {"triggered": True, "timestamp": data["timestamp"]}
    return {"triggered": False, "timestamp": None}
