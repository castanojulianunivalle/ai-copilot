# Pruebas de la API

## `prueba_e2e_notificacion.py` — HU-05 · AISCOP-31

Prueba end-to-end del aviso a n8n. Levanta un receptor HTTP local que se comporta como el flujo de n8n y recorre la cadena completa.

```bash
python python-api/pruebas/prueba_e2e_notificacion.py
```

No necesita Supabase, ni un LLM, ni una instancia de n8n. Corre con la librería estándar y `httpx`.

**Qué verifica**

| # | Caso | Comprueba |
|---|---|---|
| 1 | Ticket de prioridad Alta | Llega al receptor, firma HMAC válida, payload completo con tilde, tono, confianza y enlace accionable |
| 2 | Ticket de prioridad Media | **No** dispara |
| 3 | Clasificado por reglas | La firma sigue validando con campos nulos y el payload marca que no fue la IA |
| 4 | n8n caído | La API no propaga la excepción |

**Por qué el receptor reserializa el cuerpo.** No comprueba la firma contra los bytes crudos que recibió, sino que parsea el JSON y lo vuelve a serializar, que es exactamente lo que hace el nodo Code de n8n. Es la única forma de detectar el desajuste de formato que hacía fallar la validación: `json.dumps` de Python pone un espacio después de cada coma y `JSON.stringify` de JavaScript no. La prueba afirma además que los bytes reserializados son idénticos a los enviados, así que cualquier futura divergencia de formato la rompe.

## Realtime (HU-06b) — verificación manual

Realtime necesita dos navegadores y una base real, así que no está automatizado.

1. Aplicar `supabase/migrations/20261103000000_realtime_tickets.sql`.
2. Abrir el dashboard en dos ventanas: una con sesión de **cliente** y otra de **agente**.
3. Crear un ticket desde la ventana del cliente.

**Esperado**: la tarjeta aparece en la ventana del agente sin refrescar. Si el ticket sale con prioridad `Alta`, además salta un aviso. En la ventana del cliente la tarjeta aparece **una sola vez**, no dos: el `POST` ya la insertó y la suscripción descarta el duplicado por `id`.

4. Cambiar el estado desde la ventana del agente → se refleja en la del cliente.
5. Eliminar el ticket → desaparece de ambas.

**Si no llega nada**: casi siempre es que falta la migración. La suscripción se conecta igual y se queda callada, que es el modo de fallo más confuso. Comprobar con:

```sql
select tablename from pg_publication_tables where pubname = 'supabase_realtime';
```
