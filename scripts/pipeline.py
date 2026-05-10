from limpieza import *
from normalizacion import *
from validacion import *

def ejecutar_pipeline():

    ruta = "../data/raw/cine_en_cifras_datos.csv"

    df = cargar_datos(ruta)

    print("Datos cargados")

    df = limpiar_columnas(df)

    df = convertir_tipos(df)

    df = tratar_nulos(df)

    df = eliminar_duplicados(df)

    errores = validar_datos(df)

    if errores:
        print("Errores encontrados:")
        for error in errores:
            print("-", error)
    else:
        print("Validación exitosa")

    df = normalizar_datos(df)

    salida = "../data/processed/cine_en_cifras_limpio.csv"

    df.to_csv(salida, index=False)

    print("Pipeline ejecutado correctamente")


if __name__ == "__main__":
    ejecutar_pipeline()