# Guion del video explicativo del User Story Mapping

> Documento operativo para grabar el video que **explica el USM y su trazabilidad con el Diagrama de Afinidad**.

---

## Datos técnicos del video

| Campo | Valor |
|-------|-------|
| Duración objetivo | 8 a 10 minutos |
| Software de grabación | Loom o OBS (pantalla + cámara web circular esquina inferior derecha) |
| Resolución | 1920×1080 mínimo |
| Audio | Diadema externa, eliminar ruido de fondo (Krisp / NVidia Voice) |
| Material visible en pantalla | (1) tablero del USM en Miro, (2) documento Markdown del Diagrama de Afinidad, (3) las dos personas |
| Idioma | Español neutro |

---

## Estructura del video (storyboard)

```
00:00 ─────────── 00:45      Apertura y propósito
00:45 ─────────── 02:00      Recordar las 4 entrevistas + Diagrama de Afinidad
02:00 ─────────── 02:45      Presentar las 2 personas (Sandra y Karen)
02:45 ─────────── 04:00      Recorrer el backbone del USM (5 etapas)
04:00 ─────────── 06:30      Mostrar releases (Skeleton → R1 → R2 → R3)
06:30 ─────────── 08:30      Trazabilidad: 3 historias rastreadas a su cluster
08:30 ─────────── 09:30      Cómo usaremos el mapa en sprints
09:30 ─────────── 10:00      Cierre y siguiente paso
```

---

## Guion línea por línea

### 🎬 Bloque 1 — Apertura (00:00–00:45)

> Cámara: presentador a pantalla completa los primeros 5 segundos, luego se reduce a esquina.

«Hola, soy Julian Castaño, estudiante de la Maestría en Computación para el Desarrollo de Aplicaciones Inteligentes. Este video explica el **User Story Mapping** del proyecto **Mesa de Ayuda — AI Support Co-Pilot** y muestra cómo cada historia del mapa proviene del Diagrama de Afinidad construido a partir de las 4 entrevistas que ya entregué.

En 10 minutos vamos a recorrer: el origen del mapa, las personas, el backbone, los releases y, lo más importante, **la trazabilidad** entre cada card y el cluster de afinidad que la justifica.»

### 🎬 Bloque 2 — De las entrevistas al diagrama (00:45–02:00)

> Pantalla: mostrar la página del Diagrama de Afinidad con la tabla de 25 verbatims.

«Realicé 4 entrevistas de 10 minutos cada una, todas con mujeres entre 28 y 34 años, vía Google Meet: una usuaria novata —Sandra Liliana, asistente administrativa de PYME—; una cliente avanzada, Daniela, líder de e-commerce; una agente de mesa, Karen Vanessa; y una coordinadora, Lina Marcela. De esas 4 sesiones extraje 25 verbatims, que son frases textuales con valor de insight.

Esos 25 post-its pasaron por las **cuatro etapas clásicas** de Affinity Diagramming: captura, agrupamiento sin etiqueta, etiquetado de categorías y síntesis en super-categorías. El resultado fueron **11 clusters** organizados en **4 grandes temas**: confianza y transparencia, visibilidad y trazabilidad, eficiencia operativa, e inclusividad y adopción.

Estos 4 temas son los **principios de diseño** del producto y son la materia prima del USM que les voy a mostrar.»

### 🎬 Bloque 3 — Las dos personas (02:00–02:45)

> Pantalla: dividir en dos columnas con las personas Sandra y Karen.

«El producto tiene dos audiencias y por eso hay dos personas. **Sandra**, 33 años, representa a la clienta final: baja madurez digital, prefiere el teléfono y necesita que el sistema la **tranquilice**. **Karen**, 29 años, representa al staff interno: atiende 50 tickets al día, quiere atajos y necesita que el sistema sea **rápido**.

Estas dos personas son las protagonistas del recorrido del USM y los puntos de prueba para validar cualquier historia: si una historia no le sirve a Sandra ni a Karen, no va.»

### 🎬 Bloque 4 — Backbone del USM (02:45–04:00)

> Pantalla: zoom al encabezado horizontal del USM mostrando las 5 etapas.

«El backbone del mapa son **cinco etapas** que representan el journey completo, de cliente a cliente:

1. **Acceder al sistema** — Sandra entra, Karen también.
2. **Solicitar ayuda** — Sandra describe el problema.
3. **Clasificar y priorizar** — el sistema más Karen deciden urgencia y categoría.
4. **Atender el ticket** — Karen resuelve, Sandra recibe respuesta.
5. **Cerrar y aprender** — encuesta, reapertura, métricas.

Las cinco etapas son la **narrativa**: si una historia no cabe en alguna de estas etapas, posiblemente está fuera del scope del producto.»

### 🎬 Bloque 5 — Releases (04:00–06:30)

> Pantalla: ir bajando por las cuatro líneas de release.

«El mapa se corta en cuatro líneas horizontales:

**Walking Skeleton** — fin del Sprint 1. Lo mínimo para sostener una demo: cliente entra, crea ticket, motor de reglas clasifica, agente cierra. Cinco historias. Esto valida la arquitectura completa: FastAPI, Supabase y React.

**Release 1** — fin del Sprint 3, entrega del Semestre I. Aquí ya las dos personas completan su journey con calidad. Aparecen el override de categoría, atajos de teclado, modo oscuro, plantillas, semáforo de estado, encuesta CSAT. Es el cierre del alcance académico del primer semestre y la **línea base** contra la que se va a comparar el LLM en Semestre III.

**Release 2** — Sprint 4-6, Semestre II. Notificaciones webhook, asignación automática, realtime y, ojo, **el dashboard de la coordinadora**, que es nueva persona que aparece cuando se construye el módulo analítico.

**Release 3** — Sprint 7-9, Semestre III. IA en producción: clasificación con LLM, sentimiento, asistente de respuesta. Y un detalle clave: **reentrenamiento con las correcciones que hizo el agente**. El sistema aprende de su propio uso.»

### 🎬 Bloque 6 — Trazabilidad: 3 ejemplos (06:30–08:30)

> Pantalla: mostrar la **tabla de trazabilidad** del USM y al lado el Diagrama de Afinidad.

«Aquí está la parte más importante. Voy a tomar tres historias del mapa y mostrar de qué cluster del afinidad vienen.

**Ejemplo 1 — "Mostrar nombre del agente al cliente."** Historia del Release 1, persona objetivo: Sandra. Viene del cluster A, *canal humano y empatía*. Origen específico: el verbatim N06 de Sandra Liliana: «*quiero ver nombre y cara de quien me atiende*». Sin esa frase, esta card no estaría aquí. Trazabilidad cumplida.

**Ejemplo 2 — "Sobreescribir la categoría sugerida."** Release 1, persona objetivo: Karen. Viene del cluster E, *IA explicable y override*. Origen: G08 de Karen —«*que me deje sobreescribir sin penalización*»— y N08 de Sandra —«*que el sistema clasifique pero yo pueda corregir*»—. Dos perfiles distintos, mismo principio: la IA sugiere, el humano decide.

**Ejemplo 3 — "Reporte PDF mensual automático."** Release 2, persona objetivo: la coordinadora. Viene del cluster K, *gobernanza y métricas*, originado por Q12 de Lina: «*reporte ejecutivo automático en PDF: dos días al mes recuperados*». Esta historia no existiría sin la entrevista 4.

Esto es lo que significa diseño centrado en el usuario: cada decisión de producto se sostiene en una frase real de un usuario real.»

### 🎬 Bloque 7 — Uso del mapa en planning (08:30–09:30)

> Pantalla: zoom a las celdas verticales del Release 1.

«El mapa se lee así para planificar sprints: **izquierda a derecha por release, arriba a abajo por prioridad dentro de cada celda**. Eso garantiza que cada sprint entregue valor end-to-end y no solo features sueltos. La regla operativa que vamos a aplicar: si se propone una historia nueva, **debe poder mapearse a un cluster del afinidad**. Si no se puede mapear, no entra al mapa. Si la presión es muy alta, volvemos a entrevistar antes de incluirla.»

### 🎬 Bloque 8 — Cierre (09:30–10:00)

> Cámara: a pantalla completa nuevamente.

«En resumen: hicimos 4 entrevistas de 10 minutos, sintetizamos 25 verbatims en 11 clusters y 4 temas, los clusters generaron 2 personas, y las personas y los clusters alimentaron este mapa con su backbone, sus releases y su trazabilidad. El mapa se convierte ahora en el insumo de los siguientes sprints del proyecto. Gracias por ver el video; cualquier comentario me lo pueden enviar al correo `castano.julian@correounivalle.edu.co`.»

---

## Plano técnico de grabación

| Plano | Contenido visible |
|-------|-------------------|
| Plano 1 (00:00) | Cara del presentador, fondo limpio, micro visible |
| Plano 2 (00:45) | Captura del Diagrama de Afinidad con scroll lento |
| Plano 3 (02:00) | Las 2 personas en split-screen |
| Plano 4 (02:45) | USM completo en Miro, vista alejada del backbone |
| Plano 5 (04:00) | USM con highlight progresivo en cada release (animación) |
| Plano 6 (06:30) | Split-screen: tabla de trazabilidad + cluster correspondiente del afinidad |
| Plano 7 (08:30) | USM zoom en columnas verticales |
| Plano 8 (09:30) | Cara presentador con resumen tipo "key takeaways" en bullets sobre la pantalla |

## Lista de verificación pre-grabación

- [ ] Cerrar Slack, Teams, correo, notificaciones del SO.
- [ ] Modo "no molestar" en celular y computadora.
- [ ] Iluminación frontal (lámpara o luz de la ventana).
- [ ] Probar audio con muestra de 30 s.
- [ ] Tener abiertos en pestañas: USM en Miro, Diagrama de Afinidad (Markdown), Personas (Markdown), entrevistas (carpeta).
- [ ] Cronómetro visible para cumplir los 8-10 minutos.
- [ ] Ensayar bloque 6 (trazabilidad) — es el que más se enreda si no se ensaya.

## Lista de verificación post-grabación

- [ ] Revisar que el audio se escucha en al menos 50% del nivel.
- [ ] Recortar inicio y fin (saludos, despedidas innecesarias).
- [ ] Exportar en MP4, 1080p, máximo 500 MB.
- [ ] Subir a Drive del estudiante (carpeta privada compartida con docente).
- [ ] Pegar el enlace de Drive en la tabla del [`README.md`](./README.md) → sección 5 «Evidencias en video».
- [ ] Verificar permisos del Drive: solo equipo académico autorizado. Sin acceso público.
