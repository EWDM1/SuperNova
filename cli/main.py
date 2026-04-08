import os
import sys
from typing import List, Dict

import typer

# FIX: sys.path para importaciones relativas cuando se ejecuta directamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# FIX: Importaciones con try/except — CLI no debe crashear con ImportError sin mensaje útil
try:
    from core.agent import run_agent
    from config.settings import settings
except ImportError as e:
    typer.secho(f"\n❌ Error crítico al cargar SuperNova: {e}", fg="red", bold=True, err=True)
    typer.secho("   Verifica que el entorno virtual esté activo y las dependencias instaladas.", fg="yellow", err=True)
    typer.secho("   Ejecuta: pip install -e .", fg="yellow", err=True)
    raise SystemExit(1)

# Límite de turnos en historial para evitar contextos excesivos enviados a Ollama
MAX_HISTORY_TURNS = 20  # 20 pares user/assistant = 40 mensajes máximo

app = typer.Typer(
    help="🌟 SuperNova - Tu Asistente IA Personal (Modo COO)",
    add_completion=False,
)


@app.command()
def ask(
    query: str = typer.Argument(..., help="Tu pregunta o instrucción para SuperNova"),
):
    """Hazle una pregunta o dale una tarea puntual a SuperNova."""
    typer.secho("\n🤖 SuperNova: Procesando tu solicitud...", fg="cyan")
    try:
        # FIX: pasar history=[] explícitamente para ser consistente con la firma de run_agent
        response = run_agent(query, history=[])
        typer.secho("\n✨ Respuesta:", fg="green", bold=True)
        typer.echo(response)
    except Exception as e:
        typer.secho(f"\n❌ Error al generar respuesta: {e}", fg="red", err=True)
        raise SystemExit(1)


@app.command()
def chat():
    """Inicia una conversación interactiva con SuperNova."""
    typer.secho(
        f"\n🌟 Bienvenido a SuperNova ({settings.MODEL_NAME}). Escribe 'salir' para terminar.\n",
        fg="cyan",
        bold=True,
    )
    chat_history: List[Dict[str, str]] = []

    while True:
        # FIX: manejar Ctrl+C con mensaje limpio en lugar de traceback
        try:
            user_input = typer.prompt("\n👤 Tú")
        except (KeyboardInterrupt, EOFError):
            typer.secho("\n\n👋 ¡Hasta pronto!", fg="yellow")
            break

        if user_input.lower() in ["salir", "exit", "q", "quit"]:
            typer.secho("\n👋 ¡Hasta pronto!", fg="yellow")
            break

        if not user_input.strip():
            continue

        try:
            response = run_agent(user_input, chat_history)
            typer.secho("\n🤖 SuperNova:", fg="cyan", bold=True)
            typer.echo(response)

            # Actualizar historial
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response})

            # FIX: Limitar historial para evitar contextos excesivos en Ollama
            # Mantener solo los últimos MAX_HISTORY_TURNS pares (cada par = 2 entradas)
            max_entries = MAX_HISTORY_TURNS * 2
            if len(chat_history) > max_entries:
                chat_history = chat_history[-max_entries:]

        except KeyboardInterrupt:
            typer.secho("\n\n👋 ¡Hasta pronto!", fg="yellow")
            break
        except Exception as e:
            typer.secho(f"\n❌ Error: {e}", fg="red", err=True)
            # No romper el loop — el usuario puede seguir conversando


if __name__ == "__main__":
    app()
