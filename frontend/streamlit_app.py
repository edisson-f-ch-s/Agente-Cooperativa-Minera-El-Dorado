"""
Frontend Streamlit para Agente El Dorado — Cooperativa Minera El Dorado.
Se comunica exclusivamente por HTTP con el backend FastAPI.
"""
import base64
import os
import uuid
import requests
import streamlit as st

# ── Configuración ─────────────────────────────────────────────────────────────

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 90  # segundos

st.set_page_config(
    page_title="Agente El Dorado — Cooperativa Minera El Dorado",
    page_icon="⛏️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Helper para Cargar Imágenes en Base64 ──────────────────────────────────────

def get_base64_image(file_path: str) -> str:
    """Lee una imagen local y la convierte a string base64 para HTML/CSS inline."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

logo_b64 = get_base64_image("assets/logo.png")
banner_b64 = get_base64_image("assets/banner.png")

# ── CSS Ajustado (Optimización de Márgenes y Paddings) ─────────────────────────

st.markdown(f"""
<style>
    /* 1. Reset de márgenes de la aplicación y header superior de Streamlit */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 2.5rem !important;
    }}
    
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 900px !important;
    }}

    .stApp {{
        background-color: #0b0f19;
        color: #f1f5f9;
    }}

    /* 2. Logo compacto en el Sidebar */
    .sidebar-logo-wrapper {{
        text-align: center;
        padding: 0.2rem 0 0.8rem 0;
    }}
    .sidebar-logo-img {{
        width: 100px !important;
        height: auto !important;
        border-radius: 12px;
        filter: drop-shadow(0 4px 12px rgba(245, 158, 11, 0.25));
        border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    /* 3. Header Banner Compacto y Elegante */
    .hero-banner-container {{
        position: relative;
        width: 100%;
        height: 140px;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(245, 158, 11, 0.35);
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.6);
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }}
    
    .hero-banner-bg {{
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: url('data:image/png;base64,{banner_b64}');
        background-size: cover;
        background-position: center 35%;
        opacity: 0.45;
    }}

    .hero-banner-overlay {{
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(90deg, rgba(11, 15, 25, 0.95) 0%, rgba(11, 15, 25, 0.65) 50%, rgba(11, 15, 25, 0.2) 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 0 1.8rem;
    }}

    .hero-title {{
        color: #fbbf24;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 1.6rem;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
    }}

    .hero-subtitle {{
        color: #cbd5e1;
        font-size: 0.88rem;
        margin-top: 0.3rem;
        font-weight: 400;
    }}

    /* 4. Badges visuales de estado */
    .model-badge {{
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }}

    /* 5. Tarjeta de Bienvenida compacta */
    .welcome-card {{
        background: rgba(30, 41, 59, 0.4);
        border: 1px dashed rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        margin: 0.8rem 0 1.5rem 0;
    }}
    .welcome-card h4 {{
        color: #f59e0b;
        margin: 0 0 0.4rem 0;
        font-size: 1.05rem;
    }}
    .welcome-card p {{
        color: #94a3b8;
        font-size: 0.88rem;
        margin: 0;
        line-height: 1.4;
    }}

    /* 6. Reducción de espaciados en la barra lateral */
    [data-testid="stSidebar"] {{
        padding-top: 0.5rem !important;
    }}
    [data-testid="stSidebar"] div.stButton > button {{
        padding: 0.35rem 0.6rem;
        font-size: 0.82rem;
        border-radius: 6px;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }}
    [data-testid="stSidebar"] div.stButton > button:hover {{
        border-color: #f59e0b;
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.1);
    }}

    /* Ajuste de separadores */
    hr {{
        margin: 0.8rem 0 !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Inicialización de Estado ──────────────────────────────────────────────────

if "sesion_id" not in st.session_state:
    st.session_state.sesion_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Barra Lateral (Sidebar) ───────────────────────────────────────────────────

with st.sidebar:
    # Logo oficial compacto
    if logo_b64:
        st.markdown(f"""
        <div class="sidebar-logo-wrapper">
            <img src="data:image/png;base64,{logo_b64}" class="sidebar-logo-img" alt="Logo CM El Dorado" />
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### CM El Dorado")

    st.markdown("#### ⚙️ Estado del Sistema")

    # Verificar salud del backend
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health.status_code == 200:
            data = health.json()
            st.success("✅ Backend Conectado")
            model = data.get("modelo_activo", "desconocido")
            st.markdown(f'Modelo: <span class="model-badge">{model}</span>', unsafe_allow_html=True)
        else:
            st.error("⚠️ Backend con observaciones")
    except Exception:
        st.error("❌ Backend fuera de línea")
        st.caption(f"Endpoint: `{BACKEND_URL}`")

    st.divider()

    if st.button("🔄 Nueva Conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sesion_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    # Consultas Rápidas por Rol
    st.markdown("#### 📋 Consultas por Rol")

    st.caption("👷 **Supervisor de Área**")
    if st.button("Faltas por EPP", key="btn_epp", use_container_width=True):
        st.session_state["_pregunta_pendiente"] = "¿Cuántos trabajadores faltaron esta semana por falta de EPP?"
        st.rerun()

    if st.button("Incidencias Pendientes", key="btn_incidencias", use_container_width=True):
        st.session_state["_pregunta_pendiente"] = "Muéstrame las incidencias de alta severidad que están pendientes."
        st.rerun()

    st.caption("🔎 **Inspector de Molienda**")
    if st.button("Grupo Inspector INS-005", key="btn_ins005", use_container_width=True):
        st.session_state["_pregunta_pendiente"] = "¿A qué grupo pertenece el inspector INS-005 en julio de 2026?"
        st.rerun()

    if st.button("Molinos en Reevaluación", key="btn_molinos", use_container_width=True):
        st.session_state["_pregunta_pendiente"] = "¿Qué molinos requieren reevaluación?"
        st.rerun()

    st.caption("📦 **Acopio y Normativa**")
    if st.button("Cargas en Molienda", key="btn_cargas", use_container_width=True):
        st.session_state["_pregunta_pendiente"] = "¿Cuántas cargas están actualmente en estado de molienda?"
        st.rerun()

    if st.button("Protocolo EPP (PDF)", key="btn_pdf", use_container_width=True):
        st.session_state["_pregunta_pendiente"] = "¿Cuáles son los requisitos de EPP según el protocolo de seguridad?"
        st.rerun()

    st.divider()
    st.markdown(
        '<p style="font-size:0.72rem;color:#64748b;text-align:center;margin-top:0.4rem;">'
        'Cooperativa Minera El Dorado<br>'
        f'Sesión: <code>{st.session_state.sesion_id[:8]}…</code>'
        '</p>',
        unsafe_allow_html=True,
    )

# ── Cabecera Principal ────────────────────────────────────────────────────────

st.markdown(f"""
<div class="hero-banner-container">
    <div class="hero-banner-bg"></div>
    <div class="hero-banner-overlay">
        <h1 class="hero-title">Agente El Dorado</h1>
        <div class="hero-subtitle">Asistente Operativo Inteligente · Área de Acopio de Material Aurífero</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Función de comunicación HTTP ──────────────────────────────────────────────

def _llamar_backend(pregunta: str) -> str:
    """Envía la pregunta al backend FastAPI y devuelve la respuesta del agente."""
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
            "⚠️ **No se pudo conectar con el servidor backend.**\n\n"
            "Verifica que el servicio esté corriendo en el puerto configurado."
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
                "⚠️ **Cuota de la API agotada.**\n\n"
                "Se alcanzó el límite de consultas. Intente nuevamente en breve."
            )
        return f"⚠️ {detalle or f'Error en la consulta ({status}). Intenta nuevamente.'}"
    except Exception:
        return "⚠️ **Error inesperado en el procesamiento.** Intenta nuevamente."

# ── Pantalla de Bienvenida o Mensajes ─────────────────────────────────────────

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h4>👋 Bienvenido al Asistente Operativo Agente El Dorado</h4>
        <p>
            Consulta en tiempo real sobre <strong>asistencia y EPP</strong>, 
            <strong>cargas de mineral aurífero</strong>, <strong>estado de molinos</strong>, 
            <strong>inspectores</strong> y <strong>reglamentos internos</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Renderizar Historial de Mensajes
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⛏️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Manejo de Preguntas ───────────────────────────────────────────────────────

pregunta_sidebar = st.session_state.pop("_pregunta_pendiente", None)
pregunta_input = st.chat_input("Escribe tu consulta operativa aquí...")

pregunta_final = pregunta_input or pregunta_sidebar

if pregunta_final:
    st.session_state.messages.append({"role": "user", "content": pregunta_final})
    with st.chat_message("user", avatar="👤"):
        st.markdown(pregunta_final)

    with st.chat_message("assistant", avatar="⛏️"):
        with st.spinner("Consultando datos y normativa..."):
            respuesta = _llamar_backend(pregunta_final)
        st.markdown(respuesta)

    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    st.rerun()
