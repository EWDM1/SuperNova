#!/bin/bash

# --- Configuración ---
PROJECT_ROOT=$(dirname "$(readlink -f "$0")")
VENV_PATH="$PROJECT_ROOT/.venv"
LOGS_DIR="$PROJECT_ROOT/logs"

# --- Funciones de Utilidad ---
log_info()    { echo -e "✨ \033[1;34mINFO:\033[0m $1"; }
log_success() { echo -e "✅ \033[1;32mÉXITO:\033[0m $1"; }
log_warn()    { echo -e "⚠️  \033[1;33mADVERTENCIA:\033[0m $1"; }
log_error()   { echo -e "❌ \033[1;31mERROR:\033[0m $1" >&2; exit 1; }

check_command() {
    command -v "$1" >/dev/null 2>&1 || log_error "El comando '$1' no está instalado. Por favor, instálalo y vuelve a intentarlo."
}

# --- Crear directorio de logs PRIMERO (antes de cualquier nohup) ---
mkdir -p "$LOGS_DIR" || log_error "Fallo al crear el directorio de logs."

# --- Verificaciones Iniciales ---
log_info "Verificando entorno..."
check_command "python3"
check_command "git"

# --- Entorno Virtual ---
if [ ! -d "$VENV_PATH" ]; then
    log_info "Creando entorno virtual en $VENV_PATH..."
    python3 -m venv "$VENV_PATH" || log_error "Fallo al crear el entorno virtual."
fi

log_info "Activando entorno virtual..."
source "$VENV_PATH/bin/activate" || log_error "Fallo al activar el entorno virtual."

# --- Instalación de Dependencias ---
log_info "Instalando/actualizando dependencias desde pyproject.toml..."
pip install --upgrade pip setuptools wheel || log_error "Fallo al actualizar pip/setuptools."
pip install -e "$PROJECT_ROOT" || log_error "Fallo al instalar dependencias del proyecto. Asegúrate de que pyproject.toml esté correcto."

# --- Ollama (Modelo de Lenguaje Local) ---
log_info "Verificando instalación de Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
    log_warn "Ollama no encontrado. Por favor, instálalo desde https://ollama.com/download"
    log_error "Ollama es necesario para ejecutar SuperNova. Abortando."
fi

log_info "Verificando si el modelo Ollama está disponible..."
MODEL_NAME=$(python -c "from config.settings import settings; print(settings.MODEL_NAME)")

if ! ollama list | grep -q "$MODEL_NAME"; then
    log_info "Modelo '$MODEL_NAME' no encontrado localmente. Descargándolo..."
    ollama pull "$MODEL_NAME" || log_error "Fallo al descargar el modelo '$MODEL_NAME'."
fi

log_info "Iniciando servidor Ollama en segundo plano si no está corriendo..."
if ! pgrep -x "ollama" > /dev/null; then
    nohup ollama serve > "$LOGS_DIR/ollama.log" 2>&1 &
    log_info "Ollama iniciado. Esperando unos segundos para que se inicialice..."
    sleep 5
else
    log_info "Ollama ya está corriendo."
fi

# --- Manejo de Puertos (para la API) ---
API_PORT=$(python -c "from config.settings import settings; print(settings.API_PORT)")
log_info "Verificando disponibilidad del puerto $API_PORT para la API..."

if lsof -i :"$API_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    log_warn "El puerto $API_PORT ya está en uso. Buscando un puerto libre..."
    FREE_PORT=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')
    log_warn "Usando el puerto libre $FREE_PORT para la API."
    API_PORT=$FREE_PORT
    export SUPERNOVA_API_PORT=$API_PORT
fi

# --- Iniciar Voice Daemon (Wake Word) ---
log_info "Iniciando el demonio de detección de palabra clave en segundo plano..."
nohup python "$PROJECT_ROOT/cli/voice_daemon.py" > "$LOGS_DIR/wake_word.log" 2>&1 &
VOICE_DAEMON_PID=$!
log_info "Demonio de voz iniciado con PID: $VOICE_DAEMON_PID. Logs en $LOGS_DIR/wake_word.log"

# --- Abrir Dashboard ---
log_info "Abriendo el dashboard en tu navegador..."
if command -v open >/dev/null 2>&1; then
    open "http://localhost:$API_PORT/dashboard"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:$API_PORT/dashboard"
else
    log_warn "No se pudo abrir el navegador automáticamente. Abre manualmente: http://localhost:$API_PORT/dashboard"
fi

# --- Limpieza al Salir ---
cleanup() {
    log_info "Deteniendo el demonio de voz (PID: $VOICE_DAEMON_PID)..."
    kill "$VOICE_DAEMON_PID" 2>/dev/null
    log_info "Desactivando entorno virtual..."
    deactivate
    log_success "SuperNova se ha detenido limpiamente."
}
trap cleanup EXIT

# --- Iniciar API (Uvicorn) ---
log_info "Iniciando la API de SuperNova con Uvicorn en http://localhost:$API_PORT..."
uvicorn api.main:app --host 0.0.0.0 --port "$API_PORT" --reload || log_error "Fallo al iniciar la API de SuperNova."
