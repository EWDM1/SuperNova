.PHONY: install run doctor test clean

install:
	@echo "📦 Instalando dependencias..."
	pip install -r requirements.txt

run:
	@echo "🌐 Iniciando API en http://localhost:8000..."
	uvicorn api.main:app --reload

doctor:
	@echo "🩺 Ejecutando diagnóstico..."
	python cli/doctor.py check

test:
	@echo "🧪 Verificando estructura..."
	python -c "import core.agent; import cli.doctor; import api.main; print('✅ Todo OK')"

clean:
	@echo "🧹 Limpiando caché..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Limpieza completada."
