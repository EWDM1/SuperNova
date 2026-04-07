# config/settings.py
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Ruta base del proyecto (apunta a la carpeta raíz de SuperNova)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # 🤖 Motor de IA
    MODEL_NAME: str = Field(default="qwen2.5:7b", description="Modelo de Ollama a usar")
    OLLAMA_HOST: str = Field(default="http://localhost:11434", description="URL del servidor Ollama")
    TEMPERATURE: float = Field(default=0.3, ge=0.0, le=1.0, description="Creatividad del modelo (0=preciso, 1=creativo)")

    # 🌐 API & Servidor
    API_HOST: str = Field(default="0.0.0.0", description="Host del servidor API")
    API_PORT: int = Field(default=8000, ge=1, le=65535, description="Puerto del servidor API")

    # 💾 Memoria & Almacenamiento
    MEMORY_PATH: Path = Field(default=BASE_DIR / "memory", description="Ruta para la base de datos vectorial")
    BACKUP_ENABLED: bool = Field(default=True, description="Habilitar backups automáticos")
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging (DEBUG, INFO, WARNING, ERROR)")

    # 🔐 Seguridad (Opcional)
    API_KEY: str | None = Field(default=None, description="Clave API opcional para proteger endpoints")
    ALLOWED_ORIGINS: list[str] = Field(default=["http://localhost:8000", "http://localhost:3000"], description="Orígenes CORS permitidos")

    # Configuración de Pydantic V2
    model_config = {
        "env_file": BASE_DIR / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

# Instancia global lista para importar en toda la app
settings = Settings()
