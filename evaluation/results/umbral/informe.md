# Umbral de revisión humana — clasificacion-v2

> Sprint 6 · AISCOP-51 · commit `db0739d` · umbral vigente 0.5

## Práctica: 22 tickets, 1 errores del modelo

Confianza en los errores: [0.95] · mínima en los aciertos: 0.9

| Umbral | A revisión | Carga | Errores atrapados |
|---:|---:|---:|---:|
| ≤ 0.5 | 0 | 0% | 0 de 1 |
| ≤ 0.6 | 0 | 0% | 0 de 1 |
| ≤ 0.7 | 0 | 0% | 0 de 1 |
| ≤ 0.8 | 0 | 0% | 0 de 1 |
| ≤ 0.85 | 0 | 0% | 0 de 1 |
| ≤ 0.9 | 2 | 9% | 0 de 1 |
| ≤ 0.95 | 22 | 100% | 1 de 1 |

Señal alternativa, el modelo y las reglas discrepan: 10 a revisión (45%), 1 de 1 errores atrapados.

## Examen: 44 tickets, 6 errores del modelo

Confianza en los errores: [0.95, 0.95, 0.95, 0.95, 0.95, 0.95] · mínima en los aciertos: 0.9

| Umbral | A revisión | Carga | Errores atrapados |
|---:|---:|---:|---:|
| ≤ 0.5 | 0 | 0% | 0 de 6 |
| ≤ 0.6 | 0 | 0% | 0 de 6 |
| ≤ 0.7 | 0 | 0% | 0 de 6 |
| ≤ 0.8 | 0 | 0% | 0 de 6 |
| ≤ 0.85 | 0 | 0% | 0 de 6 |
| ≤ 0.9 | 4 | 9% | 0 de 6 |
| ≤ 0.95 | 43 | 98% | 6 de 6 |

Señal alternativa, el modelo y las reglas discrepan: 22 a revisión (50%), 5 de 6 errores atrapados.

## Los 66 (práctica y examen): 66 tickets, 7 errores del modelo

Confianza en los errores: [0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95] · mínima en los aciertos: 0.9

| Umbral | A revisión | Carga | Errores atrapados |
|---:|---:|---:|---:|
| ≤ 0.5 | 0 | 0% | 0 de 7 |
| ≤ 0.6 | 0 | 0% | 0 de 7 |
| ≤ 0.7 | 0 | 0% | 0 de 7 |
| ≤ 0.8 | 0 | 0% | 0 de 7 |
| ≤ 0.85 | 0 | 0% | 0 de 7 |
| ≤ 0.9 | 6 | 9% | 0 de 7 |
| ≤ 0.95 | 65 | 98% | 7 de 7 |

Señal alternativa, el modelo y las reglas discrepan: 32 a revisión (48%), 6 de 7 errores atrapados.

## Sondas: tickets sin información suficiente

| Ticket | Confianza | ¿A revisión? |
|---|---:|---|
| Consulta Hola, tengo una duda. | 0.45 | sí |
| Ayuda No sé si esto es un error o si lo estoy haciendo mal, pero algo no cuadra. | 0.45 | sí |
| Problema No funciona. | 0.45 | sí |
| Urgente Necesito que me llamen hoy. | 0.95 | no |
