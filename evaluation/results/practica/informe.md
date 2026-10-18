# Evaluación de modelos — AI Support Co-Pilot

> Sprint 6 · HU-09 · generado el 2026-10-18T01:22:09+00:00 · commit `db0739d`
> Partición **practica** · 22 tickets · huella del conjunto `c69d84040663`

### Motor de reglas (línea base, Semestre 1)

- **Exactitud**: 54.55% (12/22)
- **F1 macro**: 0.5216 · F1 ponderado 0.5216 · F1 micro 0.5455 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.5818 · **Recall macro**: 0.5455

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.400 | 1.000 | 0.571 | 2 |
| Facturación | 1.000 | 1.000 | 1.000 | 2 |
| Comercial | 0.000 | 0.000 | 0.000 | 2 |
| Acceso | 1.000 | 1.000 | 1.000 | 2 |
| Cuenta | 0.500 | 1.000 | 0.667 | 2 |
| Rendimiento | 1.000 | 0.500 | 0.667 | 2 |
| UX/UI | 0.000 | 0.000 | 0.000 | 2 |
| Seguridad | 0.000 | 0.000 | 0.000 | 2 |
| Integraciones | 1.000 | 0.500 | 0.667 | 2 |
| Móvil | 0.500 | 0.500 | 0.500 | 2 |
| Solicitudes | 1.000 | 0.500 | 0.667 | 2 |

### Matriz de confusión — motor de reglas

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **2** | · | · | · | · | · | · | · | · | · | · |
| **Facturación** | · | **2** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | · | · | · | · | 2 | · | · | · | · |
| **Acceso** | · | · | · | **2** | · | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **2** | · | · | · | · | · | · |
| **Rendimiento** | 1 | · | · | · | · | **1** | · | · | · | · | · |
| **UX/UI** | 1 | · | · | · | · | · | · | · | · | 1 | · |
| **Seguridad** | · | · | · | · | 1 | · | 1 | · | · | · | · |
| **Integraciones** | 1 | · | · | · | · | · | · | · | **1** | · | · |
| **Móvil** | · | · | · | · | · | · | 1 | · | · | **1** | · |
| **Solicitudes** | · | · | · | · | 1 | · | · | · | · | · | **1** |

### LLM · clasificacion-v1 · openai/gpt-oss-20b@clasificacion-v1

- **Exactitud**: 86.36% (19/22)
- **F1 macro**: 0.8545 · F1 ponderado 0.8545 · F1 micro 0.8636 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.9091 · **Recall macro**: 0.8636

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.667 | 1.000 | 0.800 | 2 |
| Facturación | 1.000 | 1.000 | 1.000 | 2 |
| Comercial | 1.000 | 1.000 | 1.000 | 2 |
| Acceso | 1.000 | 1.000 | 1.000 | 2 |
| Cuenta | 1.000 | 1.000 | 1.000 | 2 |
| Rendimiento | 1.000 | 0.500 | 0.667 | 2 |
| UX/UI | 0.667 | 1.000 | 0.800 | 2 |
| Seguridad | 1.000 | 1.000 | 1.000 | 2 |
| Integraciones | 1.000 | 0.500 | 0.667 | 2 |
| Móvil | 1.000 | 0.500 | 0.667 | 2 |
| Solicitudes | 0.667 | 1.000 | 0.800 | 2 |

### Matriz de confusión — LLM clasificacion-v1

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **2** | · | · | · | · | · | · | · | · | · | · |
| **Facturación** | · | **2** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **2** | · | · | · | · | · | · | · | · |
| **Acceso** | · | · | · | **2** | · | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **2** | · | · | · | · | · | · |
| **Rendimiento** | 1 | · | · | · | · | **1** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **2** | · | · | · | · |
| **Seguridad** | · | · | · | · | · | · | · | **2** | · | · | · |
| **Integraciones** | · | · | · | · | · | · | · | · | **1** | · | 1 |
| **Móvil** | · | · | · | · | · | · | 1 | · | · | **1** | · |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **2** |

**Frente a las reglas, sobre los mismos 22 tickets:** Δ exactitud +31.82%, Δ F1 macro +0.3329. McNemar: las reglas aciertan y el LLM falla en 1; el LLM acierta y las reglas fallan en 8; p = 0.0391: la diferencia **es** estadísticamente significativa.

Latencia: mediana 6950 ms · p95 11272 ms · máx 11535 ms.

### LLM · clasificacion-v2 · openai/gpt-oss-20b@clasificacion-v2

- **Exactitud**: 95.45% (21/22)
- **F1 macro**: 0.9515 · F1 ponderado 0.9515 · F1 micro 0.9545 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.9697 · **Recall macro**: 0.9545

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 1.000 | 1.000 | 1.000 | 2 |
| Facturación | 1.000 | 1.000 | 1.000 | 2 |
| Comercial | 1.000 | 1.000 | 1.000 | 2 |
| Acceso | 1.000 | 1.000 | 1.000 | 2 |
| Cuenta | 1.000 | 1.000 | 1.000 | 2 |
| Rendimiento | 1.000 | 1.000 | 1.000 | 2 |
| UX/UI | 1.000 | 1.000 | 1.000 | 2 |
| Seguridad | 1.000 | 1.000 | 1.000 | 2 |
| Integraciones | 1.000 | 0.500 | 0.667 | 2 |
| Móvil | 1.000 | 1.000 | 1.000 | 2 |
| Solicitudes | 0.667 | 1.000 | 0.800 | 2 |

### Matriz de confusión — LLM clasificacion-v2

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **2** | · | · | · | · | · | · | · | · | · | · |
| **Facturación** | · | **2** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **2** | · | · | · | · | · | · | · | · |
| **Acceso** | · | · | · | **2** | · | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **2** | · | · | · | · | · | · |
| **Rendimiento** | · | · | · | · | · | **2** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **2** | · | · | · | · |
| **Seguridad** | · | · | · | · | · | · | · | **2** | · | · | · |
| **Integraciones** | · | · | · | · | · | · | · | · | **1** | · | 1 |
| **Móvil** | · | · | · | · | · | · | · | · | · | **2** | · |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **2** |

**Frente a las reglas, sobre los mismos 22 tickets:** Δ exactitud +40.91%, Δ F1 macro +0.4299. McNemar: las reglas aciertan y el LLM falla en 0; el LLM acierta y las reglas fallan en 9; p = 0.0039: la diferencia **es** estadísticamente significativa.

Latencia: mediana 1425 ms · p95 2226 ms · máx 2298 ms.

### clasificacion-v2 frente a clasificacion-v1

Sobre 22 tickets: Δ exactitud +9.09%, Δ F1 macro +0.0970. McNemar: clasificacion-v1 acierta y clasificacion-v2 falla en 0; al revés, en 2; p = 0.5000.
