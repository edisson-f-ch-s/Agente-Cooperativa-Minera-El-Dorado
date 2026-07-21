"""
Script de validación end-to-end para AlurAgente.
Ejecuta preguntas de ejemplo directamente contra agent.py sin levantar FastAPI.

Uso:
    GOOGLE_API_KEY=<key> python test_local.py
    GOOGLE_API_KEY=<key> python test_local.py --quick   # Solo 2 preguntas (consume menos cuota)
"""
import os
import sys
import time

# Asegurar que tenemos GOOGLE_API_KEY configurada
if not os.environ.get("GOOGLE_API_KEY"):
    print("ERROR: Variable de entorno GOOGLE_API_KEY no configurada.")
    print("Configúrala con: export GOOGLE_API_KEY='tu_clave_aqui'")
    sys.exit(1)

from app.agent import get_respuesta, initialize_agent
from app.vectorstore import get_vectorstore

print("═" * 80)
print("  TEST LOCAL DE ALURAGENTE — Cooperativa Minera El Dorado")
print("═" * 80)
print()

# Inicializar vectorstore (se hace una sola vez)
print("[INFO] Inicializando vectorstore FAISS...")
get_vectorstore()
print("[INFO] Vectorstore listo.\n")

print("[INFO] Inicializando agente (selección de modelo Gemini)...")
initialize_agent()
print("[INFO] Agente listo.\n")

# ── Preguntas de prueba organizadas por rol ───────────────────────────────────

PREGUNTAS_COMPLETAS = [
    # Supervisor de Área
    ("Supervisor de Área", "¿Cuántos trabajadores faltaron en la última semana por falta de EPP?"),
    ("Supervisor de Área", "Muéstrame las incidencias de alta severidad que están pendientes."),
    ("Supervisor de Área", "¿Qué molinos requieren reevaluación?"),
    # Inspector de Molienda
    ("Inspector de Molienda", "¿A qué grupo pertenece el inspector INS-005 en julio de 2026?"),
    ("Inspector de Molienda", "¿Qué molino tiene asignado el grupo G-02 en el periodo 2026-07?"),
    # Administrativo de Acopio
    ("Administrativo de Acopio", "¿Cuántas cargas están actualmente en estado de molienda?"),
    ("Administrativo de Acopio", "¿Cuáles son las cargas asignadas al molino M-03?"),
    # Consulta documental (cualquier rol)
    ("Cualquier rol", "¿Cuáles son los requisitos de EPP según el protocolo de seguridad?"),
]

# Modo rápido: 2 preguntas representativas para validar sin consumir cuota
PREGUNTAS_QUICK = [
    ("Inspector de Molienda", "¿A qué grupo pertenece el inspector INS-005 en julio de 2026?"),
    ("Cualquier rol", "¿Cuáles son los requisitos de EPP según el protocolo de seguridad?"),
]

quick_mode = "--quick" in sys.argv
preguntas = PREGUNTAS_QUICK if quick_mode else PREGUNTAS_COMPLETAS

if quick_mode:
    print("[INFO] Modo rápido: ejecutando 2 preguntas para conservar cuota de API.\n")

# ── Ejecución de preguntas ─────────────────────────────────────────────────────

# Pausa entre preguntas para no exceder el RPM (requests per minute) del tier gratuito.
# El tier gratuito de Gemini permite ~15 RPM; con pausa de 8s se queda en ~7 RPM.
PAUSA_ENTRE_PREGUNTAS = 8  # segundos

sesion_id = "test-local"

for i, (rol, pregunta) in enumerate(preguntas, start=1):
    print(f"{'─' * 80}")
    print(f"[{i}/{len(preguntas)}] ROL: {rol}")
    print(f"PREGUNTA: {pregunta}")
    print()

    try:
        respuesta = get_respuesta(sesion_id, pregunta)
        print(f"RESPUESTA:\n{respuesta}")
    except Exception as exc:
        print(f"ERROR: {exc}")

    print()

    # Pausa entre preguntas para respetar el rate limit del tier gratuito
    if i < len(preguntas):
        print(f"[INFO] Esperando {PAUSA_ENTRE_PREGUNTAS}s para respetar el rate limit...")
        time.sleep(PAUSA_ENTRE_PREGUNTAS)

print("═" * 80)
print("  Test completado.")
print("═" * 80)
