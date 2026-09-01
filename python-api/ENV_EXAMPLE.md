# Variables de entorno

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
PORT=8001
```

- **SUPABASE_JWT_SECRET**: JWT Secret para verificar tokens. **NO** uses la anon key ni la service_role key. En Supabase: Project Settings → API → despliega "JWT Settings" → copia el valor de "JWT Secret" (es una cadena larga tipo hex/base64). Si usas un valor incorrecto (ej. "sb_publishable_..."), la API devolverá 401.
- **SKIP_AUTH** (opcional): Si lo defines como `1` o `true`, la API no requerirá token (solo para desarrollo local).

---

## Componente inteligente (Semestre 2 · Sprint 5)

```
LLM_ENABLED=1
LLM_BASE_URL=https://router.huggingface.co/v1
LLM_API_KEY=hf_xxxxxxxxxxxxxxxxx
LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
LLM_TIMEOUT=20
LLM_MAX_REINTENTOS=2
LLM_TEMPERATURA=0
LLM_MAX_TOKENS=300
```

- **LLM_ENABLED**: apagado por defecto. Sin esta variable la API se comporta exactamente como el Semestre 1 (solo motor de reglas) y no intenta salir a la red. Es lo que permite desplegar el codigo del Sprint 5 sin activar la IA todavia.
- **LLM_BASE_URL**: cualquier endpoint que hable el dialecto OpenAI de `/chat/completions`. Probado contra Hugging Face Router; sirve igual para vLLM (`http://localhost:8000/v1`) u Ollama (`http://localhost:11434/v1`).
- **LLM_TEMPERATURA**: dejar en `0`. La clasificacion debe ser reproducible: si el mismo ticket cambia de categoria entre corridas, la matriz de confusion del Sprint 6 deja de significar algo.
- **LLM_TIMEOUT**: segundos. Al agotarse, la API cae al motor de reglas y el ticket se crea igual.
