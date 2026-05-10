def validar_datos(df):

    errores = []

    # Validar años
    if (df['año'] < 2000).any():
        errores.append("Existen años menores a 2000")

    # Validar porcentajes
    porcentajes = [
        'recuperacion_nacional_pct',
        'recuperacion_ciudad_pct',
        'participacion_col_pct'
    ]

    for col in porcentajes:
        if ((df[col] < 0) | (df[col] > 100)).any():
            errores.append(f"Valores inválidos en {col}")

    # Validar negativos
    columnas_no_negativas = [
        'taquilla_m_cop',
        'espectadores_nacional_m'
    ]

    for col in columnas_no_negativas:
        if (df[col] < 0).any():
            errores.append(f"Valores negativos en {col}")

    return errores