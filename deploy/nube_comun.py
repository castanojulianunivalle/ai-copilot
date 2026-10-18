"""
HU-10: utilidades que comparten los scripts de despliegue de deploy/. Solo libreria estandar.

Los secretos llegan por variables de entorno, viajan solo al proveedor que corresponde y no se
imprimen ni se escriben en disco.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REPO = "https://github.com/castanojulianunivalle/ai-copilot"

# Proyecto de Supabase de la demo (AISCOP-53). La API de Render vive en la misma region de AWS.
PROYECTO_SUPABASE = "aiscop-demo"
SUPABASE_API = "https://api.supabase.com"


class ErrorAPI(RuntimeError):
    def __init__(self, metodo: str, url: str, estado: int, cuerpo: str):
        super().__init__(f"{metodo} {url} -> HTTP {estado}: {cuerpo[:400]}")
        self.estado, self.cuerpo = estado, cuerpo


def pedir(metodo: str, url: str, *, token: str | None = None, cuerpo=None, cabeceras: dict | None = None,
          reintentos: int = 3, timeout: float = 60) -> tuple[int, object]:
    """Peticion HTTP con cuerpo JSON. Reintenta 429, 5xx y fallas de red con espera creciente.

    Devuelve (estado, cuerpo); el cuerpo se decodifica como JSON si se puede y si no queda como texto.
    """
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    h = {"Accept": "application/json", "User-Agent": "aiscop-deploy/1.0", **(cabeceras or {})}
    if token:
        h["Authorization"] = f"Bearer {token}"
    if datos is not None:
        h["Content-Type"] = "application/json"
    for intento in range(reintentos + 1):
        req = urllib.request.Request(url, data=datos, method=metodo, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, _decodificar(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            texto = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and intento < reintentos:
                time.sleep(2 ** intento * 3)
                continue
            raise ErrorAPI(metodo, url, e.code, texto) from None
        except (urllib.error.URLError, TimeoutError):
            if intento < reintentos:
                time.sleep(2 ** intento * 3)
                continue
            raise


def _decodificar(texto: str):
    try:
        return json.loads(texto) if texto.strip() else None
    except json.JSONDecodeError:
        return texto


def variable(nombre: str, *, obligatoria: bool = True) -> str | None:
    valor = (os.getenv(nombre) or "").strip()
    if obligatoria and not valor:
        sys.exit(f"Falta la variable de entorno {nombre}.")
    return valor or None


def leer_env_local(nombre: str) -> str | None:
    """Lee una sola variable de python-api/.env (ignorado por git) sin cargar el resto al entorno."""
    ruta = RAIZ / "python-api" / ".env"
    if not ruta.exists():
        return None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        clave, igual, valor = linea.strip().partition("=")
        if igual and clave.strip() == nombre:
            return valor.strip().strip('"').strip("'") or None
    return None


# ---------------------------------------------------------------------------
# Supabase Management API
# ---------------------------------------------------------------------------
def supabase_mgmt(metodo: str, ruta: str, cuerpo=None):
    return pedir(metodo, SUPABASE_API + ruta, token=variable("SUPABASE_ACCESS_TOKEN"), cuerpo=cuerpo)[1]


def proyecto_supabase(nombre: str = PROYECTO_SUPABASE) -> dict | None:
    return next((p for p in supabase_mgmt("GET", "/v1/projects") if p.get("name") == nombre), None)


def llaves_supabase(ref: str) -> dict:
    """URL y llaves anon y service_role del proyecto.

    Se prefieren las llaves JWT (anon y service_role), que entienden supabase-py 2.8 y la verificacion
    de la API. Si el proyecto solo tiene las nuevas (sb_publishable / sb_secret), se usan esas.
    """
    llaves = supabase_mgmt("GET", f"/v1/projects/{ref}/api-keys?reveal=true")
    por_nombre = {k.get("name"): k.get("api_key") for k in llaves if k.get("api_key")}
    por_tipo = {k.get("type"): k.get("api_key") for k in llaves if k.get("api_key")}
    anon = por_nombre.get("anon") or por_tipo.get("publishable")
    servicio = por_nombre.get("service_role") or por_tipo.get("secret")
    if not anon or not servicio:
        sys.exit(f"El proyecto {ref} no devolvio sus llaves anon y service_role.")
    return {"url": f"https://{ref}.supabase.co", "anon": anon, "service_role": servicio}
