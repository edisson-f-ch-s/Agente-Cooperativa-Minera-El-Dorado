# AlurAgente — Cooperativa Minera El Dorado

Agente conversacional de IA para el Área de Acopio de Material Aurífero de la Cooperativa Minera El Dorado. Permite a supervisores, inspectores y administrativos consultar en lenguaje natural datos operativos y documentación interna sin necesidad de conocimientos técnicos.

Desarrollado como proyecto final para el **Challenge Alura Latam / ONE (Oracle Next Education)**.

---

## 🎯 Características

- **Consultas en lenguaje natural** sobre datos operativos (CSV) y documentación interna (PDF).
- **6 herramientas especializadas** para consultar asistencia, cargas, incidencias, molinos, grupos de inspectores y documentos.
- **Memoria conversacional** aislada por sesión (`sesion_id`) para preguntas de seguimiento.
- **Arquitectura desacoplada**: Backend en FastAPI + Frontend en Streamlit comunicados mediante HTTP REST API.
- **RAG semántico** sobre 5 documentos PDF institucionales usando FAISS y Embeddings.
- **Tool-calling con LangChain 1.x** sobre el modelo `gemini-2.0-flash` (1,500 solicitudes/día en la capa gratuita).

---

## 🏗️ Arquitectura del Sistema

```text
               ┌──────────────────────────────┐
               │    Frontend (Streamlit)      │
               │   Chat UI + Estado Sesión    │
               └──────────────┬───────────────┘
                              │ HTTP REST API (JSON)
                              ▼
               ┌──────────────────────────────┐
               │      Backend (FastAPI)       │
               │   Rate Limiter + CORS        │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │     Agente LangChain 1.x     │
               │ Tool-Calling + Chat History  │
               └──────────────┬───────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
 ┌─────────────────┐                     ┌─────────────────┐
 │   Tools CSV     │                     │    Tool RAG     │
 │ (Pandas Engine) │                     │ (FAISS Vector)  │
 └─────────────────┘                     └─────────────────┘
  - Asistencia                            - Manual Acopio
  - Cargas                                - Protocolo EPP
  - Incidencias                           - Rotación
  - Molinos                               - Recepción Mat.
  - Grupos Inspectores                    - Pol. Molinos
```

---

## 📁 Estructura del Proyecto

```text
Agente-Cooperativa-Minera-El-Dorado/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # API FastAPI (Endpoints POST /preguntar, GET /health)
│   │   ├── agent.py          # Agente LangChain + memoria por sesión
│   │   ├── tools.py          # 6 herramientas de consulta (CSV y PDF)
│   │   ├── vectorstore.py    # Generador/cargador del índice vectorial FAISS
│   │   ├── gemini_config.py  # Manejador de modelos Gemini, fallbacks y rate limits
│   │   ├── rate_limit.py     # Limitador de peticiones por minuto/día
│   │   └── schemas.py        # Esquemas de validación Pydantic
│   ├── data/
│   │   ├── *.csv             # 6 archivos de datos operativos
│   │   └── documentos/       # 5 PDFs de manuales y protocolos institucionales
│   ├── test_local.py         # Script de pruebas end-to-end automáticas
│   ├── requirements.txt      # Dependencias backend con versiones probadas
│   ├── Dockerfile            # Contenedor del backend
│   └── .env.example
├── frontend/
│   ├── streamlit_app.py      # Interfaz de usuario interactiva en Streamlit
│   ├── requirements.txt      # Dependencias del frontend
│   ├── Dockerfile            # Contenedor del frontend
│   └── .env.example
├── docker-compose.yml        # Orquestación de contenedores
├── README.md                 # Documentación principal
└── INICIO_RAPIDO.md          # Guía rápida de instalación
```

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.11+
- **Orquestador IA**: LangChain 1.x (`langchain_classic`)
- **LLM / Embeddings**: Google Gemini (`gemini-2.0-flash`) vía `langchain-google-genai`
- **Lectura de Documentos y RAG**: PyPDF, Pandas, FAISS (`faiss-cpu`)
- **Backend API**: FastAPI, Uvicorn, Pydantic
- **Frontend UI**: Streamlit
- **Contenedores y Despliegue**: Docker, Docker Compose

---

## 🚀 Instalación y Ejecución Local

> **¿Primera vez?** Revisa [INICIO_RAPIDO.md](INICIO_RAPIDO.md) para la guía paso a paso.

### Requisitos Previos

- Docker y Docker Compose instalados.
- Clave de API de Google Gemini ([obtener en Google AI Studio](https://aistudio.google.com/app/apikey)).

### Opción 1: Docker Compose (Recomendado)

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/Agente-Cooperativa-Minera-El-Dorado.git
   cd Agente-Cooperativa-Minera-El-Dorado
   ```

2. Crea el archivo `.env` en la raíz copiando la plantilla:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` y coloca tu clave de API:
   ```env
   GOOGLE_API_KEY=tu_clave_aqui
   GEMINI_MODEL=gemini-2.0-flash
   ```

3. Levanta los contenedores:
   ```bash
   docker-compose up -d --build
   ```

4. Accede a las aplicaciones:
   - **Frontend Streamlit**: `http://localhost:8501`
   - **Backend API Docs**: `http://localhost:8000/docs`

---

### Opción 2: Ejecución Manual en Entornos Virtuales

#### 1. Backend (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GOOGLE_API_KEY="tu_clave_aqui"
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend (Streamlit)

```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BACKEND_URL="http://localhost:8000"
streamlit run streamlit_app.py
```

---

## 🧪 Pruebas Automáticas End-to-End

Puedes validar el funcionamiento completo de las 6 herramientas ejecutando el script de prueba local:

```bash
GOOGLE_API_KEY="tu_clave_aqui" backend/venv/bin/python backend/test_local.py --quick
```

---

## 🎭 Roles y Ejemplos de Consultas

El agente resuelve dudas específicas según el rol del usuario en la mina:

### 1. Supervisor de Área
- **Pregunta**: *"¿Cuántos trabajadores faltaron esta semana por falta de EPP?"*
- **Respuesta esperada**: Resumen cuantitativo filtrando la asistencia y el estado de EPP en el archivo `asistencia.csv`.
- **Pregunta**: *"Muéstrame las incidencias de alta severidad pendientes."*

### 2. Inspector de Molienda
- **Pregunta**: *"¿A qué grupo pertenece el inspector INS-005 en julio de 2026?"*
- **Respuesta esperada**: Consulta en `grupos_inspectores.csv` identificando el grupo (ej. G-02) y su molino asignado.

### 3. Administrativo de Acopio
- **Pregunta**: *"¿Cuántas cargas están actualmente en estado de molienda?"*
- **Respuesta esperada**: Total de cargas registradas en `cargas.csv` con estado 'en molienda'.

### 4. Consultas de Procedimientos y Normativa (RAG)
- **Pregunta**: *"¿Cuáles son los requisitos de EPP según el protocolo de seguridad?"*
- **Respuesta esperada**: Recuperación semántica de fragmentos del `Protocolo_de_Seguridad_y_EPP.pdf` mediante FAISS.

---

## 📸 Demostración de Despliegue

La solución está lista para desplegarse en plataformas con soporte Docker (Hugging Face Spaces, Render, Koyeb, OCI Compute, etc.).

> **Captura de Pantalla / Enlace de la Aplicación en Ejecución**:
> *(Inserta aquí el enlace a tu app desplegada o la captura de pantalla comprobando el funcionamiento)*

---

## 📜 Licencia

Este proyecto fue desarrollado bajo la licencia **MIT** como entregable para el Challenge de Alura Latam y Oracle Next Education (ONE).
