# Guion de grabación — Lina Marcela Q.

> **Para la persona que interpreta a Lina.** Este guion contiene **tu** parte de la entrevista. Lo que dirá Julian está resumido al inicio de cada bloque para que sepas cuándo te toca hablar. **Duración total: 10 minutos.**

---

## Tu personaje (léelo antes de grabar)

| Campo | Valor |
|-------|-------|
| Nombre | Lina Marcela Q. |
| Edad | 34 años |
| Ciudad | Cali, Colombia |
| Cargo | Coordinadora de Mesa de Ayuda en una empresa de tecnología SaaS |
| Antigüedad | 6 años (4 como agente N1, 2 como coordinadora) |
| Personalidad | Profesional, ejecutiva, eficiente, prefiere data sobre intuición, formal pero cercana |
| Madurez digital | **Intermedia**. Excel avanzado (tablas dinámicas), Power BI básico, Freshdesk |
| Frase que la define | *«Si yo tengo visibilidad, yo defiendo la herramienta.»* |

### Tono al hablar

- Hablas con seguridad de quien rinde cuentas a un comité.
- Vocabulario de gestión: *«SLA, CSAT, FCR, comité directivo, KPI, indicador, capacidad»*.
- Eres directa con tus límites de tiempo.
- Cuando mencionas problemas, los enmarcas como impacto al negocio: *«es plata real»*.

### Backstory (úsala si Julian se desvía)

- Coordinas un equipo de **12 agentes**: 8 N1 y 4 N2.
- Tu gerente: **Roberto** (exigente, mide por números).
- Herramienta de mesa: **Freshdesk**.
- Hay un cliente VIP del que están pendientes (no des nombre, di "el cliente importante").
- Tus KPIs: SLA ≥ 95%, CSAT ≥ 4.5/5, FCR ≥ 70%.

---

## 📋 El producto sobre el que te van a preguntar

> Tu personaje **NO conoce el producto**: lo escucha por primera vez en el bloque 5 y reacciona desde la lente ejecutiva. Esta sección es para que tú entiendas qué hace la herramienta y la compares con Freshdesk si Julian profundiza.

**Nombre:** AI Support Co-Pilot — Mesa de Ayuda Inteligente. Compite en el mismo segmento de **Freshdesk, ServiceNow, Zendesk**.

**Roles del sistema (lo que más te importa como coordinadora):**
- **Cliente:** crea tickets desde un portal web.
- **Agente:** atiende tickets desde un dashboard.
- **Administrador (tu rol):** gestiona usuarios, asigna roles, ve métricas, exporta reportes.

**Pantallas y funcionalidades del rol Administrador:**
- **Panel de gestión de usuarios:** listar, cambiar rol (Cliente, Agente, Administrador), invitar nuevos.
- **Auditoría:** log de quién hizo qué, cuándo (criterio de gobernanza).
- **A futuro (Sem II — no implementado aún):** dashboard analítico con tendencias de tickets resueltos vs. pendientes, métricas por agente, tiempo medio de resolución.
- **A futuro (Sem II):** webhooks → notificaciones por **Telegram y Email** cuando entran tickets urgentes.
- **A futuro (Sem II):** vista en **tiempo real** (Supabase Realtime) de los tickets nuevos sin refrescar la página.
- **A futuro (Sem III):** **análisis de sentimiento del cliente** vía LLM (Llama-3.1). Detecta tono "frustrado" o "urgente" y prioriza automáticamente.
- **A futuro (Sem III):** **comparación matemática** del aporte del LLM vs. el motor de reglas inicial (matriz de confusión, F1-Score, recall).

**Lo que NO existe todavía** (y tu personaje pediría como condición de adopción):
- **Vista de carga por agente** (cuál está saturado, cuál tiene capacidad).
- **Asignación inteligente automática** por carga + skills + tickets pendientes.
- **Reporte ejecutivo mensual en PDF** generado solo, con gráficas listas para el comité directivo.
- **Exportación a Excel** sí o sí (porque el comité te pide tablas en Word/PowerPoint).
- **Modo manual** para revertir cualquier decisión automática de la IA.
- **Modo "aprendiz"** para agentes nuevos en su curva de onboarding.
- **Roles finos / RBAC granular** (no todos en tu equipo deben ver todo).

**Stack tecnológico (para tu cultura general, no para que lo recites):**
- React + Vite (frontend) · FastAPI Python (backend) · Supabase con PostgreSQL y Row-Level Security (datos y auth) · Docker Compose en local · Render + Vercel en producción.

**Lo que tu personaje pensaría espontáneamente al oírlo:**
- *«¿Cómo audito lo que la IA decide? Necesito ver la tasa de error y los falsos positivos.»*
- *«Si me dan análisis de sentimiento, detecto clientes frustrados antes que escalen a Roberto. Eso es plata real.»*
- *«¿Mi equipo lleva 7 años con Freshdesk? Cambiarlos cuesta capacitación; el onboarding tiene que ser excelente.»*
- *«¿Exporta a Excel? Si no, no lo apruebo.»*
- *«¿Modo manual para intervenir cualquier automatización? Imprescindible.»*

> Si Julian profundiza en arquitectura técnica, redirige al impacto del negocio: *«no soy yo quien evalúa stack, yo evalúo si me devuelve horas y me protege los KPIs»*. Eso preserva tu rol ejecutivo.

---

## Estructura de la sesión (10 min)

### 🎬 Bloque 1 — Apertura (0:00 – 0:30)

**Julian:** *(Te saluda formalmente, recuerda las reglas, pregunta si pueden iniciar.)*

**Tú respondes:**
> «Sí, dale. Tengo 10 minutos exactos porque tengo comité.»

*(Julian inicia la grabación.)*

---

### 🎬 Bloque 2 — Calentamiento (0:30 – 1:30)

**Julian:** «Cuéntame en una frase a qué te dedicas y qué tan cómoda te sientes con la tecnología.»

**Tú:**
> «Coordino un equipo de 12 agentes —8 N1 y 4 N2— en una empresa SaaS. Soy responsable del cumplimiento de SLAs, calidad y reporte mensual al comité. Manejo Excel avanzado y Power BI básico. Aprendí Excel para sobrevivir, no por gusto, pero me defiendo. Lo que no me gusta es perder tiempo configurando dashboards.»

---

### 🎬 Bloque 3 — Comportamiento actual (1:30 – 4:30)

**Julian:** «Llévame por un día típico tuyo en pocas frases: cómo te llegan los tickets y cómo los priorizas.»

**Tú:**
> «Llego 8 en punto. Abro el dashboard de Freshdesk y miro tres cosas: tickets abiertos del día anterior, cuáles van a vencer SLA hoy, y si hay alguno crítico sin tocar en la última hora. Standup a las 8:30 con los líderes de turno. Después atiendo escalamientos, reviso calidad de cinco tickets aleatorios, contesto al cliente VIP y a las 4 me siento a hacer reporte ejecutivo.»

**Julian:** «¿Cuál es la parte del proceso que más tiempo te roba sin agregar valor?»

**Tú:**
> «**El reporte ejecutivo mensual.** Lo armo en Excel desde cero con tablas dinámicas; me toma una mañana entera. La mitad del tiempo es **copiando y pegando datos**, no analizándolos. Y no tengo vista de **carga por agente**: cuál está saturado, cuál tiene capacidad. Eso lo veo "a ojo" llamando al líder de turno por Teams. **Tres KPIs me miden: SLA arriba del 95%, CSAT mínimo 4.5/5 y FCR mínimo 70%.** La presión cae sobre mí.»

---

### 🎬 Bloque 4 — Pain point clave (4:30 – 5:30)

**Julian:** «Si pudieras arreglar UNA sola cosa de cómo funciona hoy la mesa de ayuda, ¿cuál sería?»

**Tú:**
> «**Asignación inteligente de tickets** por carga del agente, sus skills y los pendientes que ya tiene. Hoy se reparte por orden de llegada y termino con un agente con 30 tickets y otro con 8. Los dos cobran lo mismo.»

---

### 🎬 Bloque 5 — Validación del concepto (5:30 – 8:00)

**Julian:** *(Te lee el concepto: portal cliente, clasificación automática, dashboard del agente, IA prioriza por urgencia y sentimiento.)*

**Tú:**
> «Me suena bien, pero pongo dos condiciones. Una: yo necesito un panel de **coordinador** con cinco bloques en una sola pantalla — estado, SLA en riesgo, carga por agente, tendencia 4 semanas, últimos 5 escalamientos. Dos: cualquier automatización debe tener **modo manual** para que yo intervenga. Si la IA reasigna, yo debo poder revertir en 2 clics.»

**Julian:** «Si tuvieras que recomendarnos UNA funcionalidad imprescindible para la primera versión, ¿cuál sería?»

**Tú:**
> «**Análisis de sentimiento** que me detecte clientes frustrados antes de que escalen a mi gerente. Eso me ahorra muchos dolores de cabeza. **Es plata real.**»

---

### 🎬 Bloque 6 — Cierre (8:00 – 10:00)

**Julian:** «¿Hay algo importante que no te pregunté?»

**Tú:**
> «Sí: la herramienta tiene que **exportar a Excel sí o sí**. El comité directivo me pide tablas pegadas en Word o PowerPoint. Si no exporta, no sirve.»

**Julian:** «En una sola palabra: ¿qué debería ser este sistema para ti?»

**Tú:** *(con tono firme y profesional)*
> «**Confiable.**»

**Julian:** «Listo, gracias Lina. Detengo grabación.»

---

## Si te preguntan algo no escrito

- **Si te preguntan por números:** ten a mano SLA 95%, CSAT 4.5/5, FCR 70%, equipo de 12 agentes (8 N1 + 4 N2).
- **Si te preguntan por el cliente VIP:** evade con *«no te puedo dar el nombre por confidencialidad»*.
- **Si Julian profundiza:** habla en términos de impacto al negocio, no de funcionalidades en abstracto.
- **Lo que NO haría Lina:** dejar el control a una automatización ciega, descuidar las métricas.

## Justo antes de grabar

- [ ] Lee el guion una vez (10 min). Subraya los **negritas**.
- [ ] Firma el [consentimiento](../anexos/01_consentimiento_informado.md).
- [ ] Conéctate al Google Meet 5 min antes.
- [ ] Si te equivocas: di «perdón, lo digo de nuevo» y continúa.
- [ ] Si Julian se alarga, recuérdale: *«Tengo que cerrar pronto por el comité»*. Refuerza tu personaje.
