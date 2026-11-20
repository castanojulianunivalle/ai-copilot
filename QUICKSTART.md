# 🚀 Guía Rápida - AI Support Co-Pilot

## 📋 Prerrequisitos

- Docker y Docker Compose instalados
- Cuenta en Supabase (gratis): https://supabase.com
- (Opcional) Token de Hugging Face para usar modelos LLM: https://huggingface.co/settings/tokens

---

## ⚡ Inicio Rápido (5 minutos)

### Paso 1: Configurar Supabase

1. Crea un proyecto en https://supabase.com
2. Ve a **SQL Editor** y ejecuta el contenido de `supabase/setup.sql`:
   ```sql
   -- Copia y pega todo el contenido de supabase/setup.sql
   ```
3. (Opcional) Ejecuta `supabase/seed.sql` para datos de prueba

### Paso 2: Obtener Credenciales de Supabase

1. En tu proyecto de Supabase, ve a **Settings** → **API**
2. Copia:
   - **Project URL** → `SUPABASE_URL`
   - **service_role key** (secreto) → `SUPABASE_SERVICE_ROLE_KEY`
   - **anon public key** → `VITE_SUPABASE_ANON_KEY`

### Paso 3: Configurar Variables de Entorno

**API (`python-api/.env`):**
```bash
# Opción A: Usar script automático (recomendado)
chmod +x setup-env.sh
./setup-env.sh

# Opción B: Crear manualmente
# Ver python-api/ENV_EXAMPLE.md para todas las variables

# Luego edita python-api/.env con tus credenciales reales
```

**Nota sobre el LLM:**
- **Modelo por defecto**: `meta-llama/Llama-3.1-8B-Instruct` (chat-compatible, funciona en Router)
- **Configuración mínima** en `python-api/.env`:
  ```
  LLM_API_BASE_URL=https://router.huggingface.co/v1/chat/completions
  HF_API_TOKEN=tu-token-de-hf
  HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
  ```
- **Modelos alternativos chat-compatibles** (si el por defecto no está disponible):
  - `google/gemma-2-9b-it`
  - `microsoft/Phi-3-mini-4k-instruct`
  - `Qwen/Qwen2.5-7B-Instruct`
- **Opción avanzada**: Si quieres usar `mistralai/Ministral-3-3B-Instruct-2512`, necesitas vLLM local:
  ```bash
  pip install vllm
  vllm serve mistralai/Ministral-3-3B-Instruct-2512 \
    --tokenizer-mode mistral --config-format mistral --load-format mistral \
    --enable-auto-tool-choice --tool-call-parser mistral
  ```
  Luego en `python-api/.env`:
  ```
  LLM_API_BASE_URL=http://localhost:8000/v1/chat/completions
  HF_MODEL=mistralai/Ministral-3-3B-Instruct-2512
  ```

**Frontend (`frontend/.env`):**
```bash
cp frontend/.env.example frontend/.env
# Edita frontend/.env con tus credenciales
```

### Paso 4: Iniciar con Docker Compose

**Opción A: Script automático**
```bash
chmod +x start.sh
./start.sh
```

**Opción B: Manual**
```bash
docker compose up --build
```

### Paso 5: Abrir el Dashboard

- **Frontend**: http://localhost:5200
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

---

## 🌍 Opciones Local vs Cloud (Frontend / API / n8n)

### ✅ Local (desarrollo)
- **API**: Docker Compose o `uvicorn` local en `http://localhost:8001`
- **Frontend**: Vite en `http://localhost:5200`
- **n8n**: Docker local `http://localhost:5678`
- **Config env frontend**: `VITE_API_URL=http://localhost:8001`

### ☁️ Cloud (producción)
- **API (Render)**: URL pública de Render `https://tu-api.onrender.com`
- **Frontend (Vercel/Netlify)**: URL pública del dashboard
- **n8n Cloud**: Workflow en n8n Cloud y webhook público
- **Config env frontend**: `VITE_API_URL=https://tu-api.onrender.com`

## 🧪 Probar el Sistema

### 1. Insertar un ticket manualmente en Supabase

Ve a **Table Editor** → `tickets` → **Insert row**:
- `description`: "No funciona el login"
- `category`: null
- `sentiment`: null
- `processed`: false

### 2. Procesar el ticket vía API

```bash
curl -X POST http://localhost:8001/process-ticket \
  -H "Content-Type: application/json" \
  -d '{"description": "No funciona el login"}'
```

O con `ticket_id` para actualizar Supabase:
```bash
curl -X POST http://localhost:8001/process-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": "uuid-del-ticket", "description": "No funciona el login"}'
```

### 3. Ver en tiempo real

El dashboard en http://localhost:5200 se actualizará automáticamente gracias a Supabase Realtime.

Si no ves actualizaciones en tiempo real, ejecuta en el SQL Editor:
```sql
alter table public.tickets replica identity full;
alter publication supabase_realtime add table public.tickets;
```

---

## 🔄 Configurar n8n (workflow) - Paso a paso

### ⚡ Funcionamiento Automático

La API llama automáticamente al webhook de n8n cuando detecta un ticket con sentimiento **"Negativo"**.

**Flujo automático**:
1. Usuario crea un ticket desde el frontend (o vía API)
2. La API procesa y clasifica el ticket
3. Si el sentimiento es "Negativo", la API llama automáticamente al webhook de n8n
4. n8n recibe el webhook, procesa y envía email de alerta

**Payload que recibe n8n desde la API**:
- `body.description`, `body.category`, `body.sentiment`, `body.id`
- Opcional: `email_from`, `email_to`, `email_subject` (para sobreescribir el correo)
- Telegram: configurar `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en n8n

### Opción A: n8n Cloud (Recomendado para producción)

#### Paso 1: Importar workflow
1. Entra a tu workspace de n8n Cloud: https://app.n8n.io
2. Click en **"Workflows"** → **"Add workflow"** → **"Import from File"**
3. Selecciona `n8n-workflow/workflow.json`

#### Paso 2: Configurar nodo Email con Gmail
1. Abre el nodo **"Send Email (Simulado)"**
2. Click en **"Credential for SMTP"** → **"Create New Credential"**
3. Configura:
   - **Name**: `Gmail Support Co-Pilot`
   - **User**: Tu email de Gmail
   - **Password**: Contraseña de aplicación de Gmail (ver sección Gmail abajo)
   - **Host**: `smtp.gmail.com`
   - **Port**: `465`
   - **Secure**: `SSL/TLS`
   - **Sender Email**: Tu email de Gmail
4. Configura el email (usa variables de n8n):
   - **From Email**: `={{ $vars.EMAIL_FROM }}`
   - **To Email**: `={{ $vars.EMAIL_TO }}`
   - **Subject**: `⚠️ Ticket con sentimiento negativo - Support Co-Pilot`
   - **Email Body** (usar modo expresión):
     ```
     Se ha recibido un ticket con sentimiento negativo:
     
     Descripción: {{ $json.body.description }}
     Categoría: {{ $json.body.category }}
     Sentimiento: {{ $json.body.sentiment }}
     ID del Ticket: {{ $json.body.id }}
     
     Por favor, revisar con prioridad.
     ```

#### Paso 3: Obtener URL del webhook
1. Abre el nodo **"Webhook"**
2. Verifica que el **Path** sea: `support-copilot-webhook`
3. Click en **"Listen for test event"** o busca la **"Production URL"**
4. Copia la URL completa (ejemplo: `https://tu-workspace.n8n.cloud/webhook/support-copilot-webhook`)

#### Paso 4: Configurar variable de entorno en Render
1. Ve a tu servicio en Render → **Environment**
2. Agrega nueva variable:
   - **Key**: `N8N_WEBHOOK_URL`
   - **Value**: La URL del webhook que copiaste en el Paso 4
3. Guarda y espera a que se redespliegue

#### Paso 5: Activar workflow
1. En n8n, activa el workflow con el toggle **"Active"** (arriba a la derecha)
2. El workflow queda escuchando en el webhook

#### Paso 6: Probar
1. Ve al frontend y crea un ticket con texto negativo:
   - Ejemplo: "No funciona el login y estoy muy molesto con este problema terrible"
2. La API procesará el ticket automáticamente
3. Si el sentimiento es "Negativo", recibirás un email en el correo configurado
4. Verifica en **"Executions"** de n8n que el workflow se ejecutó

#### Paso 7: Configurar variables (Email + Telegram)

**Importante**: El workflow solo envía mensajes cuando el sentimiento es **"Negativo"**.

##### 7.1: Variables de Email y Frontend en n8n
1. Ve a **Settings → Variables**
2. Agrega:
   - `EMAIL_FROM` → tu correo
   - `EMAIL_TO` → correo destinatario
   - `FRONTEND_URL` → URL de tu frontend desplegado (ej: `https://tu-app.vercel.app`)
     - ⚠️ **Importante**: Esta URL se usa para generar links directos a los tickets en las notificaciones
3. Guarda

##### 7.2: Crear el bot en Telegram
1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot`
3. Sigue las instrucciones y dale un nombre y username (debe terminar en `bot`)
4. BotFather te dará un **token** → guárdalo (ejemplo: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

##### 7.3: Obtener el Chat ID

**Para un grupo o canal:**
1. Agrega el bot al grupo/canal
2. Envía un mensaje en el grupo/canal (puede ser cualquier cosa)
3. Abre en el navegador:
   ```
   https://api.telegram.org/bot<TU_BOT_TOKEN>/getUpdates
   ```
   Reemplaza `<TU_BOT_TOKEN>` con el token que te dio BotFather
4. En la respuesta JSON busca:
   ```json
   "chat": { "id": -1001234567890, ... }
   ```
   **Nota**: Para grupos/canales, el `chat_id` será un número **negativo** (ej: `-1001234567890`)

**Para chat privado:**
1. Inicia una conversación con tu bot (envíale `/start`)
2. Envía un mensaje cualquiera
3. Haz el mismo `getUpdates` de arriba
4. El `chat_id` será un número positivo (ej: `123456789`)

##### 7.4: Configurar credenciales en n8n
1. En n8n, abre el nodo **"Send Telegram"**
2. Click en **"Credential for Telegram"** → **"Create New Credential"**
3. Configura:
   - **Name**: `Telegram Bot`
   - **Access Token**: Pega el token que te dio BotFather
4. Guarda la credencial

##### 7.5: Configurar Chat ID en el nodo
1. En el nodo **"Send Telegram"**, en el campo **"Chat ID"**:
   - Usa: `={{ $env.TELEGRAM_CHAT_ID }}`
2. En n8n, ve a **Settings** → **Environment Variables**
3. Agrega:
   - **Key**: `TELEGRAM_CHAT_ID`
   - **Value**: El chat_id que obtuviste (ej: `-1001234567890` para grupos)
4. Guarda

##### 7.6: Probar
1. Activa el workflow
2. Crea un ticket con sentimiento negativo desde el frontend
3. **Esperado**: Llega un mensaje al grupo/canal de Telegram con el detalle del ticket

**Nota**: Si el sentimiento es "Positivo" o "Neutral", **NO** se enviará mensaje a Telegram (solo se envía para "Negativo").

### Opción B: n8n en local con Docker (para desarrollo)

1. Ejecuta n8n:
   ```bash
   docker run -it --rm -p 5678:5678 n8nio/n8n
   ```
2. Abre n8n: http://localhost:5678
3. Importa `n8n-workflow/workflow.json`
4. Configura el nodo **Email** con Gmail (mismo proceso que arriba)
5. Copia la URL del webhook (ejemplo: `http://localhost:5678/webhook/support-copilot-webhook`)
6. Agrega `N8N_WEBHOOK_URL=http://localhost:5678/webhook/support-copilot-webhook` en `python-api/.env`
7. Reinicia la API para que tome la nueva variable

---

## ☁️ Deploy rápido (Render + Vercel + n8n Cloud)

### API en Render (requerido por la prueba)
1. Crea un **Web Service** en Render.
2. Conecta el repo y selecciona `/python-api`.
3. Build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Start command:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```
5. Configura variables de entorno (ver `python-api/ENV_EXAMPLE.md`).
6. Guarda la URL pública para usarla en frontend y n8n.

### Frontend en Vercel/Netlify
1. Importa el repo y selecciona `/frontend`.
2. Build command: `npm run build`
3. Output directory: `dist`
4. Agrega variables de entorno (ver `frontend/ENV_EXAMPLE.md`).

### n8n Cloud
1. Importa `n8n-workflow/workflow.json`.
2. Configura el nodo **Email** con credenciales SMTP (Gmail recomendado).
3. Activa el workflow y copia la **URL del webhook** (Production URL).
4. Agrega `N8N_WEBHOOK_URL` en las variables de entorno de Render.
5. Configura `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en n8n si quieres alertas por Telegram.
6. **Listo**: Ahora cuando crees un ticket negativo desde el frontend, recibirás alertas automáticamente.

## 🔧 Desarrollo Local (sin Docker)

### API Python

```bash
cd python-api
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus credenciales
uvicorn main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edita .env con tus credenciales
npm run dev
```

---

## 🐛 Troubleshooting

### Error: "No such file or directory: .env"
- Asegúrate de haber copiado `.env.example` a `.env` en ambas carpetas
- Verifica que los archivos `.env` tengan las credenciales correctas

### Error: "Connection refused" en Supabase
- Verifica que `SUPABASE_URL` y las keys sean correctas
- Asegúrate de haber ejecutado `setup.sql` en Supabase

### El dashboard no muestra tickets
- Verifica que `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY` estén correctos
- Abre la consola del navegador (F12) para ver errores

### La API no procesa tickets (falla LLM)
- Si no tienes `HF_API_TOKEN`, el sistema usa clasificación por reglas (keywords)
- Esto es normal y funcional, solo menos preciso que usar un LLM

### Docker no inicia
- Verifica que Docker esté corriendo: `docker ps`
- Revisa logs: `docker compose logs`

---

## 📚 Próximos Pasos

1. **Configurar n8n**: Importa `n8n-workflow/workflow.json` y conecta el webhook (ver sección n8n arriba)
2. **Desplegar a producción**: Ver [DEPLOY.md](./DEPLOY.md) para guía completa paso a paso
3. **Personalizar categorías**: Edita `classify_with_rules()` en `python-api/main.py`

---

## 📞 Soporte

Si tienes problemas, revisa:
- Logs de Docker: `docker compose logs`
- Consola del navegador (F12)
- Logs de Supabase en el dashboard
