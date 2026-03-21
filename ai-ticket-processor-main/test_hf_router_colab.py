"""
Script para probar Hugging Face Router en Google Colab
Usa el endpoint de Router directamente (más confiable que InferenceClient)
"""

import requests
import json

# ===== CONFIGURACIÓN =====
HF_TOKEN = "TU_TOKEN_AQUI"  # Reemplaza con tu token de HF
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"  # Modelo chat-compatible

# ===== ENDPOINT =====
ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ===== PROMPT DE PRUEBA =====
prompt = """Eres un clasificador de tickets de soporte. Analiza el texto y devuelve un JSON válido con exactamente dos claves: "category" y "sentiment".

Categorías disponibles (elige UNA):
- Técnico: errores, bugs, fallos técnicos, problemas de funcionamiento
- Facturación: pagos, cobros, facturas, suscripciones, reembolsos
- Comercial: precios, planes, cotizaciones, ventas
- Acceso: login, contraseñas, autenticación, bloqueos, 2FA
- Cuenta: perfil, registro, modificación de datos, baja de cuenta
- Rendimiento: lentitud, latencia, demoras, problemas de velocidad
- UX/UI: diseño, interfaz, botones, navegación, usabilidad
- Seguridad: phishing, fraudes, vulnerabilidades, seguridad
- Integraciones: APIs, webhooks, conexiones con otros servicios
- Móvil: problemas en Android, iOS, aplicaciones móviles
- Solicitudes: peticiones de nuevas funcionalidades, mejoras

Sentimientos (elige UNO):
- Positivo: agradecimientos, elogios, satisfacción
- Neutral: consultas, preguntas, información
- Negativo: quejas, problemas, frustración, errores

Responde SOLO con JSON válido. Ejemplo de formato:
{"category": "Técnico", "sentiment": "Negativo"}

Ticket a clasificar: la app no sirve rey"""

payload = {
    "model": MODEL_ID,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1,
    "max_tokens": 200
}

# ===== HACER REQUEST =====
print(f"🔍 Probando modelo: {MODEL_ID}")
print(f"📡 Endpoint: {ROUTER_URL}\n")

try:
    response = requests.post(
        ROUTER_URL,
        json=payload,
        headers=headers,
        timeout=30
    )
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"✅ Respuesta recibida:\n{content}\n")
        
        # Intentar parsear JSON
        try:
            import re
            json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                print(f"✅ JSON parseado correctamente:")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except:
            print("⚠️ No se pudo parsear JSON, pero la respuesta llegó")
            
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        # Si es 400, mostrar detalles del error
        if response.status_code == 400:
            try:
                error_data = response.json()
                print(f"\n🔍 Detalles del error:")
                print(json.dumps(error_data, indent=2))
            except:
                pass
                
except requests.exceptions.RequestException as e:
    print(f"❌ Error de conexión: {e}")

# ===== LISTA DE MODELOS ALTERNATIVOS =====
print("\n" + "="*60)
print("📋 MODELOS ALTERNATIVOS PARA PROBAR:")
print("="*60)
alternative_models = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "google/gemma-2-9b-it",
    "microsoft/Phi-3-mini-4k-instruct",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "Qwen/Qwen2.5-7B-Instruct",
]

for i, model in enumerate(alternative_models, 1):
    print(f"{i}. {model}")

print("\n💡 Para cambiar de modelo, modifica la variable MODEL_ID arriba")
