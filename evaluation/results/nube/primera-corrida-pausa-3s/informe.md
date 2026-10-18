# Evaluación del examen contra la versión desplegada

> HU-10 · AISCOP-57 · 2026-10-18 10:30 (Colombia) · API https://aiscop-api.onrender.com · versión 2.0.0 · commit `794fdb2` · openai/gpt-oss-20b

- **Respuestas:** 44 de 44 · por el LLM 40 · repliegues a reglas 4 · fallas HTTP 0
- **En la nube:** exactitud 81.82% · F1 macro 0.8271 · F1 micro 0.8182
- **Local, mismo prompt (clasificacion-v2), mismos tickets:** exactitud 86.36% · F1 macro 0.8634
- **Misma categoría que en local:** 39 de 44. McNemar local frente a nube: b = 3, c = 1, p = 0.6250
- **Latencia de punta a punta** (cliente → Render → Groq → Supabase): mediana 1746 ms · p95 10688 ms · máx 11205 ms
- **A revisión humana:** 0 de 44

| Ticket | Real | Local | Nube |
|---|---|---|---|
| ev-019 | Comercial | Comercial | Cuenta (reglas) |
| ev-025 | Técnico | Técnico | UX/UI (reglas) |
| ev-036 | Rendimiento | Rendimiento | Técnico (reglas) |
| ev-047 | Seguridad | Solicitudes | Técnico (reglas) |
| ev-060 | Móvil | Acceso | Móvil (llm) |

### Métricas en la nube

- **Exactitud**: 81.82% (36/44)
- **F1 macro**: 0.8271 · F1 ponderado 0.8271 · F1 micro 0.8182 (igual a la exactitud con una etiqueta por ticket)
- **Precisión macro**: 0.8697 · **Recall macro**: 0.8182

| Categoría | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| Técnico | 0.500 | 0.750 | 0.600 | 4 |
| Facturación | 1.000 | 0.750 | 0.857 | 4 |
| Comercial | 1.000 | 0.750 | 0.857 | 4 |
| Acceso | 1.000 | 0.750 | 0.857 | 4 |
| Cuenta | 0.600 | 0.750 | 0.667 | 4 |
| Rendimiento | 1.000 | 0.750 | 0.857 | 4 |
| UX/UI | 0.800 | 1.000 | 0.889 | 4 |
| Seguridad | 1.000 | 0.750 | 0.857 | 4 |
| Integraciones | 1.000 | 1.000 | 1.000 | 4 |
| Móvil | 1.000 | 0.750 | 0.857 | 4 |
| Solicitudes | 0.667 | 1.000 | 0.800 | 4 |

### Matriz de confusión — nube

| real \ pred | Técnico | Factur… | Comerc… | Acceso | Cuenta | Rendim… | UX/UI | Seguri… | Integr… | Móvil | Solici… |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Técnico** | **3** | · | · | · | · | · | 1 | · | · | · | · |
| **Facturación** | 1 | **3** | · | · | · | · | · | · | · | · | · |
| **Comercial** | · | · | **3** | · | 1 | · | · | · | · | · | · |
| **Acceso** | · | · | · | **3** | 1 | · | · | · | · | · | · |
| **Cuenta** | · | · | · | · | **3** | · | · | · | · | · | 1 |
| **Rendimiento** | 1 | · | · | · | · | **3** | · | · | · | · | · |
| **UX/UI** | · | · | · | · | · | · | **4** | · | · | · | · |
| **Seguridad** | 1 | · | · | · | · | · | · | **3** | · | · | · |
| **Integraciones** | · | · | · | · | · | · | · | · | **4** | · | · |
| **Móvil** | · | · | · | · | · | · | · | · | · | **3** | 1 |
| **Solicitudes** | · | · | · | · | · | · | · | · | · | · | **4** |
