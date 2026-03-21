# Variables de entorno (frontend)

## Local (desarrollo)
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8001
```

## Producción (Vercel/Netlify)
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=https://tu-api.onrender.com
```

**Nota**: 
- `VITE_API_URL` es opcional en local (por defecto usa `http://localhost:8001`)
- En producción, **debes** configurar `VITE_API_URL` con la URL de tu API desplegada en Render
