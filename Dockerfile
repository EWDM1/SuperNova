# 🐳 SuperNova - Contenedor Oficial
# Optimizado para macOS (Apple Silicon) y Linux AMD64

FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias primero (cachea mejor)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY . .

# Exponer puerto API
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
