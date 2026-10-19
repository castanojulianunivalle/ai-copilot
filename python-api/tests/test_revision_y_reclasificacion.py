"""
Sprint 7 · HU-11 (motivo de revisión) y HU-12 (reclasificación en segundo plano).

Usa la misma API real con Supabase en memoria y el LLM simulado de test_api_crear_ticket.
"""
from __future__ import annotations

import json

import httpx
import pytest

from ai.revision import MOTIVO_CONFIANZA_BAJA, MOTIVO_URGENTE_SIN_DETALLE, motivo_revision
from tests.test_api_crear_ticket import TICKET, _Consulta, _Tabla, api, respuesta_llm  # noqa: F401  (fixture)


def _update(self, datos):
    tabla = self

    class _Filtro:
        def eq(self, columna, valor):
            return _Consulta(tabla.base, tabla.nombre, "update", {**datos, columna: valor}, None)
    return _Filtro()


def _select(self, _columnas):
    tabla = self

    class _Seleccion:
        def eq(self, *_a):
            return self

        def limit(self, _n):
            return self

        def execute(self):
            return type("R", (), {"data": tabla.base.pendientes})()
    return _Seleccion()


@pytest.fixture(autouse=True)
def tabla_completa(monkeypatch):
    monkeypatch.setattr(_Tabla, "update", _update, raising=False)
    monkeypatch.setattr(_Tabla, "select", _select, raising=False)
    monkeypatch.setenv("RECLASIFICAR_ESPERA_S", "0")


def respuesta(categoria, confianza, prioridad="Media", sentimiento="Neutral"):
    contenido = json.dumps({"categoria": categoria, "sentimiento": sentimiento, "prioridad": prioridad,
                            "confianza": confianza, "justificacion": "prueba"})
    return httpx.Response(200, json={"model": "llama-test", "choices": [{"message": {"content": contenido}}]})


# ------------------------------------------------------------------ HU-11
def test_urgente_sin_detalle_va_a_revision_aunque_la_confianza_sea_alta(api):
    api["manejador"] = lambda req: respuesta("Solicitudes", 0.95, prioridad="Alta", sentimiento="Urgente")
    cuerpo = api["cliente"].post("/create-ticket", json={"titulo": "Urgente",
                                                         "description": "Necesito que me llamen hoy."}).json()
    assert cuerpo["requiere_revision"] is True and cuerpo["motivo_revision"] == MOTIVO_URGENTE_SIN_DETALLE
    assert api["base"].filas("tickets")[0]["motivo_revision"] == MOTIVO_URGENTE_SIN_DETALLE


def test_urgente_con_detalle_no_va_a_revision(api):
    cuerpo = api["cliente"].post("/create-ticket", json=TICKET).json()
    assert cuerpo["requiere_revision"] is False and cuerpo["motivo_revision"] is None


def test_confianza_baja_lleva_su_motivo(api):
    api["manejador"] = lambda req: respuesta_llm(confianza=0.45)
    cuerpo = api["cliente"].post("/create-ticket", json=TICKET).json()
    assert cuerpo["motivo_revision"] == MOTIVO_CONFIANZA_BAJA


def test_lo_que_clasifican_las_reglas_no_tiene_motivo():
    assert motivo_revision("Urgente llamen", "Neutral", "Alta", None, False) is None


# ------------------------------------------------------------------ HU-12
def test_si_el_proveedor_limita_se_reclasifica_en_segundo_plano(api):
    llamadas = {"n": 0}

    def limitado_y_luego_responde(req):
        llamadas["n"] += 1
        if llamadas["n"] <= 3:          # el intento inicial y sus dos reintentos: 429
            return httpx.Response(429, json={"error": {"message": "Rate limit reached"}})
        return respuesta_llm()
    api["manejador"] = limitado_y_luego_responde
    cuerpo = api["cliente"].post("/create-ticket", json=TICKET).json()
    assert cuerpo["clasificado_por"] == "reglas" and cuerpo["reclasificar"] is True
    assert api["base"].filas("tickets")[0]["reclasificar"] is True

    # TestClient corre las tareas en segundo plano al terminar la respuesta
    actualizacion = [f for t, a, f in api["base"].escrituras if t == "tickets" and a == "update"][0]
    assert actualizacion["clasificado_por"] == "llm" and actualizacion["reclasificar"] is False
    assert actualizacion["category"] == "Seguridad" and actualizacion["id"] == "ticket-1"
    assert {f["motor"] for f in api["base"].filas("classification_log")[-1]} == {"reglas", "llm"}


def test_con_el_llm_apagado_no_se_marca_para_reclasificar(api, monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "0")
    cuerpo = api["cliente"].post("/create-ticket", json=TICKET).json()
    assert cuerpo["clasificado_por"] == "reglas" and cuerpo["reclasificar"] is False


def test_reprocesar_pendientes_solo_lo_hace_un_agente(api):
    assert api["cliente"].post("/tickets/reclasificar-pendientes").status_code == 403   # SKIP_AUTH entra como cliente


def test_reprocesar_pendientes(api):
    import main
    main.app.dependency_overrides[main._verify_token] = lambda: ("agente-1", "agente")
    try:
        api["base"].pendientes = [{"id": "t-9", "titulo": "Me cobraron", "description": "dos veces la suscripción"}]
        r = api["cliente"].post("/tickets/reclasificar-pendientes").json()
        assert r == {"pendientes": 1, "reclasificados": 1}
    finally:
        main.app.dependency_overrides.clear()
