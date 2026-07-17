"""
Entry point de la API FastAPI para AlurAgente.
Expone los endpoints POST /preguntar y GET /health.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agent import get_respuesta, initialize_agent
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
    logger.info("AlurAgente listo.")
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
    try:
        respuesta = get_respuesta(request.sesion_id, request.pregunta)
        return RespuestaResponse(respuesta=respuesta)

    except Exception as exc:
        mensaje = str(exc).lower()
        # Errores de la API de Google (clave inválida, cuota, etc.)
        if any(kw in mensaje for kw in ("api key", "quota", "google", "credentials", "permission")):
            raise HTTPException(
                status_code=503,
                detail="El servicio de IA no está disponible temporalmente.",
            )
        logger.exception("Error interno al procesar la consulta.")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {exc}",
        )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Verifica que el servicio está en funcionamiento."""
    return HealthResponse(status="ok")
