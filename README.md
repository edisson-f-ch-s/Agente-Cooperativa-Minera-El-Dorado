# ⛏️ Agente El Dorado — Cooperativa Minera El Dorado

> **Asistente Inteligente de IA para la Gestión Operativa y Normativa del Área de Acopio de Material Aurífero**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain 1.x](https://img.shields.io/badge/LangChain-1.x-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

---

## 📌 Origen y Contexto del Proyecto

Este proyecto fue desarrollado como solución al **Challenge Final de Inteligencia Artificial** del programa **Oracle Next Education (ONE)** impulsado por **Alura Latam**.

### El Problema
La **Cooperativa Minera El Dorado** administra el acopio, molienda y procesamiento de material aurífero. En el día a día, supervisores de área, inspectores de molienda y personal administrativo enfrentan dificultades para consultar rápidamente información crítica dispersa en múltiples archivos CSV (asistencia, rotación, estado de cargas e incidencias) y manuales normativos en PDF (protocolos de EPP, rotación de personal, evaluaciones).

### La Solución: Agente El Dorado
Un agente conversacional inteligente capaz de interpretar preguntas en lenguaje natural, seleccionar de forma autónoma la herramienta correcta (**Tool-Calling**) o realizar búsquedas semánticas sobre documentos PDF (**RAG**), devolviendo respuestas precisas, estructuradas y verificables sin inventar datos.

---

## 🎬 Demostración Visual y Capturas

<!-- 
   PLACEHOLDER: Inserta aquí un GIF animado o imagen de la aplicación en ejecución.
   Ejemplo: ![Demo AlurAgente](docs/assets/demo_aluragente.gif) 
-->
> 📷 **Demostración de la Interfaz (Streamlit UI)**  
> *(Espacio reservado para GIF o Captura de la aplicación en funcionamiento)*  
> ![Placeholder Demostración UI](https://via.placeholder.com/800x450/1a1a2e/e2b040?text=Demostrac%C3%B3n+Streamlit+UI+-+AlurAgente)

---

## 🏗️ Arquitectura del Sistema

El proyecto implementa una **arquitectura desacoplada en 3 capas** que separa estrictamente la interfaz de usuario, la lógica del agente y las fuentes de datos:

<!-- 
   PLACEHOLDER: Inserta aquí el diagrama de arquitectura en imagen si lo prefieres.
   Ejemplo: ![Arquitectura](docs/assets/arquitectura.png) 
-->

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
 │                    SERVIDORE / BACKEND                      │
 │                      FastAPI Service                        │
 │           - Middleware CORS & Rate Limiter                  │
 │           - Manejo Grácil de Errores de Cuota API           │
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
| **Agente / Orquestador** | LangChain 1.x (`langchain_classic`) | Estándar de la industria para agentes tool-calling y RAG. |
| **Modelo LLM** | Google Gemini 2.0 Flash | 1,500 peticiones/día gratuitas, baja latencia y soporte nativo de herramientas. |
| **Embeddings & VectorStore** | Google Generative AI + FAISS | Búsqueda semántica ultrarrápida sobre PDFs sin dependencias de base de datos externa. |
| **Backend Web** | FastAPI + Uvicorn | Rendimiento asíncrono elevado, validación automática Pydantic y swagger docs. |
| **Frontend UI** | Streamlit | Interfaz interactiva de chat nativa en Python, limpia y responsiva. |
| **Contenedores** | Docker & Docker Compose | Garantiza despliegue idéntico en cualquier entorno local o en la nube. |

---

## 🎭 Roles de Usuario y Ejemplos de Consultas

AlurAgente adapta sus respuestas a los 3 roles clave del Área de Acopio:

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
│   ├── data/                 # Fuentes de datosCSV y PDFs institucionales
│   ├── Dockerfile            # Imagen contenedor Backend
│   ├── requirements.txt      # Dependencias backend con versiones fijadas
│   └── test_local.py         # Script de pruebas end-to-end automáticas
├── frontend/
│   ├── Dockerfile            # Imagen contenedor Frontend
│   ├── requirements.txt      # Dependencias frontend
│   └── streamlit_app.py      # Interfaz de usuario interactiva
├── docker-compose.yml        # Orquestación multicontenedor
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
   git clone https://github.com/tu-usuario/Agente-Cooperativa-Minera-El-Dorado.git
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
GOOGLE_API_KEY="tu_clave_aqui" backend/venv/bin/python backend/test_local.py --quick
```

---

## 🌐 Despliegue en la Nube

La aplicación está completamente dockerizada y lista para desplegarse en cualquier proveedor cloud:

- **Hugging Face Spaces** (Docker Space / Streamlit)
- **Render / Koyeb / Railway**
- **OCI Compute (Oracle Cloud Infrastructure)**

<!-- 
   PLACEHOLDER: Inserta aquí el enlace o captura del proyecto en producción.
   Ejemplo: [Probá la app en vivo aquí](https://huggingface.co/spaces/tu-usuario/aluragente)
-->
> 🔗 **Enlace de Producción**: *(Insertar enlace a la app desplegada en HF Spaces / Render / OCI)*  
> 📷 **Captura de Producción**:  
> ![Placeholder App en Producción](https://via.placeholder.com/800x400/0f3460/6ee7b7?text=Aplicaci%C3%B3n+Desplegada+en+la+Nube+-+AlurAgente)

---

## 📜 Licencia y Créditos

- **Programa**: Oracle Next Education (ONE) / Alura Latam
- **Challenge**: Agente Conversacional de IA
- **Licencia**: [MIT License](LICENSE)
