#!/bin/bash

# 🌟 SuperNova - Script de Instalación Automática
# 🍎 Optimizado para macOS (Apple Silicon M1/M2/M3/M4)
# 📌 Uso: chmod +x install.sh && ./install.sh

echo "🌟 Iniciando instalación de SuperNova..."
echo "========================================="

# 1. Verificar sistema operativo
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ Este script está diseñado para macOS."
    echo "   Si usas Windows/Linux, sigue la guía en README.md"
    exit 1
fi

# 2. Verificar conexión a internet
echo "🌐 Verificando conexión a internet..."
if ! ping -c 1 -t 5 google.com &> /dev/null; then
    echo "❌ No hay conexión a internet. Conéctate y vuelve a ejecutar."
    exit 1
fi

# 3. Verificar espacio en disco (mínimo ~15GB libres)
echo "💾 Verificando espacio disponible..."
FREE_SPACE=$(df -m / | awk 'NR==2 {print $4}')
if [ "$FREE_SPACE" -lt 15000 ]; then
    echo "⚠️  Espacio libre bajo: ${FREE_SPACE}MB"
    echo "   Se recomiendan al menos 15GB para el modelo de IA."
    echo "   ¿Deseas continuar? (s/n)"
    read -r response
    if [[ "$response" != "s" && "$response" != "S" ]]; then
        echo "❌ Instalación cancelada."
        exit 1
    fi
else
    echo "✅ Espacio disponible: ${FREE_SPACE}MB"
fi

# 4. Instalar Homebrew si no existe
if ! command -v brew &> /dev/null; then
    echo "📦 Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo "✅ Homebrew instalado."
else
    echo "✅ Homebrew ya está instalado."
fi

# 5. Instalar Ollama (motor de IA local)
if ! command -v ollama &> /dev/null; then
    echo "🤖 Instalando Ollama..."
    brew install --cask ollama
    brew services start ollama
    echo "✅ Ollama instalado y ejecutándose."
else
    echo "✅ Ollama ya está instalado."
fi

# 6. Instalar portaudio (dependencia de audio para macOS)
if ! brew list portaudio &>/dev/null; then
    echo "🔧 Instalando portaudio (dependencia de audio)..."
    brew install portaudio
    echo "✅ portaudio instalado."
else
    echo "✅ portaudio ya está instalado."
fi

# 7. Instalar Python 3.11+
if ! command -v python3 &> /dev/null || ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "🐍 Instalando Python 3.11+..."
    brew install python@3.11
    echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    echo "✅ Python instalado."
else
    echo "✅ Python compatible ya está instalado."
fi

# 8. Configurar entorno virtual de Python
echo "📦 Configurando entorno Python..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Entorno virtual creado."
fi

source .venv/bin/activate
pip install --upgrade pip setuptools wheel

# Instalar dependencias desde pyproject.toml (fuente única de verdad)
echo "📥 Instalando dependencias del proyecto desde pyproject.toml..."
pip install -e . || {
    echo "❌ Fallo al instalar dependencias. Verifica que pyproject.toml esté correcto."
    exit 1
}
deactivate
echo "✅ Entorno Python configurado."

# 9. Descargar modelo de IA (Qwen3 8B — generación actual, supera a Qwen2.5-72B en mismo tamaño)
echo "🧠 Descargando modelo de IA (qwen3:8b)..."
echo "   ⏳ Esto puede tardar 5-15 min según tu conexión (~5GB)..."
ollama pull qwen3:8b || {
    echo "❌ Fallo al descargar el modelo. Revisa tu conexión u Ollama."
    exit 1
}
echo "✅ Modelo descargado."

# 10. Crear estructura de carpetas y directorios de runtime
echo "📁 Creando estructura del proyecto..."
mkdir -p memory backups logs config core/memory core/tools api cli docs
touch core/__init__.py core/tools/__init__.py api/__init__.py cli/__init__.py
echo "✅ Carpetas creadas."

# 11. Mensaje final
echo "========================================="
echo "🎉 ¡Instalación completada con éxito!"
echo "📌 Próximos pasos:"
echo "   1. cd SuperNova"
echo "   2. ./start.sh"
echo "💡 Tip: Para usar la CLI directamente: ./.venv/bin/supernova ask 'hola'"
echo "========================================="
echo "✅ SuperNova está listo. ¡Disfruta tu COO personal!"
