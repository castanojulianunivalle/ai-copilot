# Variables de entorno (frontend)

## Local (desarrollo)
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8001
```

## Nube (Render, Sprint 6 · HU-10)
```
VITE_SUPABASE_URL=https://<ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<llave anon del proyecto de la nube>
VITE_API_URL=https://aiscop-api.onrender.com
NODE_VERSION=20
```

**Notas**
- Vite incrusta las variables `VITE_*` en el bundle al construir. Por eso cambiarlas en Render exige un nuevo deploy del sitio, y por eso nunca debe ir aquí una llave secreta: la anon es pública por diseño y la protegen las políticas RLS de Supabase.
- `VITE_API_URL` es opcional en local (por defecto `http://localhost:8001`). En la nube es obligatoria.
- El pie de la aplicación muestra la versión del frontend (de `package.json`) y el commit con que se construyó (`RENDER_GIT_COMMIT`), junto con la versión y el commit que reporta la API en `/health`.
- El procedimiento completo del despliegue está en `DEPLOY.md`.
