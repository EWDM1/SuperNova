# core/agent.py
import os, logging
from datetime import datetime
from typing import List, Dict
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
import chromadb
from config.settings import settings, logger
from core.tools import ALL_TOOLS

logger = logging.getLogger("supernova.agent")

def get_vector_memory():
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=settings.OLLAMA_HOST)
    client = chromadb.PersistentClient(path=str(settings.MEMORY_PATH / "chroma_db"))
    return client.get_or_create_collection(name="supernova_memory", embedding_function=embeddings)

@tool
def save_memory(content: str, topic: str = "general") -> str:
    try:
        memory = get_vector_memory()
        memory.add(documents=[content], metadatas=[{"topic": topic, "saved_at": datetime.now().isoformat()}])
        logger.info(f"Memoria guardada: {topic}")
        return f"✅ Información guardada bajo '{topic}'."
    except Exception as e:
        logger.error(f"Error guardando memoria: {e}")
        return f"⚠️ Error al guardar: {e}"

@tool
def recall_memory(query: str) -> str:
    try:
        memory = get_vector_memory()
        results = memory.query(query_texts=[query], n_results=3)
        if not results["documents"][0]: return "🤔 No encontré información previa."
        return "\n".join([f"- {doc}" for doc in results["documents"][0]])
    except Exception as e:
        logger.error(f"Error recuperando memoria: {e}")
        return f"⚠️ Error al recuperar: {e}"

def create_coo_agent():
    llm = OllamaLLM(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE, base_url=settings.OLLAMA_HOST)
    # Combina herramientas base + registry
    tools = [save_memory, recall_memory] + ALL_TOOLS
    system_prompt = """Eres SuperNova, COO/Operator personal. Responde SIEMPRE en español.
    Sé eficiente, claro y orientado a la acción. Usa las herramientas disponibles.
    Si no sabes algo, dilo y sugiere alternativas."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    return prompt | llm.bind_tools(tools), tools

def run_agent(query: str, chat_history: List[Dict] = []):
    agent, _ = create_coo_agent()
    try:
        history_ctx = "\n".join([f"{h['role']}: {h['content']}" for h in chat_history[-3:]])
        return agent.invoke({"input": f"{query}\n(Contexto: {history_ctx})", "chat_history": chat_history})
    except Exception as e:
        logger.critical(f"Fallo crítico en agente: {e}")
        return f"❌ El agente encontró un error: {e}"
