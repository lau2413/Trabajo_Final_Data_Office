"""
extract_cine_cifras.py
======================
Extrae datos estadísticos de los boletines "Cine en Cifras" (Proimágenes Colombia)
y los exporta a CSV usando Gemini Flash.

REQUISITOS:
    pip install google-genai pandas

CONFIGURACIÓN:
    1. Ve a https://aistudio.google.com/app/apikey
    2. Crea una API key GRATIS
    3. Define la variable de entorno GEMINI_API_KEY

WINDOWS:
    set GEMINI_API_KEY=tu_api_key

LINUX / MAC:
    export GEMINI_API_KEY=tu_api_key

USO:
    python extract_cine_cifras.py CineEnCifras30.pdf
"""
from dotenv import load_dotenv
import sys
import os
import json
import time
import pandas as pd
from google import genai
load_dotenv()

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
MODEL_NAME = "gemini-flash-latest"
OUTPUT_CSV = os.path.join("data", "raw", "cine_en_cifras_datos.csv")
# ──────────────────────────────────────────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

COLUMNS = [
    "año",
    "ciudad",
    "espectadores_nacional_M",
    "estrenos_total",
    "taquilla_M_COP",
    "precio_boleta_real",
    "indice_asistencia",
    "pantallas",
    "recuperacion_nacional_pct",
    "espectadores_ciudad_M",
    "recuperacion_ciudad_pct",
    "estrenos_col",
    "espectadores_col_M",
    "participacion_col_pct",
    "taquilla_col_M_COP",
]

CIUDADES = ["Bogota", "Medellin", "Cali", "Bucaramanga", "Barranquilla"]
CIUDADES_DISPLAY = ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Barranquilla"]

PROMPT_TEMPLATE = """
Eres un extractor de datos estadísticos experto. Analiza este boletín PDF de
"Cine en Cifras" de Proimágenes Colombia y extrae TODOS los datos numéricos
históricos que encuentres en los gráficos, tablas y textos.

IMPORTANTE:
- El boletín contiene series históricas de 2010 hasta el año de publicación.
- Los datos están en gráficas de barras, gráficas de líneas y tablas.
- Lee los valores numéricos directamente de las etiquetas de los gráficos.
- Para ciudades, los datos están en la sección "Asistencia a cine en ciudades principales".
- La taquilla usa precios constantes base diciembre 2018.
- Si un valor no aparece en el boletín, usa null.

Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta:
{
  "asistencia_total_y_estrenos": [
    {"año": 2010, "espectadores_millones": 33.66, "estrenos_totales": 206},
    ...
  ],
  "asistencia_cine_colombiano": [
    {"año": 2010, "espectadores_millones": 1.53, "estrenos_colombianos": 10, "participacion_mercado_porcentaje": 4.5},
    ...
  ],
  "asistencia_por_ciudades_millones": {
    "Bogota": [v2010, v2011, ...],
    "Medellin": [v2010, v2011, ...],
    "Cali": [v2010, v2011, ...],
    "Bucaramanga": [v2010, v2011, ...],
    "Barranquilla": [v2010, v2011, ...]
  },
  "taquilla_total_millones_cop_constantes": [
    {"año": 2010, "valor": 351378},
    ...
  ],
  "taquilla_cine_colombiano_millones_cop_constantes": [
    {"año": 2010, "valor": 13647},
    ...
  ],
  "precio_promedio_boleta_cop_constantes": [
    {"año": 2010, "valor": 10441},
    ...
  ],
  "indice_asistencia_habitante": [
    {"año": 2010, "indice": 0.76},
    ...
  ],
  "pantallas_exhibicion": [
    {"año": 2010, "numero": 588},
    ...
  ]
}
"""


def configurar_gemini():
    if not GEMINI_API_KEY:
        print("ERROR: No existe la variable de entorno GEMINI_API_KEY")
        print("\nWINDOWS:   set GEMINI_API_KEY=tu_api_key")
        print("LINUX/MAC: export GEMINI_API_KEY=tu_api_key")
        sys.exit(1)
    return genai.Client(api_key=GEMINI_API_KEY)


def extraer_datos_pdf(client, pdf_path):
    print(f"\n Procesando: {os.path.basename(pdf_path)}")
    print("Subiendo PDF a Gemini...")

    uploaded_file = client.files.upload(
        file=pdf_path,
        config={"mime_type": "application/pdf"}
    )

    print("Extrayendo datos con Gemini Flash...")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[PROMPT_TEMPLATE, uploaded_file],
        config={"temperature": 0.0, "max_output_tokens": 16000},
    )

    texto = response.text.strip()

    # Guardar respuesta cruda para debug
    with open("debug_respuesta.txt", "w", encoding="utf-8") as f:
        f.write(texto)

    # Limpiar markdown
    if "```" in texto:
        partes = texto.split("```")
        for parte in partes:
            parte = parte.strip()
            if parte.startswith("json"):
                parte = parte[4:]
            parte = parte.strip()
            if parte.startswith("{"):
                texto = parte
                break

    texto = texto.strip()
    print("Datos extraídos correctamente.")
    return json.loads(texto)


def json_a_filas(datos):
    """Convierte el JSON de Gemini al formato de filas para el CSV."""

    filas = []

    # Construir lookups por año
    asistencia = {r["año"]: r for r in datos.get("asistencia_total_y_estrenos", [])}
    colombiano = {r["año"]: r for r in datos.get("asistencia_cine_colombiano", [])}
    taquilla = {r["año"]: r["valor"] for r in datos.get("taquilla_total_millones_cop_constantes", [])}
    taquilla_col = {r["año"]: r["valor"] for r in datos.get("taquilla_cine_colombiano_millones_cop_constantes", [])}
    precio = {r["año"]: r["valor"] for r in datos.get("precio_promedio_boleta_cop_constantes", [])}
    indice = {r["indice"] if "indice" in r else None: r for r in datos.get("indice_asistencia_habitante", [])}
    indice = {r["año"]: r.get("indice") for r in datos.get("indice_asistencia_habitante", [])}
    pantallas = {r["año"]: r.get("numero") for r in datos.get("pantallas_exhibicion", [])}

    # Ciudades: arrays indexados por posición (índice 0 = 2010)
    ciudades_data = datos.get("asistencia_por_ciudades_millones", {})

    # Determinar años disponibles
    años = sorted(asistencia.keys())

    # Máximo nacional para calcular recuperación
    max_nacional = max(
        (r.get("espectadores_millones", 0) for r in datos.get("asistencia_total_y_estrenos", [])),
        default=73.11
    )

    # Máximos por ciudad
    max_ciudad = {}
    for ciudad in CIUDADES:
        vals = ciudades_data.get(ciudad, [])
        max_ciudad[ciudad] = max((v for v in vals if v is not None), default=None)

    for i, año in enumerate(años):

        esp_nacional = asistencia[año].get("espectadores_millones")
        estrenos_total = asistencia[año].get("estrenos_totales")

        col = colombiano.get(año, {})
        esp_col = col.get("espectadores_millones")
        estrenos_col = col.get("estrenos_colombianos")
        part_col = col.get("participacion_mercado_porcentaje")
        taq_col = taquilla_col.get(año)

        taq = taquilla.get(año)
        # Convertir a millones si está en miles
        if taq and taq > 100000:
            taq = round(taq / 1000, 2)
        if taq_col and taq_col > 100000:
            taq_col = round(taq_col / 1000, 2)

        rec_nacional = round((esp_nacional / max_nacional) * 100, 1) if esp_nacional and max_nacional else None

        # Fila Nacional
        filas.append({
            "año": año,
            "ciudad": "Nacional",
            "espectadores_nacional_M": esp_nacional,
            "estrenos_total": estrenos_total,
            "taquilla_M_COP": taq,
            "precio_boleta_real": precio.get(año),
            "indice_asistencia": indice.get(año),
            "pantallas": pantallas.get(año),
            "recuperacion_nacional_pct": rec_nacional,
            "espectadores_ciudad_M": None,
            "recuperacion_ciudad_pct": None,
            "estrenos_col": estrenos_col,
            "espectadores_col_M": esp_col,
            "participacion_col_pct": part_col,
            "taquilla_col_M_COP": taq_col,
        })

        # Filas por ciudad
        for ciudad, ciudad_display in zip(CIUDADES, CIUDADES_DISPLAY):
            vals = ciudades_data.get(ciudad, [])
            esp_ciudad = vals[i] if i < len(vals) else None
            max_c = max_ciudad.get(ciudad)
            rec_ciudad = round((esp_ciudad / max_c) * 100, 1) if esp_ciudad and max_c else None

            filas.append({
                "año": año,
                "ciudad": ciudad_display,
                "espectadores_nacional_M": esp_nacional,
                "estrenos_total": estrenos_total,
                "taquilla_M_COP": taq,
                "precio_boleta_real": precio.get(año),
                "indice_asistencia": indice.get(año),
                "pantallas": pantallas.get(año),
                "recuperacion_nacional_pct": rec_nacional,
                "espectadores_ciudad_M": esp_ciudad,
                "recuperacion_ciudad_pct": rec_ciudad,
                "estrenos_col": estrenos_col,
                "espectadores_col_M": esp_col,
                "participacion_col_pct": part_col,
                "taquilla_col_M_COP": taq_col,
            })

    return filas


def guardar_csv(filas_nuevas, output_path):
    df_nuevo = pd.DataFrame(filas_nuevas, columns=COLUMNS)

    if os.path.exists(output_path):
        df_existente = pd.read_csv(output_path)
        df_combined = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=["año", "ciudad"], keep="last")
        df_combined = df_combined.sort_values(["año", "ciudad"])
    else:
        df_combined = df_nuevo.sort_values(["año", "ciudad"])

    df_combined.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"\n CSV guardado en: {output_path}")
    print(
        f"   Total filas: {len(df_combined)} | "
        f"Años cubiertos: {df_combined['año'].min()} – {df_combined['año'].max()}"
    )


def main():
    if len(sys.argv) < 2:
        print("Uso: python extract_cine_cifras.py archivo1.pdf [archivo2.pdf ...]")
        sys.exit(1)

    pdfs = sys.argv[1:]
    client = configurar_gemini()
    todas_filas = []

    for pdf_path in pdfs:
        if not os.path.exists(pdf_path):
            print(f"Archivo no encontrado: {pdf_path}")
            continue

        try:
            datos = extraer_datos_pdf(client, pdf_path)
            filas = json_a_filas(datos)
            todas_filas.extend(filas)
            print(f" Filas generadas: {len(filas)}")

            if pdfs.index(pdf_path) < len(pdfs) - 1:
                print("Esperando 5s entre archivos...")
                time.sleep(5)

        except json.JSONDecodeError as e:
            print(f" Error parseando JSON de {pdf_path}: {e}")
        except Exception as e:
            print(f" Error procesando {pdf_path}: {e}")

    if todas_filas:
        guardar_csv(todas_filas, OUTPUT_CSV)
    else:
        print("\n No se extrajeron datos.")


if __name__ == "__main__":
    main()