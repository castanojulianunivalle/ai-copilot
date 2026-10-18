"""
HU-06 · AISCOP-43: el flujo completo de POST /create-ticket, que es lo que se
demuestra en el Avance 2.

Corre la API FastAPI real. Lo unico simulado es lo externo: Supabase con una
tabla en memoria y el LLM con un MockTransport de httpx.
"""
from __future__ import annotations

import json

import httpx
import pytest
from fastapi.testclient import TestClient

import main
from ai import classifier, llm_client
from ai.llm_client import ClienteLLM, ConfigLLM


class _Resultado:
    def __init__(self, data):
        self.data = data


class _Consulta:
    def __init__(self, base, tabla, accion, filas, error):
        self.base, self.tabla, self.accion, self.filas, self.error = base, tabla, accion, filas, error

    def execute(self):
        if self.error:
            raise self.error
        self.base.escrituras.append((self.tabla, self.accion, self.filas))
        if self.accion == "insert":
            return _Resultado([{"id": "ticket-1", **self.filas}])
        return _Resultado(self.filas)


class _Tabla:
    def __init__(self, base, nombre):
        self.base, self.nombre = base, nombre

    def insert(self, fila):
        return _Consulta(self.base, self.nombre, "insert", fila, None)

    def upsert(self, filas, on_conflict=None):
        self.base.on_conflict = on_conflict
        return _Consulta(self.base, self.nombre, "upsert", filas, self.base.falla_log)


class SupabaseFalsa:
    def __init__(self, falla_log=None):
        self.escrituras = []
        self.falla_log = falla_log
        self.on_conflict = None

    def table(self, nombre):
        return _Tabla(self, nombre)

    def filas(self, tabla):
        return [f for t, _, f in self.escrituras if t == tabla]


TICKET = {"titulo": "Acceso sospechoso", "description": "Me llego un correo de un inicio de sesion desde otro pais que no fui yo"}


def respuesta_llm(confianza=0.88):
    contenido = json.dumps({"categoria": "Seguridad", "sentimiento": "Urgente", "prioridad": "Alta",
                            "confianza": confianza, "justificacion": "Inicio de sesion no reconocido"})
    return httpx.Response(200, json={"model": "llama-test", "choices": [{"message": {"content": contenido}}]})


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("SKIP_AUTH", "1")
    monkeypatch.setenv("LLM_ENABLED", "1")
    monkeypatch.setenv("LLM_API_KEY", "hf_prueba")
    monkeypatch.setenv("LLM_BASE_URL", "http://llm.test/v1")
    monkeypatch.setattr(llm_client.time, "sleep", lambda _s: None)

    estado = {"manejador": lambda req: respuesta_llm(), "base": SupabaseFalsa()}
    monkeypatch.setattr(main, "get_supabase", lambda: estado["base"])
    monkeypatch.setattr(classifier, "ClienteLLM", lambda: ClienteLLM(
        ConfigLLM.desde_entorno(), transporte=httpx.MockTransport(lambda req: estado["manejador"](req))))
    estado["cliente"] = TestClient(main.app)
    return estado


def test_el_ticket_se_clasifica_con_el_llm(api):
    r = api["cliente"].post("/create-ticket", json=TICKET)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["clasificado_por"] == "llm"
    assert (cuerpo["category"], cuerpo["sentimiento"], cuerpo["prioridad"]) == ("Seguridad", "Urgente", "Alta")
    assert cuerpo["confianza_ia"] == 0.88 and cuerpo["requiere_revision"] is False

    guardado = api["base"].filas("tickets")[0]
    assert guardado["clasificado_por"] == "llm" and guardado["confianza_ia"] == 0.88


def test_se_registran_los_dos_motores_aunque_gane_el_llm(api):
    api["cliente"].post("/create-ticket", json=TICKET)
    log = api["base"].filas("classification_log")[0]
    assert {f["motor"] for f in log} == {"reglas", "llm"}
    assert api["base"].on_conflict == "ticket_id,motor"


def test_con_el_llm_caido_el_ticket_se_crea_con_reglas(api):
    def caido(req):
        raise httpx.ConnectError("sin red", request=req)
    api["manejador"] = caido
    r = api["cliente"].post("/create-ticket", json=TICKET)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["clasificado_por"] == "reglas"
    assert cuerpo["confianza_ia"] is None and cuerpo["requiere_revision"] is False
    assert [f["motor"] for f in api["base"].filas("classification_log")[0]] == ["reglas"]


def test_confianza_baja_queda_para_revision_humana(api):
    api["manejador"] = lambda req: respuesta_llm(confianza=0.4)
    assert api["cliente"].post("/create-ticket", json=TICKET).json()["requiere_revision"] is True


def test_si_falla_el_registro_el_ticket_igual_se_crea(api):
    api["base"] = SupabaseFalsa(falla_log=RuntimeError("classification_log no existe"))
    r = api["cliente"].post("/create-ticket", json=TICKET)
    assert r.status_code == 200 and r.json()["ticket_id"] == "ticket-1"


def test_sin_supabase_responde_500(api, monkeypatch):
    monkeypatch.setattr(main, "get_supabase", lambda: None)
    assert api["cliente"].post("/create-ticket", json=TICKET).status_code == 500


def test_health_refleja_el_llm_encendido(api):
    estado = api["cliente"].get("/health").json()["clasificacion"]
    assert estado["llm_habilitado"] is True and estado["advertencias"] == []
