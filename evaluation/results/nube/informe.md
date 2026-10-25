# Evaluación del examen contra la versión desplegada

> HU-10 · AISCOP-57 · 2026-10-25 17:06 (Colombia) · API https://aiscop-api.onrender.com · versión 2.1.0 · commit `d36f1f5` · openai/gpt-oss-20b

- **Respuestas:** 44 de 44 · por el LLM 44 · repliegues a reglas 0 · fallas HTTP 0
- **En la nube:** exactitud 90.91% · F1 macro 0.9097 · F1 micro 0.9091
- **Local, mismo prompt (clasificacion-v2), mismos tickets:** exactitud 86.36% · F1 macro 0.8634
- **Misma categoría que en local:** 42 de 44. McNemar local frente a nube: b = 0, c = 2, p = 0.5000
- **Latencia de punta a punta** (cliente → Render → Groq → Supabase): mediana 1413 ms · p95 11129 ms · máx 76290 ms
- **A revisión humana:** 0 de 44

| Ticket | Real | Local | Nube |
|---|---|---|---|
| ev-011 | Cuenta | Solicitudes | Cuenta (llm) |
| ev-060 | Móvil | Acceso | Móvil (llm) |

### Métricas en la nube

- **Exactitud**: 90.91% (40/44)
- **F1 macro**: 0.9097 · F1 ponderado 0.9097 · F1 micro 0.9091 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.9333 · **Recall macro**: 0.9091

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.800 | 1.000 | 0.889 | 4 |
| Facturación | 1.000 | 0.750 | 0.857 | 4 |
| Comercial | 1.000 | 1.000 | 1.000 | 4 |
| Acceso | 1.000 | 0.750 | 0.857 | 4 |
| Cuenta | 0.800 | 1.000 | 0.889 | 4 |
| Rendimiento | 1.000 | 1.000 | 1.000 | 4 |
| UX/UI | 1.000 | 1.000 | 1.000 | 4 |
| Seguridad | 1.000 | 0.750 | 0.857 | 4 |
| Integraciones | 1.000 | 1.000 | 1.000 | 4 |
| Móvil | 1.000 | 0.750 | 0.857 | 4 |
| Solicitudes | 0.667 | 1.000 | 0.800 | 4 |

### Matriz de confusión — nube

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **4** | · | · | · | · | · | · | · | · | · | · |
| **Facturación** | 1 | **3** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **4** | · | · | · | · | · | · | · | · |
| **Acceso** | · | · | · | **3** | 1 | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **4** | · | · | · | · | · | · |
| **Rendimiento** | · | · | · | · | · | **4** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **4** | · | · | · | · |
| **Seguridad** | · | · | · | · | · | · | · | **3** | · | · | 1 |
| **Integraciones** | · | · | · | · | · | · | · | · | **4** | · | · |
| **Móvil** | · | · | · | · | · | · | · | · | · | **3** | 1 |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **4** |
