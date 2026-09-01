# Dataset histórico de tickets — AI Support Co-Pilot

> Sprint 4 · HU-08 · AISCOP-39
> Datasheet del corpus que alimenta la clasificación con LLM (Sprint 5) y su evaluación contra el motor de reglas (Sprint 6).

Estructurado según [*Datasheets for Datasets*](https://arxiv.org/abs/1803.09010) (Gebru et al.), que es el formato que se citará en el artículo de grado.

---

## 1. Motivación

El Semestre 1 clasifica tickets con un motor de reglas por palabras clave (`classify_with_rules`). Para sostener la afirmación central de la tesis —que un LLM clasifica mejor que ese motor— hace falta un corpus con tres cosas que el sistema transaccional no guardaba:

1. **Qué predijo cada motor**, registrado en el momento de la predicción y no reconstruido después.
2. **Cuál era la categoría correcta**, anotada por una persona.
3. **Una partición train/test estable**, para que dos ejecuciones de la evaluación den el mismo número.

Sin esas tres piezas no hay matriz de confusión ni F1-Score defendibles.

## 2. Composición

Una fila = un ticket de soporte.

| Campo | Tipo | Origen |
|---|---|---|
| `ticket_id` | uuid | `tickets.id` |
| `created_at` | timestamptz | `tickets.created_at` |
| `titulo`, `description` | text | Texto del cliente, normalizado y anonimizado |
| `texto` | text | `titulo + " " + description`. **Es la entrada exacta que consumen ambos motores** |
| `estado` | text | `Abierto` \| `Cerrado` |
| `categoria_reglas` | text | Predicción del motor de reglas (`classification_log.motor='reglas'`) |
| `categoria_llm`, `sentimiento_llm`, `prioridad_llm` | text | Predicción del LLM (`motor='llm'`) — se llena desde el Sprint 5 |
| `confianza_llm` | numeric | Autoevaluación del modelo, 0–1 |
| `modelo_llm`, `latencia_llm_ms` | text/int | Trazabilidad de qué modelo produjo la fila y cuánto tardó |
| `categoria_real`, `sentimiento_real`, `prioridad_real` | text | **Ground truth** anotado a mano (`ticket_labels`) |
| `etiquetado` | bool | `true` si el ticket tiene ground truth |
| `split` | text | `train` \| `test` |

**Categorías** (11, cerradas): Técnico · Facturación · Comercial · Acceso · Cuenta · Rendimiento · UX/UI · Seguridad · Integraciones · Móvil · Solicitudes.
**Sentimiento** (4): Frustrado · Urgente · Neutral · Satisfecho.
**Prioridad** (3): Alta · Media · Baja.

Las cifras concretas de cada exportación (total, etiquetados, distribución por clase, rango de fechas) quedan en `metadata.json`; no se repiten aquí para que este documento no envejezca.

## 3. Recolección

Los tickets los crean clientes reales desde el dashboard (`POST /create-ticket`). No hay generación sintética ni scraping.

Dos detalles que afectan la interpretación:

- **El histórico anterior al Sprint 4 se rellenó por *backfill***. Esos tickets no pasaron por `classification_log` en su momento; su predicción de reglas se copió desde `tickets.category` y se marcó con `modelo='classify_with_rules@sem1'`. Es fiel —el motor era determinista y no cambió— pero la marca de tiempo es la del ticket, no la de la predicción.
- **El ground truth no es exhaustivo.** Solo una parte de los tickets está anotada. Todas las métricas se calculan sobre `etiquetado = true`.

## 4. Preprocesamiento

Lo aplica `export_dataset.py`:

1. **Normalización de espacios** — se colapsan saltos de línea y espacios repetidos.
   No se baja a minúsculas ni se quitan signos: el análisis de sentimiento pierde señal si se destruyen mayúsculas sostenidas y signos de exclamación.
2. **Anonimización** — se redactan correos (`<EMAIL>`), teléfonos (`<TELEFONO>`) y URLs (`<URL>`) *antes* de escribir a disco. El dataset se versiona en el repositorio y los tickets son texto libre de personas reales. Los patrones vigentes quedan registrados en `metadata.json` bajo `anonimizacion`.
3. **Descarte de vacíos** — un ticket sin título ni descripción no aporta nada que clasificar.
4. **Split determinista** — `train` si los dos primeros dígitos hex del `md5(ticket_id)` son `< 'cc'` (≈80/20). Se deriva del identificador, no de un `random()`: el mismo ticket cae siempre en la misma partición, y por eso la evaluación es reproducible entre exportaciones.

⚠️ **La anonimización es de expresión regular, no de NER.** Atrapa los formatos comunes; no garantiza que no sobreviva un nombre propio o una dirección escrita en prosa. Antes de publicar el corpus fuera del repositorio hay que hacer una revisión manual.

## 5. Uso previsto

- **Sprint 5** — `train` para calibrar prompts y few-shot examples.
- **Sprint 6** — `test` para la matriz de confusión y el F1-Score. **Nunca** se ajustan prompts mirando `test`; hacerlo invalida la comparación.
- **Artículo de grado** — cifras de precisión, recall y F1 de LLM vs reglas.

**No sirve para**: entrenar un modelo desde cero (el volumen es de decenas/centenas, no de miles), ni para generalizar a otros dominios de soporte — el corpus es de un solo producto y en español.

## 6. Sesgos y limitaciones conocidos

- **Desbalance de clases.** Las categorías no aparecen con la misma frecuencia; `Técnico` es el *fallback* del motor de reglas y por eso está sobrerrepresentada. Por eso el Sprint 6 reporta **F1 macro** además de exactitud: la exactitud sola premiaría a un clasificador que siempre dijera `Técnico`.
- **Anotador único.** El ground truth lo etiqueta una sola persona, así que no hay acuerdo inter-anotador (Kappa) que reportar. Es una limitación a declarar en el artículo.
- **Fuga de información por el *backfill*.** La categoría de reglas del histórico se copió de `tickets.category`, campo que un agente pudo haber editado a mano vía `PUT /tickets/{id}`. En esos casos la "predicción de reglas" puede estar contaminada con corrección humana.
- **Un solo idioma y un solo producto.**

## 7. Cómo regenerarlo

```bash
# Desde Supabase (requiere service role)
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...
python python-api/dataset/export_dataset.py --out data/dataset

# Sin red, desde un volcado JSON de la vista
python python-api/dataset/export_dataset.py --from-file muestra.json --out data/dataset

# Solo los tickets con ground truth (lo que consume la evaluación)
python python-api/dataset/export_dataset.py --out data/dataset --solo-etiquetados
```

Requisito previo: aplicar `supabase/migrations/20260902000000_dataset_historico.sql`.

**Salida**

```
data/dataset/
├── train.jsonl / train.csv
├── test.jsonl  / test.csv
└── metadata.json
```

## 8. Mantenimiento

- **Responsable**: Julian Castaño · castano.julian@correounivalle.edu.co
- **Versionado**: cada exportación registra en `metadata.json` el commit de git y el `sha256` de cada partición. Para citar una cifra en el artículo hay que citar también ese par (commit + checksum); es lo que hace verificable el resultado.
- **Cadencia**: se re-exporta al cierre de cada sprint del componente inteligente.
