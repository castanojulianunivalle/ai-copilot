# AI Support Co-Pilot

Mesa de ayuda que clasifica los tickets de soporte con un modelo de lenguaje de pesos abiertos y demuestra, con una evaluación reproducible, que lo hace mejor que un motor de reglas por palabras clave.

Proyecto integrador de la Maestría en Computación para el Desarrollo de Aplicaciones Inteligentes (Universidad del Valle), desarrollado con Scrum: Jira (proyecto AISCOP) y este repositorio.

## Versión actual: v2.0.0

| | |
|---|---|
| Aplicación | https://aiscop-web.onrender.com |
| API | https://aiscop-api.onrender.com (`/health` dice qué versión y qué commit corren) |
| Despliegue | [DEPLOY.md](DEPLOY.md) |

## Qué hace

- **Cliente:** se registra, inicia sesión y crea tickets.
- **Al crear el ticket:** el modelo (gpt-oss-20b servido por Groq) deduce categoría, tono, prioridad y confianza.
  - Si el modelo no responde a tiempo, el motor de reglas asigna la categoría y el ticket se crea igual.
  - Con confianza de 0,5 o menos, el ticket queda marcado «Requiere revisión».
- **Agente:** ve la bandeja priorizada, revisa los marcados y cambia el estado.
- **Administrador:** gestiona los roles.

## Estructura

| Carpeta | Qué hay |
|---|---|
| `python-api/` | API FastAPI y el componente inteligente (`ai/`): taxonomía, prompts, cliente del LLM, parser y motor de reglas |
| `frontend/` | React 18 + TypeScript + Tailwind |
| `supabase/migrations/` | Esquema, RLS y vistas, en el orden en que se aplican |
| `evaluation/` | Evaluación de HU-09: partición congelada, métricas, McNemar exacta y umbral de revisión. Ver [evaluation/README.md](evaluation/README.md) |
| `deploy/` | Scripts del despliegue en Render y Supabase, y las pruebas contra la nube |
| `.github/workflows/` | CI en cada PR y pruebas diarias contra la nube |

## Cómo se trabaja

- **Ramas:**
  - cada historia tiene su rama `feature/AISCOP-<id>-...`;
  - cada subtarea, una rama propia con PR hacia la de su historia;
  - la historia llega a `develop` por PR;
  - una release es un PR de `develop` a `main` con su tag.
- **Commits:** cada mensaje empieza por la clave de Jira, así la trazabilidad queda en el tablero.
- **CI:** cada PR corre las pruebas de la API, las de la evaluación y el build del frontend.

## Correr en local

```bash
./setup-env.sh          # crea python-api/.env y frontend/.env desde los ejemplos
./start.sh              # o docker compose up
```

Variables: `python-api/ENV_EXAMPLE.md` y `frontend/ENV_EXAMPLE.md`.

## Pruebas

```bash
cd python-api && pip install -r requirements-dev.txt && pytest
pip install -r evaluation/requirements-dev.txt && pytest evaluation/tests
python deploy/pruebas_nube.py --solo-humo      # contra la nube; ver DEPLOY.md
```
