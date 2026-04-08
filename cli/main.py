# cli/main.py
import typer
import sys
import logging
from config.settings import settings, logger

app = typer.Typer(help="🌟 SuperNova - Tu Asistente IA Personal (Modo COO)")

def get_llm():
    try:
        from langchain_ollama import OllamaLLM
        from ollama import Client
        client = Client(host=settings.OLLAMA_HOST)
        client.list()
        return OllamaLLM(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE, base_url=settings.OLLAMA_HOST)
    except Exception as e:
        logger.error(f"Error conectando a Ollama: {e}")
        typer.secho(f"❌ Error al conectar con Ollama: {e}", fg="red", err=True)
        typer.secho("💡 Asegúrate de que Ollama esté corriendo: `ollama serve`", fg="yellow")
        sys.exit(1)

@app.command()
def ask(query: str = typer.Argument(..., help="Tu pregunta o instrucción")):
    """Consulta única a SuperNova"""
    typer.secho("\n🤖 SuperNova: Procesando...", fg="cyan")
    try:
        from core.agent import run_agent
        # ✅ CORREGIDO: chat_history=[] en vez de history=[]
        response = run_agent(query, chat_history=[])
        typer.secho("\n✨ Respuesta:", fg="green", bold=True)
        typer.echo(response)
    except ImportError as e:
        logger.error(f"Error de importación: {e}")
        typer.secho(f"❌ Error: Módulo no encontrado. Ejecuta ./install.sh primero.", fg="red")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error en ask: {e}")
        typer.secho(f"❌ Error: {e}", fg="red")

@app.command()
def chat():
    """Conversación interactiva"""
    typer.secho("🌟 Bienvenido a SuperNova. Escribe 'salir' para terminar.\n", fg="cyan", bold=True)
    try:
        from core.agent import run_agent
    except ImportError as e:
        logger.error(f"Error de importación: {e}")
        typer.secho(f"❌ Error: Ejecuta ./install.sh primero.", fg="red")
        sys.exit(1)
    
    history = []
    while True:
        try:
            user_input = typer.prompt("\n👤 Tú")
            if user_input.lower() in ["salir", "exit", "q"]:
                typer.secho("👋 ¡Hasta pronto!", fg="yellow")
                break
            if not user_input.strip():
                continue

            # ✅ CORREGIDO: historial limitado a últimos 5 mensajes
            response = run_agent(user_input, chat_history=history[-5:])
            typer.secho(f"\n🤖 SuperNova:", fg="cyan")
            typer.echo(response)
            history.append({"role": "assistant", "content": response})
        except KeyboardInterrupt:
            typer.secho("\n🛑 Interrumpido por usuario.", fg="yellow")
            break
        except Exception as e:
            logger.error(f"Error en chat: {e}")
            typer.secho(f"❌ Error: {e}", fg="red")

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        typer.secho("\n👋 Detenido por usuario.", fg="yellow")
        sys.exit(0)
