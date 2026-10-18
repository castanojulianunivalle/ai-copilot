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

## Validez

**Lo que garantiza el montaje:**
- **Comparación pareada.** Si el modelo cubre 40 de 44 tickets, las reglas se recalculan sobre esos mismos 40.
- **Reproducibilidad.** La temperatura es 0, el reparto es determinista y las predicciones están en caché.
- **Pruebas.** `tests/test_reproduce_avance2.py` comprueba que el script reproduce exactamente las cifras del Avance 2 desde la caché de v1.

**Lo que hay que declarar en el artículo:**
- **n es pequeño:** 66 tickets, 44 de examen. Alcanza para detectar diferencias grandes, no las pequeñas.
- **Anotador único:** no hay índice Kappa.
- **El conjunto es sintético y balanceado:** el resultado vale para este conjunto, no como predicción de producción.
