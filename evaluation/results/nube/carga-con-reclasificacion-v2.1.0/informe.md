# Evaluación del examen contra la versión desplegada

> HU-10 · AISCOP-57 · 2026-10-19 12:47 (Colombia) · API https://aiscop-api.onrender.com · versión 2.1.0 · commit `d36f1f5` · openai/gpt-oss-20b

- **Respuestas:** 44 de 44 · por el LLM 42 · repliegues a reglas 2 · fallas HTTP 0
- **En la nube:** exactitud 86.36% · F1 macro 0.8612 · F1 micro 0.8636
- **Local, mismo prompt (clasificacion-v2), mismos tickets:** exactitud 86.36% · F1 macro 0.8634
- **Misma categoría que en local:** 40 de 44. McNemar local frente a nube: b = 2, c = 2, p = 1.0000
- **Latencia de punta a punta** (cliente → Render → Groq → Supabase): mediana 6688 ms · p95 12557 ms · máx 19070 ms
- **A revisión humana:** 0 de 44

| Ticket | Real | Local | Nube |
|---|---|---|---|
| ev-011 | Cuenta | Solicitudes | Cuenta (llm) |
| ev-019 | Comercial | Comercial | Cuenta (reglas) |
| ev-023 | Comercial | Comercial | UX/UI (reglas) |
| ev-060 | Móvil | Acceso | Móvil (llm) |

### Métricas en la nube

- **Exactitud**: 86.36% (38/44)
- **F1 macro**: 0.8612 · F1 ponderado 0.8612 · F1 micro 0.8636 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.9030 · **Recall macro**: 0.8636

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.800 | 1.000 | 0.889 | 4 |
| Facturación | 1.000 | 0.750 | 0.857 | 4 |
| Comercial | 1.000 | 0.500 | 0.667 | 4 |
| Acceso | 1.000 | 0.750 | 0.857 | 4 |
| Cuenta | 0.667 | 1.000 | 0.800 | 4 |
| Rendimiento | 1.000 | 1.000 | 1.000 | 4 |
| UX/UI | 0.800 | 1.000 | 0.889 | 4 |
| Seguridad | 1.000 | 0.750 | 0.857 | 4 |
| Integraciones | 1.000 | 1.000 | 1.000 | 4 |
| Móvil | 1.000 | 0.750 | 0.857 | 4 |
| Solicitudes | 0.667 | 1.000 | 0.800 | 4 |

### Matriz de confusión — nube

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **4** | · | · | · | · | · | · | · | · | · | · |
| **Facturación** | 1 | **3** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **2** | · | 1 | · | 1 | · | · | · | · |
| **Acceso** | · | · | · | **3** | 1 | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **4** | · | · | · | · | · | · |
| **Rendimiento** | · | · | · | · | · | **4** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **4** | · | · | · | · |
| **Seguridad** | · | · | · | · | · | · | · | **3** | · | · | 1 |
| **Integraciones** | · | · | · | · | · | · | · | · | **4** | · | · |
| **Móvil** | · | · | · | · | · | · | · | · | · | **3** | 1 |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **4** |
