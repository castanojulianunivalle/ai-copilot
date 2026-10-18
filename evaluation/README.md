# Evaluación de modelos: LLM frente a motor de reglas

> Sprint 6 · HU-09 (AISCOP-44) · subtareas AISCOP-45, 46, 47, 50 y 51

Ambos motores clasifican los **mismos** tickets de un conjunto etiquetado a mano y se comparan.

| Métrica | Por qué |
|---|---|
| Exactitud | Es la cifra de titular, fácil de comunicar. |
| **F1 macro** | **Es la métrica principal.** Cada categoría pesa igual, sin importar cuántos tickets tenga. |
| F1 ponderado | Se reporta junto al macro. |
| Precisión y recall por clase | Muestran dónde mejora o empeora el modelo. |
| Matriz de confusión | Muestra con qué se confunde cada categoría. |
| **McNemar exacta** | Dice si la diferencia entre motores es significativa, mirando solo los tickets en que discrepan. |

Se usa la versión **exacta** (binomial) de McNemar y no la aproximación chi-cuadrado, porque con decenas de tickets los desacuerdos son pocos.

## Conjunto y particiones

`fixtures/tickets_etiquetados.jsonl` tiene 66 tickets: 6 por categoría, 12 casos límite anotados, y la categoría correcta puesta por una persona. `particion.py` los reparte de forma estratificada y determinista:

| Partición | Tickets | Para qué |
|---|---:|---|
| `practica` | 22 (2 por categoría) | Es lo único que se mira al ajustar el prompt. |
| `examen` | 44 (4 por categoría) | Solo se usa para medir, una vez congelado el prompt. |

Dentro de cada categoría los tickets se ordenan por `md5(id)` y los dos primeros van a práctica. `fixtures/particion_congelada.json` guarda el reparto y la huella SHA-256 del conjunto, y `tests/test_particion.py` falla si cualquiera de los dos cambia.

## Versiones de prompt y caché

Cada predicción del modelo se guarda en `results/cache/<versión del prompt>.jsonl`, con el modelo, la confianza y la latencia. La caché cumple dos funciones:
- **Es el registro auditable del experimento:** una cifra publicada sale de unas predicciones concretas.
- Permite repetir la evaluación sin volver a consultar al proveedor.

Un repliegue a reglas nunca se guarda como predicción del modelo.

| Versión | Origen |
|---|---|
| `clasificacion-v1` | Corrida del 5 de octubre de 2026 con gpt-oss-20b en Groq: los 66 tickets, sin repliegues. Es la que se presentó en el Avance 2. |
| `clasificacion-v2` | Prompt del Sprint 6 (AISCOP-50), congelado el 17 de octubre. Corrió sobre práctica mientras se ajustaba y una sola vez sobre examen. |

### Cómo se ajustó el prompt v2 (AISCOP-50)

1. Se miraron solo los errores de v1 en **práctica**, que fueron 3 de 22. Los tres caían en los pares Rendimiento/Técnico, Integraciones/Solicitudes y Móvil/UX-UI, y por ellos se agregaron distinciones al prompt.
2. **Borrador 1.** Sacó 21 de 22, pero metió un error nuevo: «Móvil prevalece» se llevó un ticket cuya nota de anotación dice «la queja es de diseño, no del dispositivo».
3. **Borrador 2.** Recogió ese criterio: Móvil cuando lo causa el dispositivo o la app; UX/UI cuando es el diseño. Sacó 21 de 22.
4. **Borrador 3.** Redefinió Solicitudes y también sacó 21 de 22, pero desvió un ticket de **Seguridad**, la clase crítica. Por eso **se congeló el borrador 2.**
5. Con el prompt congelado se corrió **una sola vez** el examen.

Las predicciones de los tres borradores quedan en `results/cache/borradores/`, como registro del ajuste. También queda ahí una corrida de control de v1 del 17 de octubre: mide la latencia del proveedor ese día con el prompt anterior, para no atribuirle a v2 una mejora que no es suya.

## Cómo se corre

```bash
python evaluation/evaluate.py                        # partición de examen, con lo que haya en caché
python evaluation/evaluate.py --particion practica   # para ajustar el prompt
python evaluation/evaluate.py --particion todo       # los 66, comparable con el Avance 2
python evaluation/evaluate.py --llm                  # consulta al modelo por lo que falte (versión actual del prompt)
python -m pytest -q evaluation/tests                 # pruebas
```

Con `--llm` hacen falta `LLM_ENABLED=1` y `LLM_API_KEY`; se leen de `python-api/.env`. Los resultados quedan en `results/<partición>/metricas.json` e `informe.md`. Cada `metricas.json` registra el commit que lo produjo y si el árbol estaba limpio.

## Resultados del Sprint 6

Los produjo el commit `860c942` y están en `results/<partición>/`: `metricas.json`, `informe.md` y las figuras `resumen`, `comparativa_f1` y `matriz_*`, en PNG y SVG.

**Examen** (44 tickets que el prompt v2 no vio): es la medición formal de HU-09.

| Motor | Exactitud | F1 macro | McNemar contra reglas | Latencia mediana · p95 |
|---|---:|---:|---|---|
| Reglas | 52,3 % | 0,516 | — | instantánea |
| LLM v1 | 79,5 % | 0,763 | 4 frente a 16 · p = 0,012 | 4,5 s · 11,0 s (5 de octubre) |
| **LLM v2** | **86,4 %** | **0,863** | **2 frente a 17 · p = 0,0007** | **1,0 s · 1,6 s** (17 de octubre) |

- **Regla de decisión del Evento 1** (F1 mayor y p < 0,05): se cumple con v1 y con v2.
- **v2 frente a v1:** +6,8 puntos y +0,100 de F1, pero no significativo con 44 tickets (2 frente a 5, p = 0,45).
- **Por categoría:** Móvil pasa de F1 0 a 0,667. Seguridad (recall 1,00 → 0,75) y Facturación bajan por un ticket cada una: un pago con error que v2 manda a Técnico y una consulta de cumplimiento legal que manda a Solicitudes.
- **Latencia:** bajó en la misma medida para v1. Una corrida de control del 17 de octubre lo confirma, así que es el proveedor y no el prompt.
- **Todo** (66): v2 89,4 % y F1 0,897. Incluye la práctica, sobre la que se ajustó, así que no es la cifra que se reporta.

## Umbral de revisión humana (AISCOP-51)

`umbral.py` compara umbrales de 0,5 a 0,95: los elige mirando práctica y los reporta en examen. Además corre cuatro sondas sin información suficiente (`fixtures/sondas_revision.jsonl`). Resultados en `results/umbral/`.

| Umbral | Examen: a revisión | Errores atrapados |
|---:|---:|---:|
| ≤ 0,5 (vigente) | 0 de 44 | 0 de 6 |
| ≤ 0,9 | 4 de 44 (9 %) | 0 de 6 |
| ≤ 0,95 | 43 de 44 (98 %) | 6 de 6 |
| El modelo y las reglas discrepan | 22 de 44 (50 %) | 5 de 6 |

**Decisión: se mantiene 0,5.**
- Subirlo a 0,9 manda un 9 % de tickets a revisión sin atrapar ningún error. Los seis errores de v2 llegan con confianza 0,95, igual que los aciertos, así que la confianza que declara el modelo no distingue sus errores.
- El umbral sí cumple el propósito para el que existe: tres de las cuatro sondas (consultas sin contexto, como «Hola, tengo una duda») salen con confianza 0,45 y van a revisión.
- La cuarta sonda, «Urgente: necesito que me llamen hoy», sale como Solicitudes con 0,95. Para el modelo la intención es clara.

La señal de discrepancia con las reglas atrapa casi todos los errores, pero con la mitad de los tickets en revisión. Queda como trabajo descubierto en el Product Backlog.

## Validez

**Lo que garantiza el montaje:**
- **Comparación pareada.** Si el modelo cubre 40 de 44 tickets, las reglas se recalculan sobre esos mismos 40.
- **Reproducibilidad.** La temperatura es 0, el reparto es determinista y las predicciones están en caché.
- **Pruebas.** `tests/test_reproduce_avance2.py` comprueba que el script reproduce exactamente las cifras del Avance 2 desde la caché de v1.

**Lo que hay que declarar en el artículo:**
- **n es pequeño:** 66 tickets, 44 de examen. Alcanza para detectar diferencias grandes, no las pequeñas.
- **Anotador único:** no hay índice Kappa.
- **El conjunto es sintético y balanceado:** el resultado vale para este conjunto, no como predicción de producción.
