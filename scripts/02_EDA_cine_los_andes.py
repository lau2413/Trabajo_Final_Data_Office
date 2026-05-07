import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.family'] = 'sans-serif'

def run_eda():
    csv_path = 'cine_los_andes_sector (1).csv'
    if not os.path.exists(csv_path):
        print(f"Error: No se encontro el archivo {csv_path}.")
        return

    df = pd.read_csv(csv_path)

    # Columnas del CSV:
    # año, ciudad, espectadores_nacional_M, estrenos_total, taquilla_M_COP,
    # precio_boleta_real, indice_asistencia, pantallas, recuperacion_nacional_pct,
    # espectadores_ciudad_M, recuperacion_ciudad_pct, estrenos_col,
    # espectadores_col_M, participacion_col_pct, taquilla_col_M_C

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

    # 3. Tendencia de asistencia nacional
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

    ax.annotate('Pandemia\nCOVID-19', xy=(2020, val_2020), xytext=(2020.3, val_2020 + 10),
                arrowprops=dict(arrowstyle='->', color='#F44336'), fontsize=9, color='#F44336')
    ax.annotate('Estancamiento\npost-pandemia', xy=(2025, val_2025), xytext=(2023.3, val_2025 + 8),
                arrowprops=dict(arrowstyle='->', color='#FF9800'), fontsize=9, color='#FF9800')

    for bar, val in zip(bars, nacional['espectadores_nacional_M']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}', ha='center', va='bottom', fontsize=7, rotation=45)

    ax.set_title('Por que Cine Los Andes necesita reinventarse?\nAsistencia total a salas de cine en Colombia 2010-2025',
                 fontsize=13, fontweight='bold')
    ax.set_ylabel('Millones de espectadores')
    ax.set_xlabel('año')
    ax.set_xticks(nacional['año'])

    p1 = mpatches.Patch(color='#2196F3', alpha=0.85, label='Crecimiento prepandemia')
    p2 = mpatches.Patch(color='#F44336', alpha=0.85, label='Pandemia')
    p3 = mpatches.Patch(color='#FF9800', alpha=0.85, label='Recuperacion parcial / Estancamiento')
    ax.legend(handles=[p1, p2, p3], loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig('img/01_tendencia_nacional.png', bbox_inches='tight')
    plt.close()
    print(f"\nInsight: La asistencia de 2025 equivale al {val_2025/pico_2019*100:.1f}% del pico de 2019.")

    # 4. Precio vs Asistencia
    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()

    ax1.fill_between(nacional['año'], nacional['espectadores_nacional_M'], alpha=0.3, color='steelblue')
    ax1.plot(nacional['año'], nacional['espectadores_nacional_M'], marker='o', color='steelblue',
             linewidth=2, label='Espectadores (M)')
    ax2.plot(nacional['año'], nacional['precio_boleta_real'], marker='s', color='tomato',
             linewidth=2, linestyle='--', label='Precio real boleta (COP)')

    ax1.set_ylabel('Millones de espectadores', color='steelblue', fontsize=11)
    ax2.set_ylabel('Precio real boleta (COP)', color='tomato', fontsize=11)
    ax1.set_xlabel('año')
    ax1.set_title('Bajar el precio fue suficiente? No.\nPrecio real de boleta vs Asistencia 2010-2025',
                  fontsize=13, fontweight='bold')
    ax1.set_xticks(nacional['año'])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig('img/02_precio_vs_asistencia.png', bbox_inches='tight')
    plt.close()

    # 5. Estrenos vs Asistencia
    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()

    ax1.bar(nacional['año'], nacional['espectadores_nacional_M'], alpha=0.6,
            color='steelblue', label='Espectadores (M)')
    ax2.plot(nacional['año'], nacional['estrenos_total'], marker='o',
             color='darkorange', linewidth=2, label='Estrenos totales')

    ax1.set_ylabel('Millones de espectadores', color='steelblue', fontsize=11)
    ax2.set_ylabel('Numero de estrenos', color='darkorange', fontsize=11)
    ax1.set_xlabel('año')
    ax1.set_title('Mas peliculas atrajeron mas publico? Tampoco.\nEstrenos totales vs Asistencia 2010-2025',
                  fontsize=13, fontweight='bold')
    ax1.set_xticks(nacional['año'])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig('img/03_estrenos_vs_asistencia.png', bbox_inches='tight')
    plt.close()

    # 6. Recuperacion por Ciudad (2025)
    ciudades_2025 = df[df['año'] == 2025].sort_values('recuperacion_ciudad_pct').reset_index(drop=True)
    if not ciudades_2025.empty:
        colores_barras = [
            '#F44336' if v < 70 else '#FF9800' if v < 80 else '#4CAF50'
            for v in ciudades_2025['recuperacion_ciudad_pct']
        ]
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.barh(ciudades_2025['ciudad'], ciudades_2025['recuperacion_ciudad_pct'],
                       color=colores_barras, alpha=0.85)
        ax.axvline(100, color='green', linestyle='--', linewidth=1.2, alpha=0.6,
                   label='Nivel 2019 (100%)')
        ax.axvline(75, color='gray', linestyle=':', linewidth=1, alpha=0.6,
                   label='Umbral recomendado piloto (75%)')

        for bar, val in zip(bars, ciudades_2025['recuperacion_ciudad_pct']):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', fontsize=11, fontweight='bold')

        ax.set_xlim(0, 115)
        ax.set_xlabel('% de recuperacion vs pico 2019')
        ax.set_title('Donde lanzar primero el piloto de experiencia?\nRecuperacion de asistencia por ciudad vs pico 2019 - 2025',
                     fontsize=13, fontweight='bold')
        ax.legend(fontsize=9)
        plt.tight_layout()
        plt.savefig('img/04_recuperacion_ciudades.png', bbox_inches='tight')
        plt.close()

    # 7. Asistencia por Ciudad (serie historica)
    fig, ax = plt.subplots(figsize=(13, 6))
    colores_ciudades = {
        'Bogota':       '#1565C0',
        'Medellin':     '#2E7D32',
        'Cali':         '#F57F17',
        'Bucaramanga':  '#6A1B9A',
        'Barranquilla': '#C62828'
    }
    for ciudad, color in colores_ciudades.items():
        subset = df[df['ciudad'] == ciudad]
        if not subset.empty:
            ax.plot(subset['año'], subset['espectadores_ciudad_M'], marker='o',
                    label=ciudad, color=color, linewidth=2)

    ax.axvspan(2020, 2021, alpha=0.08, color='red', label='Pandemia')
    ax.axvline(2019, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.set_title('Asistencia por ciudad 2010-2025\nNinguna ciudad volvio a su nivel prepandemia',
                 fontsize=13, fontweight='bold')
    ax.set_ylabel('Millones de espectadores')
    ax.set_xlabel('año')
    ax.set_xticks(df['año'].unique())
    ax.legend(loc='upper left', fontsize=9)
    plt.tight_layout()
    plt.savefig('img/05_asistencia_ciudades.png', bbox_inches='tight')
    plt.close()

    # 8. CINE COLOMBIANO — Produccion vs Asistencia
    fig, ax1 = plt.subplots(figsize=(13, 6))
    ax2 = ax1.twinx()

    ax1.bar(nacional['año'], nacional['estrenos_col'],
            alpha=0.4, color='#5C6BC0', label='Estrenos colombianos')
    ax2.plot(nacional['año'], nacional['espectadores_col_M'],
             marker='o', color='darkgreen', linewidth=2,
             label='Espectadores cine col (M)')

    ax1.set_ylabel('Numero de peliculas colombianas', color='#5C6BC0', fontsize=11)
    ax2.set_ylabel('Millones de espectadores cine colombiano', color='darkgreen', fontsize=11)
    ax1.set_xlabel('año')
    ax1.set_xticks(nacional['año'])
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_title(
        'Impacto del Cine Colombiano: Produccion vs Asistencia\nFunciona la estrategia de impulso al talento local?',
        fontsize=13, fontweight='bold'
    )

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig('img/07_cine_colombiano_impacto.png', bbox_inches='tight')
    plt.close()

    # 9. Participacion de mercado cine colombiano (%)
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(nacional['año'], nacional['participacion_col_pct'],
            marker='D', color='purple', linewidth=2, label='Participacion %')
    ax.fill_between(nacional['año'], nacional['participacion_col_pct'],
                    alpha=0.2, color='purple')

    ax.set_ylabel('Porcentaje de Participacion (%)', fontsize=11)
    ax.set_xlabel('año')
    ax.set_title('Participacion del Cine Colombiano en el Mercado Total\nEvolucion de la cuota de pantalla y asistencia',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(nacional['año'])
    ax.legend(loc='upper left')

    plt.tight_layout()
    plt.savefig('img/08_participacion_colombiana.png', bbox_inches='tight')
    plt.close()

    print("\n=== Analisis de Cine Colombiano ===")
    part_2025 = nacional.loc[nacional['año'] == 2025, 'participacion_col_pct'].values[0]
    print(f"Participacion final 2025: {part_2025:.2f}%")
    print("Insight: Se analiza si el aumento en estrenos colombianos se tradujo en mas espectadores.")
    print("Si la participacion % es estable o baja mientras los estrenos suben,")
    print("la estrategia de Impulso Local requiere ajustes de calidad o distribucion.")

    print("\nEDA completado. Imagenes guardadas en la carpeta 'img/'.")

if __name__ == "__main__":
    run_eda()