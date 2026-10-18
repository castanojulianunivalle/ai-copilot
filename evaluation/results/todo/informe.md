# Evaluación de modelos — AI Support Co-Pilot

> Sprint 6 · HU-09 · generado el 2026-10-18T01:22:11+00:00 · commit `db0739d`
> Partición **todo** · 66 tickets · huella del conjunto `c69d84040663`

### Motor de reglas (línea base, Semestre 1)

- **Exactitud**: 53.03% (35/66)
- **F1 macro**: 0.5271 · F1 ponderado 0.5271 · F1 micro 0.5303 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.6672 · **Recall macro**: 0.5303

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.250 | 0.833 | 0.385 | 6 |
| Facturación | 1.000 | 1.000 | 1.000 | 6 |
| Comercial | 1.000 | 0.333 | 0.500 | 6 |
| Acceso | 0.800 | 0.667 | 0.727 | 6 |
| Cuenta | 0.400 | 0.667 | 0.500 | 6 |
| Rendimiento | 1.000 | 0.500 | 0.667 | 6 |
| UX/UI | 0.222 | 0.333 | 0.267 | 6 |
| Seguridad | 0.000 | 0.000 | 0.000 | 6 |
| Integraciones | 1.000 | 0.667 | 0.800 | 6 |
| Móvil | 0.667 | 0.667 | 0.667 | 6 |
| Solicitudes | 1.000 | 0.167 | 0.286 | 6 |

### Matriz de confusión — motor de reglas

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **5** | · | · | · | · | · | 1 | · | · | · | · |
| **Facturación** | · | **6** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **2** | · | 1 | · | 3 | · | · | · | · |
| **Acceso** | · | · | · | **4** | 1 | · | 1 | · | · | · | · |
| **Cuenta** | 2 | · | · | · | **4** | · | · | · | · | · | · |
| **Rendimiento** | 3 | · | · | · | · | **3** | · | · | · | · | · |
| **UX/UI** | 3 | · | · | · | · | · | **2** | · | · | 1 | · |
| **Seguridad** | 1 | · | · | 1 | 3 | · | 1 | · | · | · | · |
| **Integraciones** | 2 | · | · | · | · | · | · | · | **4** | · | · |
| **Móvil** | 1 | · | · | · | · | · | 1 | · | · | **4** | · |
| **Solicitudes** | 3 | · | · | · | 1 | · | · | · | · | 1 | **1** |

### LLM · clasificacion-v1 · openai/gpt-oss-20b@clasificacion-v1

- **Exactitud**: 81.82% (54/66)
- **F1 macro**: 0.8043 · F1 ponderado 0.8043 · F1 micro 0.8182 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.8672 · **Recall macro**: 0.8182

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.556 | 0.833 | 0.667 | 6 |
| Facturación | 1.000 | 1.000 | 1.000 | 6 |
| Comercial | 1.000 | 0.833 | 0.909 | 6 |
| Acceso | 0.833 | 0.833 | 0.833 | 6 |
| Cuenta | 0.800 | 0.667 | 0.727 | 6 |
| Rendimiento | 1.000 | 0.833 | 0.909 | 6 |
| UX/UI | 0.750 | 1.000 | 0.857 | 6 |
| Seguridad | 1.000 | 1.000 | 1.000 | 6 |
| Integraciones | 1.000 | 0.833 | 0.909 | 6 |
| Móvil | 1.000 | 0.167 | 0.286 | 6 |
| Solicitudes | 0.600 | 1.000 | 0.750 | 6 |

### Matriz de confusión — LLM clasificacion-v1

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **5** | · | · | · | · | · | 1 | · | · | · | · |
| **Facturación** | · | **6** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **5** | · | · | · | · | · | · | · | 1 |
| **Acceso** | · | · | · | **5** | 1 | · | · | · | · | · | · |
| **Cuenta** | · | · | · | 1 | **4** | · | · | · | · | · | 1 |
| **Rendimiento** | 1 | · | · | · | · | **5** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **6** | · | · | · | · |
| **Seguridad** | · | · | · | · | · | · | · | **6** | · | · | · |
| **Integraciones** | · | · | · | · | · | · | · | · | **5** | · | 1 |
| **Móvil** | 3 | · | · | · | · | · | 1 | · | · | **1** | 1 |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **6** |

**Frente a las reglas, sobre los mismos 66 tickets:** Δ exactitud +28.79%, Δ F1 macro +0.2773. McNemar: las reglas aciertan y el LLM falla en 5; el LLM acierta y las reglas fallan en 24; p = 0.0005: la diferencia **es** estadísticamente significativa.

Latencia: mediana 4573 ms · p95 11272 ms · máx 12617 ms.

### LLM · clasificacion-v2 · openai/gpt-oss-20b@clasificacion-v2

- **Exactitud**: 89.39% (59/66)
- **F1 macro**: 0.8970 · F1 ponderado 0.8970 · F1 micro 0.8939 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.9203 · **Recall macro**: 0.8939

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.857 | 1.000 | 0.923 | 6 |
| Facturación | 1.000 | 0.833 | 0.909 | 6 |
| Comercial | 1.000 | 1.000 | 1.000 | 6 |
| Acceso | 0.833 | 0.833 | 0.833 | 6 |
| Cuenta | 0.833 | 0.833 | 0.833 | 6 |
| Rendimiento | 1.000 | 1.000 | 1.000 | 6 |
| UX/UI | 1.000 | 1.000 | 1.000 | 6 |
| Seguridad | 1.000 | 0.833 | 0.909 | 6 |
| Integraciones | 1.000 | 0.833 | 0.909 | 6 |
| Móvil | 1.000 | 0.667 | 0.800 | 6 |
| Solicitudes | 0.600 | 1.000 | 0.750 | 6 |

### Matriz de confusión — LLM clasificacion-v2

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **6** | · | · | · | · | · | · | · | · | · | · |
| **Facturación** | 1 | **5** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **6** | · | · | · | · | · | · | · | · |
| **Acceso** | · | · | · | **5** | 1 | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **5** | · | · | · | · | · | 1 |
| **Rendimiento** | · | · | · | · | · | **6** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **6** | · | · | · | · |
| **Seguridad** | · | · | · | · | · | · | · | **5** | · | · | 1 |
| **Integraciones** | · | · | · | · | · | · | · | · | **5** | · | 1 |
| **Móvil** | · | · | · | 1 | · | · | · | · | · | **4** | 1 |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **6** |

**Frente a las reglas, sobre los mismos 66 tickets:** Δ exactitud +36.36%, Δ F1 macro +0.3699. McNemar: las reglas aciertan y el LLM falla en 2; el LLM acierta y las reglas fallan en 26; p = 0.0000: la diferencia **es** estadísticamente significativa.

Latencia: mediana 1155 ms · p95 1880 ms · máx 2298 ms.

### clasificacion-v2 frente a clasificacion-v1

Sobre 66 tickets: Δ exactitud +7.58%, Δ F1 macro +0.0927. McNemar: clasificacion-v1 acierta y clasificacion-v2 falla en 2; al revés, en 7; p = 0.1797.
