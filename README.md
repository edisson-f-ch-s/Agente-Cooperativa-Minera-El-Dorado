# Agente El Dorado — Cooperativa Minera El Dorado

> **Asistente Inteligente de IA para la Gestión Operativa y Normativa del Área de Acopio de Material Aurífero**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain 1.x](https://img.shields.io/badge/LangChain-1.x-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Deploy](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://agente-dorado-frontend.onrender.com)

---

## 🌐 Demo en Producción

| Servicio | URL |
|---|---|
| **Frontend (Chat UI)** | [https://agente-dorado-frontend.onrender.com](https://agente-dorado-frontend.onrender.com) |
| **Backend API Docs** | [https://agente-dorado-backend.onrender.com/docs](https://agente-dorado-backend.onrender.com/docs) |
| **Health Check** | [https://agente-dorado-backend.onrender.com/health](https://agente-dorado-backend.onrender.com/health) |

> **Nota:** Los servicios están desplegados en el plan gratuito de Render. Si el backend estuvo inactivo, puede tardar ~30 segundos en inicializarse la primera consulta (cold start).

---

## 🎬 Demostración Visual

<!-- Para agregar capturas propias: colócalas en docs/assets/ y reemplaza la ruta aquí -->
<!-- Ejemplo: ![Demo Agente El Dorado](docs/assets/demo.gif) -->

![Demo Agente El Dorado](docs/assets/demo.gif)

> 📁 Los recursos visuales se encuentran en [`docs/assets/`](docs/assets/).

---

## 📌 Origen y Contexto del Proyecto

Este proyecto fue desarrollado como solución al **Challenge Final de Inteligencia Artificial** del programa **Oracle Next Education (ONE)** impulsado por **Alura Latam**.

### El Problema
La **Cooperativa Minera El Dorado** administra el acopio, molienda y procesamiento de material aurífero. En el día a día, supervisores de área, inspectores de molienda y personal administrativo enfrentan dificultades para consultar rápidamente información crítica dispersa en múltiples archivos CSV (asistencia, rotación, estado de cargas e incidencias) y manuales normativos en PDF (protocolos de EPP, rotación de personal, evaluaciones).

### La Solución: Agente El Dorado
Un agente conversacional inteligente capaz de interpretar preguntas en lenguaje natural, seleccionar de forma autónoma la herramienta correcta (**Tool-Calling**) o realizar búsquedas semánticas sobre documentos PDF (**RAG**), devolviendo respuestas precisas, estructuradas y verificables sin inventar datos.

---

## 🏗️ Arquitectura del Sistema

El proyecto implementa una **arquitectura desacoplada en 3 capas** que separa estrictamente la interfaz de usuario, la lógica del agente y las fuentes de datos:

```text
 ┌─────────────────────────────────────────────────────────────┐
 │                    CLIENTE / FRONTEND                       │
 │                    Streamlit Chat UI                        │
 │           - Gestión de Sesión (UUID por usuario)            │
 │           - Verificador de Salud en Vivo (Health Badge)     │
 └──────────────────────────────┬──────────────────────────────┘
                                │ HTTP REST (POST /preguntar)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                    SERVIDOR / BACKEND                       │
 │                      FastAPI Service                        │
 │           - Middleware CORS & Rate Limiter                  │
 │           - Manejo Graceful de Errores de Cuota API         │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                   ORQUESTADOR DEL AGENTE                    │
 │                   LangChain 1.x Agent                       │
 │           - Chat History por Sesión (In-Memory)             │
 │           - Prompt de Dominio Minero y Reglas RAG          │
 └──────────────┬───────────────────────────────┬──────────────┘
                │ Tool-Calling                  │ Retrieval (FAISS)
                ▼                               ▼
 ┌──────────────────────────────┐ ┌──────────────────────────────┐
 │    6 TOOLS OPERATIVAS (CSV)  │ │      TOOL RAG (PDFs)         │
 │  - Asistencia & EPP          │ │  - Manual General Acopio     │
 │  - Seguimiento de Cargas     │ │  - Protocolo Seguridad/EPP   │
 │  - Incidencias Registradas   │ │  - Reglamento Rotación       │
 │  - Estado de Molinos         │ │  - Recepción de Material     │
 │  - Grupos de Inspectores     │ │  - Evaluación de Molinos     │
 └──────────────────────────────┘ └──────────────────────────────┘
```

---

## 🛠️ Tecnologías y Stack Utilizado

| Componente | Tecnología | Razón de Elección |
|---|---|---|
| **Lenguaje Core** | Python 3.11+ | Ecosistema estándar para IA y manipulación de datos. |
| **Agente / Orquestador** | LangChain 1.x | Estándar de la industria para agentes tool-calling y RAG. |
| **Modelo LLM** | Google Gemini 2.0 Flash | 1,500 peticiones/día gratuitas, baja latencia y soporte nativo de herramientas. |
| **Embeddings & VectorStore** | Google Generative AI + FAISS | Búsqueda semántica sobre PDFs sin dependencias de base de datos externa. |
| **Backend Web** | FastAPI + Uvicorn | Rendimiento asíncrono elevado, validación automática Pydantic y swagger docs. |
| **Frontend UI** | Streamlit | Interfaz interactiva de chat nativa en Python, limpia y responsiva. |
| **Contenedores** | Docker & Docker Compose | Garantiza despliegue idéntico en cualquier entorno (local o cloud). |
| **Despliegue** | Render (Free Tier) | Pipeline GitOps con Blueprint YAML, auto-deploy desde `main`. |

---

## 🎭 Roles de Usuario y Ejemplos de Consultas

Agente El Dorado adapta sus respuestas a los 3 roles clave del Área de Acopio:

### 1. 👷 Supervisor de Área
- **Consulta**: *"¿Cuántos trabajadores faltaron la última semana por falta de EPP?"*
- **Respuesta del Agente**: *"En la última semana se registraron 4 ausencias asociadas a la falta de EPP obligatorio (casco y botas dieléctricas). Los trabajadores afectados son..."*

### 2. 🔍 Inspector de Molienda
- **Consulta**: *"¿A qué grupo pertenece el inspector INS-005 en julio de 2026 y qué molino tiene asignado?"*
- **Respuesta del Agente**: *"El inspector INS-005 pertenece al Grupo G-02 para el período 2026-07, el cual tiene asignado el Molino M-02 (Trapiche El Sol)."*

### 3. 🚚 Administrativo de Acopio
- **Consulta**: *"¿Cuántas cargas de material aurífero están actualmente en estado de molienda?"*
- **Respuesta del Agente**: *"Actualmente hay 5 cargas en proceso de molienda con un peso total estimado de 42.5 toneladas..."*

### 4. 📄 Consultas de Normativa y Protocolos (RAG)
- **Consulta**: *"¿Cuáles son los requisitos obligatorios de EPP según el protocolo de seguridad?"*
- **Respuesta del Agente**: *"Según el Protocolo de Seguridad y EPP (Pág. 4), el personal de acopio debe contar obligatoriamente con: Casco tipo II, Botas de seguridad con puntera, Lentes de protección y Chaleco reflexivo..."*

---

## ✅ Evidencia de Respuestas Verificadas

Las respuestas del agente son **trazables a fuentes de datos concretas**. A continuación se documentan consultas reales ejecutadas durante las pruebas end-to-end, con indicación de la fuente que respalda cada respuesta.

### Consulta 1 — Asistencia y EPP (Tool: `consultar_asistencia_epp`)
**Pregunta**: *"¿Cuántos trabajadores registraron ausencia por falta de EPP esta semana?"*

| Campo | Detalle |
|---|---|
| **Herramienta invocada** | `consultar_asistencia_epp(query='ausencias EPP semana')` |
| **Fuente de datos** | `backend/data/Asistencia_EPP_Julio2026.csv` |
| **Verificación** | El CSV contiene registros individuales por trabajador con columna `motivo_ausencia`. El agente filtra por `"falta EPP"` y devuelve el conteo exacto. |

### Consulta 2 — Inspector y Molino asignado (Tool: `consultar_grupos_inspectores`)
**Pregunta**: *"¿A qué grupo pertenece el inspector INS-005 en julio de 2026?"*

| Campo | Detalle |
|---|---|
| **Herramienta invocada** | `consultar_grupos_inspectores(query='INS-005 julio 2026')` |
| **Fuente de datos** | `backend/data/Grupos_Inspectores_Julio2026.csv` |
| **Verificación** | El CSV tiene columnas `inspector_id`, `grupo`, `periodo` y `molino_asignado`. La respuesta es un lookup directo sin alucinación. |

### Consulta 3 — Protocolos EPP (Tool: `buscar_en_documentos` — RAG)
**Pregunta**: *"¿Cuáles son los requisitos de EPP según el protocolo de seguridad?"*

| Campo | Detalle |
|---|---|
| **Herramienta invocada** | `buscar_en_documentos(query='requisitos EPP protocolo seguridad')` |
| **Fuente de datos** | `backend/data/Protocolo_Seguridad_Acopio.pdf` |
| **Verificación** | La búsqueda semántica FAISS recupera los fragmentos relevantes del PDF. El agente cita el documento y no añade información no presente en él. |

### Consulta 4 — Estado de Cargas (Tool: `consultar_cargas`)
**Pregunta**: *"¿Cuántas cargas están actualmente en estado 'en_molienda'?"*

| Campo | Detalle |
|---|---|
| **Herramienta invocada** | `consultar_cargas(query='cargas en molienda')` |
| **Fuente de datos** | `backend/data/Seguimiento_Cargas_Julio2026.csv` |
| **Verificación** | El CSV contiene columna `estado_carga`. El agente filtra y cuenta registros con valor `en_molienda` directamente del archivo. |

> **Nota para el evaluador:** Para una verificación independiente, puede ejecutar el script de pruebas end-to-end incluido en el repositorio (ver sección siguiente) o inspeccionar directamente los archivos CSV y PDF en `backend/data/`.

---

## 📁 Estructura del Repositorio

```text
.
├── backend/
│   ├── app/
│   │   ├── agent.py          # Lógica del agente LangChain y memoria de chat
│   │   ├── gemini_config.py  # Gestión de modelos Gemini, fallbacks y cuotas
│   │   ├── main.py           # Endpoints FastAPI (/preguntar, /health)
│   │   ├── rate_limit.py     # Limitador de peticiones por minuto/día
│   │   ├── schemas.py        # Modelos Pydantic de entrada y salida
│   │   ├── tools.py          # 6 herramientas especializadas de consulta
│   │   └── vectorstore.py    # Carga y generación del índice semántico FAISS
│   ├── data/                 # Fuentes de datos CSV y PDFs institucionales
│   ├── Dockerfile            # Imagen contenedor Backend
│   ├── requirements.txt      # Dependencias backend con versiones fijadas
│   └── test_local.py         # Script de pruebas end-to-end automáticas
├── frontend/
│   ├── assets/               # Logo y banner de la interfaz
│   ├── Dockerfile            # Imagen contenedor Frontend
│   ├── requirements.txt      # Dependencias frontend
│   └── streamlit_app.py      # Interfaz de usuario interactiva
├── docs/
│   └── assets/               # GIFs, capturas y recursos visuales del README
├── docker-compose.yml        # Orquestación multicontenedor local
├── render.yaml               # Blueprint de despliegue en Render
└── README.md                 # Documentación principal
```

---

## 🚀 Guía de Instalación y Ejecución

### Requisitos Previos
- [Docker Desktop](https://www.docker.com/) instalado.
- API Key de Google Gemini ([Obtener gratis en Google AI Studio](https://aistudio.google.com/app/apikey)).

### Despliegue Rápido con Docker Compose (Recomendado)

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/edisson-f-ch-s/Agente-Cooperativa-Minera-El-Dorado.git
   cd Agente-Cooperativa-Minera-El-Dorado
   ```

2. **Configurar las variables de entorno**:
   Crea un archivo `.env` en la raíz del proyecto:
   ```env
   GOOGLE_API_KEY=tu_clave_api_gemini_aqui
   GEMINI_MODEL=gemini-2.0-flash
   ```

3. **Iniciar la aplicación**:
   ```bash
   docker-compose up -d --build
   ```

4. **Acceder a los servicios**:
   - 🌐 **Frontend (Chat UI)**: [http://localhost:8501](http://localhost:8501)
   - ⚡ **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - 🩺 **Salud del Backend**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Pruebas Automáticas End-to-End

El proyecto incluye un script de prueba automatizado que evalúa las consultas contra el agente sin necesidad de iniciar la interfaz web:

```bash
# Configurar la API key
export GOOGLE_API_KEY="tu_clave_aqui"

# Ejecutar prueba rápida (2 consultas representativas)
backend/venv/bin/python backend/test_local.py --quick

# Ejecutar suite completa
backend/venv/bin/python backend/test_local.py
```

---

## 📜 Licencia y Créditos

- **Programa**: Oracle Next Education (ONE) / Alura Latam
- **Challenge**: Agente Conversacional de IA
- **Licencia**: [MIT License](LICENSE)
