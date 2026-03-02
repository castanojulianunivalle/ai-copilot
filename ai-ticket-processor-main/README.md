# AI-Powered Support Co-Pilot

Sistema de procesamiento automático de tickets de soporte con IA, dashboard en tiempo real y automatización con n8n.

## ✨ Características Destacadas

- **Dashboard Moderno**: Interfaz responsiva con animaciones suaves, tema oscuro accesible y navegación intuitiva.
- **Experiencia de Usuario Mejorada**: Notificaciones en tiempo real, búsqueda de tickets, modales para detalles y indicadores visuales con iconos.
- **Gestión Completa de Tickets**: Crear, editar y eliminar tickets con re-evaluación automática por IA al editar.
- **Links Directos**: Las notificaciones (email y Telegram) incluyen links directos al ticket específico.
- **Accesibilidad**: Soporte completo para navegación por teclado, etiquetas ARIA y alto contraste.
- **Animaciones Fancy**: Transiciones fluidas con Framer Motion para una experiencia interactiva premium.
- **Componentes Interactivos**: Botones con estados de carga, spinners animados y feedback visual inmediato.

## 🚀 Inicio Rápido

**👉 Ver [QUICKSTART.md](./QUICKSTART.md) para instrucciones detalladas paso a paso.**

### Resumen rápido:

1. **Configura Supabase**: Ejecuta `supabase/setup.sql` en SQL Editor
2. **Crea archivos `.env`**:
   ```bash
   chmod +x setup-env.sh
   ./setup-env.sh
   # Edita python-api/.env y frontend/.env con tus credenciales
   ```
3. **Inicia con Docker**:
   ```bash
   docker compose up --build
   ```
   O usa el script:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
4. **Abre**: http://localhost:5200

## 📁 Estructura

- `supabase/`: esquema SQL y seed
- `python-api/`: microservicio FastAPI + LangChain
- `n8n-workflow/`: flujo de automatización exportado
- `frontend/`: dashboard React + Vite + Tailwind con mejoras UX/UI (animaciones, notificaciones, modales)
- `docker-compose.yml`: orquestación local
- `start.sh`: script de inicio rápido
- `setup-env.sh`: script para crear archivos .env

## 📝 URLs de entrega
- **Dashboard (Frontend)**: https://tu-app.vercel.app/
- **API Python (Backend)**: https://tu-api.onrender.com/docs
- **Canal de Telegram**: https://t.me/tu_canal (configurar según tu canal)

⚠️ **Nota sobre Render**: El backend está desplegado en el plan gratuito de Render. La primera petición después de un período de inactividad puede tardar entre 30-60 segundos mientras el servicio se "despierta". Las peticiones subsiguientes son inmediatas.

## 🎨 Mejoras en el Frontend

### UX/UI Enhancements
- **Tema Oscuro/Claro**: Toggle completo entre modos oscuro y claro con persistencia local.
- **Header Moderno**: Banner con gradiente azul, logo mejorado y toggle de tema integrado.
- **Logo Rediseñado**: SVG personalizado representando IA y soporte con gradientes.
- **Animaciones Suaves**: Entradas y salidas animadas con Framer Motion para una experiencia fluida.
- **Notificaciones Toast**: Feedback visual inmediato para acciones exitosas, errores y eventos en tiempo real.
- **Modal de Detalles**: Vista expandida de tickets con información completa en un modal centrado.
- **Búsqueda en Tiempo Real**: Filtrado instantáneo de tickets por descripción o categoría.
- **Grid Responsivo**: Vista de tarjetas en grid (1 columna móvil, 2 tablet, 3 desktop) para mejor organización visual.
- **Paginación**: Navegación paginada con controles anterior/siguiente y contador de páginas.
- **Iconos Significativos**: Indicadores visuales con Lucide React para estados de sentimiento y procesamiento.
- **Estados de Carga**: Spinners animados y botones con indicadores de progreso.
- **Editar Tickets**: Botones de edición en cada card y en el modal de detalle, con re-evaluación automática por IA.
- **Eliminar Tickets**: Botones de eliminación con confirmación, disponibles en cards y modal de detalle.
- **Links Directos**: Los tickets pueden abrirse directamente desde URLs con parámetro `?ticket=ID`.

### Tecnologías Añadidas
- **Framer Motion**: Para animaciones y transiciones premium.
- **Lucide React**: Conjunto de iconos modernos y accesibles.
- **Tailwind CSS Extendido**: Configuración personalizada con colores primarios y fuente Inter.

### Accesibilidad
- Etiquetas ARIA completas para lectores de pantalla.
- Navegación por teclado con focus-visible.
- Alto contraste en todos los elementos interactivos.

## 🧠 Clasificación Inteligente
- Normalización de jerga antes de clasificar (ej. "rey", "bro", "malísimo").
- Umbral de confianza configurable para LLM (`LLM_CONFIDENCE_THRESHOLD`).
- Fallback automático a reglas cuando el modelo es ambiguo.
- Categorías ampliadas para tickets: Acceso, Cuenta, Facturación, Comercial, Técnico, Rendimiento, UX/UI, Seguridad, Integraciones, Móvil y Solicitudes.
- **Modelo LLM por defecto**: `meta-llama/Llama-3.1-8B-Instruct` (chat-compatible, funciona en Hugging Face Router)
  - Soporte nativo para JSON outputting
  - Temperatura recomendada: 0.1 (ya configurada)
  - Ideal para clasificación de tickets en tiempo real
  - **Probado y funcionando** en Router con respuestas JSON limpias
- **Modelos alternativos chat-compatibles** (si el por defecto no está disponible):
  - `google/gemma-2-9b-it`
  - `microsoft/Phi-3-mini-4k-instruct`
  - `Qwen/Qwen2.5-7B-Instruct`
- **Opción avanzada**: Si quieres usar `mistralai/Ministral-3-3B-Instruct-2512`:
  - **Auto-host** con vLLM y configura `LLM_API_BASE_URL=http://localhost:8000/v1/chat/completions`
  - Ver `QUICKSTART.md` para instrucciones detalladas de vLLM

## 🔔 Notificaciones Automáticas (n8n)

El sistema está integrado con **n8n** para enviar notificaciones por email y Telegram automáticamente:

- **Cuándo se activa**: Cuando un ticket es procesado y tiene sentimiento **"Negativo"** (solo negativo, no positivo ni neutral)
- **Cómo funciona**: 
  1. El frontend crea un ticket (o se procesa vía API)
  2. La API clasifica el ticket con IA
  3. Si el sentimiento es "Negativo", la API llama automáticamente al webhook de n8n
  4. n8n procesa el webhook y envía:
     - **Email** de alerta (configurado con Gmail)
     - **Telegram** (opcional, soporta grupos y canales)
- **Configuración**: 
  - Agrega `N8N_WEBHOOK_URL` en las variables de entorno de la API (ver `python-api/ENV_EXAMPLE.md`)
  - Si no configuras `N8N_WEBHOOK_URL`, el sistema funciona pero no envía notificaciones
- **Payload**: n8n recibe los datos en `body` (`body.description`, `body.category`, `body.sentiment`, `body.id`)
- **Links Directos**: 
  - Las notificaciones incluyen links directos al ticket específico usando el ID
  - El link abre automáticamente el modal de detalle del ticket en el frontend
  - Configura `FRONTEND_URL` en n8n (Settings → Variables) con la URL de tu frontend desplegado
- **Telegram**: 
  - El workflow usa el nodo nativo de Telegram (mejor para grupos/canales)
  - Configura `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en n8n
  - Para grupos/canales, el `chat_id` será negativo (ej: `-1001234567890`)
  - **Canal público**: Los mensajes se envían al canal público configurado en `TELEGRAM_CHAT_ID`
  - Ver [QUICKSTART.md](./QUICKSTART.md) para instrucciones detalladas paso a paso

## 🐳 Docker Compose (Recomendado)

```bash
docker compose up --build
```

- Frontend: http://localhost:5200
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## 🔧 Desarrollo Local (sin Docker)

Ver [QUICKSTART.md](./QUICKSTART.md) para instrucciones detalladas.

## 📊 Seed de Datos

**Opción 1: SQL directo**
En Supabase SQL Editor, ejecuta `supabase/seed.sql`

**Opción 2: Vía API** (requiere API corriendo)
```bash
chmod +x seed-api.sh
./seed-api.sh
```

## Deploy (resumen)
- **API Python**: Render / Railway / Vercel (FastAPI)
- **Frontend**: Vercel / Netlify
- **n8n**: instancia local o cloud (importar workflow)

👉 **Ver [DEPLOY.md](./DEPLOY.md) para guía completa paso a paso con troubleshooting**

## Deploy paso a paso (resumen)

### API (Render)

1. **Crear Web Service en Render**:
   - Ve a https://render.com/dashboard
   - Click en **"New"** → **"Web Service"**
   - Conecta tu repositorio de GitHub

2. **Configuración del servicio**:
   - **Name**: `tu-api-name` (o el nombre que prefieras)
   - **Region**: Elige la región más cercana
   - **Branch**: `main` (o la rama que uses)
   - **Root Directory**: `python-api` ⚠️ **IMPORTANTE**
   - **Runtime**: `Docker` (o `Python 3` si prefieres)
   - **Instance Type**: `Free` (para empezar) o `Starter` ($7/mes)

3. **Build & Deploy** (si usas Docker):
   - **Dockerfile Path**: `./Dockerfile` (ya está en `python-api/`)
   - Render detectará automáticamente el Dockerfile

4. **Start Command** (si NO usas Docker):
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   ⚠️ Render inyecta `$PORT` automáticamente, no uses `8001` fijo

5. **Variables de entorno en Render**:
   Ve a **Environment** y agrega todas estas variables:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   HF_API_TOKEN=your-hf-api-token
   HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
   LLM_API_BASE_URL=https://router.huggingface.co/v1/chat/completions
   LLM_TEMPERATURE=0.1
   LLM_MAX_TOKENS=200
   LLM_CONFIDENCE_THRESHOLD=0.6
   N8N_WEBHOOK_URL=https://tu-workspace.n8n.cloud/webhook/support-copilot-webhook
   ```
   ⚠️ **NO agregues** `PORT` - Render lo inyecta automáticamente

6. **Health Check** (opcional pero recomendado):
   - **Health Check Path**: `/health`

7. **Deploy**: Click en **"Create Web Service"** y espera el deploy

8. **Verificar**: Una vez desplegado, ve a `https://tu-api.onrender.com/docs` para ver la documentación

### Frontend (Vercel)

1. **Importar proyecto**:
   - Ve a https://vercel.com/dashboard
   - Click en **"Add New"** → **"Project"**
   - Importa tu repositorio de GitHub

2. **Configuración**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend` ⚠️ **IMPORTANTE**
   - **Build Command**: `npm run build` (automático con Vite)
   - **Output Directory**: `dist` (automático con Vite)

3. **Variables de entorno en Vercel**:
   ```
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   VITE_API_URL=https://tu-api.onrender.com
   ```
   ⚠️ **IMPORTANTE**: `VITE_API_URL` debe apuntar a tu API de Render

4. **Deploy**: Click en **"Deploy"** y espera

5. **Verificar**: Una vez desplegado, abre la URL de Vercel y prueba crear un ticket

### n8n
1) Importa `n8n-workflow/workflow.json` en n8n Cloud.
2) Configura el nodo **Email** con tus credenciales SMTP (Gmail recomendado).
3) (Opcional) Configura el nodo **Telegram** con tu bot token y chat_id (soporta grupos/canales).
4) Activa el workflow y copia la **URL del webhook** (Production URL).
5) Agrega `N8N_WEBHOOK_URL` en las variables de entorno de la API en Render.
6) **Listo**: Ahora cuando crees un ticket con sentimiento negativo desde el frontend, recibirás:
   - Un email automáticamente
   - Un mensaje en Telegram (si está configurado)
   
**Nota**: Solo se envían notificaciones cuando el sentimiento es **"Negativo"**. Los tickets positivos o neutrales no activan el workflow.

## Variables de entorno
- API: `python-api/ENV_EXAMPLE.md`
- Frontend: `frontend/ENV_EXAMPLE.md`

## 🔍 Monitoreo y Diagnóstico

### Verificar estado del LLM

El endpoint `/diagnostics` te permite verificar si el LLM está funcionando correctamente:

```bash
curl https://tu-api.onrender.com/diagnostics
```

Respuesta ejemplo:
```json
{
  "llm": {
    "status": "working",
    "message": "LLM responded successfully",
    "available": true
  },
  "config": {
    "hf_model": "mistralai/Ministral-3-3B-Instruct-2512",
    "hf_token_configured": true,
    "confidence_threshold": 0.5
  }
}
```

### Ver logs en Render

1. Ve a tu servicio en Render Dashboard
2. Click en **"Logs"** (pestaña superior)
3. Busca mensajes con prefijos:
   - `LLM:` - Estado del modelo de lenguaje
   - `Classification:` - Proceso de clasificación
   - `n8n:` - Notificaciones a n8n

**Ejemplos de logs importantes:**
- `LLM: Client initialized successfully` - LLM configurado correctamente
- `LLM: Classification attempt X failed` - El LLM falló, usando reglas
- `LLM: Low confidence detected` - El LLM respondió pero con baja confianza
- `Classification: Using rules fallback` - Se está usando clasificación por reglas

### Troubleshooting

**Si el LLM no funciona:**
1. Verifica `/diagnostics` - Si `llm.available` es `false`, revisa `HF_API_TOKEN`
2. Revisa logs en Render - Busca errores específicos
3. El sistema automáticamente usa reglas si el LLM falla (no se rompe)
