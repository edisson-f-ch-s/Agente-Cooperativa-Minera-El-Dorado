"""
Configuración de modelos Gemini para AlurAgente.

Estrategia de selección:
- Primary: gemini-2.0-flash  → 1500 RPD en free tier, estable, excelente para tool-calling
- Fallback 1: gemini-1.5-flash → 1500 RPD en free tier, muy estable
- Fallback 2: gemini-2.5-flash → 500 RPD, mayor calidad de razonamiento
- Last resort: gemini-3.5-flash → solo 20 RPD (preview), evitar como default

Referencia de límites: https://ai.google.dev/gemini-api/docs/rate-limits
"""
import os

# gemini-2.0-flash: el mejor balance cuota/calidad para tool-calling en free tier (jul 2026).
# 1500 RPD, thought_signature manejado nativamente por langchain-google-genai >=4.0.
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"

# Orden de fallback: modelos activos compatibles en la plataforma.
FALLBACK_GEMINI_MODELS = (
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
)


def get_configured_model() -> str:
    """Devuelve el modelo solicitado por entorno o el default del proyecto."""
    return os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()


def get_model_candidates() -> list[str]:
    """
    Lista de modelos a probar en orden.
    El configurado va primero; luego se agregan fallbacks sin duplicar.
    """
    configured = get_configured_model()
    candidates = [configured]
    for model in FALLBACK_GEMINI_MODELS:
        if model not in candidates:
            candidates.append(model)
    return candidates


def is_model_unavailable_error(exc: Exception) -> bool:
    """
    Detecta errores de modelo inexistente, deprecado o no disponible temporalmente (503).
    """
    message = str(exc).lower()
    return (
        "404" in message
        or "503" in message
        or "not found" in message
        or "no longer available" in message
        or "is not supported for generatecontent" in message
        or "not_found" in message
        or "model_not_found" in message
        or "unavailable" in message
    )


def is_quota_error(exc: Exception) -> bool:
    """
    Detecta errores de cuota, rate limit o credenciales de la API.
    Compatible con gRPC ResourceExhausted (SDK antiguo) y ClientError 429 (nuevo).
    """
    message = str(exc).lower()
    return any(
        keyword in message
        for keyword in (
            "api key",
            "quota",
            "credentials",
            "permission",
            "resourceexhausted",
            "resource_exhausted",
            "rate limit",
            "rate_limit",
            "429",
            "billing",
        )
    )
