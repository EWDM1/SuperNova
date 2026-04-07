# core/agent.py
import os
from datetime import datetime
from typing import List, Dict
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
import chromadb
from langchain_ollama import OllamaEmbeddings

# ==========================================
# 🧠 CONFIGURACIÓN DE MEMORIA (ChromaDB)
# ==========================================
def get_vector_memory():
    """Inicializa o conecta a la base de datos vectorial local"""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    client = chromadb.PersistentClient(path="./memory/chroma_db")
    return chromadb.Collection(client.get_or_create_collection(name="supernova_memory", embedding_function=embeddings))

# ==========================================
# 🛠️ HERRAMIENTAS DEL AGENTE
# ==========================================
@tool
def save_memory(content: str, topic: str = "general") -> str:
    """Guarda información importante para recordar más tarde."""
    try:
        memory = get_vector_memory()
        memory.add(
            documents=[content],
            metadatas=[{"topic": topic, "saved_at": datetime.now().isoformat()}]
        )
        return f"✅ Información guardada bajo '{topic}'. Podré recordarla cuando la necesites."
    except Exception as e:
        return f"⚠️ No se pudo guardar la nota: {e}"

@tool
def recall_memory(query: str) -> str:
    """Busca información guardada previamente sobre un tema."""
    try:
        memory = get_vector_memory()
        results = memory.query(query_texts=[query], n_results=3)
        if not results["documents"] or not results["documents"][0]:
            return "🤔 No encontré información guardada sobre eso."
        return "\n".join([f"- {doc}" for doc in results["documents"][0]])
    except Exception as e:
        return f"⚠️ No se pudo recuperar información: {e}"

# ==========================================
# 🤖 CONFIGURACIÓN DEL LLM & AGENTE
# ==========================================
def get_llm():
    """Devuelve el modelo de IA configurado para razonamiento y herramientas"""
    return OllamaLLM(
        model="qwen2.5:7b",
        temperature=0.3,
        format="json"  # Ayuda a estructurar respuestas de herramientas
    )

def create_coo_agent():
    """Crea y devuelve el agente principal tipo COO"""
    llm = get_llm()
    tools = [save_memory, recall_memory]

    # Prompt maestro con instrucciones de comportamiento
    system_prompt = """Eres SuperNova, asistente COO/Operator personal.
- Responde SIEMPRE en español.
- Sé eficiente, claro y orientado a la acción.
- Si el usuario pide guardar información, usa `save_memory`.
- Si pregunta por algo del pasado, usa `recall_memory`.
- Si no sabes algo, dilo claramente y sugiere cómo resolverlo.
- Mantén un tono profesional pero cercano. No uses lenguaje técnico innecesario."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Agente moderno con soporte de herramientas
    agent = prompt | llm.bind_tools(tools)
    return agent, tools

# ==========================================
# 🚀 FUNCIÓN DE EJECUCIÓN (Para CLI y API)
# ==========================================
def run_agent(query: str, chat_history: List[Dict] = []):
    """Ejecuta una consulta a través del agente COO"""
    agent, tools = create_coo_agent()
    
    try:
        # En una versión completa aquí iría el bucle de llamada a herramientas
        # Para esta fase estable, usamos respuesta directa con contexto
        history_context = "\n".join([f"{h['role']}: {h['content']}" for h in chat_history[-3:]])
        full_prompt = f"{query}\n\n(Contexto reciente: {history_context})"
        
        response = agent.invoke({"input": full_prompt, "chat_history": chat_history})
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        return f"❌ El agente encontró un error: {e}"
