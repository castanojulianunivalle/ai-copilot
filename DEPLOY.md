# Despliegue en la nube

> Sprint 6 · HU-10 (AISCOP-52). Versión desplegada: **v2.0.0**, tag de `main`.

## Qué corre y dónde

| Pieza | Proveedor | Servicio | URL |
|---|---|---|---|
| Frontend: React + Vite, sitio estático | Render · Static Site | `aiscop-web` | https://aiscop-web.onrender.com |
| API FastAPI en Docker, con el componente inteligente | Render · Web Service, plan gratuito, Virginia | `aiscop-api` | https://aiscop-api.onrender.com |
| Base de datos y autenticación | Supabase, plan gratuito, us-east-1 | `aiscop-demo` | https://vdiepebgqiaobtvzsbue.supabase.co |
| Modelo de lenguaje | Groq · `openai/gpt-oss-20b`, temperatura 0 | — | https://api.groq.com/openai/v1 |

La API, la base y el modelo quedan en la costa este de Estados Unidos, para no sumar latencia entre ellos.

## Cómo comprobar qué versión corre

- `GET https://aiscop-api.onrender.com/health` devuelve `version`, `commit` y el estado del LLM.
- El pie de la aplicación muestra la versión y el commit del frontend y de la API.
- `python deploy/pruebas_nube.py --ref v2.0.0` falla si la nube no corre el commit de ese tag.

## Secretos

Ningún secreto vive en el repositorio:

| Dónde | Qué |
|---|---|
| Variables secretas de Render | `SUPABASE_SERVICE_ROLE_KEY`, `LLM_API_KEY` |
| Secretos de GitHub | `DEMO_CLIENTE_PASSWORD`, `DEMO_AGENTE_PASSWORD`, para el workflow «Nube» |
| Solo el entorno de quien despliega | `RENDER_API_KEY`, `SUPABASE_ACCESS_TOKEN` |

Son públicos por diseño: las URL y la llave anon de Supabase, que viaja en el frontend. Los datos los protege RLS, y el rol anónimo no tiene permisos sobre las tablas (migración `20261017000000_endurecer_para_la_nube.sql`).

## Procedimiento desde cero

```bash
export SUPABASE_ACCESS_TOKEN=...          # token personal de Supabase
export RENDER_API_KEY=...                 # llave de la API de Render
python deploy/supabase_nube.py crear      # proyecto aiscop-demo en us-east-1
python deploy/supabase_nube.py migrar     # las cuatro migraciones, registradas
python deploy/render_nube.py aplicar      # crea aiscop-api y aiscop-web y fija sus variables
python deploy/supabase_nube.py auth --sitio https://aiscop-web.onrender.com
DEMO_CLIENTE_PASSWORD=... DEMO_AGENTE_PASSWORD=... python deploy/supabase_nube.py usuarios
```

Release y despliegue de una versión:

1. PR de `develop` a `main`, tag `vX.Y.Z` sobre el merge y release de GitHub.
2. `python deploy/render_nube.py desplegar --ref vX.Y.Z` despliega el commit del tag en los dos servicios, espera a que queden vivos y comprueba que `/health` reporta ese commit.
3. `python deploy/pruebas_nube.py --ref vX.Y.Z` corre las pruebas de humo y la aceptación. `python deploy/evaluar_nube.py` repite el examen de HU-09 contra la nube.

Los servicios tienen `autoDeploy` desactivado: un push a `main` no cambia lo que corre. Solo se despliegan tags.

## Volver a la versión anterior

`python deploy/render_nube.py desplegar --ref <tag anterior>` vuelve a desplegar ese commit y verifica `/health`. También se puede desde el panel de Render (Deploys → Rollback). Las migraciones son aditivas, así que una versión anterior de la API funciona sobre la base actual.

## Vigilancia

El workflow **Nube** de GitHub Actions (`.github/workflows/nube.yml`):
- corre las pruebas de humo todos los días a las 8:00 de Colombia, y bajo demanda;
- deja el reporte como artefacto;
- mantiene activo el proyecto gratuito de Supabase.

## Límites del plan gratuito

| Límite | Efecto | Qué se hace |
|---|---|---|
| Render apaga el servicio gratuito tras 15 minutos sin tráfico | La primera petición tarda cerca de un minuto | Abrir `/health` antes de una demostración |
| Supabase pausa el proyecto gratuito tras 7 días sin actividad | La aplicación deja de responder | El humo diario lo mantiene activo |
| Groq limita las peticiones por minuto y por día | Un 429 o un timeout | La API se repliega al motor de reglas y el ticket se crea igual |
| El SMTP de Supabase solo entrega a los miembros del equipo | No llegan los correos de confirmación ni de recuperación | En la demo la cuenta queda confirmada al registrarse; el SMTP propio está en el Product Backlog |
