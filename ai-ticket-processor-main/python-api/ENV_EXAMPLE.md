# Variables de entorno (Semestre 1 - Con Auth)

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
PORT=8001
```

- **SUPABASE_JWT_SECRET**: JWT Secret de tu proyecto (Supabase Dashboard → Project Settings → API → JWT Secret). Requerido para verificar tokens de auth.
- **SKIP_AUTH** (opcional): Si lo defines como `1` o `true`, la API no requerirá token (solo para desarrollo local).
