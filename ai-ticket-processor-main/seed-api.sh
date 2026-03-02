#!/bin/bash

# Script para insertar tickets de prueba vía API
# Requiere que la API esté corriendo en http://localhost:8001

API_URL="${API_URL:-http://localhost:8001}"

echo "🌱 Insertando tickets de prueba..."

# Ticket 1: Técnico - Negativo
curl -X POST "$API_URL/create-ticket" \
  -H "Content-Type: application/json" \
  -d '{"description": "No puedo acceder a mi cuenta desde el móvil"}'

echo ""

# Ticket 2: Facturación - Neutral
curl -X POST "$API_URL/create-ticket" \
  -H "Content-Type: application/json" \
  -d '{"description": "Necesito factura de este mes"}'

echo ""

# Ticket 3: Comercial - Positivo
curl -X POST "$API_URL/create-ticket" \
  -H "Content-Type: application/json" \
  -d '{"description": "¿Tienen descuentos para empresas? Me encanta el servicio"}'

echo ""
echo "✅ Tickets de prueba insertados"
