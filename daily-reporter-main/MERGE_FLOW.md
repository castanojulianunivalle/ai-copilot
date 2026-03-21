# Flujo de Merge Strategy

## Estructura Inicial

Tienes:
- **3 tareas de encabezado** (ya existen, hardcodeadas):
  1. `Planning` (86c7890v3) - contiene el encabezado morado con instrucciones
  2. `Daily Summary` (86c789103) - contiene el encabezado morado con instrucciones
  3. `Final Summary` (86c78914f) - contiene el encabezado morado con instrucciones

- **1 tarea objetivo**: La tarea diaria donde quieres el resultado final

## Flujo Paso a Paso

### STEP 1: Crear Tareas de Contenido (dinámico)

Se crean **3 tareas pequeñas** con solo el contenido dinámico (sin encabezados):

```
Tarea Content Planning        → Solo filas de tabla con issues
Tarea Content Daily Summary   → Solo filas de tabla con stats de desarrolladores  
Tarea Content Final Summary   → Solo resumen final (si fase = close)
```

### STEP 2: Duplicar Encabezados y Mergear Contenido

Para cada par (encabezado, contenido):

1. **Duplicar** la tarea de encabezado original (para preservarla)
   - Original: `Planning` (86c7890v3) → **Se preserva intacta**
   - Copia: `[2025-12-26] Planning - ...` → Nueva tarea con encabezado

2. **Mergear** la tarea de contenido en la copia del encabezado
   - Content Planning → se mergea en → Copia de Planning
   - Resultado: Copia de Planning ahora tiene encabezado + contenido

3. Repetir para Daily Summary y Final Summary

Después del STEP 2:
- **Originales intactas**: Planning (86c7890v3), Daily Summary (86c789103), Final Summary (86c78914f)
- **3 tareas de contenido**: Eliminadas (se mergearon)
- **3 copias de encabezado con contenido**: Listas para merge final

### STEP 3: Merge Final

Mergear todas las copias de encabezado (que ya tienen contenido) en la tarea objetivo:

```
Copia Planning (con contenido)
Copia Daily Summary (con contenido)
Copia Final Summary (con contenido)
        ↓
    [MERGE]
        ↓
   Tarea Objetivo (tiene TODO: encabezados + contenido)
```

Después del STEP 3:
- **3 copias de encabezado**: Eliminadas (se mergearon)
- **Tarea objetivo**: Tiene todo el contenido completo
- **3 tareas de encabezado originales**: Siguen intactas (se pueden reutilizar)

## Resumen Visual

```
INICIO:
  [Planning Original] [Daily Summary Original] [Final Summary Original]  (preservadas)
  [Target Task]  (vacía o con template)

STEP 1 - Crear contenidos:
  [Content Planning] [Content Daily Summary] [Content Final Summary]  (nuevas, pequeñas)

STEP 2 - Duplicar y mergear:
  [Planning Copy] = [Planning Original] (copiada) + [Content Planning] (mergeada)
  [Daily Summary Copy] = [Daily Summary Original] (copiada) + [Content Daily Summary] (mergeada)
  [Final Summary Copy] = [Final Summary Original] (copiada) + [Content Final Summary] (mergeada)
  
  [Content tasks] → Eliminadas (mergeadas)
  [Originals] → Intactas (preservadas)

STEP 3 - Merge final:
  [Target Task] = [Planning Copy] + [Daily Summary Copy] + [Final Summary Copy]
  
  [Copies] → Eliminadas (mergeadas)
  [Target Task] → Completa con todo
  [Originals] → Intactas (listas para reutilizar)
```

## Ventajas

✅ Evita error ITEM_238 (cada operación es pequeña)
✅ Preserva tareas de encabezado originales (reutilizables)
✅ Mantiene formato rico (encabezados morados se preservan)
✅ Resultado final completo en una sola tarea

