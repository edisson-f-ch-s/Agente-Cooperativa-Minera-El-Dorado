"""
Modelos Pydantic para request/response de la API de AlurAgente.
"""
from pydantic import BaseModel, field_validator


class PreguntaRequest(BaseModel):
    """Request body para el endpoint POST /preguntar."""
    sesion_id: str
    pregunta: str

    @field_validator("sesion_id", "pregunta")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v


class RespuestaResponse(BaseModel):
    """Response body del endpoint POST /preguntar."""
    respuesta: str


class HealthResponse(BaseModel):
    """Response body del endpoint GET /health."""
    status: str = "ok"
