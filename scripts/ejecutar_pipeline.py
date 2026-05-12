"""
Pipeline de procesamiento de datos Cine Los Andes.

Orquestador que integra:
- limpieza.py: LimpiadorDatos
- normalizacion.py: NormalizadorDatos
- pipeline.py: PipelineDatos
- validacion.py: ValidadorDatos

Procesa datos reales de: data/raw/cine_en_cifras_datos.csv
"""

import pandas as pd
from pathlib import Path

# Importar clases de los módulos
from limpieza import LimpiadorDatos
from normalizacion import NormalizadorDatos
from pipeline import PipelineDatos, Etapa
from validacion import ReglaValidacion, ResultadoValidacion, SeveridadError, ValidadorDatos

# DEFINIR FUNCIONES DE ETAPAS

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATASET = DATA_DIR / "raw" / "cine_en_cifras_datos.csv"
PROCESSED_DIR = DATA_DIR / "processed"
VALIDATED_DATASET = PROCESSED_DIR / "cine_en_cifras_validado.csv"
NORMALIZED_DATASET = PROCESSED_DIR / "cine_en_cifras_limpio.csv"
VALIDATION_REPORT = PROCESSED_DIR / "reporte_validacion.json"
CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"
PIPELINE_REPORT = SCRIPTS_DIR / "reporte_pipeline.json"
USAR_CHECKPOINTS = False

COLUMNAS_ESPERADAS = [
    'año',
    'ciudad',
    'espectadores_nacional_m',
    'estrenos_total',
    'taquilla_m_cop',
    'precio_boleta_real',
    'indice_asistencia',
    'pantallas',
    'recuperacion_nacional_pct',
    'espectadores_ciudad_m',
    'recuperacion_ciudad_pct',
    'estrenos_col',
    'espectadores_col_m',
    'participacion_col_pct',
    'taquilla_col_m_cop',
]

COLUMNAS_NUMERICAS = [col for col in COLUMNAS_ESPERADAS if col != 'ciudad']
COLUMNAS_PORCENTAJE = [
    'recuperacion_nacional_pct',
    'recuperacion_ciudad_pct',
    'participacion_col_pct',
]

def limpiar_columnas(df):
    """Limpia y estandariza nombres de columnas."""
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.strip()
    return df


def convertir_tipos(df):
    """Convierte columnas numéricas (excluye ciudad y año)."""
    for col in df.columns:
        if col in ['ciudad', 'año']:
            continue
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        except:
            pass
    return df


def tratar_nulos(df):
    """Imputa valores faltantes (excluye ciudad y año)."""
    # Solo procesar columnas que no sean 'ciudad' ni 'año'
    columnas_a_procesar = [col for col in df.columns if col not in ['ciudad', 'año']]
    df_temp = df[columnas_a_procesar].copy()
    
    limpiador = LimpiadorDatos()
    df_temp = limpiador.manejar_nulos(df_temp, estrategia="media")
    
    # Recombinar con las columnas excluidas
    for col in columnas_a_procesar:
        df[col] = df_temp[col]
    
    return df


def eliminar_duplicados(df):
    """Elimina registros duplicados."""
    limpiador = LimpiadorDatos()
    return limpiador.limpiar_duplicados(df)


def validar_columnas_obligatorias(df):
    """Verifica que el dataset tenga la estructura esperada."""
    faltantes = [col for col in COLUMNAS_ESPERADAS if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {faltantes}")
    return df


def validar_clave_anio_ciudad(df, columna, columnas):
    """Valida unicidad compuesta por año y ciudad."""
    faltantes = [col for col in columnas if col not in df.columns]
    if faltantes:
        return ResultadoValidacion(
            nombre_regla="validar_clave_anio_ciudad",
            columna=columna,
            paso=False,
            errores_encontrados=len(faltantes),
            severidad=SeveridadError.CRITICO,
            mensaje=f"Columnas faltantes para validar unicidad: {faltantes}",
            detalles={"columnas_faltantes": faltantes}
        )

    duplicados = df.duplicated(subset=columnas, keep=False)
    total_duplicados = int(duplicados.sum())
    indices_error = df[duplicados].index.tolist()

    return ResultadoValidacion(
        nombre_regla="validar_clave_anio_ciudad",
        columna=columna,
        paso=total_duplicados == 0,
        errores_encontrados=total_duplicados,
        indices_error=indices_error,
        severidad=SeveridadError.ALTO,
        mensaje=f"Se encontraron {total_duplicados} registros duplicados por {columnas}",
        detalles={"columnas_clave": columnas}
    )


def configurar_reglas_validacion(validador):
    """Registra las reglas de calidad del proyecto Cine Los Andes."""
    for columna in COLUMNAS_ESPERADAS:
        validador.agregar_regla(
            ReglaValidacion(
                nombre=f"{columna}_sin_nulos",
                columna=columna,
                funcion_validacion=validador.validar_no_nulos,
                severidad=SeveridadError.ALTO,
                mensaje_error=f"La columna {columna} no debe tener valores nulos"
            )
        )

    for columna in COLUMNAS_NUMERICAS:
        validador.agregar_regla(
            ReglaValidacion(
                nombre=f"{columna}_no_negativa",
                columna=columna,
                funcion_validacion=validador.validar_rango,
                severidad=SeveridadError.ALTO,
                mensaje_error=f"La columna {columna} no debe tener valores negativos",
                parametros={"minimo": 0}
            )
        )

    for columna in COLUMNAS_PORCENTAJE:
        validador.agregar_regla(
            ReglaValidacion(
                nombre=f"{columna}_porcentaje_valido",
                columna=columna,
                funcion_validacion=validador.validar_rango,
                severidad=SeveridadError.ALTO,
                mensaje_error=f"La columna {columna} debe estar entre 0 y 100",
                parametros={"minimo": 0, "maximo": 100}
            )
        )

    validador.agregar_regla(
        ReglaValidacion(
            nombre="anio_en_rango_historico",
            columna="año",
            funcion_validacion=validador.validar_rango,
            severidad=SeveridadError.ALTO,
            mensaje_error="El año debe estar entre 2010 y 2025",
            parametros={"minimo": 2010, "maximo": 2025}
        )
    )

    validador.agregar_regla(
        ReglaValidacion(
            nombre="clave_anio_ciudad_unica",
            columna="año_ciudad",
            funcion_validacion=validar_clave_anio_ciudad,
            severidad=SeveridadError.ALTO,
            mensaje_error="No deben existir registros duplicados para la misma combinación año + ciudad",
            parametros={"columnas": ["año", "ciudad"]}
        )
    )


def validar_datos(df):
    """Valida calidad de datos."""
    validador = ValidadorDatos()
    validar_columnas_obligatorias(df)
    configurar_reglas_validacion(validador)
    validador.ejecutar_validaciones(df)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    validador.guardar_reporte(str(VALIDATION_REPORT), mostrar_indices=True)

    errores_criticos = validador.obtener_errores_criticos()
    if errores_criticos:
        mensajes = [f"{error.nombre_regla}: {error.mensaje}" for error in errores_criticos]
        raise ValueError(f"Errores críticos de validación: {mensajes}")

    return df


def guardar_datos_validados(df):
    """Guarda una capa validada sin normalizar para dashboard y análisis descriptivo."""
    VALIDATED_DATASET.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(VALIDATED_DATASET, index=False)
    return df


def normalizar_datos(df):
    """Normaliza variables (excluye ciudad y año)."""
    normalizador = NormalizadorDatos()
    columnas_numericas = df.select_dtypes(include=['number']).columns.tolist()
    # Excluir 'ciudad' y 'año'
    columnas_numericas = [col for col in columnas_numericas if col not in ['ciudad', 'año']]
    if columnas_numericas:
        return normalizador.normalizar_minmax(df, columnas=columnas_numericas)
    return df


if __name__ == "__main__":

    # CARGAR DATOS

    df = pd.read_csv(RAW_DATASET)

    print(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")


    # CREAR PIPELINE

    pipeline = PipelineDatos(
        nombre="CineLosAndesPipeline",
        log_level="WARNING",
        checkpoint_dir=str(CHECKPOINT_DIR) if USAR_CHECKPOINTS else None,
        modo_dry_run=False
    )


    # AGREGAR ETAPAS


    pipeline.agregar_etapa(
        Etapa(
            nombre="Limpiar columnas",
            funcion=limpiar_columnas,
            descripcion="Limpieza y estandarización de nombres de columnas"
        )
    )

    pipeline.agregar_etapa(
        Etapa(
            nombre="Convertir tipos",
            funcion=convertir_tipos,
            descripcion="Conversión de columnas numéricas"
        )
    )

    pipeline.agregar_etapa(
        Etapa(
            nombre="Tratar nulos",
            funcion=tratar_nulos,
            descripcion="Imputación de valores faltantes"
        )
    )

    pipeline.agregar_etapa(
        Etapa(
            nombre="Eliminar duplicados",
            funcion=eliminar_duplicados,
            descripcion="Eliminación de registros duplicados"
        )
    )

    pipeline.agregar_etapa(
        Etapa(
            nombre="Validar datos",
            funcion=validar_datos,
            descripcion="Validaciones de calidad de datos",
            critica=True
        )
    )

    pipeline.agregar_etapa(
        Etapa(
            nombre="Guardar datos validados",
            funcion=guardar_datos_validados,
            descripcion="Persistencia de capa validada sin normalizar"
        )
    )

    pipeline.agregar_etapa(
        Etapa(
            nombre="Normalizar datos",
            funcion=normalizar_datos,
            descripcion="Escalamiento y normalización de variables"
        )
    )

    # EJECUTAR PIPELINE

    print("Ejecutando pipeline...")

    df_final, reporte = pipeline.ejecutar(df, guardar_checkpoints=USAR_CHECKPOINTS)

    # GUARDAR RESULTADOS

    NORMALIZED_DATASET.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(NORMALIZED_DATASET, index=False)

    # Guardar reporte
    pipeline.guardar_reporte(str(PIPELINE_REPORT))

    print("Pipeline completado correctamente")
    print(f"Validado: {VALIDATED_DATASET}")
    print(f"Normalizado: {NORMALIZED_DATASET}")
    print(f"Reporte validacion: {VALIDATION_REPORT}")
    print(f"Reporte pipeline: {PIPELINE_REPORT}")
    print(f"Etapas completadas: {reporte['etapas_completadas']}/{reporte['total_etapas']}")
