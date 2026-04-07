#!/bin/bash
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}🌟 Iniciando SuperNova Control Center...${NC}"
echo "========================================="

if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Ejecuta desde la carpeta raíz de SuperNova${NC}"; exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"; exit 1
fi

# Verificar/crear entorno virtual
[ ! -d "venv" ] && { echo -e "${YELLOW}⚙️  Creando entorno virtual...${NC}"; python3 -m venv venv; }
source venv/bin/activate

# Instalar dependencias si es primera vez
[ ! -f "venv/.installed" ] && {
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    touch venv/.installed
    echo -e "${GREEN}✅ Dependencias listas${NC}"
}

# Instalar portaudio si falta (requerido por sounddevice en macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}⚠️  Homebrew no encontrado. Instálalo desde https://brew.sh${NC}"
    else
        if ! brew list portaudio &>/dev/null; then
            echo -e "${YELLOW}🔧 Instalando portaudio (audio macOS)...${NC}"
            brew install portaudio
        fi
    fi
fi

# Verificar Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama no está instalado. Descárgalo desde: https://ollama.com${NC}"
else
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${YELLOW}🤖 Iniciando Ollama...${NC}"
        ollama serve &
        sleep 3
    fi
fi

# Verificar puerto
if lsof -i :8000 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Puerto 8000 en uso. ¿Usar 8001? (s/n)${NC}"
    read -r r; [[ "$r" =~ ^[sS]$ ]] && PORT=8001 || exit 1
else
    PORT=8000
fi

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}🎉 SuperNova está listo!${NC}"
echo -e "${CYAN}🌐 Dashboard: http://localhost:$PORT/dashboard/${NC}"
echo -e "${YELLOW}🎙️ Wake Word: Activo. Di la palabra clave para activar.${NC}"
echo -e "${YELLOW}💡 Ctrl+C para detener${NC}"
echo -e "${GREEN}=========================================${NC}"

# Abrir navegador
[[ "$OSTYPE" == "darwin"* ]] && open "http://localhost:$PORT/dashboard/" || xdg-open "http://localhost:$PORT/dashboard/" 2>/dev/null || true

# 🆕 LANZAR DAEMON DE VOZ EN BACKGROUND
echo -e "${CYAN}🎙️ Iniciando daemon de voz...${NC}"
nohup python cli/voice_daemon.py > logs/wake_word.log 2>&1 &
WAKE_PID=$!

# Manejo limpio de Ctrl+C
cleanup() {
    echo -e "\n${YELLOW}🛑 Deteniendo SuperNova...${NC}"
    kill $WAKE_PID 2>/dev/null || true
    deactivate
    exit 0
}
trap cleanup INT TERM

# Iniciar API
echo -e "${CYAN}🚀 Iniciando servidor API...${NC}"
uvicorn api.main:app --host 0.0.0.0 --port $PORT --reload
