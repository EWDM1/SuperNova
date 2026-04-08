# core/tools/__init__.py
"""
🛠️ Registro centralizado de herramientas del agente.
Para añadir una nueva: importa la función con @tool y agrégala a ALL_TOOLS.
"""
from .doctor import doctor_diagnose

# 📦 Registro global (fácil de extender sin tocar agent.py)
ALL_TOOLS = [doctor_diagnose]

__all__ = ["ALL_TOOLS"]
