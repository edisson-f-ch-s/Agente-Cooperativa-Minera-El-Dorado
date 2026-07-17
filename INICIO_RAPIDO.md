# 🚀 Guía de Inicio Rápido — AlurAgente

## Paso 1: Obtener tu API Key de Google Gemini (GRATIS)

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **"Create API Key"**
4. Copia la clave generada

⚠️ **Importante**: La capa gratuita de Gemini 2.0 Flash es suficiente para desarrollo y pruebas.

---

## Paso 2: Configurar la clave en el proyecto

### Opción A: Con Docker Compose (Recomendado)

```bash
# 1. Crear archivo .env en la raíz del proyecto
cp .env.example .env

# 2. Editar .env y pegar tu API key
nano .env   # o usa tu editor favorito
# Debe quedar: GOOGLE_API_KEY=tu_clave_aqui

# 3. Levantar el proyecto completo
docker compose up
```

Espera a que se construyan las imágenes (primera vez tarda ~2-3 minutos).

**¡Listo!** Accede a:
- **Frontend (chat)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Docs API**: http://localhost:8000/docs

---

### Opción B: Instalación Local (sin Docker)

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
nano .env  # Agrega tu GOOGLE_API_KEY

# Iniciar servidor
uvicorn app.main:app --reload
```

Backend corriendo en http://localhost:8000

#### Frontend (en otra terminal)

```bash
cd frontend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar URL del backend (opcional si usas localhost:8000)
cp .env.example .env

# Iniciar frontend
streamlit run streamlit_app.py
```

Frontend corriendo en http://localhost:8501

---

## Paso 3: Pruebas sin Frontend (Opcional)

Si quieres probar el agente directamente desde la terminal:

```bash
cd backend
source venv/bin/activate

# Configurar API key en la sesión
export GOOGLE_API_KEY='tu_clave_aqui'

# Ejecutar script de pruebas
python test_local.py
```

Verás 8 preguntas de ejemplo procesadas directamente por el agente.

---

## 📝 Ejemplos de Consultas

Una vez que el frontend esté corriendo, prueba estas preguntas:

**Supervisor de Área:**
- "¿Cuántos trabajadores faltaron esta semana por falta de EPP?"
- "Muéstrame las incidencias de alta severidad pendientes"
- "¿Qué molinos requieren reevaluación?"

**Inspector de Molienda:**
- "¿A qué grupo pertenece el inspector INS-005?"
- "¿Qué molino tiene asignado mi grupo este mes?"

**Administrativo de Acopio:**
- "¿Cuántas cargas están en estado de molienda?"
- "Muéstrame las cargas asignadas al molino M-03"

**Documentación interna:**
- "¿Cuáles son los requisitos de EPP según el protocolo?"
- "¿Cómo funciona la rotación de inspectores?"

---

## 🛑 Solución de Problemas

### Error: "El servicio de IA no está disponible"
- Verifica que la `GOOGLE_API_KEY` esté configurada correctamente
- Revisa que la clave sea válida en [Google AI Studio](https://aistudio.google.com/app/apikey)

### El frontend no se conecta al backend
- Verifica que el backend esté corriendo en `http://localhost:8000`
- Prueba acceder a `http://localhost:8000/health` — debe devolver `{"status": "ok"}`

### Docker: Error al construir imágenes
- Asegúrate de tener Docker y Docker Compose instalados
- Verifica que no haya otros servicios usando los puertos 8000 o 8501

---

## 🎓 Siguiente Paso

Lee el [README.md](README.md) completo para entender la arquitectura, los requisitos y opciones de despliegue.
