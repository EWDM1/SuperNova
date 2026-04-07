#!/bin/bash

# 🌟 SuperNova — Script de Lanzamiento Rápido
# 🍎 Optimizado para macOS | Uso: ./start.sh
# ✅ Inicia API + abre Dashboard en navegador + maneja Ctrl+C limpiamente

set -e  # Detener script si algún comando falla

# Colores para mensajes (macOS Terminal compatible)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🌟 Iniciando SuperNova Control Center...${NC}"
echo "========================================="

# 1. Verificar que estamos en la carpeta correcta
if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Debes ejecutar este script desde la carpeta raíz de SuperNova${NC}"
    echo "   Ejemplo: cd ~/SuperNova && ./start.sh"
    exit 1
fi

# 2. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado. Instálalo desde python.org o con brew install python${NC}"
    exit 1
fi

# 3. Verificar/crear entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚙️  Creando entorno virtual (primera vez)...${NC}"
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# 4. Instalar dependencias si es necesario
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    pip install --upgrade pip -q
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q
    fi
    touch venv/.installed
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
else
    echo -e "${GREEN}✅ Dependencias ya instaladas${NC}"
fi

# 5. Verificar Ollama (motor de IA)
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama no está instalado. Descárgalo desde: https://ollama.com${NC}"
    echo -e "${YELLOW}   SuperNova funcionará, pero necesitarás el modelo para respuestas reales.${NC}"
else
    # Verificar si Ollama está corriendo
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${YELLOW}🤖 Iniciando Ollama en segundo plano...${NC}"
        ollama serve &
        sleep 3
    fi
    echo -e "${GREEN}✅ Ollama listo${NC}"
fi

# 6. Verificar puerto 8000 disponible
if lsof -i :8000 &> /dev/null; then
    echo -e "${YELLOW}⚠️  El puerto 8000 ya está en uso${NC}"
    echo -e "${YELLOW}   ¿Quieres usar el puerto 8001 en su lugar? (s/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[sS]$ ]]; then
        PORT=8001
        echo -e "${GREEN}✅ Usando puerto $PORT${NC}"
    else
        echo -e "${RED}❌ Cierra la otra aplicación o usa: lsof -i :8000 | grep LISTEN${NC}"
        exit 1
    fi
else
    PORT=8000
fi

# 7. Mensaje de éxito + abrir navegador
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}🎉 SuperNova está listo!${NC}"
echo -e "${CYAN}🌐 Dashboard: http://localhost:$PORT/dashboard/${NC}"
echo -e "${CYAN}📚 Docs API:  http://localhost:$PORT/docs${NC}"
echo -e "${YELLOW}💡 Tip: Presiona Ctrl+C para detener el servidor${NC}"
echo -e "${GREEN}=========================================${NC}"

# Abrir navegador automáticamente (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:$PORT/dashboard/"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "http://localhost:$PORT/dashboard/" 2>/dev/null || echo "🌐 Abre manualmente: http://localhost:$PORT/dashboard/"
else
    echo "🌐 Abre manualmente en tu navegador: http://localhost:$PORT/dashboard/"
fi

# 8. Iniciar servidor API (con manejo limpio de Ctrl+C)
echo -e "${CYAN}🚀 Iniciando servidor API...${NC}"
trap "echo -e '\n${YELLOW}🛑 Deteniendo SuperNova...${NC}'; deactivate; exit 0" INT TERM

uvicorn api.main:app --host 0.0.0.0 --port $PORT --reload
