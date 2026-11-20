# Investigación UX — Mesa de Ayuda · Support Co-Pilot

> Programa: **Maestría en Computación para el Desarrollo de Aplicaciones Inteligentes (CODING)**
> Estudiante: Julian Castaño · castano.julian@correounivalle.edu.co
> Proyecto base: **AI Support Co-Pilot — Mesa de Ayuda Inteligente** (ver [README.md raíz](../../README.md) y [Plan.MD](../../Plan.MD))

---

## 1. Objetivo

Aplicar técnicas de Diseño Centrado en el Usuario (DCU) sobre el dominio del proyecto **Mesa de Ayuda — Support Co-Pilot** para validar y enriquecer el backlog del producto a partir de evidencia real con usuarios potenciales. El trabajo permite trazar las decisiones de producto desde la voz del usuario (entrevistas) hasta la planeación incremental (User Story Mapping), pasando por síntesis cualitativa (Diagrama de Afinidad) y arquetipos de diseño (User Personas).

## 2. Puntos resueltos

| # | Punto | Producto resultante | Ubicación |
|---|-------|---------------------|-----------|
| 1 | 4 entrevistas a usuarios potenciales (mín. 1 novato y 1 avanzado) con guía, consentimiento y videos | 4 transcripciones, guía base, plantilla de consentimiento, evidencias en video | [`entrevistas/`](./entrevistas/), [`anexos/`](./anexos/) |
| 2 | Diagrama de Afinidad y 2 User Personas, con evidencia de etapas | Documento con post-its codificados, agrupaciones progresivas y fichas de personas | [`diagrama_afinidad/`](./diagrama_afinidad/), [`08_user_personas.md`](./08_user_personas.md) |
| 3 | User Story Mapping + video explicativo con trazabilidad al Diagrama de Afinidad | Mapa con backbone, walking skeleton, releases + guion para grabar | [`09_user_story_mapping.md`](./09_user_story_mapping.md), [`10_guion_video_usm.md`](./10_guion_video_usm.md) |

## 3. Estructura de la carpeta

El material está organizado en **dos capas separadas**:

- 🎓 **Capa A — Documentos finales**: transcripciones, análisis, diagrama, personas, USM, video del USM, consentimientos firmados.
- 🎬 **Capa B — Guiones de grabación**: un guion por cada participante —incluido Julian como entrevistador— con sus líneas y *backstory*, para grabar las cuatro entrevistas con un libreto compartido.

```
docs/UX Research/
├── README.md                              ← este índice
│
│ ───── 🎓 CAPA A · Documentos finales ─────
│
├── 08_user_personas.md                    ← 2 personas (novata + agente)
├── 09_user_story_mapping.md               ← USM con trazabilidad
├── 10_guion_video_usm.md                  ← guion del video del USM
├── anexos/
│   ├── 01_consentimiento_informado.md     ← plantilla firmable
│   └── 02_guia_entrevista.md              ← guía base usada en las 4 sesiones
├── entrevistas/                           ← transcripciones finales + verbatims
│   ├── 03_entrevista_01_cliente_novato.md
│   ├── 04_entrevista_02_cliente_avanzado.md
│   ├── 05_entrevista_03_agente_soporte.md
│   └── 06_entrevista_04_coordinador_admin.md
└── diagrama_afinidad/
    └── 07_diagrama_afinidad.md            ← etapas 1-4 del proceso
│
│ ───── 🎬 CAPA B · Guiones de grabación ─────
│
└── guiones_grabacion/                     ← una subcarpeta por sesión
    ├── README.md                          ← cómo usar los guiones durante la grabación
    ├── 01_sandra/                         ← Sesión 01 · Clienta Novata
    │   ├── entrevistador.md               ← guion de Julian, específico para Sandra
    │   └── entrevistada.md                ← guion de Sandra
    ├── 02_daniela/                        ← Sesión 02 · Clienta Avanzada
    │   ├── entrevistador.md
    │   └── entrevistada.md
    ├── 03_karen/                          ← Sesión 03 · Agente
    │   ├── entrevistador.md
    │   └── entrevistada.md
    └── 04_lina/                           ← Sesión 04 · Coordinadora
        ├── entrevistador.md
        └── entrevistada.md
```

### ¿Para qué sirve cada capa?

| Capa | Origen | Uso |
|------|--------|-----|
| 🎓 A — Documentos finales | Análisis cualitativo posterior a las grabaciones | Producto académico final |
| 🎬 B — Guiones de grabación | Preparación previa a las grabaciones | Que cada persona —incluido Julian— sepa qué decir en cada momento |

## 4. Muestra de usuarias entrevistadas

Se cubre el espectro de roles del producto (Clienta, Agente, Administradora) y se garantiza heterogeneidad en madurez digital, cumpliendo el requisito de incluir al menos **una usuaria novata** y **una avanzada**. Las cuatro entrevistadas son **mujeres entre 28 y 34 años** de distintas ciudades de Colombia.

| # | Pseudónimo | Edad | Rol en el dominio | Nivel digital | Justificación de selección |
|---|------------|------|-------------------|---------------|----------------------------|
| 1 | Sandra Liliana M. | 33 | Clienta final (asistente administrativa, PYME) | **Novata** | Representa a la usuaria que solo ha usado canales tradicionales (teléfono/correo) y nunca un portal de tickets. |
| 2 | Daniela Andrea R. | 31 | Clienta power-user (Lead Operaciones Digitales, e-commerce) | **Avanzada** | Power-user de Jira, Zendesk y ServiceNow; valida los requisitos no funcionales (filtros, API, integraciones). |
| 3 | Karen Vanessa G. | 28 | Agente de soporte N1 (BPO) | Intermedio-alto | Usuaria interna principal del dashboard del agente (HU-03); 3 años en mesas de ayuda. |
| 4 | Lina Marcela Q. | 34 | Coordinadora de Mesa de Ayuda | Intermedio | Representa al rol Administradora (HU-07); aporta requisitos de SLA y reportes. |

Las cuatro sesiones se realizaron por **Google Meet** con una duración de **10 minutos cada una**, siguiendo la guía base del anexo [`02_guia_entrevista.md`](./anexos/02_guia_entrevista.md).

## 5. Evidencias en video

Por restricciones de tamaño del repositorio, los videos de las cuatro entrevistas y el video explicativo del User Story Mapping se entregan vía Drive. Los enlaces deben pegarse en la siguiente tabla:

| Pieza | Duración | Enlace |
|-------|----------|--------|
| Video Entrevista 1 — Sandra L. (Clienta Novata) | ~10 min | _[pegar enlace Drive]_ |
| Video Entrevista 2 — Daniela R. (Clienta Avanzada) | ~10 min | _[pegar enlace Drive]_ |
| Video Entrevista 3 — Karen G. (Agente de Soporte) | ~10 min | _[pegar enlace Drive]_ |
| Video Entrevista 4 — Lina Q. (Coordinadora) | ~10 min | _[pegar enlace Drive]_ |
| Video explicación User Story Mapping | ~8-10 min | _[pegar enlace Drive]_ |

> Las grabaciones se realizaron con consentimiento informado firmado (ver [`anexos/01_consentimiento_informado.md`](./anexos/01_consentimiento_informado.md)). Los archivos firmados se conservan en formato PDF en la misma carpeta de Drive.

## 6. Trazabilidad metodológica

El flujo metodológico es:

```
Entrevistas (4)
    │   guía + consentimiento + grabación
    ▼
Notas / verbatims (≈25 frases-insight)
    │   1 verbatim ≈ 1 post-it
    ▼
Diagrama de Afinidad (etapas 1→4)
    │   agrupaciones temáticas → categorías
    ▼
User Personas (2)  +  User Story Mapping
    │
    └──→ Backlog priorizado (alimenta los siguientes ciclos del proyecto)
```

Esta trazabilidad permite responder, ante cualquier historia de usuario del backlog del proyecto, de qué insight de qué entrevista se origina.

## 7. Cómo leer este material

- Para una **lectura completa**: README → guía → 4 entrevistas → afinidad → personas → USM → video. La carpeta `guiones_grabacion/` no es obligatoria de revisar.
- Para el **equipo técnico (siguientes ciclos)**: ir directamente al USM y a las personas; usar las entrevistas como referencia cuando una historia de usuario sea ambigua.
- Para **auditar la metodología**: revisar el `diagrama_afinidad/07_diagrama_afinidad.md`, donde se documenta cada etapa del proceso y las decisiones de agrupamiento.
- Para **producir las grabaciones**: cada participante (incluido Julian) recibe SOLO su guion de la carpeta `guiones_grabacion/`. Los demás archivos no se comparten con las personas que interpretan los perfiles, para preservar la naturalidad de la sesión.

## 8. Flujo cronológico recomendado

```
PASO 1 — PREPARACIÓN
   ▸ Redactar guiones (capa B)        ← carpeta guiones_grabacion/
   ▸ Definir agenda con cada persona
   ▸ Enviar a cada uno SU guion + consentimiento

PASO 2 — GRABACIÓN (sesiones de Google Meet · 10 min cada una)
   ▸ Sesión 1: Sandra      ┐
   ▸ Sesión 2: Daniela     │  Julian sigue 0X_<persona>/entrevistador.md
   ▸ Sesión 3: Karen       │  Cada entrevistada sigue su entrevistada.md
   ▸ Sesión 4: Lina        ┘
   ▸ Subir videos a Drive

PASO 3 — ANÁLISIS Y CIERRE (capa A)
   ▸ Refinar transcripciones en entrevistas/  ← cotejar con lo grabado
   ▸ Construir Diagrama de Afinidad (4 etapas)
   ▸ Sintetizar 2 User Personas
   ▸ Construir User Story Mapping
   ▸ Grabar video explicativo del USM
```

Este orden hace explícito que la **capa B alimenta a la capa A**: sin grabaciones no hay transcripciones, sin transcripciones no hay verbatims, sin verbatims no hay afinidad, y sin afinidad no hay personas ni USM trazables.
