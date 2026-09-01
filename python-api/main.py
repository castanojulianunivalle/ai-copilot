"""
Mesa de Ayuda - Support Co-Pilot
Backend FastAPI. Clasificación por reglas (Semestre 1) + LLM (Semestre 2).
HU-01: Auth con roles | HU-02/03/04: CRUD y clasificación | Admin: gestión de usuarios.
HU-06: Clasificación con LLM | HU-09: Sentimiento y priorización automática.
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
from fastapi import BackgroundTasks, FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

from ai.classifier import MOTOR_LLM, MOTOR_REGLAS, ResultadoClasificacion, clasificar
# Reexportado: el motor de reglas vive en ai.reglas para que el script de
# evaluacion (Sprint 6) lo importe sin arrastrar FastAPI ni Supabase.
from ai.reglas import classify_with_rules
from notificaciones import notificar_ticket

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


def _campos_clasificacion(resultado: ResultadoClasificacion) -> dict:
    """Traduce el resultado a las columnas desnormalizadas de `tickets`."""
    c = resultado.clasificacion
    return {
        "category": c.categoria,
        "sentimiento": c.sentimiento,
        "prioridad": c.prioridad,
        # El motor de reglas no estima confianza: dejarla en NULL evita que las
        # estadisticas de confianza del articulo mezclen ambos motores.
        "confianza_ia": c.confianza if resultado.uso_ia else None,
        "clasificado_por": resultado.motor,
    }


def _registrar_clasificacion(supabase, ticket_id: str, texto: str, resultado: ResultadoClasificacion) -> None:
    """Deja constancia en classification_log de lo que predijo cada motor.

    El motor de reglas se registra SIEMPRE, incluso cuando gana el LLM. Es lo
    que permite que el Sprint 6 compare ambos motores sobre exactamente los
    mismos tickets en lugar de sobre dos muestras distintas.
    """
    filas = [{
        "ticket_id": ticket_id,
        "motor": MOTOR_REGLAS,
        "categoria": classify_with_rules(texto),
        "modelo": "classify_with_rules@sem1",
    }]
    if resultado.uso_ia:
        c = resultado.clasificacion
        filas.append({
            "ticket_id": ticket_id,
            "motor": MOTOR_LLM,
            "categoria": c.categoria,
            "sentimiento": c.sentimiento,
            "prioridad": c.prioridad,
            "confianza": c.confianza,
            "modelo": resultado.modelo,
            "latencia_ms": resultado.latencia_ms,
        })

    try:
        supabase.table("classification_log").upsert(filas, on_conflict="ticket_id,motor").execute()
    except Exception as exc:  # noqa: BLE001
        # El log alimenta la investigacion, no el producto. Si falla, el ticket
        # ya esta creado y el cliente no tiene por que enterarse.
        logger.error("No se pudo registrar la clasificacion del ticket %s: %s", ticket_id, exc)


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
def create_ticket(
    ticket: TicketIn,
    tareas: BackgroundTasks,
    auth: Tuple[str, str] = Depends(_verify_token),
):
    user_id, role = auth
    if role != "cliente":
        raise HTTPException(status_code=403, detail="Solo clientes pueden crear tickets")

    if not ticket.description or not ticket.titulo:
        raise HTTPException(status_code=400, detail="titulo y description son requeridos")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")

    texto = f"{ticket.titulo} {ticket.description}"
    # Clasificacion sincrona: la respuesta lleva ya la categoria de la IA, y el
    # timeout + fallback a reglas acotan el peor caso. Cuando Realtime entre en
    # el Sprint 7, esto puede pasar a BackgroundTasks y refrescarse solo.
    resultado = clasificar(texto, classify_with_rules)

    ticket_data = {
        "titulo": ticket.titulo,
        "description": ticket.description,
        "estado": "Abierto",
        "created_by": user_id if user_id != "dev-user" else None,
        **_campos_clasificacion(resultado),
    }
    result = supabase.table("tickets").insert(ticket_data).execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=500, detail="Error al crear ticket")

    ticket_id = result.data[0]["id"]
    _registrar_clasificacion(supabase, ticket_id, texto, resultado)

    clasificacion = resultado.clasificacion
    respuesta = {
        "ticket_id": ticket_id,
        "category": clasificacion.categoria,
        "estado": "Abierto",
        "sentimiento": clasificacion.sentimiento,
        "prioridad": clasificacion.prioridad,
        "confianza_ia": clasificacion.confianza if resultado.uso_ia else None,
        "clasificado_por": resultado.motor,
        "requiere_revision": resultado.uso_ia and clasificacion.requiere_revision,
    }

    # HU-05: el aviso sale despues de responderle al cliente. Un n8n caido o
    # lento no puede retrasar la creacion de un ticket.
    tareas.add_task(notificar_ticket, {**respuesta, "titulo": ticket.titulo,
                                       "description": ticket.description})
    return respuesta


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
    resultado = None
    texto = ""
    if ticket.titulo is not None:
        update_data["titulo"] = ticket.titulo
    if ticket.description is not None:
        update_data["description"] = ticket.description
        # Se reclasifica con titulo + descripcion, igual que en el alta. Antes
        # se usaba solo la descripcion, lo que daba al motor una entrada
        # distinta segun el ticket viniera de un POST o de un PUT y ensuciaba
        # la comparacion entre motores.
        titulo = ticket.titulo if ticket.titulo is not None else existing.data[0].get("titulo", "")
        texto = f"{titulo} {ticket.description}"
        resultado = clasificar(texto, classify_with_rules)
        update_data.update(_campos_clasificacion(resultado))
    if ticket.estado is not None:
        if ticket.estado not in ALLOWED_ESTADOS:
            raise HTTPException(status_code=400, detail="estado debe ser Abierto o Cerrado")
        update_data["estado"] = ticket.estado

    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    supabase.table("tickets").update(update_data).eq("id", ticket_id).execute()

    if resultado is not None:
        _registrar_clasificacion(supabase, ticket_id, texto, resultado)

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


# ---- HU-07: Dashboard analítico (Sprint 8) ----
# Las agregaciones viven en vistas SQL (ver la migración de reportes). La API
# solo las expone: mantener una segunda definición de cada métrica en Python
# garantizaría que las dos se separen con el tiempo.
_VISTAS_REPORTE = {
    "resumen": "reportes_resumen",
    "por-categoria": "reportes_por_categoria",
    "serie": "reportes_serie_diaria",
    "por-sentimiento": "reportes_por_sentimiento",
    "ia-vs-reglas": "reportes_ia_vs_reglas",
}

# Un cliente ve solo sus propios tickets; darle las métricas agregadas de todos
# sería una fuga de información sobre el volumen y los problemas de terceros.
_ROLES_REPORTES = {"agente", "administrador"}


def _leer_vista(nombre: str, limite: int | None = None) -> list:
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    consulta = supabase.table(nombre).select("*")
    if limite:
        consulta = consulta.limit(limite)
    try:
        return consulta.execute().data or []
    except Exception as exc:  # noqa: BLE001
        # El fallo típico es que las migraciones de reportes no se aplicaron.
        logger.error("No se pudo leer la vista %s: %s", nombre, exc)
        raise HTTPException(
            status_code=503,
            detail=f"La vista '{nombre}' no está disponible. ¿Se aplicaron las migraciones de reportes?",
        ) from exc


@app.get("/reports/{seccion}", response_model=dict)
def get_report(seccion: str, auth: Tuple[str, str] = Depends(_verify_token)):
    """Métricas agregadas para el dashboard analítico (HU-07)."""
    _, role = auth
    if role not in _ROLES_REPORTES:
        raise HTTPException(status_code=403, detail="Solo agentes y administradores ven reportes")

    vista = _VISTAS_REPORTE.get(seccion)
    if not vista:
        raise HTTPException(
            status_code=404,
            detail=f"Sección desconocida. Disponibles: {', '.join(sorted(_VISTAS_REPORTE))}",
        )

    # ia-vs-reglas es un producto cruzado de categorías: se acota para que una
    # base grande no devuelva cientos de combinaciones con conteo 1.
    filas = _leer_vista(vista, limite=40 if seccion == "ia-vs-reglas" else None)

    # `resumen` es una vista de una sola fila; se devuelve como objeto para que
    # el frontend no tenga que hacer datos[0] en un caso y datos en los demás.
    if seccion == "resumen":
        return {"seccion": seccion, "datos": filas[0] if filas else {}}
    return {"seccion": seccion, "datos": filas}


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
