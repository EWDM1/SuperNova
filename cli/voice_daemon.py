# cli/voice_daemon.py
import sys
import os
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.tools.wakeword import wake_word_loop

def main():
    print("🎙️ 🌟 Iniciando Daemon de Voz SuperNova...")
    stop_event = threading.Event()
    
    thread = threading.Thread(target=wake_word_loop, args=(stop_event,), daemon=True)
    thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo daemon de voz...")
        stop_event.set()
        thread.join()
        print("✅ Daemon cerrado correctamente.")

if __name__ == "__main__":
    main()
