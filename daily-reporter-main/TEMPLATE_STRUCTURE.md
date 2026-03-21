# Estructura del Template de ClickUp

Este documento explica cómo debe estar estructurado tu template de ClickUp para que funcione correctamente con el script.

## ✅ Marcadores que el código espera

El código busca estos marcadores **exactos** (con guiones bajos `_`):

### 1. Planning & Execution (tabla de issues)
```
<!-- DR:PLANNING_ISSUES_START -->
<!-- DR:PLANNING_ISSUES_END -->
```

**Ubicación**: Entre las filas de la tabla, después del header:

```markdown
| Issue Link | Status Rep. #1 | Status Rep. #2 |
|---|---|---|
<!-- DR:PLANNING_ISSUES_START -->
| (esto será reemplazado por filas dinámicas) |
<!-- DR:PLANNING_ISSUES_END -->
```

### 2. Daily Summary (tabla de desarrolladores)
```
<!-- DR:DAILY_SUMMARY_START -->
<!-- DR:DAILY_SUMMARY_END -->
```

**Ubicación**: Después del header de la tabla, antes de las filas:

```markdown
| Developer | Daily | Status Report #1 | Status Report #2 |
|---|---|---|---|
| Issues | Workload | ⏳ / 📝 / ✅ | 🕒 / 🛑 | ⏳ / 📝 / ✅ | 🕒 / 🛑 |
<!-- DR:DAILY_SUMMARY_START -->
| (esto será reemplazado por filas de desarrolladores) |
<!-- DR:DAILY_SUMMARY_END -->
```

### 3. Status Rep. #1 (solo se actualiza en fase `report1`)
```
<!-- DR:STATUS_REP_1_START -->
<!-- DR:STATUS_REP_1_END -->
```

**Ubicación**: Donde quieras que aparezca el resumen de Status Rep. #1 (ej: después de Daily Summary, antes de Final Summary).

### 4. Status Rep. #2 (se actualiza en fases `report2` y `close`)
```
<!-- DR:STATUS_REP_2_START -->
<!-- DR:STATUS_REP_2_END -->
```

**Ubicación**: Donde quieras que aparezca el resumen de Status Rep. #2.

### 5. Final Summary (solo se actualiza en fase `close`)
```
<!-- DR:FINAL_SUMMARY_START -->
<!-- DR:FINAL_SUMMARY_END -->
```

**Ubicación**: Al final del template, donde quieras que aparezca el resumen final del día.

---

## ⚠️ Importante: Nombres exactos de los marcadores

**✅ CORRECTO** (con guiones bajos):
- `<!-- DR:PLANNING_ISSUES_START -->`
- `<!-- DR:DAILY_SUMMARY_START -->`
- `<!-- DR:STATUS_REP_1_START -->`
- `<!-- DR:STATUS_REP_2_START -->`
- `<!-- DR:FINAL_SUMMARY_START -->`

**❌ INCORRECTO** (con espacios):
- `<!-- DR:PLANNING ISSUES START -->` ❌
- `<!-- DR:DAILY SUMMARY START -->` ❌

---

## 📋 Estructura completa recomendada del template

```markdown
# Planning & Execution
[Tu banner/callout morado con instrucciones]

| Issue Link | Status Rep. #1 | Status Rep. #2 |
|---|---|---|
<!-- DR:PLANNING_ISSUES_START -->
| (placeholder) | (placeholder) | (placeholder) |
<!-- DR:PLANNING_ISSUES_END -->

# Daily Summary
[Tu banner/callout morado con instrucciones]

| Developer | Daily | Status Report #1 | Status Report #2 |
|---|---|---|---|
| Issues | Workload | ⏳ / 📝 / ✅ | 🕒 / 🛑 | ⏳ / 📝 / ✅ | 🕒 / 🛑 |
<!-- DR:DAILY_SUMMARY_START -->
| (placeholder) | | | | | | |
<!-- DR:DAILY_SUMMARY_END -->

<!-- DR:STATUS_REP_1_START -->
(placeholder - se llena en fase report1)
<!-- DR:STATUS_REP_1_END -->

<!-- DR:STATUS_REP_2_START -->
(placeholder - se llena en fase report2 y close)
<!-- DR:STATUS_REP_2_END -->

# Final Summary
[Tu banner/callout morado con instrucciones]

<!-- DR:FINAL_SUMMARY_START -->
(placeholder - se llena en fase close)
<!-- DR:FINAL_SUMMARY_END -->
```

---

## 🔍 Cómo verificar que los marcadores están correctos

1. Abre tu template en ClickUp
2. Edita la descripción
3. Busca cada marcador usando Ctrl+F (o Cmd+F en Mac)
4. Verifica que los nombres coincidan **exactamente** con los de arriba (con guiones bajos `_`)

---

## 💡 Notas

- Los marcadores son **comentarios HTML**, así que no se ven en la vista final de ClickUp, pero el script los puede leer/editar.
- Si falta algún marcador, el script usará un fallback (añadirá un bloque al final), pero puede verse diferente.
- El formato rico (banners, badges, etc.) se preserva porque solo actualizamos el contenido **entre** los marcadores.

