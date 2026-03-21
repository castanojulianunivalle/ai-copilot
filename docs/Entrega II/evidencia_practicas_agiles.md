# **Entrega II — Evidencia de prácticas ágiles**

**Proyecto:** AI Support Co-Pilot (Mesa de ayuda inteligente)  
**Programa:** Maestría en Computación para el Desarrollo de Aplicaciones Inteligentes (CODING) · Universidad del Valle  
**Modalidad:** Solo Developer (Scrum adaptado)

---

## Contexto de esta entrega

Esta entrega documenta la **aplicación de prácticas ágiles** hasta el punto en que se han **completado el Sprint 0 y el Sprint 1** del plan de proyecto. A partir de aquí el backlog y el release plan reflejan el **estado real** de lo ya entregado y lo pendiente.

| Iteración | Estado al cierre de Entrega II |
|-----------|--------------------------------|
| **Sprint 0** | Completado (documentación técnica, mockups, preparación de entorno — HU-00) |
| **Sprint 1** | Completado (autenticación y perfiles — HU-01, HU-02) |
| **Sprint 2 en adelante** | Planificado / no desarrollado en el alcance de esta evidencia |

*Referencia de fechas de sprints:* `docs/Entrega I/6.release_plan_agilismo.md` y tablero Jira (proyecto configurado con `daily-reporter-main/scripts/setup_jira_ai_copilot.py`).

---

## 1. Product Backlog actualizado

El backlog se mantiene **priorizado por valor** y **dependencias técnicas**, con estimación en **Story Points** (Fibonacci). Tras Sprint 0 y 1, las historias completadas se marcan como entregadas; el resto permanece ordenado para los siguientes sprints.

### 1.1 Resumen por estado (visión Entrega II)

| ID | Historia | SP | Sprint planificado | Estado (Entrega II) |
|----|----------|---:|--------------------|----------------------|
| HU-00 | Documentación técnica, mockups y preparación de entorno | 2 | 0 | **Hecho** |
| HU-01 | Registro de usuarios (clientes) | 3 | 1 | **Hecho** |
| HU-02 | Inicio de sesión y redirección por rol | 2 | 1 | **Hecho** |
| HU-03 | Creación de ticket de soporte | 5 | 2 | Pendiente |
| HU-04 | Dashboard de agente y cambio de estado | 5 | 3 | Pendiente |
| HU-04b | Clasificación por reglas (sistema) | 3 | 3 | Pendiente |
| HU-05 | Notificaciones automatizadas (n8n) | 3 | 4 | Pendiente |
| HU-07 | Dashboard analítico y reportes (Recharts) | 5 | 5 | Pendiente |
| HU-08 | Dataset histórico e ingeniería de datos | 5 | 6 | Pendiente |
| HU-06 | Clasificación mediante IA (LLM) | 8 | 7 | Pendiente |
| HU-09 | Evaluación de modelos (métricas) | 5 | 8 | Pendiente |

**Total Story Points entregados (Sprint 0–1):** HU-00 (2) + HU-01 (3) + HU-02 (2) = **7 SP**  
**Backlog restante (priorizado):** HU-03 … HU-09 según épicas y releases en sección 2.

### 1.2 Épicas (sin cambio estructural)

| Épica | Contenido | Avance relativo Entrega II |
|-------|-----------|----------------------------|
| **Épica 1:** Autenticación y arquitectura base | HU-00, HU-01, HU-02 | Completada respecto al alcance Sprint 0–1 |
| **Épica 2:** Gestión integral de tickets (CRUD) | HU-03 … HU-04b | Pendiente (inicia Sprint 2) |
| **Épica 3:** IA y automatización | HU-05 … HU-09 | Pendiente (semestres siguientes) |

### 1.3 Criterio de actualización

- Las historias **Hecho** cumplen **Definition of Done** acordada en desarrollo (código integrado, pruebas locales, revisión de criterios de aceptación en Jira).
- El backlog **no incluye** documentos de entrega académica formal; solo trabajo de producto, alineado a `docs/Entrega I/6.release_plan_agilismo.md`.

---

## 2. Release Plan actualizado y justificación

### 2.1 Release Plan (vigente)

| Release | Sprints | Objetivo | Estado al cierre Entrega II |
|---------|---------|----------|-----------------------------|
| **Release 1** | 0 – 3 | Sistema transaccional sin IA; base, auth y CRUD con reglas | **En curso** — completados Sprint 0 y 1; faltan Sprint 2 y 3 |
| **Release 2** | 4 – 6 | Automatización (n8n), reportes, dataset | No iniciado |
| **Release 3** | 7 – 8 | Clasificación LLM y evaluación | No iniciado |

### 2.2 Justificación de la actualización

1. **Priorización por riesgo y valor:** Se completó primero **entorno y diseño** (Sprint 0) y **autenticación** (Sprint 1), porque sin identidad y rutas por rol no es viable el CRUD de tickets ni el panel de agente.
2. **Dependencias técnicas:** HU-03 en adelante requieren **Supabase Auth y RLS** ya establecidos en Sprint 1; el plan no adelanta HU de Épica 3 antes de cerrar Release 1.
3. **Alcance realista (Solo Developer):** Los sprints de **3 semanas** y el reparto por releases permiten entregas incrementales sin sobrecargar un único desarrollador.
4. **Alineación con el tablero:** Las versiones (Fix Version) por sprint en Jira siguen reflejando el mismo desglose que el documento de release de Entrega I, actualizado solo en **estado de avance** (Sprint 0–1 cerrados).

No se modifican los **objetivos de negocio** de cada release; solo se documenta el **progreso** respecto a la línea base de la Entrega I.

---

## 3. Sprint Planning — iteraciones desarrolladas (Sprint 0 y 1)

### 3.1 Sprint 0 — Planning

| Campo | Contenido |
|-------|-----------|
| **Fecha (referencia)** | Inicio alineado a calendario: 15 mar 2026 (planificación al inicio del sprint) |
| **Duración del sprint** | ~3 semanas (hasta cierre 4 abr 2026) |
| **Objetivo del sprint** | Dejar documentación técnica, mockups y entorno listo para desarrollo (HU-00), sin incluir redacción de entregas académicas en el backlog de desarrollo. |
| **Elementos traídos del backlog** | HU-00 únicamente (2 SP). |
| **Capacidad** | Estimación coherente con 2 SP y dedicación de un solo desarrollador. |
| **Compromiso del sprint** | Completar ADR/stack en repo, wireframes en `assets/` o `docs/`, README con `.env.example` y flujo de ramas. |
| **Riesgos identificados** | Bloqueo por dependencias de cuentas (Supabase/GitHub); mitigación: checklist de preparación el primer día. |

### 3.2 Sprint 1 — Planning

| Campo | Contenido |
|-------|-----------|
| **Fecha (referencia)** | Inicio alineado: 5 abr 2026 (primer día hábil del sprint; si cae domingo, planning el lunes siguiente, según calendario de ceremonias). |
| **Duración del sprint** | ~3 semanas (hasta ~25 abr 2026) |
| **Objetivo del sprint** | Implementar registro e inicio de sesión con **Supabase Auth**, roles y redirección (HU-01, HU-02). |
| **Elementos traídos del backlog** | HU-01 (3 SP), HU-02 (2 SP) — total **5 SP**. |
| **Dependencias** | Sprint 0 cerrado (entorno y convenciones listas). |
| **Compromiso del sprint** | Formularios validados, JWT/sesión, rutas protegidas y redirección Cliente → `/mis-tickets`, Agente → `/dashboard`, Admin según diseño. |
| **Definición de “listo”** | Criterios de aceptación de HU-01 y HU-02 verificados en entorno local y reflejados en Jira. |

---

## 4. Sprint Review

### 4.1 Sprint 0 — Review

| Campo | Contenido |
|-------|-----------|
| **Fecha (referencia)** | Cierre de sprint: 4 abr 2026 |
| **Participación** | Desarrollador (y, si aplica, tutor/product owner académico como observador). |
| **Incremento mostrado** | Repositorio con notas de arquitectura, mockups accesibles, README reproducible. |
| **Feedback** | Aceptación de que el incremento cumple HU-00; ajustes menores de redacción en README si se detectan. |
| **Estado del backlog** | HU-00 marcada como **Done**; siguiente foco: Sprint 1 (auth). |

### 4.2 Sprint 1 — Review

| Campo | Contenido |
|-------|-----------|
| **Fecha (referencia)** | Cierre de sprint: ~25 abr 2026 |
| **Incremento mostrado** | Demo: registro de cliente, login, redirección por rol y rutas protegidas (navegador / vídeo corto / capturas según política de la asignatura). |
| **Feedback** | Validación de criterios de aceptación; posibles mejoras UX (mensajes de error, accesibilidad) anotadas como refinamiento futuro, no como bloqueo. |
| **Estado del backlog** | HU-01 y HU-02 **Done**; Release 1 avanza; siguiente Sprint 2 (HU-03). |

---

## 5. Sprint Retrospective

### 5.1 Sprint 0 — Retrospective

| Dimensión | Qué salió bien | Qué mejorar | Acciones acordadas |
|-----------|----------------|-------------|---------------------|
| **Proceso** | Checklist de entorno evitó ambigüedad | Falta de tiempo en documentar ramas en el primer día | Añadir diagrama de flujo de Git en README |
| **Técnico** | Mockups acotan alcance de pantallas | Decisiones de tema responsive pendientes | Definir breakpoints mínimos en Sprint 1 |
| **Herramientas** | Jira alineado con sprints | — | Mantener Fix Version por sprint |

### 5.2 Sprint 1 — Retrospective

| Dimensión | Qué salió bien | Qué mejorar | Acciones acordadas |
|-----------|----------------|-------------|---------------------|
| **Proceso** | Commits pequeños facilitan revisión | Pruebas E2E aún frágiles | Reforzar un flujo E2E crítico en Sprint 2 |
| **Técnico** | Integración Supabase estable | Manejo de errores de red en UI | Mensajes explícitos en formularios |
| **Calidad** | Criterios de aceptación claros | Cobertura de casos borde (email duplicado) | Caso de prueba documentado en siguiente sprint |

*Nota:* En equipo reducido, la retrospectiva puede documentarse en **bullet points** en Confluence/Jira o en este repositorio; lo importante es registrar **mejora continua** visible para el siguiente sprint.

---

## Referencias internas

| Documento | Uso |
|-----------|-----|
| `docs/Entrega I/5.backlog_historias.md` | Línea base del backlog y HUs |
| `docs/Entrega I/6.release_plan_agilismo.md` | Releases, sprints y fechas |
| `docs/calendario-ceremonias-semestre-I.csv` | Ceremonias Semestre I (importación calendario) |
| `daily-reporter-main/scripts/setup_jira_ai_copilot.py` | Sincronización conceptual con Jira |

---

*Documento generado para la Entrega II — evidencia de prácticas ágiles (backlog, release plan, planning, review, retrospectiva). Estado simulado: **Sprint 0 y Sprint 1 completados**.*
