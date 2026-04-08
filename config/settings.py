import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # 🤖 Motor de IA
    MODEL_NAME: str = Field(default="qwen3:8b", description="Modelo de Ollama (generación actual)")
    OLLAMA_HOST: str = Field(default="http://localhost:11434", description="URL del servidor Ollama")
    TEMPERATURE: float = Field(default=0.3, ge=0.0, le=1.0, description="Creatividad del modelo")

    # 🌐 API & Servidor
    API_HOST: str = Field(default="127.0.0.1", description="Host del servidor API (127.0.0.1 para local, 0.0.0.0 para Docker)")
    API_PORT: int = Field(default=8000, ge=1, le=65535, description="Puerto del servidor API")

    # 🔐 Seguridad
    API_KEY: str | None = Field(default=None, description="Clave API (recomendada si API_HOST != 127.0.0.1)")
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://127.0.0.1:8000", "http://localhost:8000"],
        description="Orígenes CORS permitidos"
    )

    # 💾 Memoria & Almacenamiento
    MEMORY_PATH: Path = Field(default=BASE_DIR / "memory", description="Ruta para memoria vectorial")
    BACKUP_ENABLED: bool = Field(default=True, description="Habilitar backups automáticos")
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging (DEBUG, INFO, WARNING, ERROR)")
    LOG_FILE: Path = Field(default=BASE_DIR / "logs" / "supernova.log", description="Ruta del archivo de log")

    model_config = {
        "env_file": BASE_DIR / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()

# FIX: Crear directorio de logs antes de configurar FileHandler
# Si logs/ no existe, logging.FileHandler lanza FileNotFoundError al arrancar
settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configuración de logging centralizada
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
    ],
)

logger = logging.getLogger("supernova")
