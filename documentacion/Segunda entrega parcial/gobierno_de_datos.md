# 🎬 Gobierno de Datos — Cine Los Andes 🍿

---

# 🧩 1. Marco de Referencia

El gobierno de datos se define sobre el proceso de negocio **“Gestión ágil de experiencias cinematográficas basadas en datos”**, modelado en BPM con cinco *pools*:

* 📊 **Data & Analytics**
* 💡 **Squad de Innovación**
* 🤝 **Alianzas & Contenidos**
* 🎥 **Operaciones de Cine**
* 👥 **Cliente**

Los roles siguen el modelo estándar:

> **Data Owner → Data Steward → Data Custodian**

Cada uno fue asignado según la participación y responsabilidad dentro del flujo del proceso BPM.

Además, se establecen dos dominios de datos diferenciados:

🎟️ **Dominio de Demanda y Experiencia**
📽️ **Dominio de Contenido y Derechos**

---

# 👑 2. Roles de Gobierno

---

## 🎟️ 2.1 Data Owner — Dominio de Demanda y Experiencia

### 👤 Responsable

💡 **Squad de Innovación (Marketing + Producto + Ops)**

### 📝 Justificación BPM

Este *pool* es el encargado de tomar decisiones estratégicas sobre los datos de demanda y experiencia del cliente.

Dentro del proceso:

* Define hipótesis de valor 💭
* Evalúa la viabilidad de ideas 🔍
* Determina cartelera y precios según demanda 🎬💰
* Activa campañas digitales 📲
* Ajusta la estrategia final 🔄

Es el actor responsable del propósito y uso de los datos de audiencia.

### 📌 Responsabilidades

* ✅ Aprobar qué datos de audiencia se recolectan y con qué finalidad.
* ✅ Definir criterios mínimos para superar el gateway **“¿Demanda suficiente?”**
* ✅ Autorizar accesos a los datos procesados.
* ✅ Validar insights antes de activar campañas o cambios estratégicos.
* ✅ Garantizar el uso ético y legal de los datos.

---

## 📽️ 2.2 Data Owner — Dominio de Contenido y Derechos

### 👤 Responsable

🤝 **Pool de Alianzas & Contenidos**

### 📝 Justificación BPM

Este *pool* administra los datos relacionados con:

* Plataformas de streaming 📺
* Catálogos disponibles 🎞️
* Derechos de exhibición ⚖️

Como estos datos tienen implicaciones legales y contractuales, requieren un responsable específico.

### 📌 Responsabilidades

* ✅ Definir qué datos de contenido y derechos se registran.
* ✅ Aprobar condiciones de consulta de datos contractuales.
* ✅ Garantizar vigencia legal de derechos de exhibición.
* ✅ Responder por el cumplimiento legal asociado a contratos y contenido.

---

## 📊 2.3 Data Steward

### 👤 Responsable

📊 **Pool de Data & Analytics**

### 📝 Justificación BPM

Este *pool* opera el ciclo completo de datos del proceso:

* Segmentación de clientes 👥
* Análisis exploratorio (EDA) 📈
* Identificación de tendencias 🔎
* Generación de insights 📑
* Actualización de dashboards 📊

Además, en el ciclo de retroalimentación:

* Recoge datos del evento 🎟️
* Analiza resultados 📉
* Genera nuevos insights 🔄

Es el rol que asegura que los datos sean correctos, consistentes y útiles.

### 📌 Responsabilidades

* ✅ Ejecutar segmentación de clientes.
* ✅ Realizar análisis históricos mediante notebooks EDA.
* ✅ Detectar tendencias de consumo.
* ✅ Generar dashboards e insights estratégicos.
* ✅ Documentar transformaciones y trazabilidad.
* ✅ Reportar problemas de calidad a los Data Owners.

---

## 🛡️ 2.4 Data Custodian

### 👤 Responsable

🎥 **Pool de Operaciones de Cine**

### 📝 Justificación BPM

Este *pool* genera los datos primarios del proceso durante la ejecución del evento.

Produce información sobre:

* Ocupación de salas 🪑
* Ventas 💵
* Satisfacción del cliente ⭐

Sin estos datos en origen:

❌ El Data Steward no puede analizar
❌ Los Data Owners no pueden decidir

Su rol es garantizar la integridad y calidad de los datos desde la fuente.

### 📌 Responsabilidades

* ✅ Garantizar datos completos y confiables.
* ✅ Asegurar entrega correcta al equipo de Data & Analytics.
* ✅ Controlar quién registra datos operacionales.
* ✅ Reportar inconsistencias detectadas.

---

# 📋 3. Matriz RACI

| 🎬 Actividad BPM                  | 🎟️ DO Demanda | 📽️ DO Contenido | 📊 Data Steward | 🛡️ Data Custodian |
| --------------------------------- | :------------: | :--------------: | :-------------: | :----------------: |
| Definir datos de audiencia        |       A/R      |         I        |        C        |          I         |
| Definir datos de contenido        |        I       |        A/R       |        C        |          I         |
| Segmentación de clientes          |        I       |         I        |       R/A       |          I         |
| Análisis histórico (EDA)          |        C       |         I        |       R/A       |          I         |
| Identificación de tendencias      |        C       |         I        |       R/A       |          I         |
| Generación de insights            |        C       |         I        |       R/A       |          I         |
| Generación de ideas de eventos    |       R/A      |         C        |        C        |          I         |
| Definición de hipótesis de valor  |       R/A      |         I        |        C        |          I         |
| Gateway: ¿Idea viable?            |       R/A      |         I        |        C        |          I         |
| Lanzamiento de encuesta           |       R/A      |         I        |        C        |          I         |
| Gateway: ¿Demanda suficiente?     |       R/A      |         I        |        C        |          I         |
| Negociación con plataformas       |        I       |        R/A       |        I        |          I         |
| Gestión de derechos de exhibición |        I       |        R/A       |        I        |          I         |
| Recolección de datos del evento   |        I       |         I        |        C        |         R/A        |
| Calidad de datos en origen        |        I       |         I        |        C        |         R/A        |
| Actualización de dashboards       |        I       |         I        |       R/A       |          C         |
| Retroalimentación e insights      |        C       |         I        |       R/A       |          I         |
| Ajuste de estrategia              |       R/A      |         I        |        C        |          I         |

---

## 🧠 Leyenda RACI

* 🟢 **R = Responsible** → Ejecuta la actividad.
* 🔵 **A = Accountable** → Responde por el resultado.
* 🟡 **C = Consulted** → Es consultado.
* ⚪ **I = Informed** → Es informado.

> 📌 DO = Data Owner

---

# 🎓 Proyecto Académico

✨ **UPB — Data Office Strategy 2026-1**
👩‍💻 *Sofía Mejía Rivas*
👩‍💻 *Laura Jiménez Moreno*
