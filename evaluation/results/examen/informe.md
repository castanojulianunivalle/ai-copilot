# Evaluación de modelos — AI Support Co-Pilot

> Sprint 6 · HU-09 · generado el 2026-10-18T01:22:06+00:00 · commit `db0739d`
> Partición **examen** · 44 tickets · huella del conjunto `c69d84040663`

### Motor de reglas (línea base, Semestre 1)

- **Exactitud**: 52.27% (23/44)
- **F1 macro**: 0.5156 · F1 ponderado 0.5156 · F1 micro 0.5227 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.5773 · **Recall macro**: 0.5227

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.200 | 0.750 | 0.316 | 4 |
| Facturación | 1.000 | 1.000 | 1.000 | 4 |
| Comercial | 1.000 | 0.500 | 0.667 | 4 |
| Acceso | 0.667 | 0.500 | 0.571 | 4 |
| Cuenta | 0.333 | 0.500 | 0.400 | 4 |
| Rendimiento | 1.000 | 0.500 | 0.667 | 4 |
| UX/UI | 0.400 | 0.500 | 0.444 | 4 |
| Seguridad | 0.000 | 0.000 | 0.000 | 4 |
| Integraciones | 1.000 | 0.750 | 0.857 | 4 |
| Móvil | 0.750 | 0.750 | 0.750 | 4 |
| Solicitudes | 0.000 | 0.000 | 0.000 | 4 |

### Matriz de confusión — motor de reglas

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **3** | · | · | · | · | · | 1 | · | · | · | · |
| **Facturación** | · | **4** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **2** | · | 1 | · | 1 | · | · | · | · |
| **Acceso** | · | · | · | **2** | 1 | · | 1 | · | · | · | · |
| **Cuenta** | 2 | · | · | · | **2** | · | · | · | · | · | · |
| **Rendimiento** | 2 | · | · | · | · | **2** | · | · | · | · | · |
| **UX/UI** | 2 | · | · | · | · | · | **2** | · | · | · | · |
| **Seguridad** | 1 | · | · | 1 | 2 | · | · | · | · | · | · |
| **Integraciones** | 1 | · | · | · | · | · | · | · | **3** | · | · |
| **Móvil** | 1 | · | · | · | · | · | · | · | · | **3** | · |
| **Solicitudes** | 3 | · | · | · | · | · | · | · | · | 1 | · |

### LLM · clasificacion-v1 · openai/gpt-oss-20b@clasificacion-v1

- **Exactitud**: 79.55% (35/44)
- **F1 macro**: 0.7632 · F1 ponderado 0.7632 · F1 micro 0.7955 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.7535 · **Recall macro**: 0.7955

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.500 | 0.750 | 0.600 | 4 |
| Facturación | 1.000 | 1.000 | 1.000 | 4 |
| Comercial | 1.000 | 0.750 | 0.857 | 4 |
| Acceso | 0.750 | 0.750 | 0.750 | 4 |
| Cuenta | 0.667 | 0.500 | 0.571 | 4 |
| Rendimiento | 1.000 | 1.000 | 1.000 | 4 |
| UX/UI | 0.800 | 1.000 | 0.889 | 4 |
| Seguridad | 1.000 | 1.000 | 1.000 | 4 |
| Integraciones | 1.000 | 1.000 | 1.000 | 4 |
| Móvil | 0.000 | 0.000 | 0.000 | 4 |
| Solicitudes | 0.571 | 1.000 | 0.727 | 4 |

### Matriz de confusión — LLM clasificacion-v1

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **3** | · | · | · | · | · | 1 | · | · | · | · |
| **Facturación** | · | **4** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **3** | · | · | · | · | · | · | · | 1 |
| **Acceso** | · | · | · | **3** | 1 | · | · | · | · | · | · |
| **Cuenta** | · | · | · | 1 | **2** | · | · | · | · | · | 1 |
| **Rendimiento** | · | · | · | · | · | **4** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **4** | · | · | · | · |
| **Seguridad** | · | · | · | · | · | · | · | **4** | · | · | · |
| **Integraciones** | · | · | · | · | · | · | · | · | **4** | · | · |
| **Móvil** | 3 | · | · | · | · | · | · | · | · | · | 1 |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **4** |

**Frente a las reglas, sobre los mismos 44 tickets:** Δ exactitud +27.27%, Δ F1 macro +0.2475. McNemar: las reglas aciertan y el LLM falla en 4; el LLM acierta y las reglas fallan en 16; p = 0.0118: la diferencia **es** estadísticamente significativa.

Latencia: mediana 4530 ms · p95 11034 ms · máx 12617 ms.

### LLM · clasificacion-v2 · openai/gpt-oss-20b@clasificacion-v2

- **Exactitud**: 86.36% (38/44)
- **F1 macro**: 0.8634 · F1 ponderado 0.8634 · F1 micro 0.8636 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.8974 · **Recall macro**: 0.8636

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.800 | 1.000 | 0.889 | 4 |
| Facturación | 1.000 | 0.750 | 0.857 | 4 |
| Comercial | 1.000 | 1.000 | 1.000 | 4 |
| Acceso | 0.750 | 0.750 | 0.750 | 4 |
| Cuenta | 0.750 | 0.750 | 0.750 | 4 |
| Rendimiento | 1.000 | 1.000 | 1.000 | 4 |
| UX/UI | 1.000 | 1.000 | 1.000 | 4 |
| Seguridad | 1.000 | 0.750 | 0.857 | 4 |
| Integraciones | 1.000 | 1.000 | 1.000 | 4 |
| Móvil | 1.000 | 0.500 | 0.667 | 4 |
| Solicitudes | 0.571 | 1.000 | 0.727 | 4 |

### Matriz de confusión — LLM clasificacion-v2

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **4** | · | · | · | · | · | · | · | · | · | · |
| **Facturación** | 1 | **3** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **4** | · | · | · | · | · | · | · | · |
| **Acceso** | · | · | · | **3** | 1 | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **3** | · | · | · | · | · | 1 |
| **Rendimiento** | · | · | · | · | · | **4** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **4** | · | · | · | · |
| **Seguridad** | · | · | · | · | · | · | · | **3** | · | · | 1 |
| **Integraciones** | · | · | · | · | · | · | · | · | **4** | · | · |
| **Móvil** | · | · | · | 1 | · | · | · | · | · | **2** | 1 |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **4** |

**Frente a las reglas, sobre los mismos 44 tickets:** Δ exactitud +34.09%, Δ F1 macro +0.3477. McNemar: las reglas aciertan y el LLM falla en 2; el LLM acierta y las reglas fallan en 17; p = 0.0007: la diferencia **es** estadísticamente significativa.

Latencia: mediana 979 ms · p95 1579 ms · máx 1880 ms.

### clasificacion-v2 frente a clasificacion-v1

Sobre 44 tickets: Δ exactitud +6.82%, Δ F1 macro +0.1002. McNemar: clasificacion-v1 acierta y clasificacion-v2 falla en 2; al revés, en 5; p = 0.4531.
