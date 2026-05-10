from sklearn.preprocessing import MinMaxScaler
import pandas as pd

def normalizar_datos(df):

    columnas = [
        'taquilla_m_cop',
        'precio_boleta_real',
        'indice_asistencia',
        'participacion_col_pct'
    ]

    scaler = MinMaxScaler()

    df[columnas] = scaler.fit_transform(df[columnas])

    return df