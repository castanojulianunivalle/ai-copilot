# Guiones de grabación — Entrevistas UX

> **Esta carpeta es material de producción**, no documento final. Su objetivo es que cada persona —incluido Julian como entrevistador— sepa qué decir en cada momento durante la grabación de las cuatro entrevistas de **10 minutos**. Los **documentos finales** (transcripciones, análisis, diagrama, personas, USM) viven fuera de esta carpeta.

---

## Estructura: una subcarpeta por sesión

Cada entrevista vive en su propia subcarpeta y contiene **dos guiones pareados**: el del entrevistador (Julian) y el de la entrevistada. El guion del entrevistador es **específico para esa sesión**, no genérico — incluye el tono adecuado, los verbatims que se esperan extraer, las sub-preguntas de profundización y los criterios para reaccionar si la conversación se desvía.

```
guiones_grabacion/
├── README.md                      ← este archivo
├── 01_sandra/                     ← Sesión 01 · Clienta Novata
│   ├── entrevistador.md           ← lo que dice Julian, específico para Sandra
│   └── entrevistada.md            ← lo que dice Sandra
├── 02_daniela/                    ← Sesión 02 · Clienta Avanzada
│   ├── entrevistador.md           ← lo que dice Julian, específico para Daniela
│   └── entrevistada.md            ← lo que dice Daniela
├── 03_karen/                      ← Sesión 03 · Agente
│   ├── entrevistador.md           ← lo que dice Julian, específico para Karen
│   └── entrevistada.md            ← lo que dice Karen
└── 04_lina/                       ← Sesión 04 · Coordinadora
    ├── entrevistador.md           ← lo que dice Julian, específico para Lina
    └── entrevistada.md            ← lo que dice Lina
```

> **¿Por qué un guion del entrevistador por sesión y no uno general?** Porque cada perfil exige un tono distinto, un set de verbatims distinto y un manejo distinto de las desviaciones. Sandra requiere paciencia y lenguaje llano; Daniela responde rápido y con jerga técnica; Karen suelta verbatims potentes que conviene repetir en voz alta para sellarlos; Lina tiene tiempo limitado y responde en lenguaje ejecutivo. Un guion genérico no puede preparar a Julian para esos cuatro escenarios.

## Tabla de archivos

| Sesión | Archivo del entrevistador | Archivo de la entrevistada |
|--------|---------------------------|----------------------------|
| 01 — Sandra Liliana M. (33, novata) | [`01_sandra/entrevistador.md`](./01_sandra/entrevistador.md) | [`01_sandra/entrevistada.md`](./01_sandra/entrevistada.md) |
| 02 — Daniela Andrea R. (31, avanzada) | [`02_daniela/entrevistador.md`](./02_daniela/entrevistador.md) | [`02_daniela/entrevistada.md`](./02_daniela/entrevistada.md) |
| 03 — Karen Vanessa G. (28, agente) | [`03_karen/entrevistador.md`](./03_karen/entrevistador.md) | [`03_karen/entrevistada.md`](./03_karen/entrevistada.md) |
| 04 — Lina Marcela Q. (34, coordinadora) | [`04_lina/entrevistador.md`](./04_lina/entrevistador.md) | [`04_lina/entrevistada.md`](./04_lina/entrevistada.md) |

## Qué hay en cada `entrevistador.md`

- **Ficha de la sesión** con tono, hora, perfil y verbatims clave esperados.
- **Reglas operativas** específicas (cuánto silencio dejar, cómo redirigir si se desvía, cómo manejar la jerga del perfil).
- **Las 8 preguntas en su forma textual** con timing (0:00 – 0:30, 0:30 – 1:30, …).
- **Para cada pregunta:** lo que se espera oír y la **sub-pregunta de profundización** si la respuesta queda corta.
- **Checklist post-sesión** con los pasos para subir el video y sincronizar la transcripción.
- **Tabla "Si algo se sale del guion"** con escenarios típicos y cómo reaccionar.

## Qué hay en cada `entrevistada.md`

- **Ficha del personaje** + *backstory* breve para mantener coherencia improvisando.
- **Tono de la voz** y vocabulario típico.
- **Estructura de la sesión por bloques** con las respuestas que debe dar, en formato fácil de leer en voz alta.
- **Sección "Si te preguntan algo no escrito"** con guías para improvisar en personaje.
- **Checklist pre-grabación** (firmar consentimiento, conectarse 5 min antes).

## Flujo recomendado de producción (por sesión)

1. **D-3 días** — enviar a la entrevistada **solo** el archivo `entrevistada.md` de su subcarpeta + el [consentimiento informado](../anexos/01_consentimiento_informado.md) por correo. Julian no comparte su `entrevistador.md`.
2. **D-1 día** — confirmar hora y enlace de Google Meet.
3. **D-0 (día de grabación)**
   1. Julian abre el `entrevistador.md` correspondiente en una segunda pantalla.
   2. Probar micrófono e iluminación 10 min antes.
   3. Iniciar Google Meet con grabación local + grabación nativa de Meet (redundancia).
   4. Confirmar que el consentimiento está firmado.
   5. Iniciar grabación. Seguir el guion.
   6. Al cerrar: agradecer, detener grabación, exportar video.
4. **D+1 día** — subir el video a Drive privado, pegar el enlace en el [README](../README.md) sección 5.
5. **D+2 días** — refinar la transcripción correspondiente en [`../entrevistas/`](../entrevistas/) cotejando lo grabado con el guion.

## Convenciones comunes

- **Bloques numerados por tiempo** (Bloque 1 — 0:00 – 0:30, Bloque 2 — 0:30 – 1:30, …) para no perder el ritmo de los 10 minutos.
- **(Indicación escénica entre paréntesis cursivas)** — describe gestos, pausas o tono. No se lee en voz alta.
- **Negrita** — palabras clave que se vuelven verbatims importantes y deben sonar tal cual.
- **«Comillas francesas»** — citas literales que conviene reproducir tal como aparecen.

## Disclaimer ético

Si las personas que interpretan los perfiles **no son** las profesionales reales con esos cargos (caso usual cuando se reclutan voluntarios entre conocidos), debe quedar **explícito en el video** que se trata de una **dramatización metodológica con consentimiento**, no de una entrevista profesional encubierta. La transcripción en [`../entrevistas/`](../entrevistas/) ya incluye ese disclaimer en el campo «Pseudónimo» y en el consentimiento firmado.
