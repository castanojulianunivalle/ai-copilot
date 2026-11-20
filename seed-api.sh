#!/bin/bash

# Script para insertar tickets de prueba vía API
# Requiere que la API esté corriendo en http://localhost:8001

API_URL="${API_URL:-http://localhost:8001}"

echo "🌱 Insertando tickets de prueba..."

# Ticket 1: Acceso
curl -X POST "$API_URL/create-ticket" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Error de acceso móvil", "description": "No puedo acceder a mi cuenta desde el móvil"}'

echo ""

# Ticket 2: Facturación
curl -X POST "$API_URL/create-ticket" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Solicitud de factura", "description": "Necesito factura de este mes"}'

echo ""

# Ticket 3: Comercial
curl -X POST "$API_URL/create-ticket" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Consulta comercial", "description": "¿Tienen descuentos para empresas?"}'

echo ""
echo "✅ Tickets de prueba insertados"
