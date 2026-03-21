# Mesa de Ayuda - Support Co-Pilot

Sistema de gestión de tickets de soporte con arquitectura evolutiva en tres semestres.

---

## Alcance Semestre I (Entrega actual)

Sistema **sin IA**: CRUD transaccional con clasificación por reglas (palabras clave) como línea base para comparación futura (Semestre 3).

### ✨ Características - Semestre I

| HU | Rol | Funcionalidad |
|----|-----|---------------|
| HU-01 | Usuario | Registro e inicio de sesión (Cliente, Agente, Administrador) |
| HU-02 | Cliente | Crear tickets con título y descripción |
| HU-03 | Agente | Ver todos los tickets y actualizar estado (Abierto/Cerrado) |
| HU-04 | Sistema | Clasificación por palabras clave (motor de reglas en Python) |

**Extras implementados:**
- **Panel Admin**: Gestión de usuarios (listar, cambiar roles) para rol Administrador.
- **Dashboard React**: Tema claro/oscuro, búsqueda, paginación, modales, edición y eliminación.
- **Accesibilidad**: Navegación por teclado, ARIA, alto contraste.
- **Animaciones**: Framer Motion, Lucide React, feedback visual.

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

- `supabase/`: esquema SQL (tickets, profiles, RLS) y seed
- `python-api/`: API FastAPI (CRUD, clasificación por reglas, auth JWT con JWKS)
- `frontend/`: dashboard React + Vite + Tailwind (tema, búsqueda, paginación, modales)
- `n8n-workflow/`: flujo de automatización (Semestre 2)
- `docker-compose.yml`, `start.sh`, `setup-env.sh`: orquestación local

## 📝 URLs de entrega

| Componente | URL |
|------------|-----|
| Dashboard (Frontend) | https://tu-app.vercel.app/ |
| API Python (Backend) | https://tu-api.onrender.com/docs |

Ver [docs/Entrega I/README.md](./docs/Entrega%20I/README.md) para la documentación académica completa.

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
- **Editar Tickets**: Botones de edición en cada card y en el modal de detalle, con re-clasificación por reglas.
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

## 🧠 Clasificación - Semestre I (Motor de Reglas)

- **Categorías**: Acceso, Cuenta, Facturación, Comercial, Técnico, Rendimiento, UX/UI, Seguridad, Integraciones, Móvil, Solicitudes.
- **Motor**: Palabras clave en `classify_with_rules()` (Python if/else). Línea base para comparación con LLM en Semestre 3.

---

## 📋 Roadmap (Semestres 2 y 3)

| Semestre | Funcionalidad planificada |
|----------|---------------------------|
| **Sem 2** | n8n (webhooks, Telegram/Email), Realtime, dashboard analítico |
| **Sem 3** | LLM (Llama-3.1) para clasificación y sentimiento, evaluación F1-Score |

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

5. **Variables de entorno en Render** (Semestre I — mínimo):
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```
   ⚠️ **NO agregues** `PORT` — Render lo inyecta automáticamente.

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

### n8n (Semestre 2)
1) Importa `n8n-workflow/workflow.json` en n8n Cloud.
2) Configura Email y/o Telegram. Activa el workflow y copia la URL del webhook.
3) Agrega `N8N_WEBHOOK_URL` en la API (Sem 2).

## Variables de entorno
- API: `python-api/ENV_EXAMPLE.md`
- Frontend: `frontend/ENV_EXAMPLE.md`

## 🔍 Monitoreo (Semestre I)

- **Health check**: `GET /health` — verifica que la API esté activa.
- **Logs en Render**: Revisa la pestaña Logs del servicio. La clasificación por reglas se registra con prefijo `Classification:`.
