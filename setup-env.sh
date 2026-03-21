#!/bin/bash

# Script para crear archivos .env desde los ejemplos

echo "🔧 Configurando archivos .env..."

# Crear .env para API
if [ ! -f "python-api/.env" ]; then
    echo "📝 Creando python-api/.env desde ENV_EXAMPLE.md"
    cat > python-api/.env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
HF_API_TOKEN=your-hf-api-token
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
LLM_API_BASE_URL=https://router.huggingface.co/v1/chat/completions
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=200
LLM_CONFIDENCE_THRESHOLD=0.6
PORT=8001
N8N_WEBHOOK_URL=
EOF
    echo "✅ python-api/.env creado"
else
    echo "⚠️  python-api/.env ya existe, no se sobrescribe"
fi

# Crear .env para Frontend
if [ ! -f "frontend/.env" ]; then
    echo "📝 Creando frontend/.env desde ENV_EXAMPLE.md"
    cat > frontend/.env << 'EOF'
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
EOF
    echo "✅ frontend/.env creado"
else
    echo "⚠️  frontend/.env ya existe, no se sobrescribe"
fi

echo ""
echo "📋 Próximos pasos:"
echo "1. Edita python-api/.env con tus credenciales de Supabase"
echo "2. Edita frontend/.env con tus credenciales de Supabase"
echo "3. Ejecuta: docker compose up --build"
