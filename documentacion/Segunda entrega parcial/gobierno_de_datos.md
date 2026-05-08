# Gobierno de Datos — Cine Los Andes
---

## 1. Marco de Referencia

El gobierno de datos se define sobre dos artefactos del proyecto:

- **BPM "Gestión ágil de experiencias cinematográficas basadas en datos"**: proceso de negocio de Cine Los Andes con cinco pools (Data & Analytics, Squad de Innovación, Alianzas & Contenidos, Operaciones de Cine, Cliente).
- **Arquitectura de datos en tres capas (ArchiMate)**: pipeline del equipo investigador que valida si la estrategia de "Experiencia Compartida" es viable, desde la ingesta del Boletín *Cine en Cifras* Ed. 30 hasta el dashboard de decisión.

Los roles siguen el modelo estándar **Data Owner → Data Steward → Data Custodian**, asignados según los pools del BPM y las capas de la arquitectura.

---

## 2. Roles de Gobierno

### 2.1 Data Owner

**Responsable:** Squad de Innovación (Marketing + Producto + Ops)

**Justificación BPM:** Este pool toma las decisiones estratégicas sobre los datos: define hipótesis de valor, aprueba o descarta ideas en el gateway `¿Es una idea viable?`, activa campañas y ajusta estrategia al final del ciclo. Es el actor que responde por el *propósito* de los datos.

**Justificación arquitectura:** Corresponde al receptor final del Business Layer — recibe los *Insights Estratégicos para Cine Los Andes* y activa las decisiones de negocio.

**Responsabilidades:**
- Aprobar qué datos se recolectan y con qué finalidad (asistencia, ocupación, satisfacción, ingresos).
- Definir los criterios de calidad mínimos aceptables para tomar decisiones (umbral del gateway de demanda en el BPM).
- Autorizar el acceso a los datos procesados por parte de otros roles.
- Validar y aprobar los insights estratégicos antes de su entrega final.
- Responder ante la organización por el uso ético y legal de los datos.

---

### 2.2 Data Steward

**Responsable:** Pool de Data & Analytics

**Justificación BPM:** Este pool opera el ciclo completo de datos: segmentación de clientes, EDA en scripts, generación de insights, actualización de dashboards y ajuste de estrategia. Es el rol que garantiza que los datos sean correctos, consistentes y útiles a lo largo del proceso.

**Justificación arquitectura:** Actúa directamente sobre el Application Layer — ejecuta el Módulo de Procesamiento (.py scripts), aplica transformaciones, genera analítica visual y mantiene el Dashboard de Estrategia de Experiencia (Plotly).

**Responsabilidades:**
- Ejecutar y documentar el pipeline de extracción y estructuración de datos desde el CSV crudo.
- Aplicar y verificar las reglas de calidad sobre los *Datos de Asistencia Procesados* (completitud, consistencia, oportunidad).
- Mantener el linaje de datos desde la *Fuente de Datos Raw* hasta el dashboard final.
- Documentar todas las transformaciones realizadas en los scripts `.py`.
- Gestionar el versionado de scripts y datos en GitHub.
- Reportar anomalías o problemas de calidad al Data Owner.

---

### 2.3 Data Custodian

**Responsable:** Pool de Operaciones de Cine / Infraestructura Técnica

**Justificación BPM:** El pool de Operaciones ejecuta los eventos físicos (preparar salas, ejecutar evento) y es la fuente primaria de datos operacionales (ventas, ocupación, satisfacción del cliente). Es quien alimenta el ciclo de retroalimentación del BPM.

**Justificación arquitectura:** Corresponde al Technology Layer completo — administra GitHub, Workstation Local, VS Code y el archivo `cine_en_cifras_datos.csv` como fuente primaria.

**Responsabilidades:**
- Garantizar la disponibilidad y seguridad del repositorio en GitHub (scripts y datos).
- Administrar la Workstation Local y el entorno de ejecución de los scripts `.py`.
- Asegurar la conectividad con los servicios externos (Internet/HTTPS).
- Gestionar el archivo `cine_en_cifras_datos.csv` como fuente de datos primaria: respaldo, integridad y acceso controlado.
- Recolectar los datos operacionales (ventas, ocupación, satisfacción) que alimentan el ciclo de retroalimentación del BPM.
- Garantizar que el archivo de datos raw permanezca como solo lectura; toda transformación ocurre en notebooks separados.

---

## 3. Matriz RACI

| Actividad (BPM / Pipeline) | Data Owner | Data Steward | Data Custodian |
|---|:---:|:---:|:---:|
| Definir qué datos recolectar y con qué fin | **A/R** | C | I |
| Recolección de datos operacionales (evento) | I | I | **R/A** |
| Extracción y estructuración desde CSV crudo | I | **R/A** | C |
| Transformación y limpieza de datos | I | **R/A** | C |
| Análisis EDA y generación de insights | C | **R/A** | I |
| Actualización de dashboards (Plotly) | I | **R/A** | I |
| Versionado en GitHub | I | C | **R/A** |
| Administración de Workstation / entorno local | I | I | **R/A** |
| Validación gateway BPM (¿demanda suficiente?) | **R/A** | C | I |
| Entrega de insights estratégicos | **R/A** | C | I |
| Aprobación de acceso a datos procesados | **R/A** | C | I |

> **R** = Responsible (ejecuta) · **A** = Accountable (responde) · **C** = Consulted · **I** = Informed

---

*Fuente primaria: Boletín Cine en Cifras Edición 30 — Proimágenes Colombia, abril 2026.*
*Proyecto académico UPB Data Office Strategy 2026-1 — Sofía Mejía Rivas · Laura Jiménez Moreno.*