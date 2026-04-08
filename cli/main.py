# cli/main.py
import typer
import sys
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from config.settings import settings, logger

app = typer.Typer(help="🌟 SuperNova - Tu Asistente IA Personal (Modo COO)")

def get_llm():
    try:
        from ollama import Client
        client = Client(host=settings.OLLAMA_HOST)
        client.list()
        return OllamaLLM(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE)
    except Exception as e:
        logger.error(f"Error conectando a Ollama: {e}")
        typer.secho(f"❌ Error al conectar con Ollama: {e}", fg="red", err=True)
        typer.secho("💡 Asegúrate de que Ollama esté corriendo: `ollama serve`", fg="yellow")
        sys.exit(1)

@app.command()
def ask(query: str = typer.Argument(..., help="Tu pregunta o instrucción")):
    """Consulta única a SuperNova"""
    typer.secho("\n🤖 SuperNova: Procesando...", fg="cyan")
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres SuperNova, COO/Operator personal. Responde en español. Sé eficiente y orientado a la acción."),
        ("user", "{query}")
    ])
    try:
        response = (prompt | llm).invoke({"query": query})
        typer.secho("\n✨ Respuesta:", fg="green", bold=True)
        typer.echo(response)
    except Exception as e:
        logger.error(f"Error en ask: {e}")
        typer.secho(f"❌ Error: {e}", fg="red")

@app.command()
def chat():
    """Conversación interactiva"""
    typer.secho("🌟 Bienvenido a SuperNova. Escribe 'salir' para terminar.\n", fg="cyan", bold=True)
    llm = get_llm()
    history = []
    while True:
        user_input = typer.prompt("\n👤 Tú")
        if user_input.lower() in ["salir", "exit", "q"]: break
        if not user_input.strip(): continue

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"Eres SuperNova, COO/Operator. Responde en español. Contexto: {history[-2:] if history else 'Primera interacción'}"),
            ("user", "{query}")
        ])
        try:
            response = (prompt | llm).invoke({"query": user_input})
            typer.secho(f"\n🤖 SuperNova:", fg="cyan")
            typer.echo(response)
            history.append({"role": "assistant", "content": response})
        except Exception as e:
            logger.error(f"Error en chat: {e}")
            typer.secho(f"❌ Error: {e}", fg="red")

if __name__ == "__main__":
    app()
