# Plan de Implementación: AlurAgente

## Descripción general

Construcción incremental del agente conversacional AlurAgente para la Cooperativa Minera El Dorado. El orden de implementación sigue la cadena de dependencias: datos → infraestructura Python → tools → agente → API HTTP → frontend → testing local. Las tareas de property-based testing se ubican junto a las unidades que validan, para detectar regresiones en el momento más temprano posible.

## Tareas

- [x] 1. Preparar datos y estructura de carpetas del proyecto
  - Crear los directorios `backend/app/`, `backend/data/documentos/`, `frontend/` si no existen aún.
  - Copiar los 6 archivos CSV (`trabajadores.csv`, `molinos.csv`, `grupos_inspectores.csv`, `asistencia.csv`, `cargas.csv`, `incidencias.csv`) desde `backend/data/documentos/` a `backend/data/`.
  - Verificar que los 5 PDFs permanezcan en `backend/data/documentos/`.
  - Crear `backend/app/__init__.py` vacío.
  - _Requisitos: 15.1, 15.2, 15.3, 15.4_

- [x] 2. Crear archivos de configuración e infraestructura de dependencias
  - [x] 2.1 Crear `backend/requirements.txt` con versiones fijadas (`==`) para: `fastapi`, `uvicorn[standard]`, `langchain`, `langchain-community`, `langchain-google-genai`, `faiss-cpu`, `pypdf`, `pandas`, `python-dotenv`, `pydantic`, `hypothesis`.
    - _Requisitos: 13.1_
  - [x] 2.2 Crear `frontend/requirements.txt` con versiones fijadas para: `streamlit`, `requests`.
    - _Requisitos: 13.2_
  - [x] 2.3 Crear `backend/.env.example` con la línea `GOOGLE_API_KEY=`.
    - _Requisitos: 13.6_
  - [x] 2.4 Crear `frontend/.env.example` con la línea `BACKEND_URL=http://localhost:8000`.
    - _Requisitos: 13.6_
  - [x] 2.5 Crear `.gitignore` en la raíz con entradas para: `.env`, `__pycache__/`, `*.faiss`, `faiss_index/`, `venv/`.
    - _Requisitos: 13.7_

- [x] 3. Implementar schemas Pydantic (`backend/app/schemas.py`)
  - Escribir el módulo `schemas.py` con las tres clases Pydantic: `PreguntaRequest` (campos `sesion_id: str` con `min_length=1` y `pregunta: str` con `min_length=1`), `RespuestaResponse` (campo `respuesta: str`) y `HealthResponse` (campo `status: str = "ok"`).
  - _Requisitos: 1.1, 1.2, 1.3_

- [ ] 4. Implementar las 5 tools sobre CSV (`backend/app/tools.py` — parte 1)
  - [ ] 4.1 Implementar `consultar_asistencia(id_trabajador, fecha_desde, fecha_hasta)`
    - Decorar con `@tool` de LangChain; incluir docstring descriptivo del cuándo usarla.
    - Aplicar filtros acumulativos sobre `asistencia.csv` con Pandas.
    - Devolver resumen estadístico cuando no hay filtros y el dataset supera 50 filas.
    - Capturar `FileNotFoundError` y excepciones de Pandas; devolver mensaje de error descriptivo.
    - _Requisitos: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 11.1, 11.4, 11.5_

  - [ ]* 4.2 Escribir property tests para `consultar_asistencia`
    - **Propiedad 5: Las tools nunca lanzan excepciones con entradas válidas**
    - **Valida: Requisitos 4.6, 11.1**
    - **Propiedad 6: Resultado vacío = mensaje descriptivo (sin excepción)**
    - **Valida: Requisitos 4.5, 11.4**
    - **Propiedad 7: Idempotencia de las tools**
    - **Valida: Requisito 11.2**
    - **Propiedad 8: Resultados acotados (< 10 000 caracteres)**
    - **Valida: Requisito 11.3**
    - Usar `hypothesis` con estrategias `st.text()` filtradas a IDs válidos y `st.dates()` para rangos de fecha.

  - [ ] 4.3 Implementar `consultar_cargas(estado, molino_id, carga_id)`
    - Decorar con `@tool`; incluir docstring con los valores posibles del campo `estado`.
    - Aplicar filtros acumulativos; limitar a 20 filas más recientes cuando el resultado supere ese umbral.
    - Capturar excepciones de acceso a archivo.
    - _Requisitos: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 11.1, 11.4, 11.5_

  - [ ]* 4.4 Escribir property tests para `consultar_cargas`
    - **Propiedad 5: Las tools nunca lanzan excepciones con entradas válidas**
    - **Valida: Requisitos 5.6, 11.1**
    - **Propiedad 9: Filtros acumulativos de cargas**
    - **Valida: Requisito 5.2**
    - **Propiedad 10: Límite de 20 filas en consultar_cargas**
    - **Valida: Requisito 5.3**
    - **Propiedad 8: Resultados acotados (< 10 000 caracteres)**
    - **Valida: Requisito 11.3**

  - [ ] 4.5 Implementar `consultar_incidencias(tipo, severidad, estado, fecha_desde)`
    - Decorar con `@tool`; incluir docstring con valores posibles de `tipo`, `severidad` y `estado`.
    - Aplicar filtros acumulativos sobre `incidencias.csv`.
    - Capturar excepciones de acceso a archivo.
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5, 11.1, 11.4, 11.5_

  - [ ]* 4.6 Escribir property tests para `consultar_incidencias`
    - **Propiedad 5: Las tools nunca lanzan excepciones con entradas válidas**
    - **Valida: Requisitos 6.5, 11.1**
    - **Propiedad 6: Resultado vacío = mensaje descriptivo (sin excepción)**
    - **Valida: Requisitos 6.3, 11.4**
    - **Propiedad 7: Idempotencia de las tools**
    - **Valida: Requisito 11.2**

  - [ ] 4.7 Implementar `consultar_molinos(estado, molino_id)`
    - Decorar con `@tool`; incluir docstring con estados válidos.
    - Aplicar filtros sobre `molinos.csv`.
    - Capturar excepciones de acceso a archivo.
    - _Requisitos: 7.1, 7.2, 7.3, 7.4, 7.5, 11.1, 11.4, 11.5_

  - [ ] 4.8 Implementar `consultar_grupo_inspector(id_trabajador, grupo_id, periodo)`
    - Decorar con `@tool`; incluir docstring indicando que `periodo` va en formato `YYYY-MM`.
    - Filtrar `grupos_inspectores.csv` por los parámetros provistos; cuando se filtra por `id_trabajador`, buscar en el campo `integrantes` (separados por `;`).
    - Capturar excepciones de acceso a archivo.
    - _Requisitos: 8.1, 8.2, 8.3, 8.4, 8.5, 11.1, 11.4, 11.5_

  - [ ]* 4.9 Escribir unit tests para `consultar_molinos` y `consultar_grupo_inspector`
    - Verificar filtros con resultados esperados usando datos reales de los CSV.
    - Verificar retorno de mensaje informativo cuando no hay resultados.
    - _Requisitos: 7.3, 7.5, 8.3, 8.5_

- [ ] 5. Checkpoint — Verificar las 5 tools CSV de forma aislada
  - Asegurarse de que todos los tests pasen. Consultar al usuario si hay dudas sobre el comportamiento esperado de algún filtro.

- [x] 6. Implementar el vectorstore FAISS (`backend/app/vectorstore.py`)
  - [x] 6.1 Implementar `_build_vectorstore(pdf_dir)` que cargue los 5 PDFs con `PyPDFLoader`, los divida con `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)` y construya el índice con `GoogleGenerativeAIEmbeddings`.
    - Registrar advertencia (`logging.warning`) y continuar si un PDF no se encuentra.
    - _Requisitos: 10.1, 10.3_

  - [x] 6.2 Implementar `get_vectorstore()` como singleton: carga desde disco si `faiss_index/` existe; si no, llama a `_build_vectorstore` y persiste el índice con `faiss.save_local`.
    - Si la carga falla (índice corrupto), reconstruir automáticamente.
    - _Requisitos: 10.2, 10.4, 10.5_

- [x] 7. Implementar la tool de RAG (`buscar_en_documentos` en `backend/app/tools.py` — parte 2)
  - Añadir la función `buscar_en_documentos(pregunta: str)` decorada con `@tool`.
  - Llamar a `get_vectorstore().similarity_search(pregunta, k=4)`.
  - Incluir la fuente (nombre del PDF tomado de `doc.metadata["source"]`) en cada fragmento del resultado.
  - Retornar mensaje informativo si no hay fragmentos relevantes.
  - _Requisitos: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ]* 7.1 Escribir property test para `buscar_en_documentos`
    - **Propiedad 5: Las tools nunca lanzan excepciones con entradas válidas**
    - **Valida: Requisito 9.5, 11.1**
    - **Propiedad 11: buscar_en_documentos incluye fuente en el resultado**
    - **Valida: Requisito 9.3**
    - Usar preguntas fijas representativas para verificar la presencia del nombre del PDF en el resultado.

- [x] 8. Implementar el agente LangChain (`backend/app/agent.py`)
  - [x] 8.1 Definir la constante `SYSTEM_PROMPT` con el contexto de la Cooperativa Minera El Dorado, indicando explícitamente que el agente responde solo con base en los resultados de las tools y declara cuando no tiene información.
    - _Requisitos: 2.5_

  - [x] 8.2 Implementar `_build_agent(vectorstore)` que instancie `ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)`, registre las 6 tools, construya el `ChatPromptTemplate` con `SystemMessage`, `MessagesPlaceholder("chat_history")`, `HumanMessagePromptTemplate` y `MessagesPlaceholder("agent_scratchpad")`, cree el agente con `create_tool_calling_agent` y devuelva `AgentExecutor(agent, tools, verbose=True, handle_parsing_errors=True, max_iterations=5)`.
    - _Requisitos: 2.1, 2.2, 2.3, 2.4, 2.6_

  - [x] 8.3 Implementar `_get_or_create_memory(sesion_id)` que gestione el dict `session_memories` creando `ConversationBufferWindowMemory(k=10, return_messages=True, memory_key="chat_history")` para sesiones nuevas.
    - _Requisitos: 3.1, 3.2, 3.3, 3.5_

  - [x] 8.4 Implementar `get_respuesta(sesion_id, pregunta)` que recupere la memoria de sesión, invoque `agent_executor.invoke({"input": pregunta, "chat_history": memoria.chat_memory.messages})`, guarde el par (pregunta, respuesta) en la memoria y retorne el string de respuesta.
    - _Requisitos: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 8.5 Escribir property tests para la capa de memoria
    - **Propiedad 3: Creación y recuperación de memoria por sesión**
    - **Valida: Requisitos 3.1, 3.2**
    - **Propiedad 4: Límite de memoria conversacional (k=10)**
    - **Valida: Requisito 3.3**
    - Usar `hypothesis` con `st.text(min_size=1)` para `sesion_id`; verificar identidad del objeto y límite de 10 pares en memoria.

- [x] 9. Implementar el entry point FastAPI (`backend/app/main.py`)
  - [x] 9.1 Escribir el `lifespan` de FastAPI que llame a `get_vectorstore()` y `_build_agent(vectorstore)` una sola vez en startup, almacenando el `AgentExecutor` como estado de la aplicación.
    - _Requisitos: 2.6, 10.2, 10.5_

  - [x] 9.2 Implementar el endpoint `POST /preguntar` que valide el request con `PreguntaRequest`, llame a `get_respuesta(sesion_id, pregunta)`, devuelva `RespuestaResponse` con HTTP 200, y capture excepciones devolviendo HTTP 503 (cuando el error sea de la API de Google) o HTTP 500 (para otros errores internos).
    - _Requisitos: 1.1, 1.2, 1.3, 1.5, 1.6_

  - [x] 9.3 Implementar el endpoint `GET /health` que devuelva `HealthResponse` con HTTP 200.
    - _Requisitos: 1.4_

  - [ ]* 9.4 Escribir tests de validación del endpoint con `TestClient` de FastAPI
    - **Propiedad 1: Validación de inputs del endpoint — no vacíos**
    - **Valida: Requisito 1.3**
    - **Propiedad 2: Respuesta siempre contiene el campo `respuesta`**
    - **Valida: Requisito 1.4** (adaptar para el endpoint `/health`)
    - Verificar HTTP 422 para `sesion_id=""`, `pregunta=""` y para campos ausentes.
    - Verificar HTTP 200 con `{"status": "ok"}` en `/health`.

- [ ] 10. Checkpoint — Verificar backend completo de forma aislada
  - Asegurarse de que todos los tests unitarios y de propiedad pasen con `pytest backend/`.
  - Consultar al usuario si hay comportamientos ambiguos del agente antes de integrar el frontend.

- [x] 11. Implementar el frontend Streamlit (`frontend/streamlit_app.py`)
  - [x] 11.1 Inicializar `st.session_state.messages` (lista vacía) y `st.session_state.sesion_id` (UUID generado con `uuid.uuid4()`) si no existen.
    - _Requisitos: 12.1, 12.2_

  - [x] 11.2 Implementar el bucle de chat: renderizar el historial desde `st.session_state.messages`, capturar la entrada del usuario con `st.chat_input`, añadir el mensaje del usuario al historial, llamar a `BACKEND_URL/preguntar` con `requests.post`, añadir la respuesta del agente al historial.
    - _Requisitos: 12.1, 12.3, 12.4_

  - [x] 11.3 Manejar errores de conexión: capturar `requests.exceptions.ConnectionError`, `requests.exceptions.Timeout` y códigos HTTP de error; mostrar `"⚠️ No se pudo conectar con el servidor. Intente nuevamente."` sin interrumpir la sesión.
    - _Requisitos: 12.5_

  - [x] 11.4 Leer `BACKEND_URL` desde `os.environ` con valor por defecto `http://localhost:8000`; no importar ningún módulo de `backend/app/`.
    - _Requisitos: 12.6, 12.7_

  - [ ]* 11.5 Escribir tests para la lógica de sesión del frontend
    - **Propiedad 12: Historial visual crece con cada mensaje**
    - **Valida: Requisitos 12.1, 12.4**
    - Extraer la lógica de gestión de historial a una función pura `agregar_turno(messages, pregunta, respuesta)` y testear que devuelve `len(messages) + 2` entradas.

- [x] 12. Crear Dockerfiles y docker-compose
  - [x] 12.1 Crear `backend/Dockerfile` que use `python:3.11-slim` como base, copie `requirements.txt`, instale dependencias, copie `app/` y `data/`, y ejecute `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
    - _Requisitos: 13.1, 13.4, 13.8_

  - [x] 12.2 Crear `frontend/Dockerfile` que use `python:3.11-slim`, copie `requirements.txt`, instale dependencias, copie `streamlit_app.py` y ejecute `streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0`.
    - _Requisitos: 13.2, 13.5, 13.8_

  - [x] 12.3 Crear `docker-compose.yml` en la raíz con dos servicios: `backend` (build `./backend`, puerto `8000:8000`, variable de entorno `GOOGLE_API_KEY`) y `frontend` (build `./frontend`, puerto `8501:8501`, variable de entorno `BACKEND_URL=http://backend:8000`, dependencia de `backend`).
    - _Requisitos: 13.3, 13.4, 13.5_

- [x] 13. Crear el script de validación end-to-end (`backend/test_local.py`)
  - Importar `get_respuesta` desde `app.agent`.
  - Definir entre 6 y 8 preguntas organizadas por rol: al menos 2 para Supervisor de Área (asistencia, incidencias, molinos), al menos 2 para Inspector de Molienda (grupo, molino asignado, período) y al menos 2 para Administrativo de Acopio (estado de cargas, procedimientos).
  - Iterar sobre las preguntas llamando a `get_respuesta("test-local", pregunta)` e imprimir cada pregunta y respuesta de forma legible.
  - Capturar cualquier excepción por pregunta e imprimirla sin interrumpir la ejecución de las demás.
  - _Requisitos: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

- [ ] 14. Checkpoint final — Asegurar que todos los tests pasen
  - Ejecutar `pytest backend/` y verificar que pasan todos los tests unitarios y de propiedad.
  - Consultar al usuario si surgen preguntas sobre el comportamiento del sistema antes de considerar el trabajo completo.

## Notas

- Las sub-tareas marcadas con `*` son opcionales y pueden omitirse para una entrega MVP más rápida.
- Las sub-tareas sin `*` son obligatorias y deben completarse antes de avanzar a la tarea siguiente.
- Cada tarea referencia los requisitos específicos del `requirements.md` para trazabilidad.
- Los property tests usan la librería `hypothesis`; ya está incluida en `backend/requirements.txt`.
- El índice FAISS generado en `faiss_index/` queda excluido del repositorio por `.gitignore`.
- Los archivos CSV deben quedar en `backend/data/` (no en `backend/data/documentos/`) para que las tools los encuentren en la ruta esperada.
