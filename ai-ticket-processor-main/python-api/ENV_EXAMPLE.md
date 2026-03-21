# Variables de entorno (ejemplo)

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
HF_API_TOKEN=your-hf-api-token
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
# Modelo por defecto: meta-llama/Llama-3.1-8B-Instruct (chat-compatible, funciona en Router)
# Modelos alternativos chat-compatibles en Router:
# - google/gemma-2-9b-it
# - microsoft/Phi-3-mini-4k-instruct
# - Qwen/Qwen2.5-7B-Instruct
# Para usar Ministral-3-3B-Instruct-2512 (requiere vLLM local):
# LLM_API_BASE_URL=http://localhost:8000/v1/chat/completions
# HF_MODEL=mistralai/Ministral-3-3B-Instruct-2512
LLM_API_BASE_URL=https://router.huggingface.co/v1/chat/completions
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=200
PORT=8001
N8N_WEBHOOK_URL=https://tu-workspace.n8n.cloud/webhook/support-copilot-webhook
LLM_CONFIDENCE_THRESHOLD=0.6
```

**Nota sobre N8N_WEBHOOK_URL**: 
- Es opcional. Si no está configurada, el sistema funcionará normalmente pero no enviará notificaciones por email.
- Obtén la URL del webhook desde tu workflow de n8n Cloud (nodo Webhook → Production URL).
