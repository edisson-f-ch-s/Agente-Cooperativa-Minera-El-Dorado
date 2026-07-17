# AlurAgente — Cooperativa Minera El Dorado
## Prompt maestro para agente de código

Plazo de entrega del challenge: **22/07/2026**. El desarrollo será continuo (sin
cronograma diario fijo); este documento define alcance, arquitectura, stack y
estructura para que el agente de código pueda construir el proyecto de punta a
punta con criterio propio, sin decisiones ambiguas que consulten dos veces lo mismo.

---

## Prompt (copiar todo el bloque siguiente en el agente de código)

```
Contexto del proyecto:
Voy a construir "AlurAgente", un agente de IA conversacional para el challenge
final de Alura (Oracle Next Education). Es un agente de preguntas y respuestas
en lenguaje natural sobre documentación interna y datos operativos de una
empresa ficticia: "Cooperativa Minera El Dorado", específicamente su Área de
Acopio de Material Aurífero.

Fuentes de información (ya generadas, se colocarán en /app/data):
Datos estructurados (CSV, en /app/data/):
  - trabajadores.csv        (personal: supervisores, inspectores, acopiadores, transportistas)
  - molinos.csv             (molinos/trapiches terceros: estado, capacidad)
  - grupos_inspectores.csv  (rotación mensual de grupos de 4 inspectores por molino)
  - asistencia.csv          (asistencia diaria y cumplimiento de EPP)
  - cargas.csv              (seguimiento de material aurífero: recepción, transporte, molienda, entrega)
  - incidencias.csv         (incidencias de trabajadores, transportistas o molinos)

Documentos no estructurados (PDF, en /app/data/documentos/):
  - Manual_General_Area_de_Acopio.pdf              (roles y flujo operativo general)
  - Protocolo_de_Seguridad_y_EPP.pdf                (EPP obligatorio, reporte de incidentes)
  - Reglamento_de_Rotacion_de_Inspectores.pdf       (periodicidad y excepciones de rotación)
  - Procedimiento_Recepcion_y_Entrega_de_Material.pdf (estados de carga, tiempos de espera)
  - Politica_de_Evaluacion_de_Molinos.pdf           (criterios de cierre/reevaluación de molinos)

Roles consultantes (sin control de acceso, es un demo funcional abierto):
  - Supervisor de Área: resúmenes de asistencia, incidencias, estado de molinos
  - Inspector de Molienda: su asistencia, grupo, molino asignado y periodo
  - Administrativo de Acopio: estado y tiempos de entrega de cargas de material

═══════════════════════════════════════════════════════════════════
ARQUITECTURA (obligatoria: backend y frontend separados y desacoplados)
═══════════════════════════════════════════════════════════════════

  [Frontend: Streamlit hoy, reemplazable después por Astro/React]
                        │  HTTP (JSON)
                        ▼
  [Backend: FastAPI — único punto de entrada del agente]
                        │
                        ▼
  [Agente LangChain con tool-calling]
        │                              │
        ▼                              ▼
  [Tools sobre CSVs vía Pandas]   [Tool de RAG sobre PDFs vía FAISS]

Regla de diseño no negociable: el frontend NUNCA importa código del agente
directamente. Toda interacción pasa por un endpoint HTTP del backend
(POST /preguntar). Esto permite reemplazar o duplicar el frontend (agregar un
sitio Astro/React más adelante) sin tocar una sola línea del backend.

═══════════════════════════════════════════════════════════════════
STACK Y DEPENDENCIAS (decisión cerrada, no evaluar alternativas)
═══════════════════════════════════════════════════════════════════

- Python 3.11+
- Backend / agente:
    fastapi
    uvicorn[standard]
    langchain
    langchain-community
    langchain-google-genai      (LLM: Gemini 2.0 Flash, capa gratuita vía GOOGLE_API_KEY)
    faiss-cpu                   (vector store para los PDFs)
    pypdf                       (carga de PDFs)
    pandas                      (consultas sobre CSVs)
    python-dotenv
    pydantic
- Frontend inicial:
    streamlit
    requests
- NO usar: LangGraph, n8n, OCI, CrewAI, AutoGen. Son innecesarios para este
  alcance y no deben aparecer en el proyecto ni en el requirements.txt.

Fijar versiones en requirements.txt (usar las últimas estables al momento de
instalar, pero siempre con versión fijada con ==, no rangos abiertos).

═══════════════════════════════════════════════════════════════════
INFRAESTRUCTURA / DEPLOY
═══════════════════════════════════════════════════════════════════

- Backend (FastAPI) y frontend (Streamlit) se despliegan como dos servicios
  independientes (aunque estén en el mismo repo), cada uno con su propio
  Dockerfile, para poder escalarlos o reemplazarlos por separado.
- Deploy objetivo: Render o Hugging Face Spaces (decidir el más simple al
  momento del deploy). NO usar OCI.
- Variables de entorno (GOOGLE_API_KEY, y URL del backend para el frontend)
  deben leerse siempre desde variables de entorno / secretos de la plataforma
  de deploy, nunca hardcodeadas.
- Incluir un docker-compose.yml para levantar backend + frontend juntos en
  local con un solo comando, aunque el deploy final los separe.

═══════════════════════════════════════════════════════════════════
ESTRUCTURA DE CARPETAS (crear exactamente así)
═══════════════════════════════════════════════════════════════════

aluragente/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI: expone POST /preguntar, GET /health
│   │   ├── agent.py             # Definición del agente LangChain + tool-calling
│   │   ├── tools.py             # Las 6 funciones de tool (ver sección siguiente)
│   │   ├── vectorstore.py       # Construcción/carga del índice FAISS sobre los PDFs
│   │   └── schemas.py           # Modelos Pydantic de request/response
│   ├── data/
│   │   ├── trabajadores.csv
│   │   ├── molinos.csv
│   │   ├── grupos_inspectores.csv
│   │   ├── asistencia.csv
│   │   ├── cargas.csv
│   │   ├── incidencias.csv
│   │   └── documentos/
│   │       ├── Manual_General_Area_de_Acopio.pdf
│   │       ├── Protocolo_de_Seguridad_y_EPP.pdf
│   │       ├── Reglamento_de_Rotacion_de_Inspectores.pdf
│   │       ├── Procedimiento_Recepcion_y_Entrega_de_Material.pdf
│   │       └── Politica_de_Evaluacion_de_Molinos.pdf
│   ├── test_local.py            # Prueba el agente end-to-end sin frontend
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── streamlit_app.py         # Chat que consume BACKEND_URL/preguntar
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example              # BACKEND_URL=http://localhost:8000
├── docker-compose.yml
├── .gitignore                    # incluir .env, __pycache__, *.faiss, venv
└── README.md                     # placeholder, se completa al final manualmente

═══════════════════════════════════════════════════════════════════
LAS 6 TOOLS DEL AGENTE (backend/app/tools.py)
═══════════════════════════════════════════════════════════════════

Cada una es una función Python pura, testeable sin LLM, con docstring claro
para que el modelo entienda cuándo usarla. Todas manejan bien "sin filtros"
(resumen general) y "sin resultados" (mensaje claro, nunca una excepción sin
capturar):

  - consultar_asistencia(id_trabajador=None, fecha_desde=None, fecha_hasta=None)
  - consultar_cargas(estado=None, molino_id=None, carga_id=None)
  - consultar_incidencias(tipo=None, severidad=None, estado=None, fecha_desde=None)
  - consultar_molinos(estado=None, molino_id=None)
  - consultar_grupo_inspector(id_trabajador=None, grupo_id=None, periodo=None)
  - buscar_en_documentos(pregunta: str)   # RAG semántico sobre los 5 PDFs vía FAISS

═══════════════════════════════════════════════════════════════════
REQUISITOS FUNCIONALES ADICIONALES
═══════════════════════════════════════════════════════════════════

1. agent.py debe usar un system prompt que fije el contexto de la Cooperativa
   Minera El Dorado y su Área de Acopio, e indicar explícitamente que el
   agente responde solo con base en los resultados de las tools, nunca
   inventa datos.
2. Memoria conversacional básica por sesión (para preguntas de seguimiento),
   manejada en el backend, no en el frontend.
3. main.py (FastAPI) expone:
     POST /preguntar   { "sesion_id": str, "pregunta": str } -> { "respuesta": str }
     GET  /health       -> { "status": "ok" }
4. streamlit_app.py solo hace requests HTTP a BACKEND_URL, mantiene el
   historial visual en session_state, y muestra errores de forma amigable si
   el backend no responde.
5. test_local.py ejecuta 6-8 preguntas de ejemplo (2-3 por rol) directamente
   contra agent.py (sin pasar por FastAPI) e imprime las respuestas, para
   validar rápido durante desarrollo.
6. No implementar autenticación, control de acceso por rol, ni features fuera
   de lo descrito arriba — mantener el alcance acotado.

Prioriza que el agente responda correctamente antes que la elegancia del
código. Si algo no queda claro en este prompt, toma la decisión más simple y
continúa, en vez de detener el desarrollo por una ambigüedad menor.
```

---

## Notas rápidas para cuando lo uses

- Copia los 6 CSVs y los 5 PDFs dentro de `backend/data/` (y `backend/data/documentos/`) antes de lanzar al agente de código — el prompt ya asume esas rutas exactas.
- El `docker-compose.yml` es lo que te permite decir en el README "clona el repo y corre `docker compose up`" — muy valorado en la validación de "instrucciones para ejecutar el proyecto".
- Cuando quieras el frontend Astro/React más adelante, el mismo prompt te sirve de base: solo cambias la sección de "Frontend inicial" y le pides al agente de código que agregue `frontend-astro/` como servicio adicional que consuma el mismo `BACKEND_URL` — el backend no se toca.
