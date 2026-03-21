Plan Maestro: AI Support Co-Pilot (Mesa de Ayuda Inteligente)  
Programa: Maestría en Computación para el Desarrollo de Aplicaciones Inteligentes (CODING)  
Rol: Solo Developer

## Calendario de desarrollo (9 sprints × 3 semanas)

- **Sprints:** `Sprint 0` … `Sprint 8` (el **Sprint 0** cierra el **4 de abril de 2026**; inicio ~15 mar 2026).
- **Backlog Jira:** solo trabajo de producto (código, integración, pruebas). **No** se planifican en sprints la redacción de informes de curso, artículo ni sustentación (se gestionan fuera del tablero de desarrollo).
- Detalle de fechas y releases: `docs/Entrega I/6.release_plan_agilismo.md`. Carga del tablero: `daily-reporter-main/scripts/setup_jira_ai_copilot.py`.

---

## SEMESTRE 1 — Arquitectura base y gestión de tickets (sin IA)

**Fase:** Fundamentación y CRUD transaccional.  
**Objetivo:** Infraestructura cloud, seguridad y flujo básico de tickets.

**Historias (referencia):** HU-00 (doc técnica, mockups, entorno), HU-01 (registro), HU-02 (login y roles), HU-03 (creación de tickets cliente), HU-04 (dashboard agente y estados), HU-04b (clasificación por reglas).

**Sprints:** 0–3 (Sprint 0: documentación técnica, mockups y preparación previa al desarrollo).

---

## SEMESTRE 2 — Automatización de flujos y analítica (sin IA de clasificación)

**Fase:** Integración de servicios y datos.  
**Objetivo:** Conectar flujos externos (n8n), tiempo real, reportes y dataset histórico.

**Historias (referencia):** HU-05 (notificaciones n8n), HU-07 (dashboard y reportes Recharts), HU-08 (dataset / ETL y documentación en repo).

**Sprints:** 4–6.

---

## SEMESTRE 3 — IA y evaluación

**Fase:** NLP y validación.  
**Objetivo:** Clasificación con LLM y evaluación reproducible (métricas, matrices).

**Historias (referencia):** HU-06 (integración LLM / prompt / persistencia), HU-09 (evaluación: conjuntos, scripts de métricas, export versionado).

**Sprints:** 7–8.

---

## Entregables técnicos (resumen)

| Semestre | Entregable principal |
|----------|----------------------|
| 1 | App web + Supabase + CRUD y reglas básicas |
| 2 | n8n + realtime + analítica + dataset en repo |
| 3 | Clasificación LLM + pipeline de evaluación en repo |

*Informes de asignatura, artículo y sustentación:* fuera del alcance del backlog de sprints de desarrollo en Jira.
