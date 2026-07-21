# AlurAgente — Cooperativa Minera El Dorado

Agente conversacional de IA para el Área de Acopio de Material Aurífero de la Cooperativa Minera El Dorado. Permite a supervisores, inspectores y administrativos consultar en lenguaje natural datos operativos y documentación interna sin necesidad de conocimientos técnicos.

## 🎯 Características

- **Consultas en lenguaje natural** sobre datos operativos (CSV) y documentación interna (PDF)
- **6 herramientas especializadas** para consultar asistencia, cargas, incidencias, molinos, grupos de inspectores y documentos
- **Memoria conversacional** por sesión para preguntas de seguimiento
- **Arquitectura desacoplada** backend FastAPI + frontend Streamlit comunicados por HTTP
- **RAG semántico** sobre 5 documentos PDF usando FAISS
- **Tool-calling** con LangChain sobre Gemini 3.5 Flash (capa gratuita)

## 🏗️ Arquitectura

```
Frontend (Streamlit)
       │  HTTP (JSON)
       ▼
Backend (FastAPI)
       │
       ▼
Agente LangChain
       │
   ┌───┴───┐
   ▼       ▼
Tools CSV  Tool RAG
(Pandas)   (FAISS)
```

## 📁 Estructura del Proyecto

```
aluragente/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # API FastAPI
│   │   ├── agent.py          # Agente LangChain
│   │   ├── tools.py          # 6 tools del agente
│   │   ├── vectorstore.py    # Índice FAISS
│   │   └── schemas.py        # Modelos Pydantic
│   ├── data/
│   │   ├── *.csv             # 6 archivos de datos operativos
│   │   └── documentos/       # 5 PDFs de documentación interna
│   ├── test_local.py         # Pruebas end-to-end
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── streamlit_app.py      # Interfaz de chat
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## 🚀 Instalación y Ejecución

> **¿Primera vez?** Ve a [INICIO_RAPIDO.md](INICIO_RAPIDO.md) para una guía paso a paso en español.

### Requisitos Previos

- Docker y Docker Compose
- Clave de API de Google Gemini ([obtener aquí](https://aistudio.google.com/app/apikey))

### Opción 1: Docker Compose (Recomendado)

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/aluragente.git
cd aluragente
```

2. Crea un archivo `.env` en la raíz con tu clave de API (no lo subas al repositorio):
```bash
GOOGLE_API_KEY=tu_clave_aqui
# Opcional; recomendado para evaluación del challenge (capa gratuita)
GEMINI_MODEL=gemini-3.5-flash
```

3. Levanta los servicios:
```bash
docker compose up
```

4. Accede a la aplicación:
   - **Frontend**: http://localhost:8501
   - **Backend API**: http://localhost:8000
   - **Documentación API**: http://localhost:8000/docs

### Opción 2: Instalación Local

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env y agrega tu GOOGLE_API_KEY
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env y agrega BACKEND_URL=http://localhost:8000
streamlit run streamlit_app.py
```

## 🧪 Pruebas

Ejecuta el script de pruebas end-to-end:

```bash
cd backend
python test_local.py
```

## 📊 Fuentes de Datos

### Datos Estructurados (CSV)
- `trabajadores.csv` - Personal de la cooperativa
- `molinos.csv` - Molinos/trapiches terceros
- `grupos_inspectores.csv` - Rotación mensual de inspectores
- `asistencia.csv` - Asistencia diaria y cumplimiento de EPP
- `cargas.csv` - Seguimiento de material aurífero
- `incidencias.csv` - Incidencias registradas

### Documentos Internos (PDF)
- Manual General del Área de Acopio
- Protocolo de Seguridad y EPP
- Reglamento de Rotación de Inspectores
- Procedimiento de Recepción y Entrega de Material
- Política de Evaluación de Molinos

## 🛠️ Tecnologías

- **Backend**: FastAPI, LangChain, Google Gemini 3.5 Flash
- **Frontend**: Streamlit
- **Procesamiento de datos**: Pandas, PyPDF
- **Vector Store**: FAISS
- **Embeddings**: Google Generative AI
- **Contenedores**: Docker, Docker Compose

## 🎭 Roles de Usuario

El sistema soporta consultas para tres roles principales:

1. **Supervisor de Área**: Resúmenes de asistencia, incidencias, estado de molinos
2. **Inspector de Molienda**: Asistencia personal, grupo asignado, molino y período
3. **Administrativo de Acopio**: Estado y tiempos de entrega de cargas

## 📝 Ejemplos de Consultas

- "¿Cuántos trabajadores faltaron esta semana por falta de EPP?"
- "¿Qué cargas están en tránsito al molino M001?"
- "Muéstrame mi grupo de inspección para este mes"
- "¿Cuáles son los requisitos de EPP según el protocolo?"
- "¿Qué molinos requieren reevaluación?"

## 🔧 Variables de Entorno

### Backend
- `GOOGLE_API_KEY`: Clave de API de Google Gemini (obligatoria)
- `GEMINI_MODEL`: Modelo de chat de Gemini (opcional; default: `gemini-3.5-flash`). Respaldo automático: `gemini-3.1-flash-lite`
- `RATE_LIMIT_RPM`: Máximo de consultas por minuto en despliegue compartido (default: `8`; `0` = sin límite)
- `RATE_LIMIT_RPD`: Máximo de consultas por día (default: `400`; `0` = sin límite)

### Capa gratuita y evaluación del challenge

El proyecto usa modelos **Flash** con capa gratuita de [Google AI Studio](https://aistudio.google.com/app/apikey). Es suficiente para la evaluación del challenge con uso moderado (varios evaluadores probando consultas puntuales).

- **Modelo recomendado**: `gemini-3.5-flash` (estable, jul 2026)
- **Respaldo automático**: si el modelo configurado está deprecado (error 404), el backend prueba `gemini-3.1-flash-lite` sin intervención manual
- **Protección de cuota**: límites configurables (`RATE_LIMIT_RPM`, `RATE_LIMIT_RPD`) para un despliegue compartido durante la calificación
- **Uso local**: cada estudiante/evaluador puede clonar el repo y usar su propia `GOOGLE_API_KEY` sin límites compartidos
- **Límite de cuota de Google**: si aparece un mensaje de límite alcanzado, espere 1–2 minutos; la capa gratuita tiene topes por minuto/día por proyecto
- **No requiere tarjeta de crédito** para desarrollo ni evaluación

### Frontend
- `BACKEND_URL`: URL del backend (default: `http://localhost:8000`)

## 📄 API Endpoints

### `POST /preguntar`
Envía una pregunta al agente.

**Request:**
```json
{
  "sesion_id": "uuid-de-sesion",
  "pregunta": "¿Cuántas cargas están en molienda?"
}
```

**Response:**
```json
{
  "respuesta": "Actualmente hay 15 cargas en estado de molienda..."
}
```

### `GET /health`
Verifica el estado del servicio.

**Response:**
```json
{
  "status": "ok",
  "agente_listo": true,
  "modelo_activo": "gemini-3.5-flash"
}
```

## 🚢 Despliegue

El proyecto está diseñado para desplegarse en plataformas como:
- Render
- Hugging Face Spaces
- Cualquier plataforma que soporte contenedores Docker

Cada servicio (backend y frontend) se puede escalar independientemente.

## 🤝 Contribuciones

Este proyecto fue desarrollado como parte del Challenge Final de Alura (Oracle Next Education).

## 📜 Licencia

MIT License - Ver archivo LICENSE para más detalles.

## 👤 Autor

Desarrollado para la Cooperativa Minera El Dorado (proyecto educativo)
