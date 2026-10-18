"""
HU-06 · AISCOP-41: configuracion del cliente del LLM desde el entorno.

Motivo: setup-env.sh generaba HF_API_TOKEN, HF_MODEL y LLM_API_BASE_URL, pero el
cliente solo leia LLM_API_KEY, LLM_MODEL y LLM_BASE_URL, y LLM_ENABLED no lo
generaba nadie. Con ese .env la API clasificaba solo con reglas y nada fallaba.
"""
from __future__ import annotations

import pytest

from ai.llm_client import ConfigLLM

VARIABLES = ("LLM_ENABLED", "LLM_BASE_URL", "LLM_API_BASE_URL", "LLM_API_KEY", "HF_API_TOKEN",
             "LLM_MODEL", "HF_MODEL", "LLM_TIMEOUT", "LLM_MAX_REINTENTOS", "LLM_TEMPERATURA",
             "LLM_MAX_TOKENS")


@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch):
    for v in VARIABLES:
        monkeypatch.delenv(v, raising=False)


def test_sin_variables_queda_apagado_y_con_valores_por_defecto():
    c = ConfigLLM.desde_entorno()
    assert not c.habilitado
    assert c.base_url == "https://api.groq.com/openai/v1"
    assert c.modelo == "openai/gpt-oss-20b"
    assert c.temperatura == 0


def test_acepta_los_nombres_que_generaba_setup_env(monkeypatch):
    monkeypatch.setenv("HF_API_TOKEN", "hf_viejo")
    monkeypatch.setenv("HF_MODEL", "otro/modelo")
    c = ConfigLLM.desde_entorno()
    assert c.api_key == "hf_viejo"
    assert c.modelo == "otro/modelo"


def test_los_nombres_nuevos_tienen_prioridad(monkeypatch):
    monkeypatch.setenv("HF_API_TOKEN", "hf_viejo")
    monkeypatch.setenv("LLM_API_KEY", "hf_nuevo")
    monkeypatch.setenv("HF_MODEL", "viejo/modelo")
    monkeypatch.setenv("LLM_MODEL", "nuevo/modelo")
    c = ConfigLLM.desde_entorno()
    assert (c.api_key, c.modelo) == ("hf_nuevo", "nuevo/modelo")


@pytest.mark.parametrize("variable", ["LLM_BASE_URL", "LLM_API_BASE_URL"])
def test_la_url_con_chat_completions_no_duplica_la_ruta(monkeypatch, variable):
    monkeypatch.setenv(variable, "https://router.huggingface.co/v1/chat/completions/")
    assert ConfigLLM.desde_entorno().base_url == "https://router.huggingface.co/v1"


def test_avisa_si_hay_key_pero_el_llm_esta_apagado(monkeypatch):
    monkeypatch.setenv("HF_API_TOKEN", "hf_x")
    avisos = ConfigLLM.desde_entorno().advertencias()
    assert any("LLM_ENABLED" in a for a in avisos)


def test_avisa_si_esta_encendido_sin_key_contra_el_router(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "1")
    avisos = ConfigLLM.desde_entorno().advertencias()
    assert any("401" in a for a in avisos)


def test_configuracion_correcta_no_da_avisos(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "1")
    monkeypatch.setenv("LLM_API_KEY", "hf_x")
    assert ConfigLLM.desde_entorno().advertencias() == []


def test_un_servidor_local_sin_key_no_da_aviso(monkeypatch):
    # Ollama o vLLM no piden key: no es un error de configuracion.
    monkeypatch.setenv("LLM_ENABLED", "1")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    assert ConfigLLM.desde_entorno().advertencias() == []


def test_el_estado_publicado_nunca_incluye_la_key(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "1")
    monkeypatch.setenv("LLM_API_KEY", "hf_secreto_123")
    estado = ConfigLLM.desde_entorno().estado()
    assert estado == {"llm_habilitado": True, "modelo": "openai/gpt-oss-20b",
                      "proveedor": "api.groq.com", "tiene_api_key": True}
    assert "hf_secreto_123" not in str(estado)

def test_hugging_face_sigue_disponible_con_dos_variables(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://router.huggingface.co/v1")
    monkeypatch.setenv("LLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    c = ConfigLLM.desde_entorno()
    assert (c.estado()["proveedor"], c.modelo) == ("router.huggingface.co", "meta-llama/Llama-3.1-8B-Instruct")


@pytest.mark.parametrize("url", ["https://api.groq.com/openai/v1", "https://router.huggingface.co/v1"])
def test_avisa_sin_key_contra_cualquier_proveedor_remoto(monkeypatch, url):
    monkeypatch.setenv("LLM_ENABLED", "1")
    monkeypatch.setenv("LLM_BASE_URL", url)
    assert any("401" in a for a in ConfigLLM.desde_entorno().advertencias())
