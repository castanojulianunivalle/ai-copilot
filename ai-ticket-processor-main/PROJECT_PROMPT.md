# Prompt: Documentación del Proyecto - Mesa de Ayuda (Semestre 1)

> Este documento funciona como prompt reutilizable para explicar el proyecto a desarrolladores o IA. Copia y pega el bloque de prompt según necesites.

---

## Bloque de Prompt (Copy-Paste)

```
Describe el proyecto **Mesa de Ayuda - Support Co-Pilot** (Semestre 1) como un sistema de gestión 
de tickets de soporte técnico **sin IA**, con las siguientes características:

## Visión General
Sistema full-stack que permite a usuarios crear tickets con título y descripción, clasificarlos 
automáticamente por reglas (palabras clave), persistirlos en Supabase y gestionarlos en un dashboard 
React. El agente puede actualizar el estado (Abierto/Cerrado) de los tickets.

## Arquitectura
- **Frontend**: React 18 + Vite + Tailwind CSS + Framer Motion + Lucide React. Dashboard con tema claro/oscuro, búsqueda, paginación, modales, edición y eliminación de tickets.
- **Backend**: FastAPI (Python) con Pydantic. API REST para CRUD y clasificación por reglas.
- **Base de datos**: Supabase (PostgreSQL) con RLS.
- **Clasificación**: Motor de reglas (Python if/else) basado en palabras clave. Línea base para comparación en Semestre 3.

## Flujo de Datos
1. Usuario crea ticket (título + descripción) → POST /create-ticket a la API.
2. API clasifica con classify_with_rules(text) según palabras clave.
3. API inserta en Supabase: titulo, description, category, estado="Abierto".
4. Frontend muestra tickets; agente puede cambiar estado vía PATCH /tickets/{id}/estado.

## Modelo de Datos (Supabase)
Tabla tickets: id (uuid), created_at, titulo (text), description (text), category (text), estado (Abierto|Cerrado).
Categorías: Técnico, Facturación, Comercial, Acceso, Cuenta, Rendimiento, UX/UI, Seguridad, Integraciones, Móvil, Solicitudes.

## Endpoints API
- GET /health: health check
- POST /create-ticket: crear ticket (titulo, description) y clasificar
- PUT /tickets/{id}: editar ticket y re-clasificar
- PATCH /tickets/{id}/estado?estado=Abierto|Cerrado: cambiar estado (HU-03)
- DELETE /tickets/{id}: eliminar ticket

## Estructura de Carpetas
- python-api/: main.py (clasificación por reglas), requirements.txt, Dockerfile
- frontend/: src/App.tsx (UI principal), lib/supabase.ts, components/
- supabase/: setup.sql (esquema + RLS), seed.sql
- docker-compose.yml, start.sh, setup-env.sh, seed-api.sh

## Variables de Entorno Principales
API: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, PORT.
Frontend: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_URL.

## Ejecución
- Docker: docker compose up --build → Frontend :5200, API :8001
- Local: uvicorn main:app --port 8001 (API); npm run dev (frontend)
```

---

## Referencia Rápida para Desarrolladores

| Componente | Ubicación | Rol |
|------------|-----------|-----|
| API principal | `python-api/main.py` | CRUD, clasificación por reglas |
| UI principal | `frontend/src/App.tsx` | Dashboard, CRUD, tema, toggle estado |
| Esquema BD | `supabase/setup.sql` | Tabla tickets, RLS |
| Docker | `docker-compose.yml` | Orquestación local |
| Motor de reglas | `main.py` → classify_with_rules | Clasificación por palabras clave (HU-04) |

---

## Documentación Adicional del Proyecto

- **README.md**: Resumen, características, despliegue Semestre 1.
- **Plan.MD**: Plan maestro completo (Semestres 1, 2 y 3).
- **QUICKSTART.md**: Configuración paso a paso.
- **DEPLOY.md**: Despliegue en Render + Vercel.
- **python-api/ENV_EXAMPLE.md**: Variables de la API.
