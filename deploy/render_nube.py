"""
HU-10 · AISCOP-54 y AISCOP-55: los servicios de la demo en Render, declarados en codigo.

    python deploy/render_nube.py plan                     # compara lo declarado con Render; no cambia nada
    python deploy/render_nube.py aplicar                  # crea lo que falte y fija las variables declaradas
    python deploy/render_nube.py desplegar --ref v2.0.0   # despliega el commit de ese tag y espera a que quede vivo

Los servicios no se despliegan solos con cada push (autoDeploy no): en la nube corre solo lo que se
despliega a proposito, y `desplegar` recibe un tag. Volver a la version anterior es desplegar su tag.

Variables de entorno:
    RENDER_API_KEY          llave de la API de Render
    SUPABASE_ACCESS_TOKEN   para leer las llaves del proyecto de Supabase sin copiarlas a mano
    LLM_API_KEY             llave de Groq; si falta se lee de python-api/.env
Los valores secretos solo viajan a la API de Render: el script no los imprime.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

from nube_comun import (REPO, RAIZ, ErrorAPI, leer_env_local, llaves_supabase, pedir, proyecto_supabase,
                        variable)

RENDER = "https://api.render.com/v1"
REGION = "virginia"          # Render en us-east, junto al Supabase de us-east-1
RAMA = "main"
API, WEB = "aiscop-api", "aiscop-web"
SERVICIOS = (API, WEB)
TERMINALES = {"live", "deactivated", "build_failed", "update_failed", "canceled", "pre_deploy_failed"}


def declarados(llaves: dict, urls: dict) -> list[dict]:
    """Lo que debe existir en Render. `urls` trae las URL publicas que Render ya asigno."""
    return [{
        "nombre": API,
        "crear": {"type": "web_service", "name": API, "repo": REPO, "branch": RAMA, "rootDir": "python-api",
                  "autoDeploy": "no",
                  "serviceDetails": {"runtime": "docker", "plan": "free", "region": REGION,
                                     "healthCheckPath": "/health",
                                     "envSpecificDetails": {"dockerfilePath": "./Dockerfile", "dockerContext": "."}}},
        "variables": {
            "SUPABASE_URL": llaves["url"],
            "SUPABASE_SERVICE_ROLE_KEY": llaves["service_role"],
            "LLM_ENABLED": "1",
            "LLM_BASE_URL": "https://api.groq.com/openai/v1",
            "LLM_API_KEY": llaves["llm"],
            "LLM_MODEL": "openai/gpt-oss-20b",
            "LLM_TEMPERATURA": "0",
            "LLM_TIMEOUT": "20",
            "LLM_MAX_REINTENTOS": "2",
            "LLM_MAX_TOKENS": "1500",
            # Mientras el frontend no exista queda abierto; `aplicar` lo cierra en la segunda pasada.
            "CORS_ORIGINS": urls.get(WEB, "*"),
        },
        "secretas": {"SUPABASE_SERVICE_ROLE_KEY", "LLM_API_KEY"},
    }, {
        "nombre": WEB,
        "crear": {"type": "static_site", "name": WEB, "repo": REPO, "branch": RAMA, "rootDir": "frontend",
                  "autoDeploy": "no",
                  "serviceDetails": {"buildCommand": "npm ci --no-audit --no-fund && npm run build",
                                     "publishPath": "dist", "pullRequestPreviewsEnabled": "no"}},
        # Vite incrusta estas variables al construir: no puede ir ninguna secreta. La anon es publica
        # por diseno y la protegen las politicas RLS.
        "variables": {
            "VITE_SUPABASE_URL": llaves["url"],
            "VITE_SUPABASE_ANON_KEY": llaves["anon"],
            "VITE_API_URL": urls.get(API, ""),
            "NODE_VERSION": "20",
        },
        # SPA: cualquier ruta que no sea un archivo sirve index.html (p. ej. el enlace de restablecer contrasena).
        "rutas": [{"type": "rewrite", "source": "/*", "destination": "/index.html"}],
    }]


# ---------------------------------------------------------------------------
# API de Render
# ---------------------------------------------------------------------------
def render(metodo: str, ruta: str, cuerpo=None):
    return pedir(metodo, RENDER + ruta, token=variable("RENDER_API_KEY"), cuerpo=cuerpo)[1]


def buscar(nombre: str) -> dict | None:
    for fila in render("GET", f"/services?name={nombre}&limit=20") or []:
        servicio = fila.get("service", fila)
        if servicio.get("name") == nombre:
            return servicio
    return None


def propietario() -> str:
    if os.getenv("RENDER_OWNER_ID"):
        return os.environ["RENDER_OWNER_ID"]
    filas = render("GET", "/owners?limit=20")
    if not filas:
        sys.exit("La llave de Render no tiene ningun workspace.")
    return filas[0].get("owner", filas[0])["id"]


def url_de(servicio: dict) -> str:
    return (servicio.get("serviceDetails") or {}).get("url", "").rstrip("/")


def variables_actuales(servicio_id: str) -> dict:
    filas = render("GET", f"/services/{servicio_id}/env-vars?limit=100") or []
    return {f.get("envVar", f)["key"]: f.get("envVar", f).get("value") for f in filas}


def llaves_nube() -> dict:
    proyecto = proyecto_supabase()
    if not proyecto:
        sys.exit("No existe el proyecto de Supabase: corre antes `python deploy/supabase_nube.py crear`.")
    llm = os.getenv("LLM_API_KEY") or leer_env_local("LLM_API_KEY")
    if not llm:
        sys.exit("Falta LLM_API_KEY (variable de entorno o python-api/.env).")
    return {**llaves_supabase(proyecto["id"]), "llm": llm}


def urls_existentes() -> tuple[dict, dict]:
    servicios, urls = {}, {}
    for nombre in SERVICIOS:
        s = buscar(nombre)
        if s:
            servicios[nombre], urls[nombre] = s, url_de(s)
    return servicios, urls


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------
def plan(_args) -> int:
    servicios, urls = urls_existentes()
    for d in declarados(llaves_nube(), urls):
        s = servicios.get(d["nombre"])
        if not s:
            print(f"{d['nombre']}: NO EXISTE · `aplicar` lo crea")
            continue
        print(f"{d['nombre']}: {url_de(s)} · rama {s.get('branch')} · autoDeploy {s.get('autoDeploy')} · "
              f"rootDir {s.get('rootDir')}")
        actuales = variables_actuales(s["id"])
        for clave, valor in d["variables"].items():
            if clave not in actuales:
                print(f"   + {clave} falta")
            elif actuales[clave] != valor:
                print(f"   ~ {clave} " + ("(secreta) cambia" if clave in d.get("secretas", ()) else f"{actuales[clave]!r} -> {valor!r}"))
        for clave in sorted(set(actuales) - set(d["variables"])):
            print(f"   - {clave} sobra")
    return 0


def aplicar(_args) -> int:
    llaves = llaves_nube()
    servicios, urls = urls_existentes()
    for d in declarados(llaves, urls):
        if d["nombre"] in servicios:
            continue
        cuerpo = {**d["crear"], "ownerId": propietario(),
                  "envVars": [{"key": k, "value": v} for k, v in d["variables"].items()]}
        creado = render("POST", "/services", cuerpo)
        s = creado.get("service", creado)
        servicios[d["nombre"]], urls[d["nombre"]] = s, url_de(s)
        print(f"creado {d['nombre']}: {urls[d['nombre']]}")
    # Segunda pasada, ya con todas las URL: CORS_ORIGINS de la API y VITE_API_URL del frontend.
    for d in declarados(llaves, urls):
        s = servicios[d["nombre"]]
        render("PUT", f"/services/{s['id']}/env-vars", [{"key": k, "value": v} for k, v in d["variables"].items()])
        print(f"variables de {d['nombre']}: {len(d['variables'])} fijadas")
        for regla in d.get("rutas", []):
            fijar_ruta(s["id"], regla)
    print("Listo. Las variables nuevas aplican en el siguiente deploy: `desplegar --ref <tag>`.")
    return 0


def fijar_ruta(servicio_id: str, regla: dict) -> None:
    # El GET devuelve cada regla envuelta en {"route": ...}; el POST recibe una sola regla.
    actuales = [f.get("route", f) for f in render("GET", f"/services/{servicio_id}/routes") or []]
    if any(r.get("source") == regla["source"] and r.get("destination") == regla["destination"] for r in actuales):
        return
    render("POST", f"/services/{servicio_id}/routes", regla)
    print(f"   ruta {regla['type']} {regla['source']} -> {regla['destination']}")


def commit_de(ref: str) -> str:
    try:
        return subprocess.run(["git", "rev-list", "-n", "1", ref], cwd=RAIZ, capture_output=True, text=True,
                              check=True).stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit(f"No existe la referencia {ref!r} en el repositorio local (git fetch --tags).")


def esperar_deploy(servicio: dict, deploy_id: str, limite_s: int = 1500) -> str:
    inicio, ultimo = time.time(), None
    while time.time() - inicio < limite_s:
        d = render("GET", f"/services/{servicio['id']}/deploys/{deploy_id}")
        estado = d.get("status")
        if estado != ultimo:
            print(f"   {servicio['name']}: {estado} ({int(time.time() - inicio)} s)")
            ultimo = estado
        if estado in TERMINALES:
            return estado
        time.sleep(15)
    return "tiempo agotado"


def desplegar(args) -> int:
    sha = commit_de(args.ref)
    servicios, urls = urls_existentes()
    faltan = [n for n in SERVICIOS if n not in servicios]
    if faltan:
        sys.exit(f"Faltan servicios en Render: {', '.join(faltan)}. Corre `aplicar` primero.")
    print(f"Desplegando {args.ref} = {sha[:7]}")
    resultado = 0
    for nombre, s in servicios.items():
        d = render("POST", f"/services/{s['id']}/deploys", {"clearCache": "do_not_clear", "commitId": sha})
        estado = esperar_deploy(s, d["id"])
        if estado != "live":
            print(f"{nombre}: el deploy termino en {estado}. Revisa los logs en Render.")
            resultado = 1
    if API in urls:
        try:
            salud = pedir("GET", urls[API] + "/health", timeout=120)[1]
            ok = salud.get("commit") == sha[:7]
            print(f"/health: version {salud.get('version')} · commit {salud.get('commit')} "
                  f"({'coincide' if ok else 'NO coincide'} con {args.ref})")
            resultado = resultado or (0 if ok else 1)
        except ErrorAPI as e:
            print(f"/health no respondio: {e}")
            resultado = 1
    return resultado


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Servicios de la demo en Render")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("plan").set_defaults(fn=plan)
    sub.add_parser("aplicar").set_defaults(fn=aplicar)
    p = sub.add_parser("desplegar")
    p.add_argument("--ref", required=True, help="tag o commit a desplegar, por ejemplo v2.0.0")
    p.set_defaults(fn=desplegar)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
