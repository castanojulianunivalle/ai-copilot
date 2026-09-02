# Evaluación de modelos — LLM vs motor de reglas

> Sprint 6 · HU-09 · AISCOP-44..47
> Produce las cifras y figuras que sustentan la afirmación central de la tesis.

---

## Qué mide

Ambos motores clasifican los **mismos** tickets de un conjunto etiquetado a mano, y se compara:

| Métrica | Por qué |
|---|---|
| **Exactitud** | Cifra de titular, fácil de comunicar |
| **F1 macro** | **La métrica principal.** Cada categoría pesa igual sin importar cuántos tickets tenga |
| F1 ponderado | Se reporta al lado del macro para hacer visible el efecto del desbalance |
| Precisión / recall por clase | Dónde exactamente mejora o empeora la IA |
| Matriz de confusión | Con qué se confunde cada categoría |
| **McNemar** | Si la diferencia entre motores es estadísticamente significativa |

**Por qué F1 macro y no exactitud.** El histórico real está sesgado hacia `Técnico`, que es la categoría de *fallback* del motor de reglas. Un clasificador que respondiera siempre `Técnico` sacaría una exactitud engañosamente digna. El F1 macro no se deja engañar por eso.

**Por qué McNemar.** Los dos motores se evalúan sobre las mismas muestras, así que sus errores están correlacionados. Comparar dos intervalos de confianza por separado no responde la pregunta; McNemar sí, porque mira solo los casos en que discrepan. Se usa la versión **exacta** (binomial) y no la aproximación chi-cuadrado, porque con n = 66 los desacuerdos son pocos y la aproximación no es fiable por debajo de ~25.

## Cómo se corre

```bash
# 1. Solo la línea base de reglas — no necesita credenciales ni red
python evaluation/evaluate.py

# 2. Con el LLM (consulta solo lo que falte en caché)
export LLM_ENABLED=1
export LLM_API_KEY=hf_xxxxxxxx
export LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
python evaluation/evaluate.py --llm --graficas

# 3. Re-generar el informe desde la caché, sin volver a pagar tokens
python evaluation/evaluate.py --graficas
```

Las figuras necesitan matplotlib: `pip install -r evaluation/requirements.txt`. Sin él, `metricas.json` e `informe.md` se generan igual.

## Archivos

| Archivo | Qué es |
|---|---|
| `fixtures/tickets_etiquetados.jsonl` | 66 tickets con ground truth. 6 por categoría, 12 casos límite anotados |
| `metricas.py` | Métricas en Python puro, sin dependencias |
| `evaluate.py` | Corre ambos motores, compara y escribe los resultados |
| `graficas.py` | Matriz de confusión y comparativa de F1 (PNG + SVG) |
| `verificar_contra_sklearn.py` | Demuestra que `metricas.py` es correcto |
| `results/` | Salidas versionadas |

## Resultados versionados

`results/` se versiona en git a propósito. Para citar una cifra en el artículo hay que poder señalar el commit exacto que la produjo.

| Archivo | Contenido |
|---|---|
| `metricas.json` | Todas las cifras, legibles por máquina |
| `informe.md` | El mismo contenido en tablas |
| `matriz_reglas.png` / `.svg` | Matriz de confusión de la línea base |
| `matriz_llm.*`, `comparativa_f1.*` | Se generan al correr con `--llm` |
| `predicciones_llm.jsonl` | Caché de predicciones — **es el registro auditable del experimento** |

⚠️ **`predicciones_llm.jsonl` no está en el repositorio todavía porque aún no se ha corrido contra un LLM real.** Los resultados publicados aquí son únicamente la línea base del motor de reglas. Las cifras del LLM aparecerán cuando se ejecute con credenciales; no se han simulado.

## Línea base medida (motor de reglas, Semestre 1)

| | |
|---|---|
| Exactitud | **53,03 %** (35/66) |
| F1 macro | **0,5271** |
| F1 ponderado | 0,5271 |

Tres hallazgos de la línea base que el artículo debería recoger:

1. **El motor de reglas nunca predice `Seguridad`** (recall 0,000, columna vacía en la matriz). La causa no es solo el orden del `if/else`: **ninguno de los seis tickets de `Seguridad` contiene una sola palabra clave de esa regla** (`phishing`, `fraude`, `seguridad`, `vulnerabilidad`, `hack`). Los seis describen el incidente con palabras corrientes —«me llegó un correo con su logo pidiéndome la contraseña», «veo sesiones activas desde una ciudad en la que nunca he estado»— y cada uno se va por la primera regla que casa: tres a `Cuenta` (por `cuenta` y `usuario`), uno a `Acceso` (por `contraseña`), uno a `Técnico` por defecto al no casar con nada, y uno a `UX/UI` porque **el cotejo es por subcadena y `ui` casa dentro de `Quisiera`**. El hallazgo para el artículo es ese: el motor solo reconoce el vocabulario que se le enumeró, y la categoría más crítica es justamente la que los usuarios nunca nombran.
2. **`Técnico` absorbe el error ajeno.** Tiene recall 0,833 pero precisión 0,250: es el *fallback*, así que recoge todo lo que ninguna palabra clave atrapó. Es exactamente el comportamiento que el desbalance de clases premiaría si se midiera solo con exactitud.
3. **Cuatro categorías tienen precisión 1,000 con recall por debajo de 0,70.** Cuando el motor se atreve, acierta; se atreve poco. Es el perfil típico de un clasificador por palabras clave: alta especificidad, cobertura pobre.

## Validez: qué garantiza este montaje y qué no

**Lo que sí:**
- Comparación **pareada**. Si el LLM cubre 62 de 66 tickets, las reglas se recalculan sobre esos mismos 62. No se comparan muestras distintas.
- **Reproducible.** `temperature=0`, split determinista y predicciones cacheadas. La misma entrada da la misma cifra.
- **Auditable.** Cada predicción queda en `predicciones_llm.jsonl` con el modelo y la versión de prompt que la produjo.
- Un *fallback* a reglas nunca se cachea como predicción del LLM: congelaría una caída del proveedor como si fuera un error del modelo.
- Las métricas propias están **verificadas contra scikit-learn** hasta 1e-12, y McNemar contra `scipy.stats.binomtest`.

**Lo que no** (declararlo en el artículo):
- **n = 66.** Suficiente para detectar diferencias grandes, corto para las pequeñas. Los intervalos por clase, con soporte 6, son muy anchos.
- **Anotador único.** Sin acuerdo inter-anotador no hay Kappa que reportar, y el *ground truth* refleja el criterio de una sola persona.
- **El conjunto está balanceado, la realidad no.** Es deliberado —evita premiar al clasificador degenerado— pero significa que la exactitud aquí no predice la exactitud en producción.
- **Los prompts se calibran mirando `train`, nunca este conjunto.** Ajustar el prompt contra estos 66 tickets convertiría la evaluación en entrenamiento e invalidaría la comparación.
