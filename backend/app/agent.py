"""
Agente LangChain con tool-calling para AlurAgente.
Orquesta las 6 tools sobre datos CSV y RAG de PDFs usando Gemini 2.0 Flash.
"""
import logging
from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools import (
    buscar_en_documentos,
    consultar_asistencia,
    consultar_cargas,
    consultar_grupo_inspector,
    consultar_incidencias,
    consultar_molinos,
)

logger = logging.getLogger(__name__)

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres AlurAgente, el asistente de IA de la Cooperativa Minera El Dorado, \
especializado en el Área de Acopio de Material Aurífero.

Tu función es responder preguntas de supervisores, inspectores y administrativos sobre:
- Asistencia del personal y cumplimiento de EPP
- Estado y seguimiento de cargas de material aurífero
- Incidencias registradas (trabajadores, transportistas, molinos)
- Estado y capacidad de molinos/trapiches
- Grupos de inspectores, rotación y molinos asignados
- Procedimientos, normas y políticas internas (documentos PDF)

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE con base en los resultados que devuelvan las herramientas disponibles.
2. Si una herramienta no devuelve datos relevantes, declara explícitamente que no tienes esa información.
3. NUNCA inventes datos, nombres, fechas, cantidades ni estados.
4. Si la pregunta no corresponde al ámbito de la Cooperativa Minera El Dorado, explica amablemente que solo puedes responder sobre esa temática.
5. Responde siempre en español, de forma clara y concisa.
6. Cuando los datos sean extensos, presenta un resumen y los puntos más importantes."""

# ── Herramientas registradas ──────────────────────────────────────────────────

TOOLS = [
    consultar_asistencia,
    consultar_cargas,
    consultar_incidencias,
    consultar_molinos,
    consultar_grupo_inspector,
    buscar_en_documentos,
]

# ── Estado global del proceso ─────────────────────────────────────────────────

_agent_executor: AgentExecutor | None = None
_session_memories: dict[str, ConversationBufferWindowMemory] = {}


# ── Construcción del agente ───────────────────────────────────────────────────

def _build_agent() -> AgentExecutor:
    """
    Construye el AgentExecutor con LangChain y Gemini 2.0 Flash.
    Se invoca una sola vez durante el startup del servidor.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )

    logger.info("AgentExecutor construido con %d tools.", len(TOOLS))
    return executor


def initialize_agent() -> None:
    """Inicializa el singleton del AgentExecutor. Llamar desde el lifespan de FastAPI."""
    global _agent_executor
    _agent_executor = _build_agent()


# ── Gestión de memoria por sesión ─────────────────────────────────────────────

def _get_or_create_memory(sesion_id: str) -> ConversationBufferWindowMemory:
    """
    Devuelve la memoria de la sesión indicada, creándola si no existe.
    Conserva los últimos 10 intercambios (k=10).
    """
    if sesion_id not in _session_memories:
        _session_memories[sesion_id] = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="chat_history",
        )
        logger.debug("Nueva sesión creada: %s", sesion_id)
    return _session_memories[sesion_id]


# ── Función principal de consulta ─────────────────────────────────────────────

def get_respuesta(sesion_id: str, pregunta: str) -> str:
    """
    Procesa una pregunta del usuario y devuelve la respuesta del agente.

    Args:
        sesion_id: Identificador único de la sesión del usuario.
        pregunta: Pregunta en lenguaje natural.

    Returns:
        Respuesta del agente como string.
    """
    global _agent_executor

    if _agent_executor is None:
        # Fallback si se llama fuera del contexto de FastAPI (ej: test_local.py)
        logger.warning("AgentExecutor no inicializado. Construyendo ahora...")
        _agent_executor = _build_agent()

    memoria = _get_or_create_memory(sesion_id)
    historial = memoria.chat_memory.messages

    resultado: dict[str, Any] = _agent_executor.invoke({
        "input": pregunta,
        "chat_history": historial,
    })

    respuesta: str = resultado.get("output", "No pude generar una respuesta.")

    # Guardar el par (pregunta, respuesta) en la memoria de la sesión
    memoria.chat_memory.add_user_message(pregunta)
    memoria.chat_memory.add_ai_message(respuesta)

    return respuesta
