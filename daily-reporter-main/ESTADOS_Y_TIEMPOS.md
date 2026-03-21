# Explicación: Asignación de Estados y Tiempos por Issue

## 📊 Asignación de Estados

Los estados se asignan automáticamente basándose en el **nombre del estado de JIRA**. El script busca palabras clave en el nombre del estado (case-insensitive) para determinar el símbolo:

### Mapeo de Estados

| Símbolo | Palabras Clave | Descripción |
|---------|---------------|-------------|
| 🛑 **Stalled** | `blocked`, `stalled`, `on hold`, `imped`, `halt` | Issue bloqueada o pausada |
| 📝 **Pending Review** | `review`, `pr`, `code review`, `pending review`, `qa review` | Esperando revisión |
| ✅ **Accepted** | `done`, `accepted`, `closed`, `released`, `qa passed`, `resolved` | Completado y aceptado |
| 🛠️ **In Progress** | `in progress`, `doing`, `development`, `dev`, `implement`, `testing` | Trabajo activo |
| ⏳ **Not Started** | (default) | Estado inicial, sin empezar |

### Lógica de Detección

```python
def _status_symbol(issue: JiraIssue) -> str:
    s = (issue.status or "").lower()
    # Se buscan las palabras clave en orden de prioridad
    # Primero "stalled" (más específico)
    # Luego "review", "done", "in progress"
    # Finalmente default a "not started"
```

**Importante:** Si un estado contiene múltiples palabras clave, se usa la primera que coincida en el orden de prioridad mostrado arriba.

### Estado Overdue (🕒)

El símbolo 🕒 es **complementario** y se añade cuando:
- El issue tiene una fecha de vencimiento (`due_date`) definida en JIRA
- Y esa fecha es **anterior a la fecha actual**

Se combina con cualquier otro estado (ej: 🛠️ 🕒 = In Progress pero vencido).

---

## ⏱️ Asignación de Tiempos

### Tiempo Original (Estimación)

El tiempo se obtiene del campo **`originalEstimateSeconds`** de JIRA, que proviene de:

1. **`timetracking.originalEstimateSeconds`** (campo de time tracking)
2. O alternativamente: **`timeoriginalestimate`** (campo directo)

### Formato de Tiempo

El tiempo se formatea en formato corto para la sección "Issue Link":

- **Menos de 1 hora:** `30m`, `45m`, etc.
- **Horas exactas:** `1h`, `2h`, `4h`, etc.
- **Horas con decimales:** `1.5h`, `2.3h`, etc. (se redondea a 1 decimal)

### Ubicación en el Reporte

El tiempo aparece en la línea de fecha del issue:
```
Issue Link –🛠️
[KEY-123](url) Issue Title
Developer Name
2025-12-2530m    ← Fecha + estimación juntas
```

**Formato:** `YYYY-MM-DD` + `{estimación}` sin espacio (ej: `2025-12-2530m` o `2025-12-251h`)

---

## 📋 Ejemplo Completo

### Issue en JIRA:
- **Estado:** "In Progress"
- **Due Date:** 2025-12-20 (hoy es 2025-12-25)
- **Original Estimate:** 7200 segundos (2 horas)
- **Asignado:** "Camilo Perez"
- **Fecha creación:** 2025-12-03

### Resultado en el Reporte:
```
Issue Link –🛠️ 🕒
[KEY-123](https://...) Issue Title
Camilo Perez
2025-12-032h

Status Rep. #1 –🛠️ 🕒

Status Rep. #2 – 
```

**Explicación:**
- 🛠️ porque el estado contiene "in progress"
- 🕒 porque la due date (2025-12-20) < hoy (2025-12-25)
- `2h` porque 7200 segundos = 2 horas exactas
- `2025-12-032h` = fecha creación + estimación concatenadas

---

## 🔍 Verificación de Datos

### Si un Issue no muestra tiempo estimado:

Posibles causas:
1. El issue no tiene `originalEstimateSeconds` configurado en JIRA
2. El campo de time tracking no está habilitado en el proyecto de JIRA
3. El tiempo fue eliminado o nunca se estableció

En este caso, el campo aparecerá solo con la fecha: `2025-12-25` (sin estimación).

### Si un Issue no muestra estado correcto:

Verifica que el **nombre del estado en JIRA** contenga alguna de las palabras clave mencionadas. Si tu JIRA usa nombres de estados personalizados que no coinciden con las palabras clave, el script asignará ⏳ (Not Started) como default.

---

## 💡 Recomendaciones

1. **Usa estimaciones consistentes** en JIRA para que los tiempos se reflejen correctamente
2. **Establece due dates** para que el sistema pueda detectar issues overdue
3. **Usa nombres de estados claros** que contengan las palabras clave estándar (o ajusta el código si necesitas mapeos personalizados)

