# Guía rápida · AI Support Co-Pilot (v3.0.1)

Cómo levantar la mesa de ayuda en local, probarla y conectar las notificaciones de n8n. El despliegue en la nube está en [DEPLOY.md](./DEPLOY.md); las variables, en [python-api/ENV_EXAMPLE.md](./python-api/ENV_EXAMPLE.md) y [frontend/ENV_EXAMPLE.md](./frontend/ENV_EXAMPLE.md); las pruebas, en [TESTING.md](./TESTING.md).

## Prerrequisitos

- Docker y Docker Compose (o Python 3.11 y Node 18 o superior para correr sin Docker).
- Un proyecto de Supabase.
- Una llave gratuita de Groq para el modelo `openai/gpt-oss-20b` (https://console.groq.com/keys). Sin ella la API clasifica solo con el motor de reglas.
- Opcional: una instancia de n8n con SMTP, para HU-05.

## 1. Base de datos

Aplicar en orden las migraciones de `supabase/migrations/` (SQL Editor de Supabase o `supabase db push`):

| Migración | Qué agrega |
|---|---|
| `20260315000000_esquema_base.sql` | `profiles`, `tickets`, roles, RLS y `handle_new_user` |
| `20260902000000_dataset_historico.sql` | `classification_log`, `ticket_labels` y la vista `dataset_tickets` |
| `20260924000000_clasificacion_ia.sql` | sentimiento, prioridad, confianza y motor en `tickets` |
| `20261017000000_endurecer_para_la_nube.sql` | el rol anónimo sin permisos sobre las tablas |
| `20261019000000_revision_y_reclasificacion.sql` | motivo de revisión y marca de reclasificación |
| `20261026000000_asignacion_y_comentarios.sql` | asignación y `ticket_eventos` (comentarios e historial) |
| `20261102000000_metricas_reportes.sql` | función `metricas_tickets` (HU-07) |

Los usuarios nuevos quedan como **cliente**. Para tener un agente o un administrador: `supabase/promote_agente.sql` y `supabase/promote_admin.sql`.

## 2. Variables de entorno

```bash
./setup-env.sh      # crea python-api/.env y frontend/.env desde los ejemplos; no sobrescribe
```

Completar como mínimo:

| Archivo | Variables |
|---|---|
| `python-api/.env` | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, `LLM_ENABLED=1`, `LLM_API_KEY` |
| `frontend/.env` | `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_URL=http://localhost:8001` |

Los `.env` no se versionan.

## 3. Arrancar

```bash
./start.sh          # o: docker compose up --build
```

- Frontend: http://localhost:5200
- API y documentación: http://localhost:8001/docs
- Salud: http://localhost:8001/health. Debe responder la versión, el commit y `"llm_habilitado": true`.

Sin Docker:

```bash
cd python-api && python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt && uvicorn main:app --reload --port 8001

cd frontend && npm install && npm run dev
```

## 4. Probar el flujo

1. Registrarse en el frontend: la cuenta queda como cliente.
2. Crear una solicitud desde el «Centro de ayuda». El frontend llama a `POST /create-ticket` con el JWT de Supabase; la API clasifica con el LLM (límite de 20 s) o, si no responde, con las reglas.
3. La respuesta trae categoría, prioridad, confianza y motor. Con confianza de 0,5 o menos el ticket queda «Requiere revisión».
4. Con un usuario agente, abrir la «Mesa de atención»: tomar el ticket, comentarlo y cambiar su estado. Cada acción queda en el historial.
5. Reportes (HU-07): pestaña de reportes del agente, servida por la función `metricas_tickets`.

Con un token a mano:

```bash
curl -X POST http://localhost:8001/create-ticket \
  -H "Authorization: Bearer <JWT de Supabase>" -H "Content-Type: application/json" \
  -d '{"titulo": "Cobro doble", "description": "Me cobraron dos veces la factura y necesito el reembolso hoy"}'
```

## 5. Notificaciones con n8n (HU-05)

Cuando un ticket queda con prioridad **Alta**, la API llama a un webhook de n8n en segundo plano y n8n envía un correo al equipo. Si n8n falla o tarda, el ticket ya está creado y el cliente no ve ningún error.

1. **Importar el flujo.** En n8n: *Workflows → Import from File →* `n8n-workflow/workflow.json`. Crea el flujo «AISCOP · HU-05 · Ticket urgente → correo» con tres nodos: Webhook → Correo al equipo → Respuesta.
2. **Credencial del webhook.** Crear una credencial *Header Auth* llamada `AISCOP webhook secreto`, con nombre de encabezado `X-AISCOP-Secret` y un valor largo aleatorio. Sin ese encabezado, n8n responde 403.
3. **Credencial SMTP.** Crear `AISCOP SMTP` (por ejemplo `smtp.gmail.com`, puerto 465, SSL, con contraseña de aplicación) y asignarla al nodo «Correo al equipo».
4. **Remitente y destinatario.** En «Correo al equipo», cambiar `soporte@tu-dominio.com` y `equipo-soporte@tu-dominio.com` por los reales.
5. **Activar** el flujo y copiar la *Production URL* del webhook (termina en `/webhook/aiscop-ticket-urgente`).
6. **Configurar la API** en `python-api/.env` (en la nube, en las variables del servicio de Render):

   ```
   N8N_WEBHOOK_URL=https://<tu-n8n>/webhook/aiscop-ticket-urgente
   N8N_WEBHOOK_SECRET=<el mismo valor de la credencial Header Auth>
   APP_URL=http://localhost:5200
   ```

7. **Probar:** crear un ticket urgente, por ejemplo «Cobro triple en la tarjeta, necesito que lo reversen ya». Debe llegar un correo con el ID, el título, el cliente, la categoría y el enlace «Abrir en la Mesa de Ayuda». En n8n queda la ejecución en *Executions*.

El correo lleva estos campos del payload (`python-api/notificaciones.py`): `ticket_id`, `titulo`, `cliente`, `categoria`, `prioridad`, `sentimiento`, `descripcion`, `creado` y `url`.

Para la demostración, `deploy/escenario_demo.py` siembra o limpia tickets de ejemplo y enciende o apaga el flujo:

```bash
python deploy/escenario_demo.py sembrar | limpiar
python deploy/escenario_demo.py n8n on | off | estado
```

## Problemas frecuentes

| Síntoma | Causa probable |
|---|---|
| La API responde 401 | `SUPABASE_JWT_SECRET` incorrecto o token vencido. No usar la llave anon ni la service role como secreto. |
| Todo se clasifica con reglas | Falta `LLM_ENABLED=1` o `LLM_API_KEY`. `/health` y el log de arranque lo avisan. |
| No llega el correo | `N8N_WEBHOOK_URL` vacía, flujo inactivo, secreto distinto (n8n responde 403) o el ticket no quedó en prioridad Alta. Ver el log de la API (`HU-05: ...`). |
| El frontend no muestra tickets | `VITE_SUPABASE_*` o `VITE_API_URL` mal configurados; revisar la consola del navegador. |
| El navegador bloquea las llamadas en la nube | `CORS_ORIGINS` de la API no incluye la URL del frontend. |
