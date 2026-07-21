"""
Entry point de la API FastAPI para AlurAgente.
Expone los endpoints POST /preguntar y GET /health.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agent import get_active_model, get_respuesta, initialize_agent
from app.gemini_config import is_model_unavailable_error, is_quota_error
from app.rate_limit import get_rate_limiter
from app.schemas import HealthResponse, PreguntaRequest, RespuestaResponse
from app.vectorstore import get_vectorstore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan: startup / shutdown ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa el vectorstore FAISS y el AgentExecutor al arrancar el servidor."""
    logger.info("Iniciando AlurAgente...")
    get_vectorstore()       # Carga o construye el índice FAISS
    initialize_agent()      # Construye el AgentExecutor con las 6 tools
    logger.info("AlurAgente listo. Modelo activo: %s", get_active_model())
    yield
    logger.info("AlurAgente detenido.")


# ── Aplicación FastAPI ────────────────────────────────────────────────────────

app = FastAPI(
    title="AlurAgente API",
    description="Agente conversacional para la Cooperativa Minera El Dorado",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/preguntar", response_model=RespuestaResponse)
async def preguntar(request: PreguntaRequest) -> RespuestaResponse:
    """
    Recibe una pregunta en lenguaje natural y devuelve la respuesta del agente.
    """
    allowed, limit_message = get_rate_limiter().check()
    if not allowed:
        raise HTTPException(status_code=429, detail=limit_message)

    try:
        respuesta = get_respuesta(request.sesion_id, request.pregunta)
        return RespuestaResponse(respuesta=respuesta)

    except RuntimeError as exc:
        mensaje = str(exc)
        if is_quota_error(exc) or "cuota" in mensaje.lower():
            raise HTTPException(
                status_code=503,
                detail=(
                    "El servicio de IA alcanzó el límite de uso de la capa gratuita. "
                    "Espere unos minutos e intente de nuevo. "
                    "Para evaluación del challenge, una clave gratuita de Google AI Studio "
                    "es suficiente con uso moderado."
                ),
            )
        if "ningún modelo gemini disponible" in mensaje.lower():
            raise HTTPException(
                status_code=503,
                detail=(
                    "No hay un modelo Gemini disponible. Configure "
                    "GEMINI_MODEL=gemini-2.0-flash (recomendado) o "
                    "gemini-1.5-flash en su archivo .env."
                ),
            )
        logger.exception("Error de configuración del agente.")
        raise HTTPException(status_code=503, detail=mensaje)

    except Exception as exc:
        if is_quota_error(exc):
            raise HTTPException(
                status_code=503,
                detail=(
                    "El servicio de IA alcanzó el límite de uso de la capa gratuita. "
                    "Espere unos minutos e intente de nuevo."
                ),
            )
        if is_model_unavailable_error(exc):
            raise HTTPException(
                status_code=503,
                detail=(
                    "El modelo Gemini configurado ya no está disponible. "
                    "Actualice GEMINI_MODEL a gemini-2.0-flash o reinicie el backend "
                    "para activar el fallback automático."
                ),
            )
        logger.exception("Error interno al procesar la consulta.")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al procesar la consulta.",
        )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Verifica que el servicio y el agente están operativos."""
    modelo = get_active_model()
    return HealthResponse(
        status="ok" if modelo else "degraded",
        agente_listo=modelo is not None,
        modelo_activo=modelo,
    )
