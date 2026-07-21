"""
Frontend Streamlit para AlurAgente — Cooperativa Minera El Dorado.
Se comunica exclusivamente por HTTP con el backend FastAPI.
"""
import os
import uuid

import requests
import streamlit as st

# ── Configuración ─────────────────────────────────────────────────────────────

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 90  # segundos — el agente puede tardar si usa varias tools

st.set_page_config(
    page_title="AlurAgente — Cooperativa Minera El Dorado",
    page_icon="⛏️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ─────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Cabecera */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #e2b04020;
    }
    .main-header h1 { color: #e2b040; margin: 0; font-size: 1.8rem; }
    .main-header p  { color: #a0aec0; margin: 0.3rem 0 0; font-size: 0.9rem; }

    /* Ejemplos de consulta */
    .ejemplo-btn {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        color: #94a3b8;
        font-size: 0.8rem;
        cursor: pointer;
        width: 100%;
        text-align: left;
        margin-bottom: 0.4rem;
    }

    /* Badge del modelo activo */
    .model-badge {
        background: #064e3b;
        color: #6ee7b7;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ── Inicialización de estado de sesión ────────────────────────────────────────

if "sesion_id" not in st.session_state:
    st.session_state.sesion_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_info" not in st.session_state:
    st.session_state.model_info = None

# ── Cabecera ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>⛏️ AlurAgente</h1>
    <p>Asistente de IA · Cooperativa Minera El Dorado · Área de Acopio de Material Aurífero</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🔧 Estado del sistema")

    # Verificar salud del backend
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health.status_code == 200:
            data = health.json()
            st.success("✅ Backend conectado")
            model = data.get("modelo_activo", "desconocido")
            st.markdown(f'Modelo activo: <span class="model-badge">{model}</span>', unsafe_allow_html=True)
            st.session_state.model_info = model
        else:
            st.error("⚠️ Backend con errores")
    except Exception:
        st.error("❌ Backend no disponible")
        st.info("Verifica que el servidor esté corriendo en:\n`" + BACKEND_URL + "`")

    st.divider()

    st.markdown("### 💬 Nueva sesión")
    if st.button("🔄 Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sesion_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    st.markdown("### 📋 Ejemplos de consultas")

    ejemplos = [
        "¿Cuántos trabajadores faltaron esta semana?",
        "Incidencias de alta severidad pendientes",
        "¿Qué molinos requieren reevaluación?",
        "¿A qué grupo pertenece INS-005 en julio?",
        "Cargas asignadas al molino M-03",
        "Requisitos de EPP según el protocolo",
    ]

    for ejemplo in ejemplos:
        if st.button(ejemplo, use_container_width=True, key=f"ej_{ejemplo[:20]}"):
            st.session_state["_pregunta_pendiente"] = ejemplo
            st.rerun()

    st.divider()
    st.markdown(
        '<p style="font-size:0.7rem;color:#64748b;text-align:center;">'
        'AlurAgente · Challenge Alura Latam 2026<br>'
        f'Sesión: <code>{st.session_state.sesion_id[:8]}…</code>'
        '</p>',
        unsafe_allow_html=True,
    )

# ── Función de comunicación con el backend ────────────────────────────────────

def _llamar_backend(pregunta: str) -> str:
    """Envía la pregunta al backend y devuelve la respuesta del agente."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/preguntar",
            json={
                "sesion_id": st.session_state.sesion_id,
                "pregunta": pregunta,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("respuesta", "Sin respuesta del servidor.")

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return (
            "⚠️ **No se pudo conectar con el servidor.**\n\n"
            "Verifica que el backend esté en ejecución e intenta nuevamente."
        )
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        detalle = ""
        if exc.response is not None:
            try:
                detalle = exc.response.json().get("detail", "")
            except ValueError:
                pass
        if status == 429:
            return (
                "⚠️ **Límite de consultas alcanzado.**\n\n"
                "La API de Gemini tiene una cuota gratuita de 1500 req/día. "
                "Espera unos minutos o verifica tu cuota en [Google AI Studio](https://ai.dev/rate-limit)."
            )
        if status == 503:
            return (
                "⚠️ **El agente no está listo todavía.**\n\n"
                "El servidor está inicializando. Espera 30 segundos y reintenta."
            )
        return f"⚠️ {detalle or f'Error del servidor ({status}). Intenta nuevamente.'}"
    except Exception:
        return "⚠️ **Error inesperado.** Intenta nuevamente en unos momentos."


# ── Renderizar historial de conversación ──────────────────────────────────────

if not st.session_state.messages:
    st.markdown(
        '<p style="color:#64748b;text-align:center;padding:2rem 0;">'
        '👋 Hola, soy AlurAgente. Puedes preguntarme sobre asistencia, cargas, '
        'incidencias, molinos o consultar los documentos del área de acopio.</p>',
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Manejar pregunta pendiente desde el sidebar ───────────────────────────────

pregunta_sidebar = st.session_state.pop("_pregunta_pendiente", None)

# ── Input del usuario ─────────────────────────────────────────────────────────

pregunta = st.chat_input("Escribe tu consulta aquí...") or pregunta_sidebar

if pregunta:
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando al agente…"):
            respuesta = _llamar_backend(pregunta)
        st.markdown(respuesta)

    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    st.rerun()
