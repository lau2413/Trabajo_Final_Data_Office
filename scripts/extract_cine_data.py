"""
extract_cine_data_fixed.py
─────────────
Extracción específica de datos del Boletín Cine en Cifras Ed.30
usando Gemini Vision.
"""

import os
import json
import csv
import re
from pathlib import Path
from google import genai

# ── Configuración ─────────────────────────────────────────────────────────────
MODEL = "gemini-2.0-flash" # Versión estable y rápida
# ──────────────────────────────────────────────────────────────────────────────

# Prompt ultra-específico para evitar que el modelo se pierda o corte la respuesta
PROMPT = """Extrae los datos estadísticos del Boletín 'Cine en Cifras Edición 30' de Proimágenes Colombia.
Necesito la información estructurada EXACTAMENTE con las siguientes columnas para cada año (2010-2025) y para las principales ciudades (Bogotá, Medellín, Cali, Barranquilla, Bucaramanga y el resto del país como 'Otras').

Columnas requeridas:
- año
- ciudad
- espectadores_nacional_M
- estrenos_total
- taquilla_M_COP (COP constante base dic 2018)
- precio_boleta_real (COP constante base dic 2018)
- indice_asistencia (Espectadores por habitante)
- pantallas (Total nacional)
- recuperacion_nacional_pct (Variación % anual nacional)
- espectadores_ciudad_M (Espectadores de la ciudad específica en millones)
- recuperacion_ciudad_pct (Variación % anual de la ciudad)
- estrenos_col (Estrenos colombianos totales)
- espectadores_col_M (Espectadores cine colombiano en millones)
- participacion_col_pct (Porcentaje de participación cine colombiano)
- taquilla_col_M_COP (Taquilla cine colombiano en millones COP)

Reglas estrictas:
1. Devuelve ÚNICAMENTE un array JSON válido. No escribas introducciones ni bloques de código ```json.
2. Para cada año, debes generar una fila por cada ciudad mencionada.
3. Usa solo números (float o int), no incluyas símbolos de moneda o letras en los valores.
4. Si un dato no es visible, usa null.

Formato esperado:
[
  {"año": 2025, "ciudad": "Bogotá", "espectadores_nacional_M": 49.55, ...},
  {"año": 2025, "ciudad": "Medellín", "espectadores_nacional_M": 49.55, ...},
  ...
]
"""

def extract_cine_data():
    pdf_path = os.path.abspath("CineEnCifras30.pdf")
    output_path = os.path.abspath("datos_cine_extraidos.csv")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: Falta la variable de entorno GEMINI_API_KEY.")
        return

    client = genai.Client(api_key=api_key)

    print(f"📄 Procesando: {pdf_path}")

    # 1. Subir PDF
    print("1/3 Subiendo PDF...")
    with open(pdf_path, "rb") as f:
        file_ref = client.files.upload(file=f, config={'mime_type': 'application/pdf'})

    # 2. Extraer datos
    print("2/3 Extrayendo datos específicos (esto puede tardar)...")
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[file_ref, PROMPT],
            config={"temperature": 0.1}
        )
        raw_text = response.text.strip()

        # Limpieza de bloques de código si Gemini los pone
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)

        data = json.loads(raw_text)
    except Exception as e:
        print(f"❌ Error durante la extracción: {e}")
        return
    finally:
        client.files.delete(name=file_ref.name)

    # 3. Guardar CSV
    print("3/3 Guardando resultados en CSV...")
    if data and isinstance(data, list):
        keys = data[0].keys()
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ ¡Éxito! Datos guardados en: {output_path}")
    else:
        print("❌ Gemini no devolvió una lista de datos válida.")

if __name__ == "__main__":
    extract_cine_data()
