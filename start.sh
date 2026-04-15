#!/bin/bash

echo "🚀 Iniciando AI Support Co-Pilot..."

# Verificar que existan los archivos .env
if [ ! -f "python-api/.env" ]; then
    echo "⚠️  No existe python-api/.env"
    echo "📝 Ejecutando setup-env.sh para crear archivos .env..."
    ./setup-env.sh
    echo ""
    echo "✏️  Por favor edita python-api/.env con tus credenciales reales:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_SERVICE_ROLE_KEY"
    echo "   - HF_API_TOKEN"
    echo "   - HF_MODEL (por defecto: meta-llama/Llama-3.1-8B-Instruct)"
    exit 1
fi

if [ ! -f "frontend/.env" ]; then
    echo "⚠️  No existe frontend/.env"
    echo "📝 Ejecutando setup-env.sh para crear archivos .env..."
    ./setup-env.sh
    echo ""
    echo "✏️  Por favor edita frontend/.env con tus credenciales reales:"
    echo "   - VITE_SUPABASE_URL"
    echo "   - VITE_SUPABASE_ANON_KEY"
    exit 1
fi

echo "✅ Archivos .env encontrados"
echo "🐳 Iniciando con Docker Compose..."
echo ""
echo "📍 URLs una vez iniciado:"
echo "   - Frontend: http://localhost:5200"
echo "   - API: http://localhost:8001"
echo "   - API Docs: http://localhost:8001/docs"
echo ""
docker compose up --build
