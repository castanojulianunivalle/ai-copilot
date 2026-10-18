"""
HU-10 · AISCOP-54: lo que necesita la API para correr en Render.

- /health dice que version y que commit estan corriendo: es la evidencia de
  que la nube ejecuta el tag que se presenta.
- CORS se restringe al frontend con CORS_ORIGINS; sin la variable queda
  abierto, como en local.
"""
from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

import main
from version import VERSION


@pytest.fixture
def cliente():
    return TestClient(main.app)


def test_health_informa_version_y_commit_de_render(cliente, monkeypatch):
    monkeypatch.setenv("RENDER_GIT_COMMIT", "0123456789abcdef0123456789abcdef01234567")
    cuerpo = cliente.get("/health").json()
    assert cuerpo["status"] == "ok"
    assert cuerpo["version"] == VERSION
    assert cuerpo["commit"] == "0123456"


def test_health_en_local_dice_local(cliente, monkeypatch):
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    monkeypatch.delenv("GIT_COMMIT", raising=False)
    assert cliente.get("/health").json()["commit"] == "local"


def test_git_commit_sirve_fuera_de_render(cliente, monkeypatch):
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    monkeypatch.setenv("GIT_COMMIT", "fedcba9876543210")
    assert cliente.get("/health").json()["commit"] == "fedcba9"


def test_version_es_semantica():
    numeros = VERSION.split("-")[0].split(".")
    assert len(numeros) == 3 and all(n.isdigit() for n in numeros)


@pytest.mark.parametrize("valor,esperado", [
    (None, ["*"]),
    ("", ["*"]),
    ("https://aiscop-web.onrender.com", ["https://aiscop-web.onrender.com"]),
    (" https://a.onrender.com/ , http://localhost:5173 ", ["https://a.onrender.com", "http://localhost:5173"]),
])
def test_origenes_cors(monkeypatch, valor, esperado):
    if valor is None:
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("CORS_ORIGINS", valor)
    assert main.origenes_cors() == esperado


@pytest.fixture
def api_con_cors_restringido(monkeypatch):
    """Recarga main con CORS_ORIGINS puesto (el middleware se arma al importar) y la deja como estaba."""
    monkeypatch.setenv("CORS_ORIGINS", "https://aiscop-web.onrender.com")
    yield TestClient(importlib.reload(main).app)
    monkeypatch.delenv("CORS_ORIGINS")
    importlib.reload(main)


def _preflight(cliente, origen):
    return cliente.options("/create-ticket", headers={
        "Origin": origen, "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type"})


def test_cors_acepta_el_frontend_de_render(api_con_cors_restringido):
    r = _preflight(api_con_cors_restringido, "https://aiscop-web.onrender.com")
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "https://aiscop-web.onrender.com"


def test_cors_rechaza_otro_origen(api_con_cors_restringido):
    r = _preflight(api_con_cors_restringido, "https://otro-sitio.example")
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers
