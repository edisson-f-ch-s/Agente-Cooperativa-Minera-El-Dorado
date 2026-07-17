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
REQUEST_TIMEOUT = 60  # segundos

st.set_page_config(
    page_title="AlurAgente — Cooperativa Minera El Dorado",
    page_icon="⛏️",
    layout="centered",
)

# ── Inicialización de estado de sesión ────────────────────────────────────────

if "sesion_id" not in st.session_state:
    st.session_state.sesion_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── UI ────────────────────────────────────────────────────────────────────────

st.title("⛏️ AlurAgente")
st.caption("Asistente de la Cooperativa Minera El Dorado — Área de Acopio de Material Aurífero")

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
        return "⚠️ No se pudo conectar con el servidor. Intente nuevamente."
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        return f"⚠️ El servidor respondió con un error ({status}). Intente nuevamente."
    except Exception:
        return "⚠️ No se pudo conectar con el servidor. Intente nuevamente."


# ── Renderizar historial de conversación ──────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input del usuario ─────────────────────────────────────────────────────────

pregunta = st.chat_input("Escribe tu consulta aquí...")

if pregunta:
    # Mostrar y registrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    # Llamar al backend
    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            respuesta = _llamar_backend(pregunta)
        st.markdown(respuesta)

    # Registrar respuesta del agente
    st.session_state.messages.append({"role": "assistant", "content": respuesta})

