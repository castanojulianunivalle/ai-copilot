"""
Mesa de Ayuda - Semestre 1
Backend FastAPI con clasificación por reglas (palabras clave).
HU-01: Auth con roles | HU-02/03/04: CRUD y clasificación.
"""
import logging
import os
import re
from typing import Optional, Tuple

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Mesa de Ayuda - Support Co-Pilot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_ESTADOS = {"Abierto", "Cerrado"}

class TicketIn(BaseModel):
    titulo: str
    description: str


class TicketUpdateIn(BaseModel):
    titulo: Optional[str] = None
    description: Optional[str] = None
    estado: Optional[str] = None


def get_supabase() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def classify_with_rules(text: str) -> str:
    """HU-04: Clasificación por palabras clave (motor de reglas)."""
    text_lower = (text or "").lower()
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
        ("Técnico", ["error", "fallo", "bug", "no funciona", "no sirve", "crash", "internet"]),
    ]

    for name, keywords in category_rules:
        if any(k in text_lower for k in keywords):
            category = name
            break

    logger.info(f"Classification: {category} (reglas)")
    return category


def _verify_token(authorization: Optional[str] = Header(None)) -> Tuple[str, str]:
    """Verifica JWT de Supabase y retorna (user_id, role)."""
    skip = os.getenv("SKIP_AUTH", "").lower() in ("1", "true")
    if skip:
        return ("dev-user", "cliente")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization Bearer requerido")

    token = authorization.replace("Bearer ", "").strip()
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="Auth no configurado (SUPABASE_JWT_SECRET)")

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    profile = supabase.table("profiles").select("role").eq("id", user_id).execute()
    role = "cliente"
    if profile.data and len(profile.data) > 0:
        role = profile.data[0].get("role", "cliente")
    return (user_id, role)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/create-ticket", response_model=dict)
def create_ticket(ticket: TicketIn, auth: Tuple[str, str] = Depends(_verify_token)):
    user_id, role = auth
    if role != "cliente":
        raise HTTPException(status_code=403, detail="Solo clientes pueden crear tickets")

    if not ticket.description or not ticket.titulo:
        raise HTTPException(status_code=400, detail="titulo y description son requeridos")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    category = classify_with_rules(ticket.titulo + " " + ticket.description)

    ticket_data = {
        "titulo": ticket.titulo,
        "description": ticket.description,
        "category": category,
        "estado": "Abierto",
        "created_by": user_id if user_id != "dev-user" else None,
    }
    result = supabase.table("tickets").insert(ticket_data).execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=500, detail="Error al crear ticket")

    ticket_id = result.data[0]["id"]
    return {
        "ticket_id": ticket_id,
        "category": category,
        "estado": "Abierto",
    }


@app.put("/tickets/{ticket_id}", response_model=dict)
def update_ticket(ticket_id: str, ticket: TicketUpdateIn, auth: Tuple[str, str] = Depends(_verify_token)):
    """Actualiza un ticket. Cliente solo sus tickets; agente puede cambiar estado en cualquiera."""
    user_id, role = auth
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    existing = supabase.table("tickets").select("*").eq("id", ticket_id).execute()
    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    created_by = existing.data[0].get("created_by")
    if role == "cliente" and (created_by and created_by != user_id):
        raise HTTPException(status_code=403, detail="Solo puedes editar tus propios tickets")
    if role == "agente" and ticket.estado is None and ticket.titulo is None and ticket.description is None:
        pass  # agente puede enviar solo estado vía PATCH

    update_data = {}
    if ticket.titulo is not None:
        update_data["titulo"] = ticket.titulo
    if ticket.description is not None:
        update_data["description"] = ticket.description
        update_data["category"] = classify_with_rules(ticket.description)
    if ticket.estado is not None:
        if ticket.estado not in ALLOWED_ESTADOS:
            raise HTTPException(status_code=400, detail="estado debe ser Abierto o Cerrado")
        update_data["estado"] = ticket.estado

    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    supabase.table("tickets").update(update_data).eq("id", ticket_id).execute()

    return {"message": "Ticket actualizado", "ticket_id": ticket_id}


@app.patch("/tickets/{ticket_id}/estado", response_model=dict)
def update_estado(ticket_id: str, estado: str, auth: Tuple[str, str] = Depends(_verify_token)):
    """Endpoint rápido para que el agente cambie el estado (Abierto/Cerrado)."""
    _, role = auth
    if role != "agente":
        raise HTTPException(status_code=403, detail="Solo agentes pueden cambiar el estado")
    if estado not in ALLOWED_ESTADOS:
        raise HTTPException(status_code=400, detail="estado debe ser Abierto o Cerrado")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    existing = supabase.table("tickets").select("*").eq("id", ticket_id).execute()
    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    supabase.table("tickets").update({"estado": estado}).eq("id", ticket_id).execute()
    return {"ticket_id": ticket_id, "estado": estado}


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: str, auth: Tuple[str, str] = Depends(_verify_token)):
    user_id, role = auth
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    existing = supabase.table("tickets").select("*").eq("id", ticket_id).execute()
    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    created_by = existing.data[0].get("created_by")
    if role == "cliente" and (created_by and created_by != user_id):
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propios tickets")

    supabase.table("tickets").delete().eq("id", ticket_id).execute()
    return {"message": "Ticket eliminado", "ticket_id": ticket_id}
