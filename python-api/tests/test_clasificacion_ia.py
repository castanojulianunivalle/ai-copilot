"""
HU-06 · AISCOP-40: pruebas del componente de clasificacion con LLM.

Cubren los criterios de aceptacion de la historia sin salir a la red: el
cliente acepta un transporte httpx inyectable, asi que cada modo de falla del
proveedor se reproduce con un MockTransport.
"""
from __future__ import annotations

import json

import httpx
import pytest

from ai import llm_client
from ai.classifier import MOTOR_LLM, MOTOR_REGLAS, clasificar
from ai.llm_client import ClienteLLM, ConfigLLM, LLMError
from ai.parser import CONFIANZA_REVISION_HUMANA, RespuestaInvalida, parsear


def reglas(_texto: str) -> str:
    return "Técnico"


def config(**cambios) -> ConfigLLM:
    base = dict(base_url="http://llm.test/v1", api_key="k", modelo="llama-test",
                timeout=1.0, max_reintentos=2, temperatura=0.0, max_tokens=300,
                habilitado=True)
    base.update(cambios)
    return ConfigLLM(**base)


def respuesta_ok(contenido: dict | str) -> httpx.Response:
    texto = contenido if isinstance(contenido, str) else json.dumps(contenido)
    return httpx.Response(200, json={
        "model": "llama-test",
        "choices": [{"message": {"content": texto}}],
        "usage": {"prompt_tokens": 120, "completion_tokens": 40},
    })


def cliente_con(manejador, **cambios) -> ClienteLLM:
    return ClienteLLM(config(**cambios), transporte=httpx.MockTransport(manejador))


@pytest.fixture(autouse=True)
def sin_esperas(monkeypatch):
    # El backoff real dormiria segundos por prueba.
    monkeypatch.setattr(llm_client.time, "sleep", lambda _s: None)


CLASIFICACION = {"categoria": "Facturación", "sentimiento": "Frustrado",
                 "prioridad": "Alta", "confianza": 0.91,
                 "justificacion": "Cobro duplicado en la tarjeta"}


# --- Criterio: la clasificacion nunca falla --------------------------------

def test_llm_deshabilitado_usa_reglas_sin_error():
    r = clasificar("no puedo pagar", reglas, cliente_con(lambda req: respuesta_ok({}), habilitado=False))
    assert r.motor == MOTOR_REGLAS
    assert r.clasificacion.categoria == "Técnico"
    assert r.error is None


def test_llm_caido_cae_a_reglas():
    def caido(req):
        raise httpx.ConnectError("conexion rechazada", request=req)
    r = clasificar("no puedo pagar", reglas, cliente_con(caido))
    assert r.motor == MOTOR_REGLAS
    assert "red" in r.error.lower()


def test_llm_lento_cae_a_reglas():
    def lento(req):
        raise httpx.ReadTimeout("sin respuesta", request=req)
    r = clasificar("no puedo pagar", reglas, cliente_con(lento))
    assert r.motor == MOTOR_REGLAS
    assert r.error


def test_respuesta_ilegible_cae_a_reglas():
    r = clasificar("no puedo pagar", reglas,
                   cliente_con(lambda req: respuesta_ok("lo siento, no puedo ayudar")))
    assert r.motor == MOTOR_REGLAS
    assert "JSON" in r.error


def test_categoria_fuera_de_la_taxonomia_cae_a_reglas():
    r = clasificar("x", reglas, cliente_con(
        lambda req: respuesta_ok({**CLASIFICACION, "categoria": "Astrologia"})))
    assert r.motor == MOTOR_REGLAS


def test_error_de_reglas_se_registra_con_confianza_cero():
    def caido(req):
        raise httpx.ConnectError("x", request=req)
    r = clasificar("x", reglas, cliente_con(caido))
    # 0.0 y no el 0.5 del LLM: si no, se mezclaria en las estadisticas.
    assert r.clasificacion.confianza == 0.0


# --- Reintentos ---------------------------------------------------------------

def test_503_se_reintenta_y_luego_responde():
    llamadas = []
    def intermitente(req):
        llamadas.append(1)
        return httpx.Response(503) if len(llamadas) < 2 else respuesta_ok(CLASIFICACION)
    r = clasificar("x", reglas, cliente_con(intermitente))
    assert r.motor == MOTOR_LLM
    assert len(llamadas) == 2


def test_401_no_se_reintenta():
    llamadas = []
    def no_autorizado(req):
        llamadas.append(1)
        return httpx.Response(401, text="token invalido")
    with pytest.raises(LLMError):
        cliente_con(no_autorizado).completar("s", "u")
    assert len(llamadas) == 1


def test_503_persistente_agota_los_reintentos():
    llamadas = []
    def siempre_503(req):
        llamadas.append(1)
        return httpx.Response(503)
    r = clasificar("x", reglas, cliente_con(siempre_503, max_reintentos=2))
    assert r.motor == MOTOR_REGLAS
    assert len(llamadas) == 3


# --- Criterio: resultado reproducible y persistible ---------------------------

def test_peticion_lleva_temperatura_cero_y_json():
    capturado = {}
    def espia(req):
        capturado.update(json.loads(req.content))
        return respuesta_ok(CLASIFICACION)
    clasificar("x", reglas, cliente_con(espia))
    assert capturado["temperature"] == 0
    assert capturado["response_format"] == {"type": "json_object"}


def test_camino_feliz_devuelve_los_cuatro_campos():
    r = clasificar("me cobraron dos veces", reglas, cliente_con(lambda req: respuesta_ok(CLASIFICACION)))
    c = r.clasificacion
    assert r.motor == MOTOR_LLM
    assert (c.categoria, c.sentimiento, c.prioridad, c.confianza) == ("Facturación", "Frustrado", "Alta", 0.91)
    assert "@" in r.modelo  # modelo@version_del_prompt


# --- Criterio: revision humana --------------------------------------------

@pytest.mark.parametrize("confianza,revisa", [(0.49, True), (0.5, True), (0.51, False), (0.95, False)])
def test_umbral_de_revision_humana_es_inclusivo(confianza, revisa):
    c = parsear(json.dumps({**CLASIFICACION, "confianza": confianza}))
    assert c.requiere_revision is revisa


# --- Parser: lo que devuelven de verdad los modelos abiertos -----------------

def test_json_envuelto_en_vallas_de_codigo():
    assert parsear("```json\n" + json.dumps(CLASIFICACION) + "\n```").categoria == "Facturación"


def test_json_precedido_de_una_frase():
    assert parsear("Claro, aqui tienes: " + json.dumps(CLASIFICACION)).categoria == "Facturación"


def test_coma_sobrante_se_repara():
    assert parsear('{"categoria": "Acceso", "sentimiento": "Neutral",}').categoria == "Acceso"


def test_llaves_dentro_de_la_justificacion_no_parten_el_objeto():
    c = parsear(json.dumps({**CLASIFICACION, "justificacion": "el error dice {code: 42}"}))
    assert c.justificacion == "el error dice {code: 42}"


def test_confianza_en_porcentaje_se_normaliza():
    assert parsear(json.dumps({**CLASIFICACION, "confianza": 85})).confianza == 0.85


def test_sinonimos_y_tildes_se_normalizan():
    assert parsear(json.dumps({**CLASIFICACION, "categoria": "billing"})).categoria == "Facturación"
    assert parsear(json.dumps({**CLASIFICACION, "categoria": "facturacion"})).categoria == "Facturación"


def test_sin_prioridad_se_deriva_del_sentimiento():
    datos = {k: v for k, v in CLASIFICACION.items() if k != "prioridad"}
    assert parsear(json.dumps({**datos, "sentimiento": "Urgente"})).prioridad == "Alta"


def test_sin_confianza_se_asume_el_umbral_y_va_a_revision():
    datos = {k: v for k, v in CLASIFICACION.items() if k != "confianza"}
    c = parsear(json.dumps(datos))
    assert c.confianza == CONFIANZA_REVISION_HUMANA and c.requiere_revision


def test_sin_categoria_es_invalida():
    with pytest.raises(RespuestaInvalida):
        parsear(json.dumps({"sentimiento": "Neutral"}))
