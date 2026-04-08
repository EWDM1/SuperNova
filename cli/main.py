import typer
import sys
from typing import List, Dict

# Importar el agente central y la configuración
from core.agent import run_agent
from config.settings import settings

app = typer.Typer(help="🌟 SuperNova - Tu Asistente IA Personal (Modo COO)")

@app.command()
def ask(query: str = typer.Argument(..., help="Tu pregunta o instrucción para SuperNova")):
    """Hazle una pregunta o dale una tarea puntual a SuperNova"""
    typer.secho("\n🤖 SuperNova: Procesando tu solicitud...", fg="cyan")
    try:
        response = run_agent(query)
        typer.secho("\n✨ Respuesta:", fg="green", bold=True)
        typer.echo(response)
    except Exception as e:
        typer.secho(f"❌ Error al generar respuesta: {e}", fg="red", err=True)

@app.command()
def chat():
    """Inicia una conversación interactiva con SuperNova"""
    typer.secho("🌟 Bienvenido a SuperNova. Escribe 'salir' para terminar.\n", fg="cyan", bold=True)
    chat_history: List[Dict[str, str]] = []

    while True:
        user_input = typer.prompt("\n👤 Tú")
        if user_input.lower() in ["salir", "exit", "q"]:
            typer.secho("👋 ¡Hasta pronto!", fg="yellow")
            break
        if not user_input.strip():
            continue

        try:
            response = run_agent(user_input, chat_history)
            typer.secho(f"\n🤖 SuperNova:", fg="cyan")
            typer.echo(response)
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            typer.secho(f"❌ Error: {e}", fg="red", err=True)

if __name__ == "__main__":
    app()
