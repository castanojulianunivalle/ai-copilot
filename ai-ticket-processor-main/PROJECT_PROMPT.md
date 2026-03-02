# Prompt: Documentación del Proyecto AI Support Co-Pilot

> Este documento funciona como prompt reutilizable para explicar el proyecto a desarrolladores o IA. Copia y pega el bloque de prompt según necesites.

---

## Bloque de Prompt (Copy-Paste)

```
Describe el proyecto **AI Support Co-Pilot** (AI-Ticket-Processor) como un sistema de procesamiento 
automático de tickets de soporte técnico con las siguientes características:

## Visión General
Sistema full-stack que permite a usuarios crear tickets de soporte, clasificarlos automáticamente 
con IA (LLM), persistirlos en Supabase, visualizarlos en tiempo real en un dashboard React, y 
disparar notificaciones por email/Telegram cuando el sentimiento es negativo.

## Arquitectura
- **Frontend**: React 18 + Vite + Tailwind CSS + Framer Motion + Lucide React. Dashboard SPA con tema claro/oscuro, animaciones, búsqueda, paginación, modales de detalle, edición y eliminación de tickets.
- **Backend**: FastAPI (Python) con Pydantic. API REST que orquesta clasificación, persistencia y notificaciones.
- **Base de datos**: Supabase (PostgreSQL) con Realtime para actualizaciones en vivo.
- **IA**: Cliente HTTP compatible con API OpenAI (Hugging Face Router o vLLM). Modelo por defecto: meta-llama/Llama-3.1-8B-Instruct.
- **Automatización**: n8n (workflow vía webhook) para enviar emails y mensajes de Telegram cuando el sentimiento es "Negativo".

## Flujo de Datos
1. Usuario crea ticket en el frontend → POST /create-ticket a la API.
2. API inserta ticket en Supabase con processed=false.
3. classify_ticket(description): si LLM disponible → invoca modelo; si no → classify_with_rules() (palabras clave).
4. Normaliza y valida salida (categoría, sentimiento).
5. Actualiza Supabase (category, sentiment, processed=true).
6. Si sentimiento = "Negativo" → POST webhook n8n → n8n envía email + Telegram.
7. Supabase Realtime notifica cambios → frontend actualiza UI en vivo.

## Modelo de Datos (Supabase)
Tabla tickets: id (uuid), created_at, description (text), category (text), sentiment (text), processed (boolean).
Categorías: Técnico, Facturación, Comercial, Acceso, Cuenta, Rendimiento, UX/UI, Seguridad, Integraciones, Móvil, Solicitudes.
Sentimientos: Positivo, Neutral, Negativo.

## Endpoints API
- GET /health: health check
- GET /diagnostics: estado del LLM y configuración
- POST /create-ticket: crear ticket y clasificar
- POST /process-ticket: clasificar ticket (opcional: actualizar por ticket_id)
- PUT /tickets/{id}: editar y re-evaluar con IA
- DELETE /tickets/{id}: eliminar ticket

## Estructura de Carpetas
- python-api/: main.py (lógica), requirements.txt, Dockerfile
- frontend/: src/App.tsx (UI principal), lib/supabase.ts, components/
- supabase/: setup.sql (esquema + Realtime + RLS), seed.sql
- n8n-workflow/: workflow.json (flujo email + Telegram)
- docker-compose.yml, start.sh, setup-env.sh, seed-api.sh

## Variables de Entorno Principales
API: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, HF_API_TOKEN, HF_MODEL, LLM_API_BASE_URL, N8N_WEBHOOK_URL.
Frontend: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_URL.

## Ejecución
- Docker: docker compose up --build → Frontend :5200, API :8001
- Local: uvicorn main:app --port 8001 (API); npm run dev (frontend)
```

---

## Referencia Rápida para Desarrolladores

| Componente | Ubicación | Rol |
|------------|-----------|-----|
| API principal | `python-api/main.py` | Clasificación, Supabase, webhook n8n |
| UI principal | `frontend/src/App.tsx` | Dashboard, CRUD, Realtime, tema |
| Esquema BD | `supabase/setup.sql` | Tabla tickets, Realtime, RLS |
| Workflow n8n | `n8n-workflow/workflow.json` | Notificaciones Email + Telegram |
| Docker | `docker-compose.yml` | Orquestación local |
| Cliente LLM | `main.py` → OpenAICompatibleAPI | HF Router / vLLM |
| Clasificación fallback | `main.py` → classify_with_rules | Reglas por palabras clave |

---

## Documentación Adicional del Proyecto

- **README.md**: Resumen, características, despliegue.
- **QUICKSTART.md**: Configuración paso a paso, Supabase, .env, n8n, Gmail, Telegram.
- **DEPLOY.md**: Despliegue en Render + Vercel, troubleshooting.
- **TESTING.md**: Pruebas manuales, curl, Realtime, n8n.
- **python-api/ENV_EXAMPLE.md**: Variables de la API.
- **frontend/ENV_EXAMPLE.md**: Variables del frontend.
