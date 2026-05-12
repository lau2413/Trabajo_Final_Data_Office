import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.family'] = 'sans-serif'

def run_eda():
    csv_path = os.path.join('data', 'processed', 'cine_en_cifras_validado.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join('data', 'raw', 'cine_en_cifras_datos.csv')

    df = pd.read_csv(csv_path)
    df = df.rename(columns={
        'espectadores_nacional_m': 'espectadores_nacional_M',
        'taquilla_m_cop': 'taquilla_M_COP',
        'espectadores_ciudad_m': 'espectadores_ciudad_M',
        'espectadores_col_m': 'espectadores_col_M',
        'taquilla_col_m_cop': 'taquilla_col_M_COP',
    })
    df = df[df['ciudad'] != 'Nacional']
    print("Shape:", df.shape)
    print("Columnas:", df.columns.tolist())
    print("\n=== Tipos de datos ===")
    print(df.dtypes)
    print("\n=== Valores nulos ===")
    print(df.isnull().sum())

    nacional = df.drop_duplicates('año').reset_index(drop=True)

    print("\n=== Estadísticas descriptivas nacionales ===")
    cols_desc = ['espectadores_nacional_M', 'estrenos_total', 'taquilla_M_COP',
                 'precio_boleta_real', 'indice_asistencia', 'pantallas']
    cols_present = [c for c in cols_desc if c in nacional.columns]
    print(nacional[cols_present].describe().round(2))

    os.makedirs('img', exist_ok=True)

    # ===========================================================
    # GRÁFICO 1 — Tendencia de asistencia nacional
    # ===========================================================
    fig, ax = plt.subplots(figsize=(13, 5))
    colores = []
    for a in nacional['año']:
        if a <= 2019:   colores.append('#2196F3')
        elif a <= 2021: colores.append('#F44336')
        else:           colores.append('#FF9800')

    bars = ax.bar(nacional['año'], nacional['espectadores_nacional_M'],
                  color=colores, alpha=0.85, zorder=2)

    pico_2019 = nacional.loc[nacional['año'] == 2019, 'espectadores_nacional_M'].values[0]
    val_2025  = nacional.loc[nacional['año'] == 2025, 'espectadores_nacional_M'].values[0]
    val_2020  = nacional.loc[nacional['año'] == 2020, 'espectadores_nacional_M'].values[0]

    ax.axhline(pico_2019, color='green', linestyle='--', linewidth=1.2, alpha=0.7,
               label=f'Pico 2019: {pico_2019:.1f}M')
    ax.axhline(val_2025, color='orange', linestyle='--', linewidth=1.2, alpha=0.7,
               label=f'2025: {val_2025:.1f}M ({val_2025/pico_2019*100:.1f}% del pico)')

    ax.annotate(
        'Pandemia\nCOVID-19',
        xy=(2020, val_2020), xytext=(2021.1, val_2020 + 15),
        arrowprops=dict(arrowstyle='->', color='#F44336', lw=1.5),
        fontsize=9, color='#F44336', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#F44336', alpha=0.9)
    )
    ax.annotate(
        'Estancamiento\npost-pandemia',
        xy=(2025, val_2025), xytext=(2023.1, val_2025 + 12),
        arrowprops=dict(arrowstyle='->', color='#FF9800', lw=1.5),
        fontsize=9, color='#FF9800', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#FF9800', alpha=0.9)
    )

    for bar, val in zip(bars, nacional['espectadores_nacional_M']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}', ha='center', va='bottom', fontsize=7, rotation=45)

    ax.set_title(
        '¿Por qué Cine Los Andes necesita reinventarse?\n'
        'Asistencia total a salas de cine en Colombia 2010–2025',
        fontsize=13, fontweight='bold'
    )
    ax.set_ylabel('Millones de espectadores')
    ax.set_xlabel('Año')
    ax.set_xticks(nacional['año'])

    p1 = mpatches.Patch(color='#2196F3', alpha=0.85, label='Crecimiento prepandemia')
    p2 = mpatches.Patch(color='#F44336', alpha=0.85, label='Pandemia COVID-19')
    p3 = mpatches.Patch(color='#FF9800', alpha=0.85, label='Recuperación parcial / Estancamiento')
    ax.legend(handles=[p1, p2, p3], loc='upper left', fontsize=9)

    fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
             ha='right', fontsize=7, color='gray')
    plt.tight_layout()
    plt.savefig('img/01_tendencia_nacional.png', bbox_inches='tight')
    plt.close()
    print(f"\nInsight G1: La asistencia de 2025 equivale al {val_2025/pico_2019*100:.1f}% del pico de 2019.")

    # ===========================================================
    # GRÁFICO 2 — Precio vs Asistencia
    # ===========================================================
    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()

    ax1.fill_between(nacional['año'], nacional['espectadores_nacional_M'], alpha=0.25, color='steelblue')
    l1, = ax1.plot(nacional['año'], nacional['espectadores_nacional_M'],
                   marker='o', color='steelblue', linewidth=2, label='Espectadores (M)')
    l2, = ax2.plot(nacional['año'], nacional['precio_boleta_real'],
                   marker='s', color='tomato', linewidth=2, linestyle='--',
                   label='Precio real boleta (COP)')

    ax1.set_ylabel('Millones de espectadores', color='steelblue', fontsize=11)
    ax2.set_ylabel('Precio real boleta (COP)', color='tomato', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='steelblue')
    ax2.tick_params(axis='y', labelcolor='tomato')
    ax2.set_ylim(7000, 11000)
    ax1.set_xlabel('Año')
    ax1.set_title(
        '¿Bajar el precio fue suficiente? No.\n'
        'Precio real de boleta vs Asistencia 2010–2025',
        fontsize=13, fontweight='bold'
    )
    ax1.set_xticks(nacional['año'])

    fig.legend(handles=[l1, l2], loc='lower center', ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, -0.05), frameon=True)

    fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
             ha='right', fontsize=7, color='gray')
    plt.tight_layout()
    plt.savefig('img/02_precio_vs_asistencia.png', bbox_inches='tight')
    plt.close()

    # ===========================================================
    # GRÁFICO 3 — Estrenos vs Asistencia
    # ===========================================================
    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()

    ax1.bar(nacional['año'], nacional['espectadores_nacional_M'], alpha=0.6,
            color='steelblue', label='Espectadores (M)')
    l2, = ax2.plot(nacional['año'], nacional['estrenos_total'],
                   marker='o', color='darkorange', linewidth=2, label='Estrenos totales')

    ax1.set_ylabel('Millones de espectadores', color='steelblue', fontsize=11)
    ax2.set_ylabel('Número de estrenos', color='darkorange', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='steelblue')
    ax2.tick_params(axis='y', labelcolor='darkorange')
    ax1.set_xlabel('Año')
    ax1.set_title(
        '¿Más películas atrajeron más público? Tampoco.\n'
        'Estrenos totales vs Asistencia 2010–2025',
        fontsize=13, fontweight='bold'
    )
    ax1.set_xticks(nacional['año'])

    p_bar = mpatches.Patch(color='steelblue', alpha=0.6, label='Espectadores (M)')
    fig.legend(handles=[p_bar, l2], loc='lower center', ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, -0.05), frameon=True)

    fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
             ha='right', fontsize=7, color='gray')
    plt.tight_layout()
    plt.savefig('img/03_estrenos_vs_asistencia.png', bbox_inches='tight')
    plt.close()

    # ===========================================================
    # GRÁFICO 4 — Recuperación por Ciudad (2025)
    # ===========================================================
    base_2019 = df[df['año'] == 2019].set_index('ciudad')['espectadores_ciudad_M']
    ciudades_2025 = df[df['año'] == 2025].copy()
    ciudades_2025['recuperacion_ciudad_pct'] = ciudades_2025.apply(
        lambda r: round(r['espectadores_ciudad_M'] / base_2019[r['ciudad']] * 100, 1), axis=1
    )
    ciudades_2025 = ciudades_2025.sort_values('recuperacion_ciudad_pct').reset_index(drop=True)

    if not ciudades_2025.empty:
        colores_barras = [
            '#F44336' if v < 70 else '#FF9800' if v < 80 else '#4CAF50'
            for v in ciudades_2025['recuperacion_ciudad_pct']
        ]
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.barh(ciudades_2025['ciudad'], ciudades_2025['recuperacion_ciudad_pct'],
                       color=colores_barras, alpha=0.85)

        ax.axvline(100, color='#1B5E20', linestyle='--', linewidth=2, alpha=0.85)
        ax.text(100.5, len(ciudades_2025) - 0.5, 'Nivel 2019\n(100%)',
                va='top', fontsize=8, color='#1B5E20', fontweight='bold')

        ax.axvline(75, color='#424242', linestyle=':', linewidth=2.2, alpha=0.9)
        ax.text(75.5, 0.3, 'Umbral piloto\n(75%)',
                va='bottom', fontsize=8, color='#424242', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#424242', alpha=0.85))

        for bar, val in zip(bars, ciudades_2025['recuperacion_ciudad_pct']):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', fontsize=11, fontweight='bold')

        ax.set_xlim(0, 118)
        ax.set_xlabel('% de recuperación vs pico 2019')
        ax.set_title(
            '¿Dónde lanzar primero el piloto de experiencia?\n'
            'Recuperación de asistencia por ciudad vs pico 2019 – 2025',
            fontsize=13, fontweight='bold'
        )

        p1 = mpatches.Patch(color='#4CAF50', alpha=0.85, label='≥ 80% recuperación')
        p2 = mpatches.Patch(color='#FF9800', alpha=0.85, label='70–80% recuperación')
        p3 = mpatches.Patch(color='#F44336', alpha=0.85, label='< 70% recuperación')
        ax.legend(handles=[p1, p2, p3], loc='lower right', fontsize=9)

        fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
                 ha='right', fontsize=7, color='gray')
        plt.tight_layout()
        plt.savefig('img/04_recuperacion_ciudades.png', bbox_inches='tight')
        plt.close()

    # ===========================================================
    # GRÁFICO 5 — Asistencia por Ciudad (serie histórica)
    # ===========================================================
    fig, ax = plt.subplots(figsize=(13, 6))

    colores_ciudades = {
        'Bogota':       '#1565C0',
        'Bogotá':       '#1565C0',
        'Medellin':     '#2E7D32',
        'Medellín':     '#2E7D32',
        'Cali':         '#F57F17',
        'Bucaramanga':  '#6A1B9A',
        'Barranquilla': '#C62828'
    }

    ciudades_en_df = df['ciudad'].unique()
    print("\nCiudades en el CSV:", ciudades_en_df)

    graficadas = set()
    for ciudad_real in ciudades_en_df:
        color = None
        for key, c in colores_ciudades.items():
            if key.lower() in ciudad_real.lower() or ciudad_real.lower() in key.lower():
                color = c
                break
        if color is None:
            continue
        label = ciudad_real
        subset = df[df['ciudad'] == ciudad_real]
        if not subset.empty and ciudad_real not in graficadas:
            ax.plot(subset['año'], subset['espectadores_ciudad_M'],
                    marker='o', label=label, color=color, linewidth=2)
            graficadas.add(ciudad_real)

    ax.axvspan(2020, 2021, alpha=0.08, color='red')
    ax.text(2020.5, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 5,
            'Pandemia', ha='center', fontsize=8, color='red', alpha=0.7)
    ax.axvline(2019, color='gray', linestyle='--', alpha=0.5, linewidth=1)

    ax.set_title(
        'Asistencia por ciudad 2010–2025\n'
        'Ninguna ciudad volvió a su nivel prepandemia',
        fontsize=13, fontweight='bold'
    )
    ax.set_ylabel('Millones de espectadores')
    ax.set_xlabel('Año')
    ax.set_xticks(df['año'].unique())
    ax.legend(loc='upper left', fontsize=9)

    fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
             ha='right', fontsize=7, color='gray')
    plt.tight_layout()
    plt.savefig('img/05_asistencia_ciudades.png', bbox_inches='tight')
    plt.close()

    # ===========================================================
    # GRÁFICO 6 — Pantallas vs Asistencia
    # ===========================================================
    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()

    ax1.fill_between(nacional['año'], nacional['espectadores_nacional_M'], alpha=0.25, color='steelblue')
    l1, = ax1.plot(nacional['año'], nacional['espectadores_nacional_M'],
                   marker='o', color='steelblue', linewidth=2, label='Espectadores (M)')
    l2, = ax2.plot(nacional['año'], nacional['pantallas'],
                   marker='s', color='#8E24AA', linewidth=2, linestyle='--',
                   label='Pantallas')

    ax1.set_ylabel('Millones de espectadores', color='steelblue', fontsize=11)
    ax2.set_ylabel('Número de pantallas', color='#8E24AA', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='steelblue')
    ax2.tick_params(axis='y', labelcolor='#8E24AA')
    ax1.set_xlabel('Año')
    ax1.set_title(
        'La infraestructura empieza a contraerse\n'
        'Pantallas de exhibición vs Asistencia 2010–2025',
        fontsize=13, fontweight='bold'
    )
    ax1.set_xticks(nacional['año'])

    fig.legend(handles=[l1, l2], loc='lower center', ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, -0.05), frameon=True)

    fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
             ha='right', fontsize=7, color='gray')
    plt.tight_layout()
    plt.savefig('img/06_pantallas_vs_asistencia.png', bbox_inches='tight')
    plt.close()

    # ===========================================================
    # GRÁFICO 7 — Cine Colombiano: Producción vs Asistencia
    # ===========================================================
    fig, ax1 = plt.subplots(figsize=(13, 6))
    ax2 = ax1.twinx()

    ax1.bar(nacional['año'], nacional['estrenos_col'],
            alpha=0.4, color='#5C6BC0', label='Estrenos colombianos')
    l2, = ax2.plot(nacional['año'], nacional['espectadores_col_M'],
                   marker='o', color='darkgreen', linewidth=2,
                   label='Espectadores cine col. (M)')

    ax1.set_ylabel('Número de películas colombianas', color='#5C6BC0', fontsize=11)
    ax2.set_ylabel('Millones de espectadores cine colombiano', color='darkgreen', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='#5C6BC0')
    ax2.tick_params(axis='y', labelcolor='darkgreen')
    ax1.set_xlabel('Año')
    ax1.set_xticks(nacional['año'])
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_title(
        'Impacto del Cine Colombiano: Producción vs Asistencia\n'
        '¿Funciona la estrategia de impulso al talento local?',
        fontsize=13, fontweight='bold'
    )

    p_bar = mpatches.Patch(color='#5C6BC0', alpha=0.4, label='Estrenos colombianos')
    fig.legend(handles=[p_bar, l2], loc='lower center', ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, -0.04), frameon=True)

    fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
             ha='right', fontsize=7, color='gray')
    plt.tight_layout()
    plt.savefig('img/07_cine_colombiano_impacto.png', bbox_inches='tight')
    plt.close()

    # ===========================================================
    # GRÁFICO 8 — Participación de mercado cine colombiano
    # ===========================================================
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(nacional['año'], nacional['participacion_col_pct'],
            marker='D', color='purple', linewidth=2, label='Participación %')
    ax.fill_between(nacional['año'], nacional['participacion_col_pct'],
                    alpha=0.18, color='purple')

    for _, row in nacional.iterrows():
        ax.text(row['año'], row['participacion_col_pct'] + 0.15,
                f"{row['participacion_col_pct']:.1f}%",
                ha='center', va='bottom', fontsize=7, color='purple')

    min_row = nacional.loc[nacional['participacion_col_pct'].idxmin()]
    ax.annotate(
        f"Mínimo histórico\n{min_row['participacion_col_pct']:.1f}% ({int(min_row['año'])})",
        xy=(min_row['año'], min_row['participacion_col_pct']),
        xytext=(min_row['año'] + 1.2, min_row['participacion_col_pct'] + 1.5),
        arrowprops=dict(arrowstyle='->', color='purple', lw=1.5),
        fontsize=9, color='purple', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='purple', alpha=0.95)
    )

    ax.set_ylabel('Porcentaje de Participación (%)', fontsize=11)
    ax.set_xlabel('Año')
    ax.set_title(
        'Participación del Cine Colombiano en el Mercado Total\n'
        'Evolución de la cuota de pantalla y asistencia',
        fontsize=13, fontweight='bold'
    )
    ax.set_xticks(nacional['año'])

    linea_morada = mlines.Line2D([], [], color='purple', marker='D',
                                  linewidth=2, label='Participación cine colombiano (%)')
    ax.legend(handles=[linea_morada], loc='upper left', fontsize=9)

    fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
             ha='right', fontsize=7, color='gray')
    plt.tight_layout()
    plt.savefig('img/08_participacion_colombiana.png', bbox_inches='tight')
    plt.close()

    # ===========================================================
    # GRÁFICO 9 — Paradoja cine colombiano: estrenos vs participación taquilla
    # ===========================================================
    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()

    ax1.bar(nacional['año'], nacional['estrenos_col'],
            alpha=0.4, color='#5C6BC0', label='Estrenos colombianos')
    l2, = ax2.plot(nacional['año'], nacional['participacion_col_pct'],
                   marker='o', color='red', linewidth=2, linestyle='--',
                   label='% participación taquilla')

    # Anotación pico estrenos
    max_estrenos = nacional.loc[nacional['estrenos_col'].idxmax()]
    ax1.annotate(
        f"Pico estrenos\n({int(max_estrenos['estrenos_col'])} en {int(max_estrenos['año'])})",
        xy=(max_estrenos['año'], max_estrenos['estrenos_col']),
        xytext=(max_estrenos['año'] - 2, max_estrenos['estrenos_col'] + 5),
        arrowprops=dict(arrowstyle='->', color='#5C6BC0', lw=1.5),
        fontsize=8, color='#5C6BC0', fontweight='bold'
    )

    # Anotación mínimo histórico participación
    min_part = nacional.loc[nacional['participacion_col_pct'].idxmin()]
    ax2.annotate(
        f"Mínimo histórico\n({min_part['participacion_col_pct']:.1f}% en {int(min_part['año'])})",
        xy=(min_part['año'], min_part['participacion_col_pct']),
        xytext=(min_part['año'] - 2, min_part['participacion_col_pct'] + 1.5),
        arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
        fontsize=8, color='red', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='red', alpha=0.85)
    )

    ax1.set_ylabel('Número de estrenos colombianos', color='#5C6BC0', fontsize=11)
    ax2.set_ylabel('% participación en taquilla nacional', color='red', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='#5C6BC0')
    ax2.tick_params(axis='y', labelcolor='red')
    ax1.set_xlabel('Año')
    ax1.set_xticks(nacional['año'])
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_title(
        'La paradoja del cine colombiano: más estrenos, menos público\n'
        'Estrenos colombianos vs % participación en taquilla 2010–2025',
        fontsize=13, fontweight='bold'
    )

    p_bar = mpatches.Patch(color='#5C6BC0', alpha=0.4, label='Estrenos colombianos')
    fig.legend(handles=[p_bar, l2], loc='lower center', ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, -0.04), frameon=True)

    fig.text(0.99, 0.01, 'Fuente: Proimágenes Colombia – Boletín Cine en Cifras Ed. 30',
             ha='right', fontsize=7, color='gray')
    plt.tight_layout()
    plt.savefig('img/09_paradoja_colombiano.png', bbox_inches='tight')
    plt.close()

    print("\n=== Análisis de Cine Colombiano ===")
    part_2025 = nacional.loc[nacional['año'] == 2025, 'participacion_col_pct'].values[0]
    print(f"Participación final 2025: {part_2025:.2f}%")
    print("Insight: Se analiza si el aumento en estrenos colombianos se tradujo en más espectadores.")

    print("\nEDA completado. Imágenes guardadas en la carpeta 'img/'.")

if __name__ == "__main__":
    run_eda()
