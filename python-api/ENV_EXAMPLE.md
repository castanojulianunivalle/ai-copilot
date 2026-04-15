# Variables de entorno (Semestre 1 - Con Auth)

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
PORT=8001
```

- **SUPABASE_JWT_SECRET**: JWT Secret para verificar tokens. **NO** uses la anon key ni la service_role key. En Supabase: Project Settings → API → despliega "JWT Settings" → copia el valor de "JWT Secret" (es una cadena larga tipo hex/base64). Si usas un valor incorrecto (ej. "sb_publishable_..."), la API devolverá 401.
- **SKIP_AUTH** (opcional): Si lo defines como `1` o `true`, la API no requerirá token (solo para desarrollo local).
