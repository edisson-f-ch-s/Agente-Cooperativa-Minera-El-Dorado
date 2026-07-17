"""
Tools para AlurAgente - Funciones puras para consultar datos CSV
"""
from pathlib import Path
from typing import Optional
import pandas as pd
from langchain_core.tools import tool


# Directorio base de datos
DATA_DIR = Path(__file__).parent.parent / "data" / "documentos"


@tool
def consultar_asistencia(
    id_trabajador: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None
) -> str:
    """
    Consulta el registro de asistencia del personal.
    Filtra por trabajador y/o rango de fechas.
    Devuelve asistencia, motivo de falta y cumplimiento de EPP.
    
    Usar cuando el usuario pregunta sobre asistencia, faltas o EPP de personal.
    
    Args:
        id_trabajador: ID del trabajador (ej: "INS-005", "SUP-001"). Opcional.
        fecha_desde: Fecha inicial del rango en formato YYYY-MM-DD. Opcional.
        fecha_hasta: Fecha final del rango en formato YYYY-MM-DD. Opcional.
    
    Returns:
        String con los registros de asistencia encontrados o mensaje informativo.
    """
    try:
        # Leer CSV de asistencia
        csv_path = DATA_DIR / "asistencia.csv"
        df = pd.read_csv(csv_path)
        df["fecha"] = pd.to_datetime(df["fecha"])
        
        # Aplicar filtros acumulativos
        if id_trabajador is not None:
            df = df[df["id_trabajador"] == id_trabajador]
        
        if fecha_desde is not None:
            df = df[df["fecha"] >= pd.to_datetime(fecha_desde)]
        
        if fecha_hasta is not None:
            df = df[df["fecha"] <= pd.to_datetime(fecha_hasta)]
        
        # Si no hay resultados
        if df.empty:
            return "No se encontraron registros de asistencia con los filtros indicados."
        
        # Resumen estadístico para consultas sin filtro de trabajador y más de 50 registros
        if id_trabajador is None and len(df) > 50:
            total = len(df)
            presentes = len(df[df["asistio"] == "si"])
            epp_ok = len(df[df["epp_completo"] == "si"])
            resumen = (
                f"Resumen: {total} registros. "
                f"Asistencia: {presentes}/{total}. "
                f"EPP completo: {epp_ok}/{total}.\n\n"
            )
            return resumen + df.head(20).to_string(index=False)
        
        # Resultado normal
        return f"{len(df)} registro(s) encontrado(s).\n\n" + df.to_string(index=False)
    
    except FileNotFoundError:
        return "No se pudo acceder a los datos de asistencia. Contacte al administrador."
    except Exception as e:
        return f"No se pudo acceder a los datos de asistencia. Contacte al administrador."


@tool
def consultar_cargas(
    estado: Optional[str] = None,
    molino_id: Optional[str] = None,
    carga_id: Optional[str] = None
) -> str:
    """
    Consulta el estado y seguimiento de cargas de material aurífero.
    Devuelve carga_id, fecha, cantidad_kg, transportista, molino, estado y tiempos.
    
    Usar cuando el usuario pregunta sobre cargas, entregas o estado del material.
    
    Args:
        estado: Estado de la carga. Valores posibles: "almacenado", "en_transporte", 
                "en_molienda", "entregado". Opcional.
        molino_id: ID del molino asignado (ej: "M-03"). Opcional.
        carga_id: ID de la carga específica (ej: "C-0045"). Opcional.
    
    Returns:
        String con las cargas encontradas o mensaje informativo.
    """
    try:
        # Leer CSV de cargas
        csv_path = DATA_DIR / "cargas.csv"
        df = pd.read_csv(csv_path)
        
        # Aplicar filtros acumulativos
        if carga_id is not None:
            df = df[df["carga_id"] == carga_id]
        
        if estado is not None:
            df = df[df["estado"] == estado]
        
        if molino_id is not None:
            df = df[df["molino_asignado"] == molino_id]
        
        # Si no hay resultados
        if df.empty:
            return "No se encontraron cargas con los filtros indicados."
        
        # Limitar resultados para evitar contextos muy largos
        if len(df) > 20:
            resumen = f"Se encontraron {len(df)} cargas. Mostrando las 20 más recientes.\n\n"
            df = df.sort_values("fecha_recepcion", ascending=False).head(20)
        else:
            resumen = f"Se encontraron {len(df)} carga(s).\n\n"
        
        return resumen + df.to_string(index=False)
    
    except FileNotFoundError:
        return "No se pudo acceder a los datos de cargas. Contacte al administrador."
    except Exception as e:
        return f"No se pudo acceder a los datos de cargas. Contacte al administrador."


@tool
def consultar_incidencias(
    tipo: Optional[str] = None,
    severidad: Optional[str] = None,
    estado: Optional[str] = None,
    fecha_desde: Optional[str] = None
) -> str:
    """
    Consulta incidencias registradas del área de acopio.
    Devuelve descripción, severidad, estado y entidad involucrada.
    
    Usar cuando el usuario pregunta sobre incidentes, problemas o infracciones.
    
    Args:
        tipo: Tipo de incidencia. Valores posibles: "trabajador", "transportista", "molino". Opcional.
        severidad: Severidad de la incidencia. Valores posibles: "baja", "media", "alta". Opcional.
        estado: Estado de la incidencia. Valores posibles: "pendiente", "resuelto", 
                "requiere_reevaluacion". Opcional.
        fecha_desde: Fecha inicial del rango en formato YYYY-MM-DD. Opcional.
    
    Returns:
        String con las incidencias encontradas o mensaje informativo.
    """
    try:
        # Leer CSV de incidencias
        csv_path = DATA_DIR / "incidencias.csv"
        df = pd.read_csv(csv_path)
        
        # Aplicar filtros acumulativos
        if tipo is not None:
            df = df[df["tipo"] == tipo]
        
        if severidad is not None:
            df = df[df["severidad"] == severidad]
        
        if estado is not None:
            df = df[df["estado"] == estado]
        
        if fecha_desde is not None:
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df[df["fecha"] >= pd.to_datetime(fecha_desde)]
        
        # Si no hay resultados
        if df.empty:
            return "No se encontraron incidencias con los filtros indicados."
        
        return f"Se encontraron {len(df)} incidencia(s).\n\n" + df.to_string(index=False)
    
    except FileNotFoundError:
        return "No se pudo acceder a los datos de incidencias. Contacte al administrador."
    except Exception as e:
        return f"No se pudo acceder a los datos de incidencias. Contacte al administrador."


@tool
def consultar_molinos(
    estado: Optional[str] = None,
    molino_id: Optional[str] = None
) -> str:
    """
    Consulta el estado y capacidad de los molinos/trapiches.
    Devuelve nombre, estado, motivo de estado y capacidad en ton/día.
    
    Usar cuando el usuario pregunta sobre molinos, trapiches o capacidad de molienda.
    
    Args:
        estado: Estado del molino. Valores posibles: "activo", "requiere_reevaluacion". Opcional.
        molino_id: ID del molino específico (ej: "M-10"). Opcional.
    
    Returns:
        String con los molinos encontrados o mensaje informativo.
    """
    try:
        # Leer CSV de molinos
        csv_path = DATA_DIR / "molinos.csv"
        df = pd.read_csv(csv_path)
        
        # Aplicar filtros acumulativos
        if estado is not None:
            df = df[df["estado"] == estado]
        
        if molino_id is not None:
            df = df[df["molino_id"] == molino_id]
        
        # Si no hay resultados
        if df.empty:
            return "No se encontraron molinos con los filtros indicados."
        
        return f"Se encontraron {len(df)} molino(s).\n\n" + df.to_string(index=False)
    
    except FileNotFoundError:
        return "No se pudo acceder a los datos de molinos. Contacte al administrador."
    except Exception as e:
        return f"No se pudo acceder a los datos de molinos. Contacte al administrador."


@tool
def consultar_grupo_inspector(
    id_trabajador: Optional[str] = None,
    grupo_id: Optional[str] = None,
    periodo: Optional[str] = None
) -> str:
    """
    Consulta la asignación de grupos de inspectores por periodo y molino.
    Devuelve grupo, periodo, molino asignado, integrantes y líder.
    
    Usar cuando el usuario pregunta sobre grupos de inspección, rotación o asignación a molinos.
    
    Args:
        id_trabajador: ID del trabajador inspector (ej: "INS-005"). Opcional. 
                       Busca en el campo integrantes (separados por ;).
        grupo_id: ID del grupo (ej: "G-03"). Opcional.
        periodo: Periodo en formato YYYY-MM (ej: "2026-07"). Opcional.
    
    Returns:
        String con los grupos encontrados o mensaje informativo.
    """
    try:
        # Leer CSV de grupos de inspectores
        csv_path = DATA_DIR / "grupos_inspectores.csv"
        df = pd.read_csv(csv_path)
        
        # Aplicar filtros acumulativos
        if grupo_id is not None:
            df = df[df["grupo_id"] == grupo_id]
        
        if periodo is not None:
            df = df[df["periodo"] == periodo]
        
        # Filtrar por id_trabajador buscando en el campo integrantes
        if id_trabajador is not None:
            # El campo integrantes contiene IDs separados por ";"
            df = df[df["integrantes"].str.contains(id_trabajador, na=False)]
        
        # Si no hay resultados
        if df.empty:
            return "No se encontraron grupos con los filtros indicados."
        
        return f"Se encontraron {len(df)} grupo(s).\n\n" + df.to_string(index=False)
    
    except FileNotFoundError:
        return "No se pudo acceder a los datos de grupos de inspectores. Contacte al administrador."
    except Exception as e:
        return f"No se pudo acceder a los datos de grupos de inspectores. Contacte al administrador."
