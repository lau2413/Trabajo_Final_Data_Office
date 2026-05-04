
## Justificación del dataset — Cine Los Andes 🦅

### Contexto de la empresa

Cine Los Andes es una empresa **privada** del sector cinematográfico colombiano. Como operador de salas de cine, no genera ni publica sus propios datos históricos de mercado — eso es exclusivo de los sistemas oficiales del sector. Su inteligencia de negocio se construye, como lo hace cualquier actor privado del sector, a partir de las fuentes sectoriales oficiales que el Estado colombiano pone a disposición pública. Por esa razón, el dataset de este proyecto se construye a partir de la fuente que Cine Los Andes misma consultaría en la realidad para tomar decisiones estratégicas.

---

### Fuente seleccionada y por qué

**Boletín *Cine en Cifras* Edición 30 — Proimágenes Colombia, abril 2026**

Proimágenes Colombia es la entidad mixta adscrita al Ministerio de las Culturas, las Artes y los Saberes encargada del fomento y la información del sector cinematográfico nacional. Su boletín *Cine en Cifras* es la **única fuente oficial que consolida series históricas completas del mercado cinematográfico colombiano**, construida con datos del Sistema de Información y Registro Cinematográfico (SIREC) y de CADBOX, propiedad de la Asociación Colombiana de Distribuidores de Películas Cinematográficas (ACDPC). Estas dos plataformas son los sistemas de registro transaccional del sector — es decir, los datos no son estimaciones ni encuestas: son registros reales de asistencia y taquilla sala por sala.

---

### Por qué esta fuente y no las alternativas sugeridas

| Fuente evaluada | Razón del descarte |
|---|---|
| **datos.gov.co** | No contiene series históricas de asistencia cinematográfica desagregadas por ciudad ni variables de taquilla o estrenos con continuidad 2010–2025 |
| **Banco Mundial** | Indicadores macroeconómicos generales; no tiene datos del sector de entretenimiento con granularidad colombiana |
| **Naciones Unidas / data.un.org** | Cobertura cultural muy limitada para Colombia; no incluye taquilla, estrenos ni asistencia por ciudad |
| **Kaggle** | Los datasets de cine disponibles en Kaggle corresponden mayoritariamente al mercado norteamericano o global (IMDb, Box Office Mojo); no son representativos del comportamiento del consumidor colombiano |
| **Our World in Data** | No tiene datos de industria cinematográfica para Colombia con el nivel de detalle requerido |
| **Proimágenes Ed.30** | Fuente oficial, cobertura 2010–2025, datos reales transaccionales, desagregación por ciudad, incluye precios, taquilla, estrenos nacionales e internacionales y pantallas |

La elección no es arbitraria: **Cine Los Andes operaría con exactamente esta fuente en un contexto real**. Ninguna otra fuente pública disponible reemplaza la especificidad sectorial y geográfica que ofrece Proimágenes para el mercado colombiano.

---

### Qué contiene el boletín y cómo se construye el dataset

El boletín Ed.30 presenta información comparativa para **series estadísticas de 2010 a 2025** (16 años), organizadas en cuatro secciones: Espectadores, Taquilla, Estrenos cinematográficos y Fomento cinematográfico. Tras revisar el PDF completo, se verificó que **todas las variables del dataset están disponibles directamente en las gráficas y tablas del boletín**, sin necesidad de fuentes adicionales:

| Variable | Disponible en Ed.30 | Página | Valores 2025 |
|---|---|---|---|
| `año` | Sí | Series 2010–2025 en todo el boletín | 2025 |
| `espectadores_M` | Sí | Pág. 4 | 49,55 M |
| `taquilla_COP_constante` | Sí | Pág. 11 (base dic. 2018) | 414.541 M COP |
| `precio_boleta_real` | Sí | Pág. 13 (base dic. 2018) | $8.366 COP |
| `estrenos_totales` | Sí | Pág. 4 (pie de gráfica) | 408 |
| `estrenos_colombianos` | Sí | Pág. 5 (pie de gráfica) | 77 |
| `espectadores_colombianos_M` | Sí | Pág. 5 | 0,75 M |
| `taquilla_colombiana_constante` | Sí | Pág. 12 (base dic. 2018) | 5.741 M COP |
| `pantallas` | Sí | Pág. 18 (SIREC) | 1.262 |
| `indice_asistencia` | Sí | Pág. 8 (espect./habitante) | 0,93 |
| `bogota_M` | Sí | Pág. 7 | 15,41 M |
| `medellin_M` | Sí | Pág. 7 | 5,39 M |
| `cali_M` | Sí | Pág. 7 | 4,07 M |
| `barranquilla_M` | Sí | Pág. 7 | 2,05 M |
| `bucaramanga_M` | Sí | Pág. 7 | 2,24 M |
| `otras_ciudades_M` | Sí | Pág. 7 (resto del país) | 20,39 M |

**Las 16 observaciones (años 2010 a 2025) y las 16 variables están completamente respaldadas por el boletín.** No hay valores faltantes que requieran imputación porque el boletín fue diseñado específicamente para presentar series históricas completas.

---

### Cómo se construye el dataset (proceso de extracción)

El boletín se publica en formato PDF con gráficas y tablas numéricas. No existe descarga directa en CSV o Excel — este es el formato estándar de publicación de Proimágenes. El proceso de construcción del archivo `cine_losandes_sector_2010_2025.csv` es el siguiente:

1. Lectura sistemática del boletín Ed.30 página por página
2. Extracción de cada valor numérico de las gráficas y tablas correspondientes a cada variable
3. Registro en hoja de trabajo con verificación cruzada entre variables (por ejemplo, la suma de espectadores por ciudad debe aproximarse al total nacional)
4. Exportación al CSV crudo, que queda como archivo de solo lectura en el repositorio
5. Toda transformación posterior ocurre en `01_limpieza.ipynb`, que genera un archivo separado `cine_losandes_clean.csv`

Este proceso garantiza **trazabilidad completa**: cada fila y cada valor del CSV puede verificarse contra la página específica del boletín original, que se incluye en el repositorio como archivo de referencia.

---

### Limitación técnica y cómo se maneja

El boletín reporta precios y taquilla **exclusivamente en precios constantes con base diciembre de 2018**, lo cual es una decisión metodológica explícita de Proimágenes para facilitar comparaciones reales entre años. Esto significa que los valores nominales (corrientes) no están disponibles directamente. Esta no es una limitación del dataset sino una fortaleza: trabajar directamente con precios reales elimina la necesidad de deflactar y reduce el riesgo de errores metodológicos. El dataset adopta esta misma convención y todas las variables monetarias se expresan en COP constantes base diciembre de 2018.

---

### Declaración de uso

> *"Cine Los Andes es una empresa privada simulada del sector cinematográfico colombiano, creada para el proyecto académico de Data Office Strategy — UPB 2026-1. Como empresa privada del sector, sus decisiones estratégicas se fundamentan en la información sectorial oficial. Los datos del mercado cinematográfico colombiano utilizados en este proyecto provienen del Boletín Cine en Cifras Ed.30, publicado por Proimágenes Colombia en abril de 2026, construido con información del Sistema de Información y Registro Cinematográfico (SIREC) y CADBOX, propiedad de la ACDPC. Los datos se usan exclusivamente con fines educativos."*

