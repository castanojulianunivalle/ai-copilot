"""
Mesa de Ayuda - Semestre 1
Backend FastAPI con clasificación por reglas (palabras clave).
HU-01: Auth con roles | HU-02/03/04: CRUD y clasificación | Admin: gestión de usuarios.
"""
import json
import logging
import os
import re
import time
from typing import Optional, Tuple

import httpx
import jwt
from dotenv import load_dotenv
from jwcrypto import jwk, jws
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


class RoleUpdateIn(BaseModel):
    role: str


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


# Cache para JWKS (Supabase usa ECC/ES256 desde 2024+)
_JWKS_CACHE: Optional[jwk.JWKSet] = None
_JWKS_CACHE_TIME = 0.0
_JWKS_CACHE_TTL = 3600  # 1 hora


def _get_jwks() -> jwk.JWKSet:
    """Obtiene JWKS de Supabase (tokens ECC/ES256)."""
    global _JWKS_CACHE, _JWKS_CACHE_TIME
    url = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
    if not url:
        raise HTTPException(status_code=503, detail="SUPABASE_URL no configurado")
    now = time.time()
    if _JWKS_CACHE is not None and (now - _JWKS_CACHE_TIME) < _JWKS_CACHE_TTL:
        return _JWKS_CACHE
    jwks_url = f"{url}/auth/v1/.well-known/jwks.json"
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(jwks_url)
            resp.raise_for_status()
            _JWKS_CACHE = jwk.JWKSet.from_json(resp.text)
            _JWKS_CACHE_TIME = now
            return _JWKS_CACHE
    except Exception as e:
        logger.error("Error al obtener JWKS: %s", e)
        raise HTTPException(status_code=503, detail="No se pudo obtener claves de verificación JWT")


def _verify_token(authorization: Optional[str] = Header(None)) -> Tuple[str, str]:
    """Verifica JWT de Supabase (ES256/JWKS o HS256 legacy) y retorna (user_id, role)."""
    skip = os.getenv("SKIP_AUTH", "").lower() in ("1", "true")
    if skip:
        return ("dev-user", "cliente")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization Bearer requerido")

    token = authorization.replace("Bearer ", "").strip()
    payload = None

    # 1. Intentar verificación con JWKS (ES256 - tokens actuales de Supabase)
    try:
        jwks = _get_jwks()
        jwt_obj = jws.JWS()
        jwt_obj.deserialize(token, key=jwks)  # key=jwks verifica la firma
        payload = json.loads(jwt_obj.payload)
    except Exception as e:
        # 2. Fallback: Legacy HS256 (tokens antiguos o anon/service_role)
        secret = os.getenv("SUPABASE_JWT_SECRET")
        if secret:
            try:
                payload = jwt.decode(token, secret, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                logger.warning("JWT expirado")
                raise HTTPException(status_code=401, detail="Token expirado")
            except jwt.InvalidTokenError:
                pass
        if payload is None:
            logger.warning("JWT inválido: %s", str(e))
            raise HTTPException(status_code=401, detail="Token inválido")

    user_id = payload.get("sub")
    if not user_id:
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


@app.get("/me", response_model=dict)
def get_me(auth: Tuple[str, str] = Depends(_verify_token)):
    """Devuelve el perfil del usuario actual (id, role). Usa service_role, evita problemas de RLS en el cliente."""
    user_id, role = auth
    return {"id": user_id, "role": role}


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
    """Endpoint rápido para que el agente o administrador cambie el estado (Abierto/Cerrado)."""
    _, role = auth
    if role not in ("agente", "administrador"):
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


# ---- Módulo de administración de usuarios ----
ALLOWED_ROLES = {"cliente", "agente", "administrador"}


def _fetch_auth_users() -> list:
    """Obtiene la lista de usuarios desde Supabase Auth Admin API."""
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    api_url = f"{url}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {key}",
        "apikey": key,
    }
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(api_url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("users", [])
    except httpx.HTTPError as e:
        logger.error(f"Error fetching auth users: {e}")
        raise HTTPException(status_code=502, detail="Error al obtener usuarios de Supabase Auth")


@app.get("/admin/users", response_model=list)
def list_admin_users(auth: Tuple[str, str] = Depends(_verify_token)):
    """Lista todos los usuarios (email, id, role). Solo administrador."""
    _, role = auth
    if role != "administrador":
        raise HTTPException(status_code=403, detail="Solo administradores pueden acceder")

    users_raw = _fetch_auth_users()
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    profiles = supabase.table("profiles").select("id, role").execute()
    role_map = {p["id"]: p.get("role", "cliente") for p in (profiles.data or [])}

    result = []
    for u in users_raw:
        uid = u.get("id")
        email = (u.get("email") or u.get("user_metadata", {}).get("email") or "")
        result.append({
            "id": uid,
            "email": email,
            "role": role_map.get(uid, "cliente"),
        })
    return result


@app.patch("/admin/users/{user_id}/role", response_model=dict)
def update_user_role(
    user_id: str,
    body: RoleUpdateIn,
    auth: Tuple[str, str] = Depends(_verify_token),
):
    """Actualiza el rol de un usuario. Solo administrador."""
    _, role = auth
    if role != "administrador":
        raise HTTPException(status_code=403, detail="Solo administradores pueden cambiar roles")
    if body.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail=f"role debe ser uno de: {', '.join(ALLOWED_ROLES)}")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    # Verificar que el perfil existe
    existing = supabase.table("profiles").select("id").eq("id", user_id).execute()
    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    supabase.table("profiles").update({"role": body.role}).eq("id", user_id).execute()
    return {"user_id": user_id, "role": body.role}
