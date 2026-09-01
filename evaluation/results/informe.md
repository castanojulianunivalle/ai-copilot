# Evaluación de modelos — AI Support Co-Pilot

> Sprint 6 · HU-09 · AISCOP-46 · generado el 2026-09-01T19:06:47+00:00
> Conjunto: `tickets_etiquetados.jsonl` · 66 tickets · 11 categorías

### Motor de reglas (línea base, Semestre 1)

- **Exactitud**: 53.03% (35/66)
- **F1 macro**: 0.5271
- **F1 ponderado**: 0.5271
- **Precisión macro**: 0.6672
- **Recall macro**: 0.5303

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
