"""
Agente LangChain con tool-calling para AlurAgente.
Orquesta las 6 tools sobre datos CSV y RAG de PDFs usando Gemini.
"""
import logging
from typing import Any

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from app.gemini_config import (
    get_model_candidates,
    is_model_unavailable_error,
    is_quota_error,
)
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
_active_model: str | None = None

# Historial de mensajes por sesión: list de HumanMessage / AIMessage.
# Se mantiene en memoria del proceso — suficiente para una evaluación de challenge
# donde los pods no escalan horizontalmente.
_session_histories: dict[str, list[BaseMessage]] = {}


# ── Construcción del agente ───────────────────────────────────────────────────

def _build_agent(model: str) -> AgentExecutor:
    """
    Construye el AgentExecutor con LangChain y el modelo Gemini indicado.
    """
    llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0,
        max_retries=1,
    )

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

    logger.info("AgentExecutor construido con %d tools usando %s.", len(TOOLS), model)
    return executor


def _probe_model(model: str) -> None:
    """
    Verifica que el modelo responde antes de usarlo en producción.
    Solo detecta errores de modelo no existente (404); los errores de cuota
    se ignoran aquí porque el agente debe arrancar aunque la cuota esté agotada.
    """
    llm = ChatGoogleGenerativeAI(model=model, temperature=0, max_retries=0)
    try:
        llm.invoke("Responde exactamente: OK")
    except Exception as exc:
        # Re-lanzar solo si el modelo no existe; la cuota agotada no impide el arranque.
        if not is_quota_error(exc):
            raise
        logger.warning(
            "Cuota agotada durante probe de %s — el agente arrancará de todas formas. "
            "Las consultas fallarán hasta que la cuota se restaure.",
            model,
        )


def _initialize_with_fallback() -> tuple[AgentExecutor, str]:
    """
    Selecciona el primer modelo disponible de la lista de candidatos.
    Si la cuota está agotada, el agente se construye igualmente para que el
    servidor arranque y retorne mensajes de error descriptivos en cada consulta.
    """
    errors: list[str] = []

    for model in get_model_candidates():
        try:
            _probe_model(model)
            executor = _build_agent(model)
            if model != get_model_candidates()[0]:
                logger.warning(
                    "Modelo configurado no disponible. Usando fallback: %s",
                    model,
                )
            return executor, model
        except Exception as exc:
            if is_model_unavailable_error(exc):
                errors.append(f"{model}: no disponible")
                logger.warning("Modelo %s no disponible: %s", model, exc)
                continue
            raise

    detail = "; ".join(errors) if errors else "sin modelos configurados"
    raise RuntimeError(
        "Ningún modelo Gemini disponible. "
        f"Detalle: {detail}. "
        "Use GEMINI_MODEL=gemini-3.5-flash o gemini-3.1-flash-lite."
    )


def initialize_agent() -> None:
    """Inicializa el singleton del AgentExecutor. Llamar desde el lifespan de FastAPI."""
    global _agent_executor, _active_model
    _agent_executor, _active_model = _initialize_with_fallback()


def get_active_model() -> str | None:
    """Devuelve el modelo Gemini activo en esta instancia."""
    return _active_model


def _ensure_agent_ready() -> AgentExecutor:
    global _agent_executor

    if _agent_executor is None:
        logger.warning("AgentExecutor no inicializado. Construyendo ahora...")
        initialize_agent()

    assert _agent_executor is not None
    return _agent_executor


def _retry_with_next_model(exc: Exception) -> AgentExecutor | None:
    """
    Si el modelo activo quedó deprecado en caliente, reconstruye con el siguiente candidato.
    """
    global _agent_executor, _active_model

    if not is_model_unavailable_error(exc) or _active_model is None:
        return None

    candidates = get_model_candidates()
    try:
        current_index = candidates.index(_active_model)
    except ValueError:
        current_index = -1

    for model in candidates[current_index + 1:]:
        try:
            logger.warning("Reintentando con modelo de respaldo: %s", model)
            _probe_model(model)
            _agent_executor = _build_agent(model)
            _active_model = model
            return _agent_executor
        except Exception as fallback_exc:
            if is_model_unavailable_error(fallback_exc):
                logger.warning("Fallback %s tampoco disponible: %s", model, fallback_exc)
                continue
            raise

    return None


# ── Gestión de historial por sesión ──────────────────────────────────────────

# Máximo de intercambios a retener en memoria por sesión.
_MAX_HISTORY_TURNS = 10


def _get_history(sesion_id: str) -> list[BaseMessage]:
    """Devuelve el historial de mensajes de la sesión, creándolo si no existe."""
    if sesion_id not in _session_histories:
        _session_histories[sesion_id] = []
        logger.debug("Nueva sesión creada: %s", sesion_id)
    return _session_histories[sesion_id]


def _append_to_history(sesion_id: str, pregunta: str, respuesta: str) -> None:
    """Agrega el último intercambio al historial, recortando si supera el límite."""
    historial = _get_history(sesion_id)
    historial.append(HumanMessage(content=pregunta))
    historial.append(AIMessage(content=respuesta))

    # Mantener solo los últimos N intercambios (1 intercambio = 2 mensajes)
    max_messages = _MAX_HISTORY_TURNS * 2
    if len(historial) > max_messages:
        _session_histories[sesion_id] = historial[-max_messages:]


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
    executor = _ensure_agent_ready()
    historial = _get_history(sesion_id)

    try:
        resultado: dict[str, Any] = executor.invoke({
            "input": pregunta,
            "chat_history": historial,
        })
    except Exception as exc:
        fallback_executor = _retry_with_next_model(exc)
        if fallback_executor is None:
            if is_quota_error(exc):
                raise RuntimeError(
                    "Cuota de la API de Gemini agotada temporalmente. "
                    "Espere unos minutos o verifique los límites en Google AI Studio."
                ) from exc
            raise

        resultado = fallback_executor.invoke({
            "input": pregunta,
            "chat_history": historial,
        })

    respuesta: str = resultado.get("output", "No pude generar una respuesta.")
    _append_to_history(sesion_id, pregunta, respuesta)
    return respuesta
