# Pruebas en la nube — 2026-10-25 17:06 (hora de Colombia)

- Modo: humo y aceptacion · Web: https://aiscop-web.onrender.com · API: https://aiscop-api.onrender.com
- Version que reporta la API: 2.1.0 · commit d36f1f5 · esperado v2.1.0 = d36f1f5
- **9 de 9 casos aprobados**

| Caso | Prueba | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|
| TC-H1 | Acceso a la aplicacion web | 200; el bundle apunta a la API de la nube y lleva el commit d36f1f5 | index y bundle /assets/index-CneQIgKh.js; API de la nube en el bundle: True | Aprobado |
| TC-H2 | La API responde con la version prevista | 200; llm_habilitado true, sin advertencias; commit d36f1f5 | version 2.1.0 · commit d36f1f5 · openai/gpt-oss-20b | Aprobado |
| TC-H3 | Autenticacion de cliente y agente | token de Supabase Auth; /me devuelve el rol de cada uno | /me: {'cliente': 'cliente', 'agente': 'agente'} | Aprobado |
| TC-H4 | Persistencia y servicio inteligente | el ticket se crea clasificado por el LLM; el agente lo lee con categoría, tono, prioridad y confianza, y quedan las dos predicciones en el log | Facturación · Frustrado · prioridad Alta · confianza 0.95 · estado Abierto · el agente lo ve: True · log ['llm', 'reglas'] | Aprobado |
| TC-H6 | El agente cambia el estado; el cliente no puede | PATCH del agente 200 y el cliente ve el ticket Cerrado (RLS: solo los suyos); PATCH del cliente 403 | agente 200 · cliente 403 · el cliente lo ve Cerrado | Aprobado |
| TC-H5 | Manejo de errores y permisos | token invalido 401; agente creando ticket 403; sin sesion no se leen tickets ni la vista del dataset | token invalido 401 · agente 403 · anon tickets 401 · anon vista 401 | Aprobado |
| TC-A1 | HU-06 · clasificacion con el modelo, igual que en local | la nube da la misma categoria que la evaluacion local en 5 tickets de examen | 5 de 5 iguales (ev-015: local Facturación / nube Facturación; ev-043: local Seguridad / nube Seguridad; ev-055: local Móvil / nube Móvil; ev-031: local Rendimiento / nube Rendimiento; ev-049: local Integraciones / nube Integraciones) | Aprobado |
| TC-A2 | HU-06 · revision humana con confianza baja | un ticket sin informacion queda con confianza <= 0.5 y requiere_revision true | Solicitudes · confianza 0.4 · requiere_revision True | Aprobado |
| TC-A4 | HU-01 · registro de un cliente nuevo en la nube | el registro abre sesion con rol cliente; repetir el correo devuelve un error y no duplica | rol cliente · correo repetido 422 · usuario de prueba borrado | Aprobado |
