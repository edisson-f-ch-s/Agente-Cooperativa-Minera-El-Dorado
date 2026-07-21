"""
Configuración de modelos Gemini para AlurAgente.

Prioriza modelos estables con capa gratuita vigente (julio 2026) y ofrece
fallback automático cuando un modelo quedó deprecado o no está disponible
para cuentas nuevas.

Referencia: https://ai.google.dev/gemini-api/docs/models
"""
import os

# Modelo principal: mejor balance calidad/cuota para tool-calling (agente).
# gemini-3.5-flash está disponible en la capa gratuita (jul 2026).
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"

# Orden de fallback: probados y disponibles en la capa gratuita.
# gemini-3.1-flash-lite: alternativa más liviana disponible en capa gratuita.
FALLBACK_GEMINI_MODELS = (
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
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
    Detecta errores de modelo inexistente o deprecado.
    Compatible con el antiguo SDK (HTTP 404) y el nuevo google-genai SDK.
    """
    message = str(exc).lower()
    return (
        "404" in message
        or "not found" in message
        or "no longer available" in message
        or "is not supported for generatecontent" in message
        # Formato del nuevo SDK google-genai (ClientError/NotFound)
        or "not_found" in message
        or "model_not_found" in message
    )


def is_quota_error(exc: Exception) -> bool:
    """
    Detecta errores de cuota, rate limit o credenciales de la API.
    Compatible con el antiguo SDK (gRPC ResourceExhausted) y el nuevo
    google-genai SDK (ClientError 429 RESOURCE_EXHAUSTED).
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
