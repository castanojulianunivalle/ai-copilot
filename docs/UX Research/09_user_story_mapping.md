# User Story Mapping — Mesa de Ayuda Inteligente

> Mapa de historias de usuario construido con la técnica de Jeff Patton (*User Story Mapping*, O'Reilly 2014) y la guía de Nielsen Norman Group. Conecta el viaje de las dos personas con un backbone de actividades y una columna vertebral por release. Cada historia se traza al cluster del Diagrama de Afinidad que la origina.

---

## 1. Notación del mapa

Un USM se lee así:

```
NIVEL 1 — Backbone (etapas grandes, en orden temporal del usuario)
NIVEL 2 — Tareas / actividades (qué hace el usuario en esa etapa)
NIVEL 3 — Historias de usuario (cómo lo hace, en cards)
                ─── línea del Walking Skeleton ───
                ─── línea del Release 1 ─────────
                ─── línea del Release 2 ─────────
```

- **Backbone (encabezado horizontal):** las grandes fases del journey. Define la *narrativa*.
- **Tareas:** debajo del backbone, agrupan historias relacionadas.
- **Historias de usuario:** cards individuales, con prioridad *vertical* (lo que va arriba se entrega primero).
- **Líneas horizontales (releases):** cortes que indican **qué subconjunto entrega valor mínimo**. La línea más alta es el *walking skeleton*: lo mínimo para que el sistema funcione end-to-end.

---

## 2. Backbone consolidado del journey

El journey une los dos lados (cliente y staff) en una sola narrativa cronológica:

```
┌──────────────────┬──────────────────┬─────────────────┬───────────────────┬──────────────────┐
│ 1. ACCEDER       │ 2. SOLICITAR     │ 3. CLASIFICAR   │ 4. ATENDER        │ 5. CERRAR Y      │
│   AL SISTEMA     │    AYUDA         │    Y PRIORIZAR  │    EL TICKET      │    APRENDER      │
└──────────────────┴──────────────────┴─────────────────┴───────────────────┴──────────────────┘
```

| Etapa | Persona protagonista | Pregunta que responde |
|-------|----------------------|----------------------|
| 1. Acceder al sistema | Ambas | «¿Cómo entro y sé qué hacer?» |
| 2. Solicitar ayuda | Sandra (cliente) | «¿Cómo cuento mi problema y sé que me oyeron?» |
| 3. Clasificar y priorizar | Sistema + Karen | «¿Quién atiende esto y con qué urgencia?» |
| 4. Atender el ticket | Karen (agente) | «¿Cómo resuelvo rápido sin perder calidad?» |
| 5. Cerrar y aprender | Ambas | «¿Quedó resuelto y qué aprendemos para la próxima?» |

---

## 3. Mapa completo

> Cada celda con `[HU-XX]` mapea con el backlog histórico del proyecto. Los `[NUEVA]` son historias derivadas exclusivamente de las entrevistas y no estaban en el backlog original.

```
ETAPA →           1. ACCEDER                 2. SOLICITAR                3. CLASIFICAR               4. ATENDER                  5. CERRAR Y APRENDER
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
TAREAS →    Registrarse / Login        Crear ticket               Asignar categoría            Resolver / responder        Cerrar / encuesta
            Recordar credencial        Adjuntar evidencia          Asignar prioridad            Comunicarse con cliente     Reportar / aprender
            Saber qué puedo hacer      Ver historial propio        Asignar agente               Escalar si toca             Reabrir si volvió
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                              W A L K I N G   S K E L E T O N   (Sprint 1)                                                         ║
║   Lo mínimo para demostrar end-to-end: cliente entra → crea ticket → motor de reglas clasifica → agente lo ve y lo cierra.                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

  [HU-01] Login con email          [HU-03] Crear ticket con      [HU-04] Clasificación        [HU-04b] Ver lista de        [HU-04b] Cambiar estado
  y contraseña                     título y descripción          por reglas (palabras         tickets en dashboard         a "Cerrado"
                                                                 clave) — línea base          del agente

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                              R E L E A S E   1   (Sprint 2-3 · Sem. I)
   El sistema completo del Semestre I: experiencia mínima viable para Sandra y Karen.

  [HU-01] Roles y registro         [NUEVA] "Crear ticket"        [NUEVA] Override humano      [NUEVA] Cabecera fija         [NUEVA] Encuesta CSAT
  con redirección por rol          en 1 sola pantalla, 2         de categoría sugerida        del agente: usuario,          al cerrar
                                   campos, 1 botón                                            ticket, prioridad, SLA
  [NUEVA] Acceso "Hablar con       [NUEVA] Confirmación post-    [NUEVA] Mostrar nombre       [NUEVA] Atajos de teclado    [NUEVA] Reabrir ticket
  una persona" desde el            envío con ID de ticket,       del agente asignado al       (C, R, Tab)                  por parte del cliente
  portal del cliente               estado, ETA concreta          cliente
                                                                                              [NUEVA] Plantillas de         [NUEVA] Auditoría: log
  [NUEVA] Botón "Crear" y          [NUEVA] Buscar y filtrar      [NUEVA] Estado por           respuesta sugeridas           de quién hizo qué
  "Mis casos" como acciones        mis tickets pasados           iconografía (semáforo)
  primarias                                                       en el portal del cliente    [NUEVA] Modo oscuro

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                              R E L E A S E   2   (Sprint 4-6 · Sem. II)

  [NUEVA] SSO (SAML/OIDC)          [NUEVA] Subir adjuntos /      [HU-05] Notificación         [HU-06] Realtime updates     [HU-07] Dashboard
  para clientes corporativos       capturas a un ticket           webhook → Telegram /        en dashboard del agente      analítico para
                                                                 Email                                                     coordinador
  [NUEVA] Recordar sesión          [NUEVA] Borrador antes de
  segura (JWT refresh)             enviar                         [NUEVA] Asignación auto     [NUEVA] Vista historial      [NUEVA] Reporte PDF
                                                                  por carga del agente        del cliente al lado          mensual automático

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                              R E L E A S E   3   (Sprint 7-9 · Sem. III)

  [NUEVA] Onboarding               [NUEVA] Asistente que          [HU-08] Clasificación        [HU-10] Borrador de         [NUEVA] Reentrenamiento
  asistido al primer login         pide info estructurada         por LLM (Llama-3.1)          respuesta sugerido por      del modelo con
  ("modo aprendiz")                cuando el ticket es vago       con confianza visible        IA                          correcciones del agente

                                   [NUEVA] Detección              [HU-09] Análisis de
                                   automática de duplicados        sentimiento del cliente
                                                                  como emoji
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
```

---

## 4. Trazabilidad ↔ Diagrama de Afinidad

Cada historia del USM se origina en uno o más clusters del [Diagrama de Afinidad](./diagrama_afinidad/07_diagrama_afinidad.md). La tabla siguiente lo deja explícito y permite auditar la decisión.

| Historia (USM) | Release | Cluster(s) afín(es) origen | Persona principal |
|----------------|---------|----------------------------|-------------------|
| HU-01 Login con email/contraseña | Skeleton | H — Integraciones / autenticación | Ambas |
| HU-03 Crear ticket título+descripción | Skeleton | C — Información esencial visible | Sandra |
| HU-04 Clasificación por reglas | Skeleton | E — IA explicable y override | Sistema |
| HU-04b Lista de tickets agente | Skeleton | C — Información esencial visible | Karen |
| HU-04b Cambiar estado a Cerrado | Skeleton | J — Eficiencia operativa | Karen |
| Roles y registro | R1 | H — Autenticación | Ambas |
| Crear ticket en 1 pantalla, 2 campos | R1 | I — UI rápida y tolerante | Sandra |
| Acceso "Hablar con una persona" | R1 | A — Canal humano y empatía | Sandra |
| Botón Crear / Mis casos como primarias | R1 | C — Información esencial visible | Sandra |
| Confirmación post-envío con ID, estado, ETA | R1 | C, D — Visibilidad / Promesas concretas | Sandra |
| Buscar y filtrar mis tickets pasados | R1 | B — Continuidad del contexto | Sandra |
| Override humano de categoría sugerida | R1 | E — IA explicable y override | Karen |
| Mostrar nombre del agente al cliente | R1 | A — Canal humano y empatía | Sandra |
| Estado por iconografía (semáforo) | R1 | C — Información esencial visible | Sandra |
| Cabecera fija del agente | R1 | C — Información esencial visible | Karen |
| Atajos de teclado (C, R, Tab) | R1 | J — Eficiencia operativa | Karen |
| Plantillas de respuesta sugeridas | R1 | F — Reducir trabajo repetitivo | Karen |
| Modo oscuro | R1 | I — UI rápida y tolerante | Karen |
| Encuesta CSAT al cerrar | R1 | K — Gobernanza y métricas | Coord. |
| Reabrir ticket por parte del cliente | R1 | B — Continuidad del contexto | Sandra |
| Auditoría: log quién hizo qué | R1 | E — IA explicable y override | Coord. |
| SSO (SAML/OIDC) | R2 | H — Autenticación corporativa | Cliente avanzado |
| Subir adjuntos a un ticket | R2 | C — Información esencial visible | Sandra |
| Recordar sesión segura (JWT refresh) | R2 | H — Autenticación | Ambas |
| Borrador antes de enviar | R2 | I — UI tolerante | Sandra |
| HU-05 Notificación webhook | R2 | A — Canal humano (alertas) | Karen |
| Asignación automática por carga | R2 | K — Gobernanza | Coord. |
| HU-06 Realtime updates dashboard | R2 | J — Eficiencia operativa | Karen |
| Vista historial cliente al lado | R2 | B — Continuidad del contexto | Karen |
| HU-07 Dashboard analítico | R2 | K — Gobernanza y métricas | Coord. |
| Reporte PDF mensual automático | R2 | K — Gobernanza y métricas | Coord. |
| Onboarding asistido (modo aprendiz) | R3 | K — Gestión del cambio | Karen |
| Asistente pide info en ticket vago | R3 | F — Reducir trabajo repetitivo | Sandra |
| Detección automática de duplicados | R3 | B — Continuidad del contexto | Sistema |
| HU-08 Clasificación por LLM con confianza | R3 | E — IA explicable y override | Sistema |
| HU-09 Sentimiento como emoji | R3 | G — Visibilidad emocional y política | Karen |
| HU-10 Borrador de respuesta IA | R3 | F — Reducir trabajo repetitivo | Karen |
| Reentrenamiento con correcciones del agente | R3 | E — IA explicable y override | Sistema |

---

## 5. Releases y criterios de corte

### Walking Skeleton — *fin de Sprint 1*

> *«Lo mínimo posible end-to-end para sostener una demo creíble.»*

**Criterio de cierre:** un cliente pueda registrarse, crear un ticket y un agente pueda verlo y cerrarlo. Sin notificaciones, sin modo oscuro, sin atajos. Probar el flujo completo. Esto valida la arquitectura (FastAPI ↔ Supabase ↔ React) y el motor de reglas.

### Release 1 — *fin de Sprint 3 / Entrega Semestre I*

**Criterio de cierre:** las dos personas pueden completar su journey con calidad.

- Sandra: crea ticket, recibe ID, ve estado por semáforo, sabe quién la atiende.
- Karen: ve cabecera fija, usa atajos, sugiere categoría con override, plantilla de respuesta.

Aquí termina el alcance del Semestre I. Coincide con la línea base de comparación con el LLM.

### Release 2 — *fin de Sprint 6 / Entrega Semestre II*

**Criterio de cierre:** automatización, realtime y analítica disponibles. Aparece el **dashboard de Lina**.

### Release 3 — *fin de Sprint 9 / Entrega Semestre III*

**Criterio de cierre:** IA en producción con métricas comparativas vs. motor de reglas (F1, recall, latencia, costo). El producto pasa de transaccional a inteligente.

---

## 6. Cómo usar este USM en planning

1. **Sprint planning:** seleccionar la fila más alta no terminada y empujarla a la línea siguiente.
2. **Si llega una historia nueva** (ej. de feedback de usuarios): pegarla bajo la tarea correspondiente del backbone, y ubicarla *vertically* según prioridad.
3. **Trazabilidad:** ante cualquier card que se proponga incluir, exigir el cluster de afinidad del que se origina. Si no se puede mapear, **no entra al mapa** (o se vuelve a entrevistar).
4. **Backlog:** el orden de entrega es **leer el mapa de izquierda a derecha y de arriba hacia abajo dentro de cada release**, no por puntos sueltos.

> El video explicativo del USM está en [`10_guion_video_usm.md`](./10_guion_video_usm.md).
