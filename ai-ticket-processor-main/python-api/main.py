import json
import logging
import os
import re
import time
from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from urllib.parse import urlparse

class OpenAICompatibleAPI:
    """Wrapper para endpoints OpenAI-compatible (HF Router o vLLM)."""
    def __init__(self, model: str, base_url: str, token: Optional[str] = None):
        self.model = model
        self.token = token
        self.api_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _build_chat_payload(self, prompt: str) -> dict:
        return {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "200"))
        }

    def _build_completion_payload(self, prompt: str) -> dict:
        return {
            "model": self.model,
            "prompt": prompt,
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "200"))
        }

    def _extract_text(self, result: dict) -> Optional[str]:
        if not isinstance(result, dict):
            return None
        choices = result.get("choices", [])
        if not choices or not isinstance(choices[0], dict):
            return None
        message = choices[0].get("message", {})
        if isinstance(message, dict) and "content" in message:
            return message["content"]
        if "text" in choices[0]:
            return choices[0]["text"]
        return None

    def invoke(self, prompt: str) -> str:
        """Invoca el modelo y retorna la respuesta."""
        is_chat_endpoint = self.api_url.rstrip("/").endswith("/v1/chat/completions")
        payload = self._build_chat_payload(prompt) if is_chat_endpoint else self._build_completion_payload(prompt)

        response = requests.post(
            self.api_url,
            json=payload,
            headers=self.headers,
            timeout=30
        )
        
        if response.status_code == 400:
            try:
                error_body = response.json()
                error_info = error_body.get("error", {})
                error_code = error_info.get("code")
                error_message = str(error_info.get("message", "")).lower()
                if error_code == "model_not_supported" and "not a chat model" in error_message:
                    raise ValueError(
                        f"Model '{self.model}' is not chat-compatible with Hugging Face Router. "
                        f"Use a chat-compatible model or host locally with vLLM. "
                        f"See QUICKSTART.md for vLLM setup instructions."
                    )
            except ValueError as e:
                if "not a chat model" in str(e).lower():
                    raise
            except (KeyError, AttributeError):
                pass
        
        if response.status_code >= 400:
            logger.error(
                "LLM: HTTP %s from %s - %s",
                response.status_code,
                self.api_url,
                response.text[:500],
            )
        response.raise_for_status()

        result = response.json()
        extracted = self._extract_text(result)
        if extracted is not None:
            return extracted

        logger.warning(f"LLM: Unexpected response format: {result}")
        return str(result)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="AI Support Co-Pilot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TicketIn(BaseModel):
    ticket_id: Optional[str] = None
    description: str


class TicketOut(BaseModel):
    category: str
    sentiment: str
    processed: bool


def get_supabase() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def llm_client() -> Optional[OpenAICompatibleAPI]:
    token = os.getenv("HF_API_TOKEN") or os.getenv("LLM_API_TOKEN")
    model = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    base_url = os.getenv("LLM_API_BASE_URL", "https://router.huggingface.co/v1/chat/completions")
    requires_token = "huggingface.co" in urlparse(base_url).netloc
    if requires_token and not token:
        logger.warning("LLM: Token not configured for Hugging Face Router, using rules fallback")
        return None
    try:
        client = OpenAICompatibleAPI(model=model, base_url=base_url, token=token)
        logger.info(f"LLM: Client initialized successfully with model {model} at {base_url}")
        return client
    except Exception as e:
        logger.error(f"LLM: Error creating client - {type(e).__name__}: {e}")
        return None


def test_llm_connection() -> dict:
    """Test if LLM is working correctly"""
    llm = llm_client()
    if not llm:
        return {
            "status": "not_configured",
            "message": "HF_API_TOKEN not set",
            "available": False
        }
    
    try:
        test_prompt = 'Respond with JSON: {"test": "ok"}'
        response = llm.invoke(test_prompt)
        return {
            "status": "working",
            "message": "LLM responded successfully",
            "available": True,
            "test_response_length": len(response) if response else 0,
            "test_response_preview": response[:100] if response else None
        }
    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        if "410" in error_msg or "Gone" in error_msg:
            return {
                "status": "error",
                "message": "Hugging Face API endpoint deprecated. Using new router API.",
                "available": False,
                "error": error_msg
            }
        return {
            "status": "error",
            "message": f"LLM test failed: HTTP {e.response.status_code if hasattr(e, 'response') else 'Unknown'}",
            "available": False,
            "error": error_msg
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"LLM test failed: {type(e).__name__}: {str(e)}",
            "available": False,
            "error": str(e)
        }


ALLOWED_CATEGORIES = {
    "Acceso",
    "Cuenta",
    "Comercial",
    "Facturación",
    "Integraciones",
    "Móvil",
    "Rendimiento",
    "Seguridad",
    "Solicitudes",
    "Técnico",
    "UX/UI",
}

ALLOWED_SENTIMENTS = {"Positivo", "Neutral", "Negativo"}


def _simplify_text(value: str) -> str:
    return re.sub(r"\s+", "", value.strip().lower()).translate(
        str.maketrans("áéíóúüñ", "aeiouun")
    )


def normalize_text(text: str) -> str:
    replacements = {
        r"\brey\b": "",
        r"\bbro\b": "",
        r"\bmalísimo\b": "muy malo",
        r"\bmalisimo\b": "muy malo",
        r"\bno sirve\b": "no funciona",
        r"\bapp\b": "aplicacion",
    }
    normalized = text.lower()
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalize_category(value: str) -> str:
    if not value:
        return ""
    simplified = _simplify_text(value)
    alias_map = {
        "tecnico": "Técnico",
        "facturacion": "Facturación",
        "comercial": "Comercial",
        "acceso": "Acceso",
        "cuenta": "Cuenta",
        "rendimiento": "Rendimiento",
        "performance": "Rendimiento",
        "ux": "UX/UI",
        "ui": "UX/UI",
        "uxui": "UX/UI",
        "usabilidad": "UX/UI",
        "seguridad": "Seguridad",
        "integraciones": "Integraciones",
        "integracion": "Integraciones",
        "movil": "Móvil",
        "mobile": "Móvil",
        "solicitudes": "Solicitudes",
        "feature": "Solicitudes",
        "request": "Solicitudes",
    }
    normalized = alias_map.get(simplified, value.strip())
    return normalized if normalized in ALLOWED_CATEGORIES else ""


def normalize_sentiment(value: str) -> str:
    if not value:
        return ""
    simplified = _simplify_text(value)
    alias_map = {
        "positivo": "Positivo",
        "positive": "Positivo",
        "neutral": "Neutral",
        "negativo": "Negativo",
        "negative": "Negativo",
    }
    normalized = alias_map.get(simplified, value.strip().capitalize())
    return normalized if normalized in ALLOWED_SENTIMENTS else ""


def classify_with_rules(text: str) -> dict:
    text_lower = text.lower()
    category = "Técnico"

    category_rules = [
        ("Facturación", ["factura", "billing", "cobro", "pago", "suscripción", "reembolso"]),
        ("Acceso", ["login", "inicio de sesión", "contraseña", "bloqueo", "2fa", "otp"]),
        ("Cuenta", ["perfil", "cuenta", "usuario", "registro", "alta", "baja"]),
        ("Integraciones", ["api", "webhook", "zapier", "slack", "integración", "integraciones"]),
        ("Rendimiento", ["lento", "latencia", "demora", "performance", "rendimiento"]),
        ("UX/UI", ["diseño", "ui", "ux", "interfaz", "botón", "boton", "pantalla"]),
        ("Seguridad", ["phishing", "fraude", "seguridad", "vulnerabilidad", "hack"]),
        ("Solicitudes", ["quiero", "me gustaría", "feature", "mejorar", "solicitud"]),
        ("Comercial", ["precio", "plan", "cotización", "ventas", "comercial"]),
        ("Móvil", ["android", "ios", "móvil", "movil", "celular"]),
        ("Técnico", ["error", "fallo", "bug", "no funciona", "no sirve", "crash"]),
    ]

    for name, keywords in category_rules:
        if any(k in text_lower for k in keywords):
            category = name
            break

    sentiment = "Neutral"
    if any(
        k in text_lower
        for k in [
            "no funciona",
            "no sirve",
            "no carga",
            "se cae",
            "error",
            "fallo",
            "mal",
            "terrible",
            "molesto",
            "horrible",
            "pésimo",
            "pesimo",
            "bug",
            "fatal",
        ]
    ):
        sentiment = "Negativo"
    if any(k in text_lower for k in ["gracias", "excelente", "genial", "perfecto", "bien", "buenísimo"]):
        sentiment = "Positivo"

    return {"category": category, "sentiment": sentiment}


def parse_json_from_text(text: str) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("Empty response")
    
    # Primero intentar parsear el texto completo (caso más común: JSON limpio)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Si no es JSON puro, buscar JSON dentro del texto
    json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    # Buscar JSON en bloques de código markdown
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    json_match = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    raise ValueError("No valid JSON found in response")


def classify_ticket(description: str) -> dict:
    normalized_text = normalize_text(description)
    llm = llm_client()
    if not llm:
        logger.info("Classification: Using rules fallback (LLM not available)")
        return classify_with_rules(normalized_text)

    max_retries = 2
    for attempt in range(max_retries):
        try:
            logger.info(f"Classification: Attempt {attempt + 1} with LLM for ticket: {description[:50]}...")
            prompt_text = f"""Eres un clasificador de tickets de soporte. Analiza el texto y devuelve un JSON válido con exactamente dos claves: "category" y "sentiment".

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
{{"category": "Técnico", "sentiment": "Negativo"}}

Ticket a clasificar: {normalized_text}"""
            
            start_time = time.time()
            try:
                response = llm.invoke(prompt_text)
            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 503:
                    logger.warning("LLM: Model is loading, will retry...")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                raise
            elapsed = time.time() - start_time
            
            logger.info(f"LLM: Response received in {elapsed:.2f}s, length: {len(response) if response else 0}")
            
            if not response or not response.strip():
                raise ValueError("Empty response from LLM")
            
            logger.debug(f"LLM: Raw response: {response[:200]}...")
            
            result = parse_json_from_text(response)
            
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")
            
            category = normalize_category(result.get("category", ""))
            sentiment = normalize_sentiment(result.get("sentiment", ""))
            
            if not category or not sentiment:
                raise ValueError(f"Missing category or sentiment - category: {category}, sentiment: {sentiment}")
            
            if category not in ALLOWED_CATEGORIES:
                raise ValueError(f"Invalid category: {category}")
            
            if sentiment not in ALLOWED_SENTIMENTS:
                raise ValueError(f"Invalid sentiment: {sentiment}")
            
            confidence = 1.0
            
            response_lower = response.lower()
            uncertainty_indicators = [
                "no estoy seguro", "no sé", "tal vez", "quizás", 
                "posiblemente", "probablemente", "?", "maybe"
            ]
            if any(indicator in response_lower for indicator in uncertainty_indicators):
                confidence = min(confidence, 0.4)
                logger.warning(f"LLM: Low confidence detected due to uncertainty indicators")
            
            if len(response) > 500:
                confidence = min(confidence, 0.5)
                logger.warning(f"LLM: Low confidence due to long response ({len(response)} chars)")
            
            threshold = float(os.getenv("LLM_CONFIDENCE_THRESHOLD", "0.5"))
            if confidence < threshold:
                logger.warning(f"LLM: Confidence {confidence} below threshold {threshold}, using rules fallback")
                return classify_with_rules(normalized_text)
            
            logger.info(f"LLM: Successfully classified - Category: {category}, Sentiment: {sentiment}")
            return {"category": category, "sentiment": sentiment}
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"LLM: Classification attempt {attempt + 1} failed - {error_type}: {error_msg}")
            if attempt < max_retries - 1:
                logger.info(f"LLM: Retrying in 0.5s...")
                time.sleep(0.5)
                continue
            logger.warning("LLM: All attempts failed, falling back to rules-based classification")
            return classify_with_rules(normalized_text)


def notify_n8n_if_negative(description: str, category: str, sentiment: str, ticket_id: Optional[str] = None):
    if sentiment.lower() != "negativo":
        return
    
    n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
    if not n8n_webhook_url:
        return
    
    try:
        payload = {
            "description": description,
            "category": category,
            "sentiment": sentiment,
        }
        if ticket_id:
            payload["id"] = ticket_id
        
        requests.post(
            n8n_webhook_url,
            json=payload,
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.warning(f"n8n: Failed to notify webhook - {type(e).__name__}: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/diagnostics")
def diagnostics():
    """Endpoint to check LLM status and configuration"""
    llm_status = test_llm_connection()
    
    return {
        "llm": llm_status,
        "config": {
            "hf_model": os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct"),
            "llm_base_url": os.getenv("LLM_API_BASE_URL", "https://router.huggingface.co/v1/chat/completions"),
            "hf_token_configured": bool(os.getenv("HF_API_TOKEN") or os.getenv("LLM_API_TOKEN")),
            "confidence_threshold": float(os.getenv("LLM_CONFIDENCE_THRESHOLD", "0.5")),
            "n8n_webhook_configured": bool(os.getenv("N8N_WEBHOOK_URL")),
            "supabase_configured": bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY")),
        },
        "timestamp": time.time()
    }


@app.post("/create-ticket", response_model=dict)
def create_ticket(ticket: TicketIn):
    if not ticket.description:
        raise HTTPException(status_code=400, detail="description is required")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    ticket_data = {
        "description": ticket.description,
        "processed": False,
    }
    result = supabase.table("tickets").insert(ticket_data).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=500, detail="Failed to create ticket")
    
    ticket_id = result.data[0]["id"]

    classification = classify_ticket(ticket.description)
    
    supabase.table("tickets").update(
        {
            "category": classification["category"],
            "sentiment": classification["sentiment"],
            "processed": True,
        }
    ).eq("id", ticket_id).execute()

    notify_n8n_if_negative(
        ticket.description,
        classification["category"],
        classification["sentiment"],
        ticket_id
    )

    return {
        "ticket_id": ticket_id,
        "category": classification["category"],
        "sentiment": classification["sentiment"],
        "processed": True,
    }


@app.post("/process-ticket", response_model=TicketOut)
def process_ticket(ticket: TicketIn):
    if not ticket.description:
        raise HTTPException(status_code=400, detail="description is required")

    result = classify_ticket(ticket.description)
    processed = True

    supabase = get_supabase()
    if ticket.ticket_id and supabase:
        supabase.table("tickets").update(
            {
                "category": result["category"],
                "sentiment": result["sentiment"],
                "processed": True,
            }
        ).eq("id", ticket.ticket_id).execute()

    notify_n8n_if_negative(
        ticket.description,
        result["category"],
        result["sentiment"],
        ticket.ticket_id
    )

    return TicketOut(
        category=result["category"],
        sentiment=result["sentiment"],
        processed=processed,
    )


@app.put("/tickets/{ticket_id}", response_model=dict)
def update_ticket(ticket_id: str, ticket: TicketIn):
    """Actualiza un ticket y lo re-evalúa con IA"""
    if not ticket.description:
        raise HTTPException(status_code=400, detail="description is required")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    # Verificar que el ticket existe
    existing = supabase.table("tickets").select("*").eq("id", ticket_id).execute()
    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Re-evaluar con IA
    classification = classify_ticket(ticket.description)

    # Actualizar en Supabase
    supabase.table("tickets").update(
        {
            "description": ticket.description,
            "category": classification["category"],
            "sentiment": classification["sentiment"],
            "processed": True,
        }
    ).eq("id", ticket_id).execute()

    # Notificar n8n si es negativo
    notify_n8n_if_negative(
        ticket.description,
        classification["category"],
        classification["sentiment"],
        ticket_id
    )

    return {
        "ticket_id": ticket_id,
        "category": classification["category"],
        "sentiment": classification["sentiment"],
        "processed": True,
        "message": "Ticket actualizado y re-evaluado"
    }


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: str):
    """Elimina un ticket"""
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    # Verificar que el ticket existe
    existing = supabase.table("tickets").select("*").eq("id", ticket_id).execute()
    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Eliminar
    supabase.table("tickets").delete().eq("id", ticket_id).execute()

    return {"message": "Ticket eliminado exitosamente", "ticket_id": ticket_id}
