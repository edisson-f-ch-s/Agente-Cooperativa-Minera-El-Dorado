"""
Script de validación end-to-end para AlurAgente.
Ejecuta preguntas de ejemplo directamente contra agent.py sin levantar FastAPI.
"""
import os
import sys

# Asegurar que tenemos GOOGLE_API_KEY configurada
if not os.environ.get("GOOGLE_API_KEY"):
    print("ERROR: Variable de entorno GOOGLE_API_KEY no configurada.")
    print("Configúrala con: export GOOGLE_API_KEY='tu_clave_aqui'")
    sys.exit(1)

from app.agent import get_respuesta
from app.vectorstore import get_vectorstore

print("═" * 80)
print("  TEST LOCAL DE ALURAGENTE — Cooperativa Minera El Dorado")
print("═" * 80)
print()

# Inicializar vectorstore (se hace una sola vez)
print("[INFO] Inicializando vectorstore FAISS...")
get_vectorstore()
print("[INFO] Vectorstore listo.\n")

# ── Preguntas de prueba organizadas por rol ───────────────────────────────────

PREGUNTAS = [
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

# ── Ejecución de preguntas ─────────────────────────────────────────────────────

sesion_id = "test-local"

for i, (rol, pregunta) in enumerate(PREGUNTAS, start=1):
    print(f"{'─' * 80}")
    print(f"[{i}/{len(PREGUNTAS)}] ROL: {rol}")
    print(f"PREGUNTA: {pregunta}")
    print()
    
    try:
        respuesta = get_respuesta(sesion_id, pregunta)
        print(f"RESPUESTA:\n{respuesta}")
    except Exception as exc:
        print(f"ERROR: {exc}")
    
    print()

print("═" * 80)
print("  Test completado.")
print("═" * 80)
