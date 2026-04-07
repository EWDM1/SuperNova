# core/tools/wakeword.py
import os
import time
import json
import threading
import numpy as np
import sounddevice as sd
from pathlib import Path
from openwakeword.model import Model

TRIGGER_PATH = Path(__file__).parent.parent.parent / "memory" / "wakeword_trigger.json"
TRIGGER_PATH.parent.mkdir(exist_ok=True)

def _write_trigger(state: bool):
    TRIGGER_PATH.write_text(json.dumps({"triggered": state, "timestamp": time.time()}))

def wake_word_loop(stop_event: threading.Event):
    _write_trigger(False)
    print("🎙️ [WakeWord] Cargando modelo (primera vez descarga ~10MB)...")
    try:
        # openwakeword auto-descarga modelos a ~/.cache/openwakeword
        # Usamos "alexa" como trigger base. Para "Nova" personalizado, 
        # puedes reemplazarlo con un modelo .onnx entrenado posteriormente.
        model = Model(wakeword_models=["alexa"]) 
        
        def audio_callback(indata, frames, time_info, status):
            if status: print(f"⚠️ {status}")
            model.predict(indata.flatten())
            # Umbral de detección (0.45-0.55 es óptimo)
            if model.prediction_buffer["alexa"][-1] > 0.5:
                print("🔔 ¡Palabra clave detectada! Activando Nova...")
                _write_trigger(True)
                model.reset()
                time.sleep(1.5)  # Cooldown para evitar doble activación

        # Configurar stream de micrófono
        with sd.InputStream(samplerate=16000, channels=1, callback=audio_callback, blocksize=1280):
            print("✅ [WakeWord] Escucha activa. Di la palabra clave para activar.")
            while not stop_event.is_set():
                time.sleep(0.5)
    except Exception as e:
        print(f"❌ [WakeWord] Error crítico: {e}")
        print("💡 macOS: Ve a Configuración > Privacidad > Micrófono > Permitir a Python/Terminal")
