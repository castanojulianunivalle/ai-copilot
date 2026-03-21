# Daily Reporter

Automatiza el ciclo completo del reporte diario del equipo (creación → actualización → cierre) en **ClickUp**, sincronizado con el estado real de los issues en **JIRA**. Incluye además documentación y scripts para gestión de proyectos (story mapping, carga a JIRA, reporte de epics).

---

## ⚠️ Antes de subir a un repo público

- **No subas nunca** el archivo `.env` (contiene tokens y datos sensibles).
- Usa `env.example` como plantilla y rellena tus valores en local.
- El archivo `cloudformation-params.json` (si existe) también debe quedar fuera del repo; usa `cloudformation-params.json.example`.

---

## Contenido del repositorio

| Parte | Descripción |
|-------|-------------|
| **Daily Reporter** | Script principal que genera reportes AM/PM en ClickUp a partir de JIRA (ver más abajo). |
| **`project/`** | Documentos de proyecto: acta de inicio, story mapping refinado, calendario de sprints, impact mapping. |
| **`scripts/`** | Utilidades: reporte de epics en JIRA, carga de epics/stories a JIRA, listado de templates ClickUp. |
| **AWS** | Plantilla CloudFormation y handler Lambda para ejecutar el reporte en horarios programados. |

---

## Daily Reporter — Automatización de reportes diarios

Automatiza el ciclo completo del reporte diario del equipo (creación → actualización → cierre) en ClickUp, sincronizado con el estado real de los issues en JIRA.

## 🚀 Ejecución Local

### 1. Requisitos Previos

- Python 3.10 o superior
- Tokens de ClickUp y JIRA configurados

### 2. Configuración Inicial

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv

# 2. Activar entorno virtual
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux/Mac/WSL:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Copiar el ejemplo y llenar con tus valores:
cp env.example .env
# Editar .env con tus tokens y configuración
```

### 3. Variables de Entorno Requeridas

Edita el archivo `.env` con tus valores:

```bash
# ClickUp
CLICKUP_TOKEN=pk_tu_token_aqui
CLICKUP_LIST_ID=123456789
CLICKUP_TEMPLATE_TASK_ID=86c780cqa

# JIRA
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_DEV_FRONTEND_BOARD_ID=32
JIRA_DEV_BACKEND_BOARD_ID=31
JIRA_QA_BOARD_ID=168
```

### 4. Ejecución

#### Ejecución Normal (detecta fase según hora actual)

```bash
python main.py
```

El script automáticamente detecta la fase según la hora:
- **11:00 AM** → `report1` (crear/clonar tarea, llenar con datos de JIRA, cambiar a "Report #1")
- **2:00 PM** → `report2` (actualizar tarea con cambios de JIRA, cambiar a "Report #2")
- **6:00 PM** → `close` (cerrar el día, cambiar a "Closed")

#### Ejecución con Fase Forzada (para pruebas)

```bash
# Forzar fase report1
RUN_PHASE=report1 python main.py

# Forzar fase report2
RUN_PHASE=report2 python main.py

# Forzar fase close
RUN_PHASE=close python main.py
```

#### Ejecución con Fecha Forzada (para pruebas)

```bash
# Probar con una fecha específica
FORCE_DATE=2024-12-20 python main.py

# Combinar con fase forzada
FORCE_DATE=2024-12-20 RUN_PHASE=report1 python main.py
```

#### Ejecutar en Fines de Semana/Festivos (para pruebas)

```bash
FORCE_RUN=true python main.py
```

## 📋 Horarios de Ejecución (Hora Colombia)

El script está diseñado para ejecutarse automáticamente en estos horarios:

- **11:00 AM** - Crear/actualizar tarea diaria, llenar Report #1
- **2:00 PM** - Actualizar tarea con Report #2
- **6:00 PM** - Cerrar tarea del día

Solo se ejecuta en **días laborales** (excluye fines de semana y festivos oficiales de Colombia).

## ☁️ Despliegue en AWS Lambda

### Archivo de Handler

Usa `lambda_handler.py` como punto de entrada:

```python
from lambda_handler import handler

# El handler recibe eventos de EventBridge
```

### Eventos de EventBridge

Ejemplos de eventos en la carpeta `examples/`:

- `eventbridge_report1.json` - Para ejecución de 11:00 AM
- `eventbridge_report2.json` - Para ejecución de 2:00 PM
- `eventbridge_close.json` - Para ejecución de 6:00 PM

### Configuración de EventBridge Rules

Crea reglas en EventBridge con expresiones cron (hora Colombia, UTC-5):

```json
// 11:00 AM Colombia = 16:00 UTC (nov-mar) o 16:00 UTC (abr-oct)
"cron(0 16 ? * MON-FRI *)"

// 2:00 PM Colombia = 19:00 UTC (nov-mar) o 19:00 UTC (abr-oct)
"cron(0 19 ? * MON-FRI *)"

// 6:00 PM Colombia = 23:00 UTC (nov-mar) o 23:00 UTC (abr-oct)
"cron(0 23 ? * MON-FRI *)"
```

**Nota**: Ajusta el horario UTC según el horario de verano/invierno de Colombia.

### Variables de Entorno en Lambda

Configura todas las variables de entorno requeridas en la configuración de Lambda (las mismas que en `.env`).

## 🧪 Pruebas Locales

### Prueba Básica

```bash
# 1. Verificar que el script detecta correctamente la fase
python main.py

# 2. Verificar creación de tarea (forzar report1)
RUN_PHASE=report1 FORCE_RUN=true python main.py

# 3. Verificar actualización (forzar report2)
RUN_PHASE=report2 FORCE_RUN=true python main.py

# 4. Verificar cierre (forzar close)
RUN_PHASE=close FORCE_RUN=true python main.py
```

### Verificar Conexión a JIRA

El script automáticamente consulta JIRA en cada ejecución. Si hay errores de autenticación, verifica:

1. `JIRA_EMAIL` y `JIRA_API_TOKEN` son correctos
2. El token tiene permisos para leer los boards especificados

### Verificar Conexión a ClickUp

Si hay errores con ClickUp, verifica:

1. `CLICKUP_TOKEN` es válido
2. `CLICKUP_LIST_ID` es correcto
3. `CLICKUP_TEMPLATE_TASK_ID` existe y es accesible

## 📁 Estructura del Proyecto

```
.
├── daily_reporter/         # Módulo principal del reporte diario
│   ├── app.py              # Lógica principal de orquestación
│   ├── calendar_utils.py   # Validación de días hábiles y festivos Colombia
│   ├── clickup/            # Cliente API ClickUp y tipos
│   │   ├── __init__.py
│   │   └── client.py
│   ├── config.py           # Carga de configuración desde env vars
│   ├── http_utils.py       # Utilidades HTTP con retries
│   ├── jira/               # Cliente API JIRA, tipos y JQL por defecto
│   │   ├── __init__.py
│   │   └── client.py
│   ├── report_builder.py   # Generación de contenido del reporte
│   └── runtime.py          # Detección de fase según horario
├── project/                # Documentación de proyectos (ej. Sales Route)
│   ├── Story_Mapping_Refinado.md
│   ├── sprints_calendar.csv
│   ├── acta_inicio.txt
│   └── ...
├── scripts/
│   ├── epics_report.py     # Mensaje con epics en progreso y tareas asociadas (JIRA)
│   ├── upload_to_jira.py  # Carga epics/stories/sprints a JIRA
│   ├── upload_to_jira_test.py  # Prueba reducida de carga a JIRA
│   └── clickup_list_templates.py
├── examples/               # Eventos de ejemplo para EventBridge
├── main.py                 # Entry point para ejecución local
├── lambda_handler.py       # Entry point para AWS Lambda
├── requirements.txt
├── env.example             # Plantilla de variables de entorno (no subir .env)
├── cloudformation.yaml
└── cloudformation-params.json.example
```

## 🧩 Usar el template de ClickUp (mantener formato visual)

ClickUp aplica estilos “rich” (callouts, tablas, headers, colores) dentro de la descripción.  
Para **no perder ese formato**, el script:
- Lee y escribe usando **`markdown_description`** (no `description`) vía API.
- **No reconstruye** la descripción completa; en su lugar **reemplaza solo secciones delimitadas por marcadores** dentro del template.

### Marcadores recomendados (ponerlos en la tarea template)

Edita la descripción del template (`CLICKUP_TEMPLATE_TASK_ID`) y añade estos comentarios HTML donde quieras que el script inserte contenido:

- **Planning issues**:
  - `<!-- DR:PLANNING_ISSUES_START -->`
  - `<!-- DR:PLANNING_ISSUES_END -->`
- **Daily summary (tabla/filas)**:
  - `<!-- DR:DAILY_SUMMARY_START -->`
  - `<!-- DR:DAILY_SUMMARY_END -->`
- **Status Rep #1**:
  - `<!-- DR:STATUS_REP_1_START -->`
  - `<!-- DR:STATUS_REP_1_END -->`
- **Status Rep #2**:
  - `<!-- DR:STATUS_REP_2_START -->`
  - `<!-- DR:STATUS_REP_2_END -->`
- **Final summary**:
  - `<!-- DR:FINAL_SUMMARY_START -->`
  - `<!-- DR:FINAL_SUMMARY_END -->`

El script reemplaza únicamente lo que está **entre** esos marcadores, preservando el resto del contenido y su formato.

### 📌 Marcadores para filas dinámicas (N issues)

Para soportar una cantidad variable de tickets, en el template crea una **tabla** con 3 columnas (Issue Link / Rep #1 / Rep #2) y deja el “cuerpo” vacío marcado así:

```text
| Issue Link | Status Rep. #1 | Status Rep. #2 |
|---|---|---|
<!-- DR:PLANNING_ISSUES_START -->
| (placeholder) | (placeholder) | (placeholder) |
<!-- DR:PLANNING_ISSUES_END -->
```

El script reemplaza todo lo que haya entre `DR:PLANNING_ISSUES_START` y `DR:PLANNING_ISSUES_END` por **N filas**, una por issue de JIRA.

### 🧊 Congelar Status Rep. #1 (11AM) y solo actualizar #2 (2PM)

- En `report1`, el script genera las filas con **Status Rep. #1** (snapshot 11AM) y deja **Status Rep. #2** vacío.
- En `report2`, el script **preserva Rep. #1** y actualiza **Rep. #2** (2PM snapshot).
- En `close`, el script **preserva Rep. #1** y vuelve a actualizar **Rep. #2** (6PM snapshot).

Si aparece un issue nuevo después de `report1`, se inicializa su Rep. #1 con el snapshot actual.

### 🧹 Borrar marcadores al final (fase close)

Si quieres que al final del día el template quede “limpio” (sin marcas), configura:

```bash
CLICKUP_STRIP_MARKERS_ON_CLOSE=true
```

En la fase `close`, el script elimina los comentarios `<!-- DR:... -->` dejando solo el contenido final.

### Fallback (si no hay marcadores)

Si el template no tiene marcadores, el script usa un bloque al final (entre `<!-- AUTO DAILY REPORT START -->` y `<!-- AUTO DAILY REPORT END -->`), pero **esto puede verse diferente** al template.

## 🧷 Crear tarea desde un *Task Template* (en vez de copiar una tarea)

El script crea la tarea diaria desde un **Task Template** de ClickUp (**recomendado**).

- **Config**: define `CLICKUP_TASK_TEMPLATE_ID` en tu `.env`.
- `CLICKUP_TEMPLATE_TASK_ID` queda como fallback opcional (solo si quieres copiar una tarea existente).

### Obtener `CLICKUP_TASK_TEMPLATE_ID` desde consola (API)

1) **Listar Teams/Workspaces** (necesitas el `team_id`):

```bash
curl --request GET \
  --url "https://api.clickup.com/api/v2/team" \
  --header "Authorization: $CLICKUP_TOKEN" \
  --header "accept: application/json"
```

2) **Listar Task Templates del team**:

```bash
curl --request GET \
  --url "https://api.clickup.com/api/v2/team/<TEAM_ID>/taskTemplate" \
  --header "Authorization: $CLICKUP_TOKEN" \
  --header "accept: application/json"
```

En la respuesta busca el template por nombre y copia su `id`.

### Alternativa: script local para listar templates

```bash
python scripts/clickup_list_templates.py
```

## 🗒️ Evitar `ITEM_238`: escribir como comentario (recomendado)

En algunos Workspaces, `PUT /task/{id}` para actualizar descripción puede fallar con `500 ITEM_238`.
Para evitarlo y **mantener intacto el formato del template**, usa comentarios:

```bash
CLICKUP_WRITE_MODE=comment
```

Esto hace que el script:
- Cree la tarea desde el template
- Publique el reporte como **comentario** en la tarea
- Cambie el estado (Report #1 / Report #2 / Closed)

## 👤 Forzar asignación de la tarea (evitar notificar al usuario del template)

Si tu template tiene un assignee “default”, ClickUp puede asignar (y notificar) a esa persona al crear la tarea.
Para evitarlo, el script ahora:
- Detecta tu usuario con `GET /user` usando el token, y
- Crea la tarea desde template **con `assignees=[tu_id]`**, y luego fuerza `assignees=[tu_id]` en un update inmediato.

### Obtener tu ClickUp user_id (desde consola)

```bash
curl --request GET \
  --url "https://api.clickup.com/api/v2/user" \
  --header "Authorization: $CLICKUP_TOKEN" \
  --header "accept: application/json"
```

El `id` está en `user.id`.

### Config opcional

Si prefieres fijarlo manualmente:

```bash
CLICKUP_OWNER_ID=123456
```



## Scripts adicionales (JIRA / ClickUp)

### Reporte de Epics en progreso (JIRA)

Genera un mensaje con los epics en proceso y sus tareas asociadas:

```bash
python scripts/epics_report.py
```

Requiere en `.env`: `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`. Opcional: `JIRA_EPICS_PROJECT` (ej. `SCRUM`) o `JIRA_EPICS_BOARD_ID`.

### Cargar Story Mapping a JIRA

Crea sprints, epics, stories y subtareas en un proyecto JIRA a partir de los datos definidos en el script:

```bash
# Vista previa (no crea nada)
python scripts/upload_to_jira.py

# Ejecutar carga real
python scripts/upload_to_jira.py --execute
```

Opcional en `.env`: `JIRA_UPLOAD_PROJECT_KEY`, `JIRA_UPLOAD_BOARD_ID`. Si no se indica board, se detecta por proyecto.

### Proyecto AI Ticket Processor — carga de epics/sprints (Jira)

Para el tablero del **AI Support Co-Pilot** (9 sprints incluido Sprint 0, versiones alineadas al calendario del repo):

```bash
python scripts/setup_jira_ai_copilot.py
python scripts/setup_jira_ai_copilot.py --execute
# Borrar issues, versiones y sprints del proyecto/tablero y volver a crear todo (destructivo):
python scripts/setup_jira_ai_copilot.py --execute --clean
# Misma limpieza sin pulsar Enter (o define JIRA_CLEAN_SKIP_CONFIRM=1 en .env):
python scripts/setup_jira_ai_copilot.py --execute --clean --yes
```

`--clean` solo puede usarse con `--execute`. Requiere las mismas variables Jira que el resto de scripts. Ver también `docs/Entrega I/6.release_plan_agilismo.md` y `docs/calendario-sprints-prs.csv` en la raíz del monorepo.

### Listar templates de ClickUp

```bash
python scripts/clickup_list_templates.py
```

---

## 🔍 Troubleshooting

### Error: "Missing required environment variables"

Verifica que todas las variables requeridas estén en tu `.env` o variables de entorno.

### Error: "Not a working day"

El script solo se ejecuta en días laborales. Para pruebas, usa `FORCE_RUN=true`.

### Error de autenticación JIRA/ClickUp

- Verifica que los tokens sean válidos y no hayan expirado
- Asegúrate de que el formato de los tokens sea correcto (sin espacios extra)

### La tarea no se encuentra en ClickUp

- Verifica que `CLICKUP_LIST_ID` sea correcto
- Asegúrate de que la tarea del día no haya sido eliminada manualmente

## 📝 Notas

- El script es **idempotente**: puedes ejecutarlo múltiples veces sin problemas
- Si la tarea del día ya existe, se actualiza en lugar de crear una duplicada
- El formato del título de la tarea es: `[YYYY-MM-DD] Daily Development Team Report`

