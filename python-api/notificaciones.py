"""HU-05 · notificaciones de tickets urgentes por n8n.

Cuando un ticket queda con prioridad «Alta» (la más alta de la taxonomía; el modelo la asigna también cuando el tono
es «Urgente» o «Frustrado»), la API llama a un webhook de n8n, que envía un correo al equipo de soporte.

Todo sale de variables de entorno:

- N8N_WEBHOOK_URL: URL del webhook; sin ella, la notificación queda apagada;
- N8N_WEBHOOK_SECRET: va en el encabezado X-AISCOP-Secret, que n8n exige;
- APP_URL: enlace a la Mesa de Ayuda que lleva el correo.

La llamada corre en segundo plano y nunca lanza excepciones: si n8n falla o tarda, el ticket ya está creado y el
cliente no se entera.
"""
import json
import logging
import os
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

PRIORIDAD_URGENTE = "Alta"
TIMEOUT_S = 10.0


def es_urgente(prioridad: str | None) -> bool:
    """Filtro de urgencia de la DoD: solo los tickets de prioridad «Alta» se notifican, para no hacer spam."""
    return prioridad == PRIORIDAD_URGENTE


def armar_payload(ticket_id: str, titulo: str, descripcion: str, cliente: str | None, categoria: str | None,
                  prioridad: str | None, sentimiento: str | None) -> dict:
    """Lo esencial que pide la DoD (ID, título y cliente), más el contexto para atender el caso desde el correo."""
    return {
        "ticket_id": ticket_id,
        "titulo": titulo,
        "cliente": cliente or "Cliente sin correo",
        "categoria": categoria,
        "prioridad": prioridad,
        "sentimiento": sentimiento,
        "descripcion": descripcion[:1000],
        "creado": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "url": os.getenv("APP_URL", ""),
    }


def notificar_urgente(payload: dict, transporte: httpx.BaseTransport | None = None) -> bool:
    """Envía el payload al webhook de n8n. Devuelve True si n8n confirmó el envío; nunca lanza excepciones."""
    url = os.getenv("N8N_WEBHOOK_URL", "").strip()
    if not url:
        logger.info("HU-05: N8N_WEBHOOK_URL no está configurada; no se notifica el ticket %s", payload.get("ticket_id"))
        return False
    try:
        with httpx.Client(timeout=TIMEOUT_S, transport=transporte) as cliente:
            r = cliente.post(url, content=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                             headers={"Content-Type": "application/json; charset=utf-8",
                                      "X-AISCOP-Secret": os.getenv("N8N_WEBHOOK_SECRET", "")})
        if r.status_code >= 400:
            logger.warning("HU-05: n8n respondió %s al notificar el ticket %s", r.status_code, payload.get("ticket_id"))
            return False
        logger.info("HU-05: notificado el ticket urgente %s", payload.get("ticket_id"))
        return True
    except Exception as exc:  # noqa: BLE001 — desacoplamiento: ningún fallo de n8n llega al cliente
        logger.warning("HU-05: no se pudo notificar el ticket %s: %s", payload.get("ticket_id"), exc)
        return False
