# cli/main.py
import typer
import sys
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

app = typer.Typer(help="🌟 SuperNova - Tu Asistente IA Personal (Modo COO)")

def get_llm():
    """Configura y verifica la conexión con el modelo local"""
    try:
        from ollama import Client
        client = Client(host='http://localhost:11434')
        client.list()  # Verifica que Ollama esté corriendo
        # Usamos qwen2.5:7b por estabilidad actual. Puedes cambiarlo cuando qwen3.6 esté disponible
        return OllamaLLM(model="qwen2.5:7b", temperature=0.3)
    except Exception as e:
        typer.secho(f"❌ Error al conectar con Ollama: {e}", fg="red", err=True)
        typer.secho("💡 Asegúrate de tener Ollama instalado y ejecutándose: `ollama serve`", fg="yellow")
        sys.exit(1)

@app.command()
def ask(query: str = typer.Argument(..., help="Tu pregunta o instrucción para SuperNova")):
    """Hazle una pregunta o dale una tarea puntual a SuperNova"""
    typer.secho("\n🤖 SuperNova: Procesando tu solicitud...", fg="cyan")
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres SuperNova, asistente IA personal (Modo COO/Operator).
        Responde en español. Sé eficiente, claro y proactivo.
        Si es una tarea, divídela en pasos accionables.
        Si falta información, pide solo lo necesario.
        Mantén un tono profesional pero cercano."""),
        ("user", "{query}")
    ])

    chain = prompt | llm
    try:
        response = chain.invoke({"query": query})
        typer.secho("\n✨ Respuesta:", fg="green", bold=True)
        typer.echo(response)
    except Exception as e:
        typer.secho(f"❌ Error al generar respuesta: {e}", fg="red", err=True)

@app.command()
def chat():
    """Inicia una conversación interactiva con SuperNova"""
    typer.secho("🌟 Bienvenido a SuperNova. Escribe 'salir' para terminar.\n", fg="cyan", bold=True)
    llm = get_llm()
    history = []

    while True:
        user_input = typer.prompt("\n👤 Tú")
        if user_input.lower() in ["salir", "exit", "q"]:
            typer.secho("👋 ¡Hasta pronto!", fg="yellow")
            break
        if not user_input.strip():
            continue

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Eres SuperNova, COO/Operator personal.
            Responde en español. Sé conciso y orientado a resultados.
            Contexto reciente: {history[-2:] if history else 'Primera interacción'}"""),
            ("user", "{query}")
        ])

        chain = prompt | llm
        try:
            response = chain.invoke({"query": user_input})
            typer.secho(f"\n🤖 SuperNova:", fg="cyan")
            typer.echo(response)
            history.append({"role": "assistant", "content": response})
        except Exception as e:
            typer.secho(f"❌ Error: {e}", fg="red", err=True)

if __name__ == "__main__":
    app()
