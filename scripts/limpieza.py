import pandas as pd

ruta = "../data/raw/cine_en_cifras_datos.csv"

def cargar_datos(ruta):
    df = pd.read_csv(ruta)
    return df


def limpiar_columnas(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def tratar_nulos(df):
    columnas_numericas = df.select_dtypes(include=['float64', 'int64']).columns

    for col in columnas_numericas:
        df[col] = df[col].fillna(df[col].median())

    return df


def convertir_tipos(df):

    columnas_numericas = [
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
        'taquilla_col_m_cop'
    ]

    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def eliminar_duplicados(df):
    df = df.drop_duplicates()
    return df