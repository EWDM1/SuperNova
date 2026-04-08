# config/settings.py
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
import logging

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # 🤖 Motor de IA (UNIFICADO: qwen2.5:7b es el más estable actualmente)
    MODEL_NAME: str = Field(default="qwen2.5:7b", description="Modelo de Ollama")
    OLLAMA_HOST: str = Field(default="http://localhost:11434", description="URL del servidor Ollama")
    TEMPERATURE: float = Field(default=0.3, ge=0.0, le=1.0, description="Creatividad del modelo")

    # 🌐 API & Servidor
    API_HOST: str = Field(default="127.0.0.1", description="Host del servidor API (usa 127.0.0.1 para local)")
    API_PORT: int = Field(default=8000, ge=1, le=65535, description="Puerto del servidor API")

    # 🔐 Seguridad
    API_KEY: str | None = Field(default=None, description="Clave API (OBLIGATORIA si API_HOST != 127.0.0.1)")
    ALLOWED_ORIGINS: list[str] = Field(default=["http://127.0.0.1:8000", "http://localhost:8000"], description="Orígenes CORS permitidos")

    # 💾 Memoria & Almacenamiento
    MEMORY_PATH: Path = Field(default=BASE_DIR / "memory", description="Ruta para memoria vectorial")
    BACKUP_ENABLED: bool = Field(default=True, description="Habilitar backups")
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging")
    LOG_FILE: Path = Field(default=BASE_DIR / "logs" / "supernova.log", description="Ruta del archivo de log")

    model_config = {
        "env_file": BASE_DIR / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()

# Configuración de logging centralizada
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
    ]
)
logger = logging.getLogger("supernova")
