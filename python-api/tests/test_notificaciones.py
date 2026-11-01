"""
HU-05: notificación de tickets urgentes por n8n.

Cubre la DoD: filtro de urgencia, estructura del payload (con tildes en UTF-8), secreto en el encabezado y
desacoplamiento (si n8n falla o tarda, el ticket se crea igual). n8n se simula con un MockTransport de httpx.
"""
from __future__ import annotations

import json

import httpx
import pytest

import main
import notificaciones
from tests.test_api_crear_ticket import TICKET, api, respuesta_llm  # noqa: F401 — fixture compartida


@pytest.fixture
def n8n(monkeypatch):
    """Webhook de n8n simulado: guarda las peticiones y responde lo que diga `estado['respuesta']`."""
    monkeypatch.setenv("N8N_WEBHOOK_URL", "http://n8n.test/webhook/aiscop-ticket-urgente")
    monkeypatch.setenv("N8N_WEBHOOK_SECRET", "secreto-prueba")
    monkeypatch.setenv("APP_URL", "https://mesa.test")
    estado = {"peticiones": [], "respuesta": lambda req: httpx.Response(200, json={"enviado": True})}

    def manejar(req):
        estado["peticiones"].append(req)
        return estado["respuesta"](req)

    real = notificaciones.notificar_urgente
    monkeypatch.setattr(main, "notificar_urgente",
                        lambda payload: real(payload, transporte=httpx.MockTransport(manejar)))
    return estado


def payload_de_prueba():
    return notificaciones.armar_payload("t-1", "Acceso sospechoso", "Inició sesión desde otro país", "ana@correo.co",
                                        "Seguridad", "Alta", "Urgente")


@pytest.mark.parametrize("prioridad, urgente", [("Alta", True), ("Media", False), ("Baja", False), (None, False)])
def test_solo_la_prioridad_alta_es_urgente(prioridad, urgente):
    assert notificaciones.es_urgente(prioridad) is urgente


def test_el_payload_lleva_id_titulo_y_cliente():
    p = payload_de_prueba()
    assert (p["ticket_id"], p["titulo"], p["cliente"]) == ("t-1", "Acceso sospechoso", "ana@correo.co")


def test_las_tildes_viajan_en_utf8_con_el_secreto(n8n, monkeypatch):
    transporte = httpx.MockTransport(lambda req: (n8n["peticiones"].append(req), httpx.Response(200))[1])
    assert notificaciones.notificar_urgente(payload_de_prueba(), transporte=transporte) is True
    req = n8n["peticiones"][0]
    assert req.headers["X-AISCOP-Secret"] == "secreto-prueba"
    assert json.loads(req.content.decode("utf-8"))["descripcion"] == "Inició sesión desde otro país"


@pytest.mark.parametrize("falla", [
    lambda req: httpx.Response(500),
    lambda req: (_ for _ in ()).throw(httpx.ReadTimeout("n8n no responde", request=req)),
    lambda req: (_ for _ in ()).throw(httpx.ConnectError("sin red", request=req)),
])
def test_si_n8n_falla_no_lanza_excepcion(falla, monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_URL", "http://n8n.test/webhook/aiscop-ticket-urgente")
    assert notificaciones.notificar_urgente(payload_de_prueba(), transporte=httpx.MockTransport(falla)) is False


def test_sin_url_no_notifica(monkeypatch):
    monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)
    assert notificaciones.notificar_urgente(payload_de_prueba()) is False


def test_ticket_urgente_dispara_el_webhook(api, n8n):
    r = api["cliente"].post("/create-ticket", json=TICKET)
    assert r.status_code == 200 and r.json()["prioridad"] == "Alta"
    assert len(n8n["peticiones"]) == 1
    cuerpo = json.loads(n8n["peticiones"][0].content)
    assert (cuerpo["ticket_id"], cuerpo["titulo"]) == ("ticket-1", TICKET["titulo"])


def test_ticket_no_urgente_no_dispara_el_webhook(api, n8n):
    contenido = json.dumps({"categoria": "Consultas", "sentimiento": "Neutral", "prioridad": "Baja",
                            "confianza": 0.9, "justificacion": "Pregunta general"})
    api["manejador"] = lambda req: httpx.Response(200, json={"model": "m", "choices": [{"message": {"content": contenido}}]})
    assert api["cliente"].post("/create-ticket", json=TICKET).status_code == 200
    assert n8n["peticiones"] == []


def test_si_n8n_cae_el_ticket_se_crea_igual(api, n8n):
    n8n["respuesta"] = lambda req: httpx.Response(500, json={"message": "Error in workflow"})
    r = api["cliente"].post("/create-ticket", json=TICKET)
    assert r.status_code == 200 and r.json()["ticket_id"] == "ticket-1"
    assert len(n8n["peticiones"]) == 1
