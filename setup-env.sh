#!/bin/bash

# Script para crear archivos .env desde los ejemplos

echo "🔧 Configurando archivos .env..."

# Crear .env para API
if [ ! -f "python-api/.env" ]; then
    echo "📝 Creando python-api/.env desde ENV_EXAMPLE.md"
    cat > python-api/.env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
PORT=8001
N8N_WEBHOOK_URL=
# Clasificacion con LLM (HU-06). Sin LLM_ENABLED=1 la API clasifica solo con reglas.
LLM_ENABLED=1
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your-groq-api-key
LLM_MODEL=openai/gpt-oss-20b
LLM_TIMEOUT=20
LLM_MAX_REINTENTOS=2
LLM_TEMPERATURA=0
LLM_MAX_TOKENS=1500
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
