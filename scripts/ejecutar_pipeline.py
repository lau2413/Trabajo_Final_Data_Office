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
from validacion import ValidadorDatos

# DEFINIR FUNCIONES DE ETAPAS

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


def validar_datos(df):
    """Valida calidad de datos."""
    validador = ValidadorDatos()
    validador.ejecutar_validaciones(df)
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

    ruta_dataset = Path("../data/raw/cine_en_cifras_datos.csv")
    df = pd.read_csv(ruta_dataset)

    print(f"\n{'='*80}")
    print("Dataset cargado correctamente")
    print(f"{'='*80}")
    print(f"Dimensiones: {df.shape}")
    print(f"\nPrimeras filas:")
    print(df.head())


    # CREAR PIPELINE

    pipeline = PipelineDatos(
        nombre="CineLosAndesPipeline",
        log_level="INFO",
        checkpoint_dir="../checkpoints",
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
            critica=False
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

    print(f"\n{'='*80}")
    print("Iniciando ejecución del pipeline")
    print(f"{'='*80}\n")

    df_final, reporte = pipeline.ejecutar(df)

    # GUARDAR RESULTADOS

    print(f"\n{'='*80}")
    print("Pipeline completado exitosamente")
    print(f"{'='*80}\n")

    ruta_output = Path("../data/processed/cine_en_cifras_limpio.csv")
    ruta_output.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(ruta_output, index=False)
    print(f"Dataset procesado guardado en: {ruta_output}")
    print(f"  Dimensiones finales: {df_final.shape}")

    # Guardar reporte
    pipeline.guardar_reporte("reporte_pipeline.json")
    print(f"Reporte del pipeline guardado en: reporte_pipeline.json")

    print(f"\nResumen del reporte:")
    print(f"  - Etapas completadas: {reporte['etapas_completadas']}/{reporte['total_etapas']}")
    print(f"  - Tiempo total: {reporte['tiempo_total_segundos']:.2f}s")
    print(f"  - Filas procesadas: {len(df_final)}")
    print(f"\n{'='*80}\n")
