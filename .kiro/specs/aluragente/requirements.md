# Documento de Requisitos: AlurAgente

## Introducción

AlurAgente es un agente conversacional de IA para la **Cooperativa Minera El Dorado**, diseñado para el Área de Acopio de Material Aurífero. El sistema permite a supervisores, inspectores y administrativos consultar en lenguaje natural datos operativos (CSV) y documentación interna (PDF) sin necesidad de conocimientos técnicos.

El sistema se compone de:
- Un **backend FastAPI** que orquesta un agente LangChain con tool-calling sobre Gemini 2.0 Flash.
- Un **frontend Streamlit** que se comunica exclusivamente por HTTP con el backend.
- **6 tools Python puras** que acceden a datos CSV vía Pandas y a documentos PDF vía FAISS.
- Infraestructura de contenedores Docker para desarrollo local y despliegue independiente de cada servicio.

---

## Glosario

- **AlurAgente**: El sistema completo agente conversacional de IA descrito en este documento.
- **Backend**: El servicio FastAPI que expone la API HTTP y orquesta el agente.
- **Frontend**: La aplicación Streamlit que proporciona la interfaz de chat al usuario.
- **AgentExecutor**: El componente LangChain que coordina el LLM con las tools.
- **Tool**: Una función Python pura registrada en el AgentExecutor que accede a datos estructurados o documentos.
- **LLM**: El modelo de lenguaje Gemini 2.0 Flash utilizado para razonamiento y generación de respuestas.
- **FAISS_Index**: El índice vectorial construido sobre los 5 PDFs de la Cooperativa para búsqueda semántica.
- **Sesion**: Un contexto conversacional identificado por un `sesion_id` único que mantiene historial de mensajes.
- **Memoria_Sesion**: Objeto `ConversationBufferWindowMemory` que almacena los últimos k intercambios de una sesión.
- **CSV_Data**: Los 6 archivos CSV con datos operativos: trabajadores, molinos, grupos_inspectores, asistencia, cargas, incidencias.
- **PDF_Docs**: Los 5 documentos PDF internos de la Cooperativa almacenados en `backend/data/documentos/`.
- **GOOGLE_API_KEY**: Variable de entorno que contiene la clave de acceso a la API de Google Gemini.
- **BACKEND_URL**: Variable de entorno leída por el frontend con la URL base del backend.
- **sesion_id**: Identificador de string único (UUID) que diferencia las conversaciones de distintos usuarios.
- **System_Prompt**: Instrucción de contexto fija inyectada al LLM que define el rol y las restricciones del agente.

---

## Requisitos

### Requisito 1: Endpoint de Consulta HTTP

**User Story:** Como usuario de la Cooperativa Minera El Dorado, quiero enviar preguntas en lenguaje natural al agente a través de una API HTTP, para obtener respuestas basadas en los datos operativos sin necesidad de acceso directo al sistema.

#### Criterios de Aceptación

1. THE Backend SHALL exponer un endpoint `POST /preguntar` que acepte un cuerpo JSON con los campos `sesion_id` (string no vacío) y `pregunta` (string no vacío).
2. WHEN el Backend recibe una solicitud válida en `POST /preguntar`, THE Backend SHALL devolver una respuesta HTTP 200 con un objeto JSON que contenga el campo `respuesta` de tipo string.
3. WHEN el campo `sesion_id` o `pregunta` están vacíos o ausentes en la solicitud, THE Backend SHALL devolver HTTP 422 con un mensaje de error de validación.
4. THE Backend SHALL exponer un endpoint `GET /health` que devuelva HTTP 200 con el objeto JSON `{"status": "ok"}`.
5. WHEN ocurre un error interno al procesar la consulta, THE Backend SHALL devolver HTTP 500 con un objeto JSON que contenga el campo `detail` con un mensaje legible en lenguaje natural.
6. WHEN la clave GOOGLE_API_KEY es inválida o el servicio de LLM no está disponible, THE Backend SHALL devolver HTTP 503 con el mensaje `{"detail": "El servicio de IA no está disponible temporalmente."}`.

---

### Requisito 2: Agente Conversacional con Tool-Calling

**User Story:** Como usuario, quiero que el agente comprenda mi pregunta y seleccione automáticamente las fuentes de datos correctas para responderla, de modo que no tenga que especificar qué datos consultar.

#### Criterios de Aceptación

1. THE AgentExecutor SHALL estar configurado con las 6 tools registradas: `consultar_asistencia`, `consultar_cargas`, `consultar_incidencias`, `consultar_molinos`, `consultar_grupo_inspector` y `buscar_en_documentos`.
2. THE AgentExecutor SHALL utilizar el LLM `gemini-2.0-flash` mediante `ChatGoogleGenerativeAI` con `temperature=0`.
3. THE AgentExecutor SHALL tener configurado `max_iterations=5` para prevenir bucles infinitos en tool-calling.
4. THE AgentExecutor SHALL tener configurado `handle_parsing_errors=True` para que errores de parsing del LLM no colapsen el servidor.
5. THE AgentExecutor SHALL inyectar un System_Prompt que instruya al agente a responder únicamente con base en los resultados de las tools y a declarar explícitamente cuando la información no está disponible.
6. WHEN el agente es construido durante el startup de la aplicación, THE Backend SHALL invocar `_build_agent()` una sola vez y reutilizar el AgentExecutor en todas las solicitudes posteriores.

---

### Requisito 3: Memoria Conversacional por Sesión

**User Story:** Como usuario, quiero que el agente recuerde el contexto de preguntas anteriores dentro de mi sesión, para poder hacer preguntas de seguimiento sin repetir contexto.

#### Criterios de Aceptación

1. WHEN el Backend recibe una solicitud con un `sesion_id` nuevo, THE Backend SHALL crear una nueva Memoria_Sesion de tipo `ConversationBufferWindowMemory` con `k=10` para ese `sesion_id`.
2. WHEN el Backend recibe una solicitud con un `sesion_id` existente, THE Backend SHALL recuperar y utilizar la Memoria_Sesion previamente creada para ese `sesion_id`.
3. WHILE una sesión está activa, THE Backend SHALL conservar los últimos 10 intercambios (pregunta + respuesta) en la Memoria_Sesion correspondiente.
4. WHEN el agente genera una respuesta para una sesión, THE Backend SHALL agregar el par (pregunta, respuesta) a la Memoria_Sesion de esa sesión antes de devolver la respuesta HTTP.
5. THE Backend SHALL mantener todas las sesiones activas en un diccionario en memoria del proceso FastAPI durante el tiempo de vida del servidor.

---

### Requisito 4: Tool — Consulta de Asistencia

**User Story:** Como supervisor de área o inspector, quiero consultar los registros de asistencia del personal, para verificar faltas, motivos de ausencia y cumplimiento de EPP.

#### Criterios de Aceptación

1. THE Tool `consultar_asistencia` SHALL aceptar los parámetros opcionales `id_trabajador` (str), `fecha_desde` (str en formato YYYY-MM-DD) y `fecha_hasta` (str en formato YYYY-MM-DD), todos con valor por defecto `None`.
2. WHEN todos los parámetros son `None`, THE Tool `consultar_asistencia` SHALL devolver un resumen estadístico con total de registros, conteo de asistencia y conteo de EPP completo más las primeras 20 filas del dataset.
3. WHEN se proporciona `id_trabajador`, THE Tool `consultar_asistencia` SHALL devolver únicamente los registros correspondientes a ese trabajador.
4. WHEN se proporcionan `fecha_desde` y/o `fecha_hasta`, THE Tool `consultar_asistencia` SHALL devolver únicamente los registros dentro del rango de fechas especificado.
5. IF los filtros aplicados no producen ningún registro, THEN THE Tool `consultar_asistencia` SHALL devolver el string `"No se encontraron registros de asistencia con los filtros indicados."`.
6. THE Tool `consultar_asistencia` SHALL devolver siempre un string no vacío para cualquier combinación válida de parámetros.
7. THE Tool `consultar_asistencia` SHALL incluir en su resultado los campos `fecha`, `id_trabajador`, `asistio`, `motivo_falta` y `epp_completo`.

---

### Requisito 5: Tool — Consulta de Cargas

**User Story:** Como administrativo de acopio, quiero consultar el estado y seguimiento de las cargas de material aurífero, para conocer su ubicación y tiempos de entrega.

#### Criterios de Aceptación

1. THE Tool `consultar_cargas` SHALL aceptar los parámetros opcionales `estado` (str: `almacenado | en_transporte | en_molienda | entregado`), `molino_id` (str) y `carga_id` (str), todos con valor por defecto `None`.
2. WHEN se aplican filtros, THE Tool `consultar_cargas` SHALL devolver únicamente las filas que cumplan todos los filtros especificados de forma acumulativa.
3. WHEN el resultado filtrado contiene más de 20 filas, THE Tool `consultar_cargas` SHALL devolver las 20 cargas más recientes ordenadas por `fecha_recepcion` descendente, precedidas por un mensaje indicando el total encontrado.
4. IF los filtros aplicados no producen ninguna carga, THEN THE Tool `consultar_cargas` SHALL devolver el string `"No se encontraron cargas con los filtros indicados."`.
5. THE Tool `consultar_cargas` SHALL incluir en su resultado los campos `carga_id`, `fecha_recepcion`, `cantidad_kg`, `transportista_id`, `molino_asignado`, `estado`, `tiempo_estimado_entrega` y `fecha_entrega_real`.
6. THE Tool `consultar_cargas` SHALL devolver siempre un string no vacío para cualquier combinación válida de parámetros.

---

### Requisito 6: Tool — Consulta de Incidencias

**User Story:** Como supervisor de área, quiero consultar las incidencias registradas del área, para hacer seguimiento de problemas pendientes y evaluar su severidad.

#### Criterios de Aceptación

1. THE Tool `consultar_incidencias` SHALL aceptar los parámetros opcionales `tipo` (str: `trabajador | transportista | molino`), `severidad` (str: `baja | media | alta`), `estado` (str: `pendiente | resuelto | requiere_reevaluacion`) y `fecha_desde` (str en formato YYYY-MM-DD), todos con valor por defecto `None`.
2. WHEN se aplican filtros, THE Tool `consultar_incidencias` SHALL devolver únicamente las incidencias que cumplan todos los filtros especificados de forma acumulativa.
3. IF los filtros aplicados no producen ninguna incidencia, THEN THE Tool `consultar_incidencias` SHALL devolver un string no vacío con un mensaje informativo.
4. THE Tool `consultar_incidencias` SHALL incluir en su resultado los campos `incidencia_id`, `fecha`, `tipo`, `entidad_id`, `descripcion`, `severidad` y `estado`.
5. THE Tool `consultar_incidencias` SHALL devolver siempre un string no vacío para cualquier combinación válida de parámetros.

---

### Requisito 7: Tool — Consulta de Molinos

**User Story:** Como supervisor de área, quiero consultar el estado y capacidad de los molinos/trapiches, para planificar la distribución de cargas y gestionar reevaluaciones.

#### Criterios de Aceptación

1. THE Tool `consultar_molinos` SHALL aceptar los parámetros opcionales `estado` (str: `activo | requiere_reevaluacion`) y `molino_id` (str), ambos con valor por defecto `None`.
2. WHEN se aplican filtros, THE Tool `consultar_molinos` SHALL devolver únicamente los molinos que cumplan los filtros especificados.
3. IF los filtros aplicados no producen ningún molino, THEN THE Tool `consultar_molinos` SHALL devolver un string no vacío con un mensaje informativo.
4. THE Tool `consultar_molinos` SHALL incluir en su resultado los campos `molino_id`, `nombre`, `estado`, `motivo_estado` y `capacidad_ton_dia`.
5. THE Tool `consultar_molinos` SHALL devolver siempre un string no vacío para cualquier combinación válida de parámetros.

---

### Requisito 8: Tool — Consulta de Grupos de Inspectores

**User Story:** Como inspector de molienda, quiero consultar mi grupo de inspección, el molino asignado y el período de rotación, para conocer mis responsabilidades del mes.

#### Criterios de Aceptación

1. THE Tool `consultar_grupo_inspector` SHALL aceptar los parámetros opcionales `id_trabajador` (str), `grupo_id` (str) y `periodo` (str en formato YYYY-MM), todos con valor por defecto `None`.
2. WHEN se aplican filtros, THE Tool `consultar_grupo_inspector` SHALL devolver únicamente los grupos que cumplan los filtros especificados.
3. IF los filtros aplicados no producen ningún grupo, THEN THE Tool `consultar_grupo_inspector` SHALL devolver un string no vacío con un mensaje informativo.
4. THE Tool `consultar_grupo_inspector` SHALL incluir en su resultado los campos `grupo_id`, `periodo`, `molino_asignado`, `integrantes` y `lider_grupo`.
5. THE Tool `consultar_grupo_inspector` SHALL devolver siempre un string no vacío para cualquier combinación válida de parámetros.

---

### Requisito 9: Tool — Búsqueda en Documentos (RAG)

**User Story:** Como cualquier usuario, quiero consultar procedimientos, normas y políticas internas en lenguaje natural, para obtener información de los manuales sin tener que leerlos completos.

#### Criterios de Aceptación

1. THE Tool `buscar_en_documentos` SHALL aceptar un parámetro obligatorio `pregunta` de tipo string no vacío.
2. WHEN se invoca `buscar_en_documentos` con una pregunta válida, THE FAISS_Index SHALL ejecutar una búsqueda de similitud semántica y devolver los 4 fragmentos (`chunks`) más relevantes.
3. THE Tool `buscar_en_documentos` SHALL incluir en su resultado la fuente (nombre del archivo PDF) de cada fragmento devuelto para garantizar trazabilidad.
4. IF la búsqueda semántica no produce fragmentos relevantes, THEN THE Tool `buscar_en_documentos` SHALL devolver el string `"No se encontró información relevante en los documentos internos."`.
5. THE Tool `buscar_en_documentos` SHALL devolver siempre un string no vacío para cualquier pregunta válida.

---

### Requisito 10: Construcción y Persistencia del Índice FAISS

**User Story:** Como operador del sistema, quiero que el índice vectorial sobre los PDFs se construya automáticamente al iniciar el backend y se persista en disco, para que los reinicios del servidor sean rápidos sin reconstruir el índice cada vez.

#### Criterios de Aceptación

1. WHEN el Backend inicia y el directorio `faiss_index/` no existe en disco, THE Backend SHALL construir el FAISS_Index cargando los 5 PDFs con `PyPDFLoader`, dividiéndolos con `RecursiveCharacterTextSplitter` (chunk_size=1000, overlap=200) y guardándolo en disco.
2. WHEN el Backend inicia y el directorio `faiss_index/` ya existe en disco, THE Backend SHALL cargar el FAISS_Index desde disco sin reconstruirlo.
3. IF uno o más PDFs no están disponibles durante la construcción del índice, THEN THE Backend SHALL registrar una advertencia y construir el FAISS_Index con los PDFs disponibles, sin detener la inicialización.
4. WHEN el FAISS_Index en disco está corrupto o no se puede cargar, THE Backend SHALL reconstruirlo automáticamente desde los PDFs disponibles.
5. THE Backend SHALL exponer el FAISS_Index como un singleton disponible para todas las invocaciones de `buscar_en_documentos` durante el tiempo de vida del proceso.

---

### Requisito 11: Propiedades de Calidad de las Tools

**User Story:** Como desarrollador del sistema, quiero que las tools sean funciones puras, robustas e idempotentes, para garantizar la corrección del agente independientemente del volumen de consultas.

#### Criterios de Aceptación

1. THE Tool de cada una de las 6 funciones SHALL devolver siempre un string no vacío para cualquier combinación válida de parámetros de entrada, incluyendo el caso en que todos los parámetros opcionales sean `None`.
2. WHEN una Tool es invocada dos veces consecutivas con los mismos parámetros, THE Tool SHALL devolver el mismo resultado en ambas invocaciones (idempotencia).
3. THE resultado de cualquier Tool SHALL tener una longitud en caracteres menor a 10,000 para cualquier combinación válida de parámetros de entrada.
4. WHEN los filtros de una Tool no producen filas en el dataset correspondiente, THE Tool SHALL devolver un string no vacío con un mensaje descriptivo en lenguaje natural, sin lanzar una excepción.
5. IF ocurre un error de acceso al archivo CSV (archivo no encontrado o formato inválido), THEN THE Tool SHALL capturar la excepción y devolver el string `"No se pudo acceder a los datos de [entidad]. Contacte al administrador."` en lugar de propagar la excepción.

---

### Requisito 12: Frontend Streamlit — Interfaz de Chat

**User Story:** Como usuario de la Cooperativa, quiero interactuar con el agente a través de una interfaz de chat visual en el navegador, para realizar consultas de forma intuitiva sin conocimientos técnicos.

#### Criterios de Aceptación

1. THE Frontend SHALL mantener el historial de mensajes de la conversación en `st.session_state.messages` durante toda la sesión del navegador.
2. WHEN el Frontend se inicializa por primera vez en una sesión del navegador, THE Frontend SHALL generar un `sesion_id` único (UUID) y almacenarlo en `st.session_state.sesion_id`.
3. WHEN el usuario envía una pregunta, THE Frontend SHALL realizar un `POST` HTTP al endpoint `BACKEND_URL/preguntar` con el cuerpo `{"sesion_id": sesion_id, "pregunta": pregunta}`.
4. WHEN el Backend devuelve una respuesta exitosa, THE Frontend SHALL agregar tanto la pregunta del usuario como la respuesta del agente al historial visual `st.session_state.messages`.
5. IF el Backend no responde (timeout, `ConnectionError`) o devuelve un código de error HTTP, THEN THE Frontend SHALL mostrar el mensaje `"⚠️ No se pudo conectar con el servidor. Intente nuevamente."` sin detener la sesión.
6. THE Frontend SHALL leer la URL del backend exclusivamente desde la variable de entorno `BACKEND_URL`, con valor por defecto `http://localhost:8000`.
7. THE Frontend SHALL comunicarse con el Backend exclusivamente mediante requests HTTP; no deberá importar módulos del backend (`app.agent`, `app.tools`, etc.).

---

### Requisito 13: Infraestructura y Despliegue

**User Story:** Como operador del sistema, quiero poder levantar el backend y el frontend con un solo comando en desarrollo local, y desplegar cada servicio de forma independiente en producción, para facilitar el mantenimiento y la escalabilidad.

#### Criterios de Aceptación

1. THE Backend SHALL tener un `Dockerfile` en `backend/Dockerfile` que construya una imagen ejecutable del servicio FastAPI con todas sus dependencias fijadas con versiones exactas (`==`).
2. THE Frontend SHALL tener un `Dockerfile` en `frontend/Dockerfile` que construya una imagen ejecutable del servicio Streamlit con todas sus dependencias fijadas con versiones exactas (`==`).
3. THE proyecto SHALL incluir un `docker-compose.yml` en la raíz que defina dos servicios (`backend` y `frontend`) que puedan levantarse juntos con el comando `docker compose up`.
4. WHEN el Backend inicia en un contenedor Docker, THE Backend SHALL leer la clave `GOOGLE_API_KEY` exclusivamente desde variables de entorno o secretos de la plataforma de despliegue.
5. WHEN el Frontend inicia en un contenedor Docker, THE Frontend SHALL leer la URL del backend exclusivamente desde la variable de entorno `BACKEND_URL`.
6. THE proyecto SHALL incluir archivos `backend/.env.example` y `frontend/.env.example` como referencia de las variables de entorno requeridas.
7. THE proyecto SHALL incluir un archivo `.gitignore` que excluya al menos: `.env`, `__pycache__/`, `*.faiss`, archivos de índice FAISS y entornos virtuales `venv/`.
8. THE Backend y THE Frontend SHALL poder desplegarse como servicios independientes en plataformas como Render o Hugging Face Spaces sin modificaciones al código fuente.

---

### Requisito 14: Pruebas de Validación Local (test_local.py)

**User Story:** Como desarrollador, quiero un script de prueba end-to-end que valide el agente directamente sin pasar por la capa HTTP, para verificar rápidamente el comportamiento del agente durante el desarrollo.

#### Criterios de Aceptación

1. THE `test_local.py` SHALL ejecutar entre 6 y 8 preguntas de ejemplo invocando directamente la función `get_respuesta` de `agent.py`, sin instanciar el servidor FastAPI.
2. THE `test_local.py` SHALL incluir al menos 2 preguntas correspondientes al rol de Supervisor de Área (asistencia, incidencias, estado de molinos).
3. THE `test_local.py` SHALL incluir al menos 2 preguntas correspondientes al rol de Inspector de Molienda (grupo asignado, molino, período).
4. THE `test_local.py` SHALL incluir al menos 2 preguntas correspondientes al rol de Administrativo de Acopio (estado de cargas, procedimientos documentados).
5. WHEN se ejecuta `test_local.py`, THE Script SHALL imprimir cada pregunta y su respuesta en la salida estándar de forma legible.
6. WHEN se ejecuta `test_local.py`, THE Script SHALL completar la ejecución de todas las preguntas sin detener el proceso por excepciones no controladas.

---

### Requisito 15: Estructura de Archivos del Proyecto

**User Story:** Como desarrollador que clone el repositorio, quiero encontrar el proyecto organizado con una estructura de carpetas predecible, para localizar rápidamente cada componente sin necesidad de documentación adicional.

#### Criterios de Aceptación

1. THE proyecto SHALL contener la estructura de directorios: `backend/app/`, `backend/data/documentos/`, `frontend/` en la raíz del repositorio.
2. THE `backend/app/` SHALL contener exactamente los módulos: `__init__.py`, `main.py`, `agent.py`, `tools.py`, `vectorstore.py` y `schemas.py`.
3. THE `backend/data/` SHALL contener los 6 archivos CSV: `trabajadores.csv`, `molinos.csv`, `grupos_inspectores.csv`, `asistencia.csv`, `cargas.csv` e `incidencias.csv`.
4. THE `backend/data/documentos/` SHALL contener los 5 archivos PDF: `Manual_General_Area_de_Acopio.pdf`, `Protocolo_de_Seguridad_y_EPP.pdf`, `Reglamento_de_Rotacion_de_Inspectores.pdf`, `Procedimiento_Recepcion_y_Entrega_de_Material.pdf` y `Politica_de_Evaluacion_de_Molinos.pdf`.
5. THE `frontend/` SHALL contener al menos: `streamlit_app.py`, `requirements.txt`, `Dockerfile` y `.env.example`.
