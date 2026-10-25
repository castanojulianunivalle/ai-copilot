"""
Mesa de Ayuda - Support Co-Pilot
Backend FastAPI. Clasificación por reglas (Semestre 1) + LLM (Semestre 2).
HU-01: Auth con roles | HU-02/03/04: CRUD y clasificación | Admin: gestión de usuarios.
HU-06: Clasificación con LLM | HU-09: Sentimiento y priorización automática.
HU-13: atención por agentes (tomar, liberar y reasignar tickets; comentarios e historial).
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
from fastapi import BackgroundTasks, Body, FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

from ai.classifier import MOTOR_LLM, MOTOR_REGLAS, ResultadoClasificacion, clasificar
from ai.llm_client import ConfigLLM
# Reexportado: el motor de reglas vive en ai.reglas para que el script de
# evaluacion (Sprint 6) lo importe sin arrastrar FastAPI ni Supabase.
from ai.reglas import classify_with_rules
from ai.revision import motivo_revision
from version import VERSION

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Que el estado del LLM quede a la vista al arrancar: si la configuracion lo
# deja apagado, la API clasifica igual con reglas y nada mas lo delataria.
_config_llm = ConfigLLM.desde_entorno()
logger.info("Clasificacion con LLM: %s", _config_llm.estado())
for _aviso in _config_llm.advertencias():
    logger.warning(_aviso)

def origenes_cors() -> list:
    """Origenes que pueden llamar a la API desde el navegador (HU-10).

    En la nube CORS_ORIGINS lleva la URL del frontend de Render, separada por
    comas si hay varias. Sin la variable queda abierto, como en local.
    """
    valor = os.getenv("CORS_ORIGINS", "")
    return [o.strip().rstrip("/") for o in valor.split(",") if o.strip()] or ["*"]


def commit_desplegado() -> str:
    """Commit que esta corriendo. Render inyecta RENDER_GIT_COMMIT en cada deploy;
    GIT_COMMIT sirve para `docker run` u otro proveedor."""
    return (os.getenv("RENDER_GIT_COMMIT") or os.getenv("GIT_COMMIT") or "local")[:7]


app = FastAPI(title="Mesa de Ayuda - Support Co-Pilot", version=VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_cors(),
    # El frontend se autentica con el header Authorization, no con cookies.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HU-13: «En proceso» le dice al cliente que un agente ya está trabajando su caso.
ALLOWED_ESTADOS = {"Abierto", "En proceso", "Cerrado"}
ROLES_STAFF = ("agente", "administrador")
MAX_COMENTARIO = 2000

class TicketIn(BaseModel):
    titulo: str
    description: str


class TicketUpdateIn(BaseModel):
    titulo: Optional[str] = None
    description: Optional[str] = None
    estado: Optional[str] = None


class RoleUpdateIn(BaseModel):
    role: str


class ComentarioIn(BaseModel):
    texto: str
    # Nota interna: solo la ven los agentes. El cliente nunca puede crearla.
    interno: bool = False


class AsignarIn(BaseModel):
    agente_id: str


class CambioEstadoIn(BaseModel):
    # Opcional: explica el cambio y queda en el historial, visible para el cliente.
    comentario: Optional[str] = None


def get_supabase() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def _campos_clasificacion(resultado: ResultadoClasificacion, texto: str) -> dict:
    """Traduce el resultado a las columnas desnormalizadas de `tickets`."""
    c = resultado.clasificacion
    confianza = c.confianza if resultado.uso_ia else None
    return {
        # HU-11: por que va a revision humana (None si no hace falta o si clasificaron las reglas).
        "motivo_revision": motivo_revision(texto, c.sentimiento, c.prioridad, confianza,
                                           resultado.uso_ia and c.requiere_revision),
        # HU-12: el proveedor fallo o limito; se reclasifica en segundo plano.
        "reclasificar": debe_reclasificar(resultado),
        "category": c.categoria,
        "sentimiento": c.sentimiento,
        "prioridad": c.prioridad,
        # El motor de reglas no estima confianza: dejarla en NULL evita que las
        # estadisticas de confianza del articulo mezclen ambos motores.
        "confianza_ia": c.confianza if resultado.uso_ia else None,
        "clasificado_por": resultado.motor,
    }


def debe_reclasificar(resultado: ResultadoClasificacion) -> bool:
    """HU-12: el LLM estaba habilitado pero fallo (429, timeout, respuesta ilegible) y clasificaron las reglas."""
    return not resultado.uso_ia and resultado.error is not None


def reclasificar_ticket(ticket_id: str, texto: str) -> bool:
    """HU-12 · AISCOP-65: vuelve a clasificar con el modelo un ticket que cayo a reglas.

    Corre en segundo plano, despues de responder al cliente. Espera antes de cada intento para no
    sumarse al pico que provoco el 429 (el plan gratuito de Groq limita los tokens por minuto). Si el
    modelo responde, actualiza el ticket, registra la prediccion del LLM y apaga la marca; si no, la
    marca queda y el ticket se reprocesa con POST /tickets/reclasificar-pendientes.
    """
    espera = float(os.getenv("RECLASIFICAR_ESPERA_S", "20"))
    intentos = int(os.getenv("RECLASIFICAR_INTENTOS", "3"))
    supabase = get_supabase()
    if not supabase:
        return False
    for intento in range(intentos):
        time.sleep(espera * (intento + 1))
        resultado = clasificar(texto, classify_with_rules)
        if resultado.uso_ia:
            supabase.table("tickets").update(_campos_clasificacion(resultado, texto)).eq("id", ticket_id).execute()
            _registrar_clasificacion(supabase, ticket_id, texto, resultado)
            logger.info("Ticket %s reclasificado con el LLM en el intento %d", ticket_id, intento + 1)
            return True
    logger.warning("Ticket %s sigue pendiente de reclasificar tras %d intentos", ticket_id, intentos)
    return False


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
    # Se lee en cada llamada: asi refleja el entorno real del despliegue, que es
    # lo que hay que comprobar antes de una demostracion.
    config = ConfigLLM.desde_entorno()
    # version y commit atan lo que corre en la nube a un tag y a un commit de main (HU-10).
    return {"status": "ok", "version": VERSION, "commit": commit_desplegado(),
            "clasificacion": {**config.estado(), "advertencias": config.advertencias()}}


@app.get("/me", response_model=dict)
def get_me(auth: Tuple[str, str] = Depends(_verify_token)):
    """Devuelve el perfil del usuario actual (id, role). Usa service_role, evita problemas de RLS en el cliente."""
    user_id, role = auth
    return {"id": user_id, "role": role}


@app.post("/create-ticket", response_model=dict)
def create_ticket(ticket: TicketIn, tareas: BackgroundTasks, auth: Tuple[str, str] = Depends(_verify_token)):
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
    # timeout + fallback a reglas acotan el peor caso. Si el proveedor fallo o
    # limito, el ticket se reclasifica despues en segundo plano (HU-12).
    resultado = clasificar(texto, classify_with_rules)

    ticket_data = {
        "titulo": ticket.titulo,
        "description": ticket.description,
        "estado": "Abierto",
        "created_by": user_id if user_id != "dev-user" else None,
        **_campos_clasificacion(resultado, texto),
    }
    result = supabase.table("tickets").insert(ticket_data).execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=500, detail="Error al crear ticket")

    ticket_id = result.data[0]["id"]
    _registrar_clasificacion(supabase, ticket_id, texto, resultado)
    if ticket_data["reclasificar"]:
        tareas.add_task(reclasificar_ticket, ticket_id, texto)

    clasificacion = resultado.clasificacion
    return {
        "ticket_id": ticket_id,
        "category": clasificacion.categoria,
        "estado": "Abierto",
        "sentimiento": clasificacion.sentimiento,
        "prioridad": clasificacion.prioridad,
        "confianza_ia": clasificacion.confianza if resultado.uso_ia else None,
        "clasificado_por": resultado.motor,
        "requiere_revision": ticket_data["motivo_revision"] is not None,
        "motivo_revision": ticket_data["motivo_revision"],
        "reclasificar": ticket_data["reclasificar"],
    }


@app.post("/tickets/reclasificar-pendientes", response_model=dict)
def reclasificar_pendientes(limite: int = 20, auth: Tuple[str, str] = Depends(_verify_token)):
    """HU-12 · AISCOP-66: reprocesa los tickets que siguen marcados (por ejemplo, tras reiniciar la API)."""
    _, role = auth
    if role not in ("agente", "administrador"):
        raise HTTPException(status_code=403, detail="Solo agentes pueden reclasificar")
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    pendientes = (supabase.table("tickets").select("id, titulo, description").eq("reclasificar", True)
                  .limit(min(limite, 50)).execute().data or [])
    hechos = sum(reclasificar_ticket(t["id"], f"{t['titulo']} {t['description']}") for t in pendientes)
    return {"pendientes": len(pendientes), "reclasificados": hechos}


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
        update_data.update(_campos_clasificacion(resultado, texto))
    if ticket.estado is not None:
        if role not in ROLES_STAFF:
            raise HTTPException(status_code=403, detail="Solo agentes pueden cambiar el estado")
        if ticket.estado not in ALLOWED_ESTADOS:
            raise HTTPException(status_code=400, detail=f"estado debe ser uno de: {', '.join(sorted(ALLOWED_ESTADOS))}")
        update_data["estado"] = ticket.estado

    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    supabase.table("tickets").update(update_data).eq("id", ticket_id).execute()

    if resultado is not None:
        _registrar_clasificacion(supabase, ticket_id, texto, resultado)
    antes = existing.data[0].get("estado")
    if ticket.estado is not None and ticket.estado != antes:
        _registrar_evento(supabase, ticket_id, user_id, "estado", estado_antes=antes, estado_despues=ticket.estado)

    return {"message": "Ticket actualizado", "ticket_id": ticket_id}


# ---- HU-13: atención por agentes ----
def _exigir_ticket(supabase, ticket_id: str) -> dict:
    existing = supabase.table("tickets").select("*").eq("id", ticket_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return existing.data[0]


def _ahora() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _registrar_evento(supabase, ticket_id: str, autor_id: str, tipo: str, **campos) -> None:
    """Deja el cambio en ticket_eventos. Si falla no se revierte la acción: el historial es secundario."""
    fila = {"ticket_id": ticket_id, "autor_id": autor_id if autor_id != "dev-user" else None, "tipo": tipo, **campos}
    try:
        supabase.table("ticket_eventos").insert(fila).execute()
    except Exception as e:  # noqa: BLE001
        logger.warning("No se pudo registrar el evento %s del ticket %s: %s", tipo, ticket_id, e)


def _asignar(supabase, ticket: dict, agente_id: Optional[str], autor_id: str) -> None:
    supabase.table("tickets").update({"asignado_a": agente_id, "asignado_en": _ahora() if agente_id else None}) \
        .eq("id", ticket["id"]).execute()
    _registrar_evento(supabase, ticket["id"], autor_id, "asignacion",
                      asignado_antes=ticket.get("asignado_a"), asignado_despues=agente_id)


@app.patch("/tickets/{ticket_id}/estado", response_model=dict)
def update_estado(ticket_id: str, estado: str, cuerpo: Optional[CambioEstadoIn] = Body(None),
                  auth: Tuple[str, str] = Depends(_verify_token)):
    """El agente o administrador cambia el estado, opcionalmente con un comentario para el cliente.

    Pasar a «En proceso» un ticket sin dueño lo asigna a quien lo cambia: no tiene sentido que alguien esté
    trabajando un caso que figura como libre.
    """
    user_id, role = auth
    if role not in ROLES_STAFF:
        raise HTTPException(status_code=403, detail="Solo agentes pueden cambiar el estado")
    if estado not in ALLOWED_ESTADOS:
        raise HTTPException(status_code=400, detail=f"estado debe ser uno de: {', '.join(sorted(ALLOWED_ESTADOS))}")
    comentario = (cuerpo.comentario or "").strip() if cuerpo else ""
    if len(comentario) > MAX_COMENTARIO:
        raise HTTPException(status_code=400, detail=f"El comentario admite hasta {MAX_COMENTARIO} caracteres")

    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    ticket = _exigir_ticket(supabase, ticket_id)

    supabase.table("tickets").update({"estado": estado}).eq("id", ticket_id).execute()
    if estado != ticket.get("estado") or comentario:
        _registrar_evento(supabase, ticket_id, user_id, "estado", estado_antes=ticket.get("estado"),
                          estado_despues=estado, texto=comentario or None)
    asignado = ticket.get("asignado_a")
    if estado == "En proceso" and not asignado and user_id != "dev-user":
        _asignar(supabase, ticket, user_id, user_id)
        asignado = user_id
    return {"ticket_id": ticket_id, "estado": estado, "asignado_a": asignado}


@app.post("/tickets/{ticket_id}/tomar", response_model=dict)
def tomar_ticket(ticket_id: str, auth: Tuple[str, str] = Depends(_verify_token)):
    """El agente toma un ticket libre. La condición «asignado_a is null» va en el mismo UPDATE: si dos agentes lo
    toman a la vez, la base acepta solo uno y el otro recibe 409."""
    user_id, role = auth
    if role not in ROLES_STAFF:
        raise HTTPException(status_code=403, detail="Solo agentes pueden tomar tickets")
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    ticket = _exigir_ticket(supabase, ticket_id)
    if ticket.get("asignado_a") == user_id:
        return {"ticket_id": ticket_id, "asignado_a": user_id}
    if ticket.get("estado") == "Cerrado":
        raise HTTPException(status_code=409, detail="El ticket está cerrado")

    tomado = (supabase.table("tickets").update({"asignado_a": user_id, "asignado_en": _ahora()})
              .eq("id", ticket_id).is_("asignado_a", "null").execute())
    if not tomado.data:
        raise HTTPException(status_code=409, detail="Otro agente ya tomó este ticket")
    _registrar_evento(supabase, ticket_id, user_id, "asignacion", asignado_antes=None, asignado_despues=user_id)
    return {"ticket_id": ticket_id, "asignado_a": user_id}


@app.post("/tickets/{ticket_id}/liberar", response_model=dict)
def liberar_ticket(ticket_id: str, auth: Tuple[str, str] = Depends(_verify_token)):
    """Devuelve el ticket a la cola. Lo puede hacer el agente que lo tiene o un administrador."""
    user_id, role = auth
    if role not in ROLES_STAFF:
        raise HTTPException(status_code=403, detail="Solo agentes pueden liberar tickets")
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    ticket = _exigir_ticket(supabase, ticket_id)
    if not ticket.get("asignado_a"):
        return {"ticket_id": ticket_id, "asignado_a": None}
    if ticket["asignado_a"] != user_id and role != "administrador":
        raise HTTPException(status_code=403, detail="Solo quien tiene el ticket o un administrador puede liberarlo")
    _asignar(supabase, ticket, None, user_id)
    return {"ticket_id": ticket_id, "asignado_a": None}


@app.post("/tickets/{ticket_id}/asignar", response_model=dict)
def asignar_ticket(ticket_id: str, body: AsignarIn, auth: Tuple[str, str] = Depends(_verify_token)):
    """El administrador asigna o reasigna el ticket a un agente."""
    user_id, role = auth
    if role != "administrador":
        raise HTTPException(status_code=403, detail="Solo administradores pueden reasignar")
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    ticket = _exigir_ticket(supabase, ticket_id)
    destino = supabase.table("profiles").select("id, role").eq("id", body.agente_id).execute().data
    if not destino or destino[0].get("role") not in ROLES_STAFF:
        raise HTTPException(status_code=400, detail="El destino debe ser un agente")
    if ticket.get("asignado_a") != body.agente_id:
        _asignar(supabase, ticket, body.agente_id, user_id)
    return {"ticket_id": ticket_id, "asignado_a": body.agente_id}


@app.post("/tickets/{ticket_id}/comentarios", response_model=dict)
def comentar_ticket(ticket_id: str, body: ComentarioIn, auth: Tuple[str, str] = Depends(_verify_token)):
    """Comentario en el ticket. El agente responde al cliente o deja una nota interna; el cliente responde en sus
    propios tickets y nunca puede escribir notas internas."""
    user_id, role = auth
    texto = body.texto.strip()
    if not texto:
        raise HTTPException(status_code=400, detail="El comentario no puede estar vacío")
    if len(texto) > MAX_COMENTARIO:
        raise HTTPException(status_code=400, detail=f"El comentario admite hasta {MAX_COMENTARIO} caracteres")
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    ticket = _exigir_ticket(supabase, ticket_id)
    if role not in ROLES_STAFF:
        if ticket.get("created_by") != user_id:
            raise HTTPException(status_code=403, detail="Solo puedes comentar tus propios tickets")
        if body.interno:
            raise HTTPException(status_code=403, detail="Las notas internas son solo para agentes")
    _registrar_evento(supabase, ticket_id, user_id, "comentario", texto=texto, interno=body.interno)
    return {"ticket_id": ticket_id, "interno": body.interno}


@app.get("/tickets/{ticket_id}/eventos", response_model=list)
def eventos_ticket(ticket_id: str, auth: Tuple[str, str] = Depends(_verify_token)):
    """Historial del ticket, del más antiguo al más reciente, con el correo y el rol de cada persona.
    El cliente solo ve sus tickets y nunca las notas internas."""
    user_id, role = auth
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    ticket = _exigir_ticket(supabase, ticket_id)
    staff = role in ROLES_STAFF
    if not staff and ticket.get("created_by") != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes ver tus propios tickets")
    consulta = supabase.table("ticket_eventos").select("*").eq("ticket_id", ticket_id).order("created_at")
    if not staff:
        consulta = consulta.eq("interno", False)
    eventos = consulta.execute().data or []
    ids = {e[k] for e in eventos for k in ("autor_id", "asignado_antes", "asignado_despues") if e.get(k)}
    perfiles = {p["id"]: p for p in (supabase.table("profiles").select("id, email, role").in_("id", list(ids))
                                     .execute().data or [])} if ids else {}

    def quien(uid):
        if not uid:
            return None
        p = perfiles.get(uid) or {}
        return {"id": uid, "email": p.get("email"), "role": p.get("role")}

    return [{**e, "autor": quien(e.get("autor_id")), "asignado_antes": quien(e.get("asignado_antes")),
             "asignado_despues": quien(e.get("asignado_despues"))} for e in eventos]


@app.get("/agentes", response_model=list)
def listar_agentes(auth: Tuple[str, str] = Depends(_verify_token)):
    """Agentes y administradores, para mostrar quién atiende cada ticket y para reasignar."""
    _, role = auth
    if role not in ROLES_STAFF:
        raise HTTPException(status_code=403, detail="Solo agentes")
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    return supabase.table("profiles").select("id, email, role").in_("role", list(ROLES_STAFF)).execute().data or []


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
