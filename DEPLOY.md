# 🚀 Guía de Deployment - AI Support Co-Pilot

Esta guía te ayudará a desplegar la aplicación en Render (API) y Vercel (Frontend).

---

## 📋 Checklist Pre-Deployment

Antes de desplegar, asegúrate de tener:

- [ ] Proyecto de Supabase creado y configurado
- [ ] Tabla `tickets` creada (ejecuta `supabase/setup.sql`)
- [ ] Token de Hugging Face (https://huggingface.co/settings/tokens)
- [ ] (Opcional) n8n Cloud configurado con workflow importado
- [ ] Repositorio en GitHub con todo el código

---

## 🔧 API en Render

### Paso 1: Crear Web Service

1. Ve a https://render.com/dashboard
2. Click en **"New"** → **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio y la rama (`main`)

### Paso 2: Configuración Básica

```
Name: tu-api-name
Region: Virginia (US East) o la más cercana
Branch: main
Root Directory: python-api ⚠️ IMPORTANTE
Runtime: Docker
Instance Type: Free (para empezar)
```

### Paso 3: Build & Deploy

**Si usas Docker** (recomendado):
- **Dockerfile Path**: `./Dockerfile` (Render lo detecta automáticamente)
- No necesitas Build Command ni Start Command

**Si NO usas Docker**:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  ⚠️ Usa `$PORT` no `8001` - Render lo inyecta automáticamente

### Paso 4: Variables de Entorno

Ve a **Environment** y agrega:

```env
# Supabase (obligatorio)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Hugging Face LLM (obligatorio)
HF_API_TOKEN=hf_xxxxxxxxxxxxx
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
LLM_API_BASE_URL=https://router.huggingface.co/v1/chat/completions
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=200
LLM_CONFIDENCE_THRESHOLD=0.6

# n8n (opcional - solo si quieres notificaciones)
N8N_WEBHOOK_URL=https://tu-workspace.n8n.cloud/webhook/support-copilot-webhook
```

⚠️ **NO agregues** `PORT` - Render lo inyecta automáticamente

### Paso 5: Health Check (Opcional)

- **Health Check Path**: `/health`
- Esto ayuda a Render a detectar si el servicio está funcionando

### Paso 6: Deploy

1. Click en **"Create Web Service"**
2. Espera 5-10 minutos mientras Render construye y despliega
3. Una vez listo, verás la URL: `https://tu-api.onrender.com`

### Paso 7: Verificar

1. Abre `https://tu-api.onrender.com/docs` - Deberías ver Swagger UI
2. Abre `https://tu-api.onrender.com/health` - Debería responder `{"status": "ok"}`
3. Abre `https://tu-api.onrender.com/diagnostics` - Verifica que `llm.available` sea `true`

---

## 🎨 Frontend en Vercel

### Paso 1: Importar Proyecto

1. Ve a https://vercel.com/dashboard
2. Click en **"Add New"** → **"Project"**
3. Importa tu repositorio de GitHub
4. Selecciona el repositorio

### Paso 2: Configuración

```
Framework Preset: Vite (o detecta automáticamente)
Root Directory: frontend ⚠️ IMPORTANTE
Build Command: npm run build (automático)
Output Directory: dist (automático)
```

### Paso 3: Variables de Entorno

Ve a **Environment Variables** y agrega:

```env
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_API_URL=https://tu-api.onrender.com
```

⚠️ **IMPORTANTE**: `VITE_API_URL` debe ser la URL de tu API en Render

### Paso 4: Deploy

1. Click en **"Deploy"**
2. Espera 2-3 minutos
3. Una vez listo, verás la URL: `https://tu-app.vercel.app`

### Paso 5: Verificar

1. Abre la URL de Vercel
2. Deberías ver el dashboard
3. Prueba crear un ticket
4. Verifica que se actualice en tiempo real
5. Prueba editar y eliminar tickets

---

## 🔔 Configurar n8n (Opcional)

Si quieres recibir notificaciones por email y Telegram cuando un ticket tiene sentimiento negativo:

### Paso 1: Importar Workflow

1. Ve a https://app.n8n.io
2. Click en **"Workflows"** → **"Add workflow"** → **"Import from File"**
3. Selecciona `n8n-workflow/workflow.json` de tu repositorio

### Paso 2: Configurar Variables en n8n

1. Ve a **Settings → Variables**
2. Agrega las siguientes variables:
   - `EMAIL_FROM` → tu correo de Gmail
   - `EMAIL_TO` → correo destinatario
   - `FRONTEND_URL` → URL de tu frontend en Vercel (ej: `https://tu-app.vercel.app`)
     - ⚠️ **Importante**: Esta URL se usa para generar links directos a los tickets en las notificaciones
   - `TELEGRAM_BOT_TOKEN` → token de tu bot de Telegram (opcional)
   - `TELEGRAM_CHAT_ID` → ID del chat/grupo/canal de Telegram (opcional)

### Paso 3: Configurar Credenciales

1. **Email (Gmail)**:
   - Abre el nodo "Send Email"
   - Crea una credencial SMTP con tus datos de Gmail
   - Usa contraseña de aplicación (no tu contraseña normal)

2. **Telegram** (opcional):
   - Abre el nodo "Send Telegram"
   - Crea una credencial de Telegram con tu bot token

### Paso 4: Obtener Webhook URL

1. Abre el nodo "Webhook"
2. Activa el workflow
3. Copia la **Production URL** (ej: `https://tu-workspace.n8n.cloud/webhook/support-copilot-webhook`)

### Paso 5: Configurar en Render

1. Ve a tu servicio en Render → **Environment**
2. Agrega:
   - **Key**: `N8N_WEBHOOK_URL`
   - **Value**: La URL del webhook que copiaste
3. Guarda y espera el redeploy

### Paso 6: Probar

1. Crea un ticket con sentimiento negativo desde el frontend
2. Deberías recibir:
   - Email con link directo al ticket
   - Mensaje en Telegram con link directo al ticket (si está configurado)

---

## 🔍 Troubleshooting

### API no inicia en Render

**Error**: `ModuleNotFoundError` o errores de importación
- **Solución**: Verifica que **Root Directory** sea `python-api`
- Verifica que el Dockerfile esté en `python-api/Dockerfile`

**Error**: `Port already in use` o errores de puerto
- **Solución**: Asegúrate de usar `$PORT` en el Start Command, no `8001`
- Si usas Docker, el Dockerfile ya está configurado correctamente

**Error**: `HF_API_TOKEN not set` en `/diagnostics`
- **Solución**: Verifica que agregaste `HF_API_TOKEN` en Environment Variables
- Verifica que el token sea válido (no tenga espacios extra)

**Error**: `llm.available: false` en `/diagnostics`
- **Solución**: 
  1. Verifica que `HF_API_TOKEN` sea válido
  2. Verifica que `HF_MODEL` sea `meta-llama/Llama-3.1-8B-Instruct` (o un modelo chat-compatible)
  3. Revisa los logs en Render para ver el error específico

### Frontend no conecta con API

**Error**: `Failed to fetch` o errores CORS
- **Solución**: 
  1. Verifica que `VITE_API_URL` apunte a la URL correcta de Render
  2. Verifica que la API esté funcionando (`/health` responde)
  3. Verifica que no haya errores CORS en la consola del navegador

**Error**: Tickets no se actualizan en tiempo real
- **Solución**: 
  1. Verifica que `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY` sean correctos
  2. Ejecuta en Supabase SQL Editor:
     ```sql
     alter table public.tickets replica identity full;
     alter publication supabase_realtime add table public.tickets;
     ```

### n8n no recibe webhooks

**Error**: No llegan notificaciones cuando el sentimiento es negativo
- **Solución**:
  1. Verifica que `N8N_WEBHOOK_URL` sea la URL correcta del webhook
  2. Verifica que el workflow esté **activo** en n8n
  3. Verifica en los logs de Render que no haya errores al llamar al webhook
  4. Prueba el webhook manualmente con curl:
     ```bash
     curl -X POST https://tu-workspace.n8n.cloud/webhook/support-copilot-webhook \
       -H "Content-Type: application/json" \
       -d '{"description": "test", "category": "Técnico", "sentiment": "Negativo", "id": "test-123"}'
     ```

---

## 📊 Verificar Deployment Completo

### Checklist Final

- [ ] API responde en `https://tu-api.onrender.com/health`
- [ ] API docs funcionan en `https://tu-api.onrender.com/docs`
- [ ] `/diagnostics` muestra `llm.available: true`
- [ ] Frontend carga en `https://tu-app.vercel.app`
- [ ] Puedo crear tickets desde el frontend
- [ ] Los tickets se actualizan en tiempo real
- [ ] (Opcional) Recibo emails cuando el sentimiento es negativo con link directo al ticket
- [ ] (Opcional) Recibo mensajes de Telegram cuando el sentimiento es negativo con link directo al ticket
- [ ] Puedo editar tickets y se re-evalúan automáticamente por IA
- [ ] Puedo eliminar tickets con confirmación

---

## 🔄 Actualizar Deployment

### Actualizar API

1. Haz commit y push a GitHub
2. Render detectará automáticamente el cambio
3. Render iniciará un nuevo deploy automáticamente
4. Espera 5-10 minutos

### Actualizar Frontend

1. Haz commit y push a GitHub
2. Vercel detectará automáticamente el cambio
3. Vercel iniciará un nuevo deploy automáticamente
4. Espera 2-3 minutos

---

## 💡 Tips

- **Render Free Tier**: Los servicios gratuitos se "duermen" después de 15 minutos de inactividad. La primera petición puede tardar ~30 segundos en despertar.
- **Vercel Free Tier**: No tiene límites de tiempo, pero tiene límites de ancho de banda.
- **Logs**: Siempre revisa los logs en Render/Vercel si algo no funciona.
- **Variables de entorno**: Nunca commitees archivos `.env` - siempre usa las variables de entorno de la plataforma.

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Render/Vercel
2. Verifica `/diagnostics` en la API
3. Revisa la consola del navegador (F12)
4. Consulta `QUICKSTART.md` para configuración local
