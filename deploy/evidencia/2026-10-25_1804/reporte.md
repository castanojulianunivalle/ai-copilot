# Pruebas en la nube — 2026-10-25 18:04 (hora de Colombia)

- Modo: humo y aceptacion · Web: https://aiscop-web.onrender.com · API: https://aiscop-api.onrender.com
- Version que reporta la API: 2.2.0 · commit d8b70fb · esperado v2.2.0 = d8b70fb
- **11 de 11 casos aprobados**

| Caso | Prueba | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|
| TC-H1 | Acceso a la aplicacion web | 200; el bundle apunta a la API de la nube y lleva el commit d8b70fb | index y bundle /assets/index-DbMDjI51.js; API de la nube en el bundle: True | Aprobado |
| TC-H2 | La API responde con la version prevista | 200; llm_habilitado true, sin advertencias; commit d8b70fb | version 2.2.0 · commit d8b70fb · openai/gpt-oss-20b | Aprobado |
| TC-H3 | Autenticacion de cliente y agente | token de Supabase Auth; /me devuelve el rol de cada uno | /me: {'cliente': 'cliente', 'agente': 'agente'} | Aprobado |
| TC-H4 | Persistencia y servicio inteligente | el ticket se crea clasificado por el LLM; el agente lo lee con categoría, tono, prioridad y confianza, y quedan las dos predicciones en el log | Facturación · Frustrado · prioridad Alta · confianza 0.95 · estado Abierto · el agente lo ve: True · log ['llm', 'reglas'] | Aprobado |
| TC-H6 | El agente cambia el estado; el cliente no puede | PATCH del agente 200 y el cliente ve el ticket Cerrado (RLS: solo los suyos); PATCH del cliente 403 | agente 200 · cliente 403 · el cliente lo ve Cerrado | Aprobado |
| TC-H5 | Manejo de errores y permisos | token invalido 401; agente creando ticket 403; sin sesion no se leen tickets ni la vista del dataset | token invalido 401 · agente 403 · anon tickets 401 · anon vista 401 | Aprobado |
| TC-A1 | HU-06 · clasificacion con el modelo, igual que en local | la nube da la misma categoria que la evaluacion local en 5 tickets de examen | 5 de 5 iguales (ev-015: local Facturación / nube Facturación; ev-043: local Seguridad / nube Seguridad; ev-055: local Móvil / nube Móvil; ev-031: local Rendimiento / nube Rendimiento; ev-049: local Integraciones / nube Integraciones) | Aprobado |
| TC-A2 | HU-06 · revision humana con confianza baja | un ticket sin informacion queda con confianza <= 0.5 y requiere_revision true | Solicitudes · confianza 0.45 · requiere_revision True | Aprobado |
| TC-A4 | HU-01 · registro de un cliente nuevo en la nube | el registro abre sesion con rol cliente; repetir el correo devuelve un error y no duplica | rol cliente · correo repetido 422 · usuario de prueba borrado | Aprobado |
| TC-A5 | HU-13 · un ticket solo lo toma un agente | el primer agente lo toma (200); el segundo recibe 409 y no puede liberarlo (403); queda asignado al primero | primer agente 200 · segundo agente 409 · liberar ajeno 403 · asignado al primero True | Aprobado |
| TC-A6 | HU-13 · comentarios, notas internas y estado con mensaje | el cliente ve la respuesta y el mensaje del cambio de estado, nunca la nota interna, y no puede escribir notas | eventos: cliente 3 / agente 4 · el cliente ve la nota interna False · nota escrita por el cliente 403 · estado En proceso | Aprobado |
