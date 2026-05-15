from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


st.set_page_config(
    page_title="Cine Los Andes - Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos
st.markdown(
    """
<style>
    .main { background-color: #0f0f1a; }
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #e50914;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #e50914; }
    .metric-label { font-size: 0.85rem; color: #aaa; margin-top: 0.2rem; }
    .metric-delta { font-size: 0.8rem; color: #4ade80; margin-top: 0.1rem; }
    .section-title {
        font-size: 1.1rem; font-weight: 600; color: #e50914;
        border-left: 3px solid #e50914; padding-left: 0.6rem;
        margin: 1.5rem 0 0.8rem 0;
    }
    h1 { color: #ffffff !important; }
    .stSidebar { background-color: #0f0f1a !important; }
</style>
""",
    unsafe_allow_html=True,
)

# Carga de datos
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed" / "cine_en_cifras_validado.csv"


@st.cache_data
def cargar_datos():
    df = pd.read_csv(DATA_PATH)
    year_aliases = {"año", "a\\u00f1o", "a\\u00c3\\u00b1o", "ano", "anio"}
    df = df.rename(columns={col: "anio" for col in df.columns if col.lower() in year_aliases})
    return df


df_all = cargar_datos()

# Paleta de colores
COLORES_CIUDAD = {
    "Bogotá": "#e50914",
    "Bogota": "#e50914",
    "Medellín": "#f5a623",
    "Medellin": "#f5a623",
    "Cali": "#4ade80",
    "Barranquilla": "#60a5fa",
    "Bucaramanga": "#c084fc",
    "Nacional": "#ffffff",
}
PLOTLY_TEMPLATE = "plotly_dark"

# Sidebar - filtros
with st.sidebar:
    st.markdown("## 🎬 Cine Los Andes")
    st.markdown("**Mercado cinematográfico Colombia 2010 - 2025**")
    st.divider()

    anios_disponibles = sorted(df_all["anio"].unique())
    rango_anios = st.slider(
        "Rango de anios",
        min_value=int(anios_disponibles[0]),
        max_value=int(anios_disponibles[-1]),
        value=(int(anios_disponibles[0]), int(anios_disponibles[-1])),
        step=1,
    )

    ciudades_opciones = sorted([c for c in df_all["ciudad"].unique() if c != "Nacional"])
    ciudades_sel = st.multiselect(
        "Ciudades",
        options=ciudades_opciones,
        default=ciudades_opciones,
    )

    st.divider()
    mostrar_covid = st.toggle("Destacar impacto COVID-19", value=True)
    st.caption("Datos: Cine en Cifras Ed. 30 - Proimágenes Colombia")

# Filtrado
df_nac = df_all[
    (df_all["ciudad"] == "Nacional")
    & (df_all["anio"] >= rango_anios[0])
    & (df_all["anio"] <= rango_anios[1])
].copy()

df_ciudad = df_all[
    (df_all["ciudad"].isin(ciudades_sel))
    & (df_all["anio"] >= rango_anios[0])
    & (df_all["anio"] <= rango_anios[1])
].copy()

df_todo = df_all[
    (df_all["anio"] >= rango_anios[0]) & (df_all["anio"] <= rango_anios[1])
].copy()

# Titulo
st.markdown("# 🎬 Dashboard - Mercado Cinematográfico Colombia")
st.markdown(
    f"Análisis del período **{rango_anios[0]} - {rango_anios[1]}** · "
    f"Ciudades seleccionadas: **{', '.join(ciudades_sel) if ciudades_sel else 'ninguna'}**"
)

st.divider()

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)

espect_max = df_nac["espectadores_nacional_m"].max()
espect_2019 = df_nac.loc[df_nac["anio"] == 2019, "espectadores_nacional_m"].values
espect_2020 = df_nac.loc[df_nac["anio"] == 2020, "espectadores_nacional_m"].values
caida_covid = (
    round(((espect_2020[0] - espect_2019[0]) / espect_2019[0]) * 100, 1)
    if (len(espect_2019) and len(espect_2020))
    else 0
)

taquilla_max = df_nac["taquilla_m_cop"].max()
pantallas_ult = df_nac.sort_values("anio").iloc[-1]["pantallas"] if len(df_nac) else 0
part_col_ult = (
    df_nac.sort_values("anio").iloc[-1]["participacion_col_pct"] if len(df_nac) else 0
)

with col1:
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-value">{espect_max:.1f}M</div>
        <div class="metric-label">Pico de espectadores<br>nacionales</div>
    </div>""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-value">{caida_covid:.0f}%</div>
        <div class="metric-label">Caída por COVID-19<br>(2019→2020)</div>
    </div>""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-value">${taquilla_max:.0f}M</div>
        <div class="metric-label">Taquilla récord<br>(COP millones)</div>
    </div>""",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-value">{pantallas_ult:,}</div>
        <div class="metric-label">Pantallas activas<br>último anio</div>
    </div>""",
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-value">{part_col_ult:.1f}%</div>
        <div class="metric-label">Participación cine<br>colombiano (últ. anio)</div>
    </div>""",
        unsafe_allow_html=True,
    )

# Fila 1: Espectadores nacionales + Taquilla
st.markdown(
    '<div class="section-title">Tendencias del mercado nacional</div>',
    unsafe_allow_html=True,
)
col_a, col_b = st.columns(2)

with col_a:
    fig_esp = go.Figure()
    fig_esp.add_trace(
        go.Scatter(
            x=df_nac["anio"],
            y=df_nac["espectadores_nacional_m"],
            mode="lines+markers",
            name="Espectadores",
            line=dict(color="#e50914", width=3),
            marker=dict(size=8, color="#e50914"),
            fill="tozeroy",
            fillcolor="rgba(229,9,20,0.12)",
        )
    )
    if mostrar_covid and 2020 in df_nac["anio"].values:
        fig_esp.add_vrect(
            x0=2019.5,
            x1=2021.5,
            fillcolor="rgba(255,200,0,0.08)",
            line_width=0,
            annotation_text="COVID-19",
            annotation_position="top left",
            annotation_font_color="#ffd700",
        )
    fig_esp.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Espectadores Nacionales (millones)",
        xaxis_title="Año",
        yaxis_title="Millones",
        height=340,
        margin=dict(t=40, b=30),
    )
    st.plotly_chart(fig_esp, use_container_width=True)

with col_b:
    fig_taq = go.Figure()
    fig_taq.add_trace(
        go.Bar(
            x=df_nac["anio"],
            y=df_nac["taquilla_m_cop"],
            name="Taquilla",
            marker_color=[
                "#ffd700" if (mostrar_covid and y in [2020, 2021]) else "#e50914"
                for y in df_nac["anio"]
            ],
        )
    )
    fig_taq.add_trace(
        go.Scatter(
            x=df_nac["anio"],
            y=df_nac["precio_boleta_real"],
            mode="lines+markers",
            name="Precio boleta (COP)",
            yaxis="y2",
            line=dict(color="#60a5fa", width=2, dash="dot"),
            marker=dict(size=6),
        )
    )
    fig_taq.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Taquilla (M COP) y Precio de Boleta",
        xaxis_title="Año",
        yaxis=dict(title="Taquilla (M COP)"),
        yaxis2=dict(title="Precio Boleta (COP)", overlaying="y", side="right"),
        height=340,
        margin=dict(t=40, b=30),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig_taq, use_container_width=True)

# Fila 2: Comparativo ciudades
st.markdown(
    '<div class="section-title">Comparativo por ciudad</div>',
    unsafe_allow_html=True,
)
col_c, col_d = st.columns([3, 2])

with col_c:
    if ciudades_sel:
        fig_ciu = go.Figure()
        for ciudad in ciudades_sel:
            df_c = df_ciudad[df_ciudad["ciudad"] == ciudad].sort_values("anio")
            fig_ciu.add_trace(
                go.Scatter(
                    x=df_c["anio"],
                    y=df_c["espectadores_ciudad_m"],
                    mode="lines+markers",
                    name=ciudad,
                    line=dict(color=COLORES_CIUDAD.get(ciudad, "#aaa"), width=2.5),
                    marker=dict(size=7),
                )
            )
        if mostrar_covid:
            fig_ciu.add_vrect(
                x0=2019.5,
                x1=2021.5,
                fillcolor="rgba(255,200,0,0.07)",
                line_width=0,
            )
        fig_ciu.update_layout(
            template=PLOTLY_TEMPLATE,
            title="Espectadores por ciudad (millones)",
            xaxis_title="Año",
            yaxis_title="Millones",
            height=360,
            margin=dict(t=40, b=30),
            legend=dict(orientation="h", y=-0.25),
        )
        st.plotly_chart(fig_ciu, use_container_width=True)
    else:
        st.info("Selecciona al menos una ciudad en el panel lateral.")

with col_d:
    anio_sel_bar = st.selectbox(
        "Año para comparar ciudades",
        options=sorted(df_all["anio"].unique(), reverse=True),
        index=0,
    )
    df_bar = df_all[
        (df_all["anio"] == anio_sel_bar) & (df_all["ciudad"].isin(ciudades_sel))
    ].sort_values("espectadores_ciudad_m", ascending=True)

    if not df_bar.empty:
        fig_bar = go.Figure(
            go.Bar(
                x=df_bar["espectadores_ciudad_m"],
                y=df_bar["ciudad"],
                orientation="h",
                marker_color=[COLORES_CIUDAD.get(c, "#aaa") for c in df_bar["ciudad"]],
                text=df_bar["espectadores_ciudad_m"].apply(lambda x: f"{x:.2f}M"),
                textposition="outside",
            )
        )
        fig_bar.update_layout(
            template=PLOTLY_TEMPLATE,
            title=f"Espectadores por ciudad - {anio_sel_bar}",
            xaxis_title="Millones",
            height=360,
            margin=dict(t=40, b=30, r=60),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# Fila 3: Cine colombiano + Pantallas/Estrenos
st.markdown(
    '<div class="section-title">Cine colombiano y crecimiento de infraestructura</div>',
    unsafe_allow_html=True,
)
col_e, col_f = st.columns(2)

with col_e:
    fig_col = make_subplots(specs=[[{"secondary_y": True}]])
    fig_col.add_trace(
        go.Bar(
            x=df_nac["anio"],
            y=df_nac["estrenos_col"],
            name="Estrenos colombianos",
            marker_color="rgba(74,222,128,0.7)",
        ),
        secondary_y=False,
    )
    fig_col.add_trace(
        go.Scatter(
            x=df_nac["anio"],
            y=df_nac["participacion_col_pct"],
            mode="lines+markers",
            name="Participación (%)",
            line=dict(color="#f5a623", width=2.5),
            marker=dict(size=7),
        ),
        secondary_y=True,
    )
    fig_col.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Estrenos Colombianos y Participación de mercado",
        height=340,
        margin=dict(t=40, b=30),
        legend=dict(orientation="h", y=-0.25),
    )
    fig_col.update_yaxes(title_text="Número de estrenos", secondary_y=False)
    fig_col.update_yaxes(title_text="Participación (%)", secondary_y=True)
    st.plotly_chart(fig_col, use_container_width=True)

with col_f:
    fig_pant = go.Figure()
    fig_pant.add_trace(
        go.Scatter(
            x=df_nac["anio"],
            y=df_nac["pantallas"],
            mode="lines+markers",
            name="Pantallas",
            line=dict(color="#c084fc", width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor="rgba(192,132,252,0.12)",
        )
    )
    fig_pant.add_trace(
        go.Scatter(
            x=df_nac["anio"],
            y=df_nac["estrenos_total"],
            mode="lines+markers",
            name="Estrenos totales",
            yaxis="y2",
            line=dict(color="#60a5fa", width=2, dash="dot"),
            marker=dict(size=6),
        )
    )
    fig_pant.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Pantallas y Estrenos Totales",
        xaxis_title="Año",
        yaxis=dict(title="Pantallas"),
        yaxis2=dict(title="Estrenos totales", overlaying="y", side="right"),
        height=340,
        margin=dict(t=40, b=30),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_pant, use_container_width=True)

# Fila 4: Recuperación post-COVID
if mostrar_covid:
    st.markdown(
        '<div class="section-title">Recuperación post-COVID por ciudad</div>',
        unsafe_allow_html=True,
    )

    df_rec = df_all[df_all["ciudad"].isin(ciudades_sel)].copy()
    df_rec_pivot = df_rec.pivot_table(
        index="anio", columns="ciudad", values="recuperacion_ciudad_pct"
    ).reset_index()

    if not df_rec_pivot.empty:
        fig_rec = go.Figure()
        for ciudad in ciudades_sel:
            if ciudad in df_rec_pivot.columns:
                fig_rec.add_trace(
                    go.Scatter(
                        x=df_rec_pivot["anio"],
                        y=df_rec_pivot[ciudad],
                        mode="lines+markers",
                        name=ciudad,
                        line=dict(color=COLORES_CIUDAD.get(ciudad, "#aaa"), width=2.5),
                        marker=dict(size=7),
                    )
                )
        fig_rec.add_hline(
            y=100,
            line_dash="dash",
            line_color="#ffd700",
            annotation_text="Nivel pre-pandemia (100%)",
            annotation_position="top right",
        )
        fig_rec.add_vrect(
            x0=2019.5,
            x1=2021.5,
            fillcolor="rgba(255,200,0,0.07)",
            line_width=0,
        )
        fig_rec.update_layout(
            template=PLOTLY_TEMPLATE,
            title="Índice de Recuperación por Ciudad (%)",
            xaxis_title="Año",
            yaxis_title="Recuperación (%)",
            height=320,
            margin=dict(t=40, b=30),
            legend=dict(orientation="h", y=-0.3),
        )
        st.plotly_chart(fig_rec, use_container_width=True)
# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE DE PROYECCIONES 2026–2028
# Combina Opción 2 (uplift por estrategia) + Opción 3 (CAGR diferenciado)
# Insertar ANTES del st.divider() y st.caption() finales del dashboard
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np

st.markdown(
    '<div class="section-title">Proyección estratégica 2026–2028</div>',
    unsafe_allow_html=True,
)

# ── 1. Parámetros base ────────────────────────────────────────────────────────
# Tomamos los valores reales 2022–2025 del dataset nacional
df_base_proj = df_nac[df_nac["anio"].between(2022, 2025)].sort_values("anio")
anios_base    = df_base_proj["anio"].values
espect_base  = df_base_proj["espectadores_nacional_m"].values

# CAGR real 2022→2025  (Opción 3 base)
cagr_real = (espect_base[-1] / espect_base[0]) ** (1 / (anios_base[-1] - anios_base[0])) - 1

# Año de partida para proyección
val_2025 = float(df_nac.loc[df_nac["anio"] == 2025, "espectadores_nacional_m"].values[0]) \
           if 2025 in df_nac["anio"].values else espect_base[-1]

# ── 2. Definición de escenarios (Opción 2 + 3) ────────────────────────────────
# Cada escenario tiene un CAGR y un conjunto de uplifts acumulados por anio
# Los uplifts están justificados en la Matriz de Convergencia (opciones D,E,F,G,H)

ESCENARIOS = {
    "Pesimista\n(sin estrategia)": {
        "cagr": cagr_real,           # CAGR real 2022-2025 ≈ tendencia actual
        "uplifts": {                  # sin uplift adicional
            2026: 0.0,
            2027: 0.0,
            2028: 0.0,
        },
        "color": "#60a5fa",
        "dash": "dot",
        "descripcion": f"CAGR histórico {cagr_real*100:.1f}% · Sin nuevas iniciativas",
    },
    "Base\n(implementación parcial)": {
        "cagr": cagr_real + 0.03,    # +3 pp por alianzas streaming (Opción E)
        "uplifts": {
            2026: 0.02,              # +2%: eventos nostalgia piloto (Opción F)
            2027: 0.03,              # +3%: talento colombiano escala (Opción G)
            2028: 0.02,              # +2%: retención por Sprint-First (Opción H)
        },
        "color": "#f5a623",
        "dash": "dashdot",
        "descripcion": "Opciones E + F + G parciales · CAGR ajustado",
    },
    "Optimista\n(estrategia completa)": {
        "cagr": cagr_real + 0.06,    # +6 pp por experiencia compartida (Opción D) + streaming
        "uplifts": {
            2026: 0.04,              # +4%: experiencia compartida full (Opción D)
            2027: 0.05,              # +5%: eventos nostalgia + talento local
            2028: 0.04,              # +4%: consolidación y alianzas maduras
        },
        "color": "#4ade80",
        "dash": "solid",
        "descripcion": "Opciones D+E+F+G+H completas · Mayor uplift acumulado",
    },
}

ANIOS_PROY = [2026, 2027, 2028]

# ── 3. Cálculo de proyecciones ────────────────────────────────────────────────
resultados = {}
for nombre, params in ESCENARIOS.items():
    valores = []
    val_ant = val_2025
    for i, anio in enumerate(ANIOS_PROY):
        # Crecimiento base por CAGR + uplift adicional de estrategia
        val_nuevo = val_ant * (1 + params["cagr"]) * (1 + params["uplifts"][anio])
        valores.append(round(val_nuevo, 2))
        val_ant = val_nuevo
    resultados[nombre] = valores

# ── 4. Visualización ─────────────────────────────────────────────────────────
col_proj1, col_proj2 = st.columns([3, 2])

with col_proj1:
    fig_proj = go.Figure()

    # Línea histórica real (2010–2025 o rango seleccionado)
    fig_proj.add_trace(
        go.Scatter(
            x=df_nac["anio"],
            y=df_nac["espectadores_nacional_m"],
            mode="lines+markers",
            name="Histórico real",
            line=dict(color="#e50914", width=3),
            marker=dict(size=7, color="#e50914"),
        )
    )

    # Banda de incertidumbre entre pesimista y optimista
    vals_pes  = resultados[list(ESCENARIOS.keys())[0]]
    vals_opt  = resultados[list(ESCENARIOS.keys())[2]]
    fig_proj.add_trace(
        go.Scatter(
            x=ANIOS_PROY + ANIOS_PROY[::-1],
            y=vals_opt + vals_pes[::-1],
            fill="toself",
            fillcolor="rgba(74,222,128,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            showlegend=False,
            name="Banda de incertidumbre",
        )
    )

    # Línea de conexión 2025→2026 (puente histórico-proyección)
    for nombre, params in ESCENARIOS.items():
        vals = resultados[nombre]
        # Punto puente desde 2025
        x_puente = [2025] + ANIOS_PROY
        y_puente = [val_2025] + vals

        fig_proj.add_trace(
            go.Scatter(
                x=x_puente,
                y=y_puente,
                mode="lines+markers+text",
                name=nombre.replace("\n", " "),
                line=dict(
                    color=params["color"],
                    width=2.5,
                    dash=params["dash"],
                ),
                marker=dict(size=8, color=params["color"]),
                text=[f"{v:.1f}M" for v in y_puente],
                textposition="top center",
            )
        )

    # Línea vertical separando histórico y proyección
    fig_proj.add_vline(
        x=2025.5,
        line_dash="dash",
        line_color="rgba(255,255,255,0.3)",
        annotation_text="→ Proyección",
        annotation_position="top right",
        annotation_font_color="#aaa",
    )

    # Nivel pre-pandemia como referencia
    if 2019 in df_nac["anio"].values:
        val_2019 = float(df_nac.loc[df_nac["anio"] == 2019, "espectadores_nacional_m"].values[0])
        fig_proj.add_hline(
            y=val_2019,
            line_dash="dot",
            line_color="rgba(255,215,0,0.4)",
            annotation_text=f"Pico 2019: {val_2019:.1f}M",
            annotation_position="bottom right",
            annotation_font_color="#ffd700",
        )

    fig_proj.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Espectadores Nacionales: Histórico + Proyección 2026–2028 (millones)",
        xaxis_title="Año",
        yaxis_title="Millones de espectadores",
        height=400,
        margin=dict(t=50, b=40),
        legend=dict(orientation="h", y=-0.3),
    )
    st.plotly_chart(fig_proj, use_container_width=True)

with col_proj2:
    # Tabla resumen de escenarios
    st.markdown("#### Supuestos por escenario")

    datos_tabla = []
    for nombre, params in ESCENARIOS.items():
        uplift_total = (
            (1 + params["uplifts"][2026])
            * (1 + params["uplifts"][2027])
            * (1 + params["uplifts"][2028])
            - 1
        ) * 100
        vals = resultados[nombre]
        datos_tabla.append({
            "Escenario": nombre.replace("\n", " "),
            "CAGR base": f"{params['cagr']*100:.1f}%",
            "Uplift acum.": f"+{uplift_total:.1f}%",
            "2026 (M)": f"{vals[0]:.1f}",
            "2027 (M)": f"{vals[1]:.1f}",
            "2028 (M)": f"{vals[2]:.1f}",
        })

    df_tabla = pd.DataFrame(datos_tabla)
    st.dataframe(
        df_tabla,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Justificación de uplifts")
    st.markdown(
        """
| Opción | Uplift | Fuente |
|--------|--------|--------|
| D – Experiencia compartida | +4%/anio | Diferenciación vs streaming |
| E – Streaming en sala | +3% anio 1 | Nuevos ingresos por alianza |
| F – Eventos nostalgia | +2–5%/anio | Alta viabilidad (Pugh: 25/25) |
| G – Talento colombiano | +3%/anio | Participación col. en riesgo (1.5%) |
| H – Sprint-First | +2% retención | Agilidad organizacional |

*Uplifts aplicados sobre CAGR histórico 2022–2025.*
        """
    )

# ── 5. KPI de brecha ─────────────────────────────────────────────────────────
st.markdown("#### ¿Cuánto falta para recuperar el nivel 2019?")
col_k1, col_k2, col_k3 = st.columns(3)

val_2019_ref = float(
    df_nac.loc[df_nac["anio"] == 2019, "espectadores_nacional_m"].values[0]
) if 2019 in df_nac["anio"].values else 73.1

nombres_esc = list(ESCENARIOS.keys())
for col, idx in zip([col_k1, col_k2, col_k3], [0, 1, 2]):
    nombre = nombres_esc[idx]
    params = ESCENARIOS[nombre]
    val_2028 = resultados[nombre][2]  # proyección final
    brecha = val_2028 / val_2019_ref * 100
    color = params["color"]
    with col:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color};">{val_2028:.1f}M</div>
            <div class="metric-label">{nombre.replace(chr(10), ' ')}<br>espectadores 2028</div>
            <div class="metric-delta" style="color:{color};">
                {brecha:.1f}% del nivel 2019
            </div>
        </div>""",
            unsafe_allow_html=True,
        )

# ── 6. Proyección Cine Los Andes (market share implícito) ────────────────────
st.markdown("#### Proyección Cine Los Andes (estimación por market share)")

# Market share histórico: pico CLA 2019 / pico mercado nacional 2019
VAL_CLA_2019 = 13.2   # millones — dato diapositivas
market_share_cla = VAL_CLA_2019 / val_2019_ref  # ≈ 18%

col_ms1, col_ms2, col_ms3, col_ms4 = st.columns(4)

with col_ms1:
    st.markdown(
        f"""
    <div class="metric-card">
        <div class="metric-value" style="color:#aaa;">{market_share_cla*100:.1f}%</div>
        <div class="metric-label">Market share histórico<br>CLA / Mercado nacional</div>
        <div class="metric-delta" style="color:#aaa;">13.2M / {val_2019_ref:.1f}M · pico 2019</div>
    </div>""",
        unsafe_allow_html=True,
    )

nombres_esc = list(ESCENARIOS.keys())
for col, idx in zip([col_ms2, col_ms3, col_ms4], [0, 1, 2]):
    nombre = nombres_esc[idx]
    params = ESCENARIOS[nombre]
    val_nac_2028 = resultados[nombre][2]
    val_cla_2028 = val_nac_2028 * market_share_cla
    pct_vs_pico = val_cla_2028 / VAL_CLA_2019 * 100
    color = params["color"]
    with col:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color};">{val_cla_2028:.1f}M</div>
            <div class="metric-label">{nombre.replace(chr(10), ' ')}<br>CLA espectadores 2028</div>
            <div class="metric-delta" style="color:{color};">
                {pct_vs_pico:.1f}% del pico CLA 2019
            </div>
        </div>""",
            unsafe_allow_html=True,
        )

st.caption(
    f"⚠️ Estimación basada en market share histórico CLA ≈ {market_share_cla*100:.1f}% "
    "(13.2M espectadores CLA 2019 / 73.1M mercado nacional 2019). "
    "La proyección nacional proviene del CAGR 2022–2025 ajustado por uplift estratégico. "
    "No representa datos internos de Cine Los Andes."
)

st.divider()
st.caption(
    "Fuente: Cine en Cifras Edición 30 - Proimágenes Colombia · "
    "Dashboard desarrollado por Cine Los Andes"
)

