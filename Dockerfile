# 🐳 SuperNova - Contenedor Oficial
# Optimizado para macOS (Apple Silicon) y Linux AMD64

FROM python:3.11-slim

# Instalar dependencias del sistema (portaudio requerido por sounddevice/openwakeword)
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias desde pyproject.toml (fuente única de verdad)
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e .

# Copiar código del proyecto
COPY . .

# Crear directorios necesarios para bind mounts (evita errores de permisos)
RUN mkdir -p /app/memory /app/backups /app/config /app/logs

# Exponer puerto API
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
