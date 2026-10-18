# Evaluación del examen contra la versión desplegada

> HU-10 · AISCOP-57 · 2026-10-18 10:39 (Colombia) · API https://aiscop-api.onrender.com · versión 2.0.0 · commit `794fdb2` · openai/gpt-oss-20b

- **Respuestas:** 44 de 44 · por el LLM 43 · repliegues a reglas 1 · fallas HTTP 0
- **En la nube:** exactitud 86.36% · F1 macro 0.8619 · F1 micro 0.8636
- **Local, mismo prompt (clasificacion-v2), mismos tickets:** exactitud 86.36% · F1 macro 0.8634
- **Misma categoría que en local:** 43 de 44. McNemar local frente a nube: b = 0, c = 0, p = 1.0000
- **Latencia de punta a punta** (cliente → Render → Groq → Supabase): mediana 1242 ms · p95 1682 ms · máx 4764 ms
- **A revisión humana:** 0 de 44

| Ticket | Real | Local | Nube |
|---|---|---|---|
| ev-047 | Seguridad | Solicitudes | Técnico (reglas) |

### Métricas en la nube

- **Exactitud**: 86.36% (38/44)
- **F1 macro**: 0.8619 · F1 ponderado 0.8619 · F1 micro 0.8636 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.8939 · **Recall macro**: 0.8636

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.667 | 1.000 | 0.800 | 4 |
| Facturación | 1.000 | 0.750 | 0.857 | 4 |
| Comercial | 1.000 | 1.000 | 1.000 | 4 |
| Acceso | 0.750 | 0.750 | 0.750 | 4 |
| Cuenta | 0.750 | 0.750 | 0.750 | 4 |
| Rendimiento | 1.000 | 1.000 | 1.000 | 4 |
| UX/UI | 1.000 | 1.000 | 1.000 | 4 |
| Seguridad | 1.000 | 0.750 | 0.857 | 4 |
| Integraciones | 1.000 | 1.000 | 1.000 | 4 |
| Móvil | 1.000 | 0.500 | 0.667 | 4 |
| Solicitudes | 0.667 | 1.000 | 0.800 | 4 |

### Matriz de confusión — nube

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **4** | · | · | · | · | · | · | · | · | · | · |
| **Facturación** | 1 | **3** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **4** | · | · | · | · | · | · | · | · |
| **Acceso** | · | · | · | **3** | 1 | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **3** | · | · | · | · | · | 1 |
| **Rendimiento** | · | · | · | · | · | **4** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **4** | · | · | · | · |
| **Seguridad** | 1 | · | · | · | · | · | · | **3** | · | · | · |
| **Integraciones** | · | · | · | · | · | · | · | · | **4** | · | · |
| **Móvil** | · | · | · | 1 | · | · | · | · | · | **2** | 1 |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **4** |
