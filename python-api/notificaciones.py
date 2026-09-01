"""
Sprint 7 · HU-05 · AISCOP-29: disparo del webhook de n8n.

Cuando entra un ticket que no puede esperar, la API avisa a n8n y n8n decide el
canal (Telegram, correo). El criterio de "no puede esperar" es la prioridad que
calculo el componente inteligente del Sprint 5, asi que esta notificacion es
directamente un resultado de la IA: sin analisis de sentimiento, todos los
tickets entrarian como Media y la alerta no distinguiria nada.

Dos propiedades que el modulo garantiza:

1. **No bloquea al cliente.** Se invoca desde un BackgroundTask, despues de que
   la respuesta del POST ya salio. Un n8n caido o lento no puede retrasar la
   creacion de un ticket.
2. **No falla nunca hacia afuera.** Cualquier excepcion se registra y se traga.
   Una notificacion perdida es un problema de operacion; un ticket perdido es un
   problema del cliente.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Solo estas prioridades disparan el aviso. Configurable porque durante las
# pruebas conviene abrirlo a todas y en produccion cerrarlo a Alta.
_PRIORIDADES_POR_DEFECTO = "Alta"


def _configuracion() -> tuple[str | None, set[str], str | None, float]:
    url = os.getenv("N8N_WEBHOOK_URL") or None
    prioridades = {
        p.strip()
        for p in os.getenv("N8N_PRIORIDADES", _PRIORIDADES_POR_DEFECTO).split(",")
        if p.strip()
    }
    secreto = os.getenv("N8N_WEBHOOK_SECRET") or None
    timeout = float(os.getenv("N8N_TIMEOUT", "5"))
    return url, prioridades, secreto, timeout


def _firmar(cuerpo: bytes, secreto: str) -> str:
    """HMAC-SHA256 del cuerpo exacto que se envia.

    El webhook de n8n es una URL publica: sin firma, cualquiera que la descubra
    puede inyectar alertas falsas. n8n valida esta cabecera con el mismo secreto
    antes de procesar el evento.
    """
    return hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()


def construir_payload(ticket: dict[str, Any]) -> dict[str, Any]:
    """Aplana lo que n8n necesita para redactar el mensaje.

    Se manda el texto ya resuelto y no ids que n8n tendria que ir a consultar:
    el flujo debe poder redactar la alerta sin volver a llamar a la API.
    """
    return {
        "evento": "ticket.prioritario",
        "ticket_id": ticket.get("ticket_id"),
        "titulo": ticket.get("titulo"),
        "descripcion": (ticket.get("description") or "")[:500],
        "categoria": ticket.get("category"),
        "sentimiento": ticket.get("sentimiento"),
        "prioridad": ticket.get("prioridad"),
        "confianza_ia": ticket.get("confianza_ia"),
        "clasificado_por": ticket.get("clasificado_por"),
        # Deja ver de un vistazo si la alerta viene de una prediccion dudosa.
        "requiere_revision": bool(ticket.get("requiere_revision")),
        "url": f"{os.getenv('APP_URL', '').rstrip('/')}/?ticket={ticket.get('ticket_id')}"
        if os.getenv("APP_URL")
        else None,
    }


def debe_notificar(ticket: dict[str, Any]) -> bool:
    url, prioridades, _, _ = _configuracion()
    if not url:
        return False
    return ticket.get("prioridad") in prioridades


def notificar_ticket(ticket: dict[str, Any]) -> None:
    """Dispara el webhook. Pensada para correr dentro de un BackgroundTask."""
    url, prioridades, secreto, timeout = _configuracion()
    if not url:
        logger.debug("N8N_WEBHOOK_URL sin configurar: no se notifica")
        return
    if ticket.get("prioridad") not in prioridades:
        return

    payload = construir_payload(ticket)
    cuerpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    cabeceras = {"Content-Type": "application/json; charset=utf-8"}
    if secreto:
        cabeceras["X-Signature-256"] = f"sha256={_firmar(cuerpo, secreto)}"

    try:
        respuesta = httpx.post(url, content=cuerpo, headers=cabeceras, timeout=timeout)
        if respuesta.status_code >= 400:
            logger.error(
                "n8n rechazo la notificacion del ticket %s: HTTP %s %s",
                payload["ticket_id"], respuesta.status_code, respuesta.text[:200],
            )
        else:
            logger.info(
                "Notificado a n8n: ticket %s (%s / %s)",
                payload["ticket_id"], payload["prioridad"], payload["categoria"],
            )
    except Exception as exc:  # noqa: BLE001
        # A proposito se atrapa todo: esto corre despues de responderle al
        # cliente, y una excepcion aqui solo ensuciaria los logs del worker.
        logger.error("No se pudo notificar a n8n el ticket %s: %s", payload["ticket_id"], exc)
