"""
HU-10 · AISCOP-57: pruebas de humo y de aceptacion contra la version desplegada en la nube.

    python deploy/pruebas_nube.py                  # humo + aceptacion de HU-06 en la nube
    python deploy/pruebas_nube.py --solo-humo      # lo que corre el workflow diario
    python deploy/pruebas_nube.py --ref v2.0.0     # ademas exige que la nube corra el commit de ese tag
    python deploy/pruebas_nube.py --repliegue      # fuerza la caida del LLM en Render y comprueba el repliegue
                                                   # (necesita RENDER_API_KEY; redespliega la API dos veces)

Variables publicas: AISCOP_WEB_URL, AISCOP_API_URL, SUPABASE_URL, SUPABASE_ANON_KEY.
Secretas: DEMO_CLIENTE_PASSWORD, DEMO_AGENTE_PASSWORD.

Deja un reporte en deploy/evidencia/<fecha>/ (JSON y Markdown) con la version probada y el resultado
de cada caso. Borra al final los tickets que crea. Solo libreria estandar: corre igual en la CI.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from nube_comun import RAIZ, ErrorAPI, pedir, variable

sys.path.insert(0, str(RAIZ / "python-api"))
sys.path.insert(0, str(RAIZ / "evaluation"))
from ai.taxonomia import CATEGORIAS  # noqa: E402  (modulo sin dependencias)
from particion import cargar, filtrar  # noqa: E402

UMBRAL_REVISION = 0.5          # CONFIANZA_REVISION_HUMANA en python-api/ai/parser.py
CLIENTE, AGENTE = "cliente.demo@aiscop.local", "agente.demo@aiscop.local"
CATEGORIAS_PARIDAD = ("Facturación", "Seguridad", "Móvil", "Rendimiento", "Integraciones")
COLOMBIA = timezone(timedelta(hours=-5))


class Contexto:
    def __init__(self, args):
        self.web = variable("AISCOP_WEB_URL").rstrip("/")
        self.api = variable("AISCOP_API_URL").rstrip("/")
        self.supabase = variable("SUPABASE_URL").rstrip("/")
        self.anon = variable("SUPABASE_ANON_KEY")
        self.sha = commit_de(args.ref) if args.ref else None
        self.ref = args.ref
        self.tokens: dict[str, str] = {}
        self.creados: list[str] = []
        self.casos: list[dict] = []
        self.salud: dict = {}


def commit_de(ref: str) -> str:
    return subprocess.run(["git", "rev-list", "-n", "1", ref], cwd=RAIZ, capture_output=True, text=True,
                          check=True).stdout.strip()


# ---------------------------------------------------------------------------
# Registro de casos
# ---------------------------------------------------------------------------
def caso(ctx: Contexto, id_: str, nombre: str, esperado: str):
    """Decorador: ejecuta la prueba, mide su duracion y guarda esperado, obtenido y estado."""
    def envolver(fn):
        inicio = time.time()
        try:
            obtenido, ok = fn()
        except Exception as e:  # noqa: BLE001  una prueba que revienta queda No aprobada, con el motivo
            obtenido, ok = f"error: {e}", False
        fila = {"id": id_, "caso": nombre, "esperado": esperado, "obtenido": obtenido,
                "estado": "Aprobado" if ok else "No aprobado", "duracion_ms": int((time.time() - inicio) * 1000)}
        ctx.casos.append(fila)
        print(f"{'OK ' if ok else 'FALLA'} {id_} {nombre}: {obtenido}")
        return fila
    return envolver


def estado_http(fn) -> int:
    try:
        return fn()[0]
    except ErrorAPI as e:
        return e.estado


# ---------------------------------------------------------------------------
# Acceso a los servicios
# ---------------------------------------------------------------------------
def iniciar_sesion(ctx: Contexto, correo: str, contrasena: str) -> str:
    r = pedir("POST", f"{ctx.supabase}/auth/v1/token?grant_type=password", cabeceras={"apikey": ctx.anon},
              cuerpo={"email": correo, "password": contrasena})[1]
    return r["access_token"]


def api(ctx: Contexto, metodo: str, ruta: str, rol: str | None = None, cuerpo=None, token: str | None = None):
    return pedir(metodo, ctx.api + ruta, token=token or (ctx.tokens[rol] if rol else None), cuerpo=cuerpo,
                 timeout=120)


def rest(ctx: Contexto, ruta: str, rol: str | None):
    cab = {"apikey": ctx.anon}
    return pedir("GET", f"{ctx.supabase}/rest/v1/{ruta}", token=ctx.tokens[rol] if rol else None,
                 cabeceras=cab, reintentos=1)


def dividir(texto: str) -> tuple[str, str]:
    """Titulo y descripcion tales que la API reconstruya exactamente el texto evaluado en local."""
    m = re.search(r"[.?!] ", texto)
    if m:
        corte = m.end() - 1
    else:  # una sola oracion: las seis primeras palabras hacen de titulo
        espacios = [i for i, c in enumerate(texto) if c == " "]
        corte = espacios[min(5, len(espacios) - 1)]
    titulo, descripcion = texto[:corte], texto[corte + 1:]
    assert f"{titulo} {descripcion}" == texto
    return titulo, descripcion


def crear_ticket(ctx: Contexto, titulo: str, descripcion: str) -> dict:
    r = api(ctx, "POST", "/create-ticket", "cliente", {"titulo": titulo, "description": descripcion})[1]
    ctx.creados.append(r["ticket_id"])
    return r


# ---------------------------------------------------------------------------
# Humo (guia del Avance 3, seccion 11.C)
# ---------------------------------------------------------------------------
def humo(ctx: Contexto) -> None:
    @caso(ctx, "TC-H1", "Acceso a la aplicacion web",
          "200; el bundle apunta a la API de la nube" + (f" y lleva el commit {ctx.sha[:7]}" if ctx.sha else ""))
    def _():
        html = pedir("GET", ctx.web + "/", cabeceras={"Accept": "text/html"}, timeout=60)[1]
        script = re.search(r'src="(/assets/[^"]+\.js)"', html)
        bundle = pedir("GET", ctx.web + script.group(1), cabeceras={"Accept": "*/*"})[1] if script else ""
        version = re.search(r"Frontend v", bundle) is not None
        ok = '<div id="root">' in html and ctx.api in bundle and version and (not ctx.sha or ctx.sha[:7] in bundle)
        return f"index y bundle {script.group(1) if script else '(sin bundle)'}; API de la nube en el bundle: {ctx.api in bundle}", ok

    @caso(ctx, "TC-H2", "La API responde con la version prevista",
          "200; llm_habilitado true, sin advertencias" + (f"; commit {ctx.sha[:7]}" if ctx.sha else ""))
    def _():
        ctx.salud = pedir("GET", ctx.api + "/health", timeout=150, reintentos=4)[1]
        c = ctx.salud.get("clasificacion", {})
        ok = (ctx.salud.get("status") == "ok" and c.get("llm_habilitado") is True and not c.get("advertencias")
              and (not ctx.sha or ctx.salud.get("commit") == ctx.sha[:7]))
        return f"version {ctx.salud.get('version')} · commit {ctx.salud.get('commit')} · {c.get('modelo')}", ok

    @caso(ctx, "TC-H3", "Autenticacion de cliente y agente", "token de Supabase Auth; /me devuelve el rol de cada uno")
    def _():
        roles = {}
        for rol, correo, var in (("cliente", CLIENTE, "DEMO_CLIENTE_PASSWORD"), ("agente", AGENTE, "DEMO_AGENTE_PASSWORD")):
            ctx.tokens[rol] = iniciar_sesion(ctx, correo, variable(var))
            roles[rol] = api(ctx, "GET", "/me", rol)[1]["role"]
        return f"/me: {roles}", roles == {"cliente": "cliente", "agente": "agente"}

    @caso(ctx, "TC-H4", "Persistencia y servicio inteligente",
          "el ticket se crea clasificado por el LLM, el agente lo lee y quedan las dos predicciones en el log")
    def _():
        t = crear_ticket(ctx, "Me cobraron dos veces", "En el extracto de este mes aparece dos veces el cargo de la suscripción.")
        fila = rest(ctx, f"tickets?id=eq.{t['ticket_id']}&select=category,clasificado_por,confianza_ia", "agente")[1]
        log = rest(ctx, f"classification_log?ticket_id=eq.{t['ticket_id']}&select=motor", "agente")[1]
        motores = sorted(f["motor"] for f in log)
        ok = (t["clasificado_por"] == "llm" and t["category"] in CATEGORIAS and 0 <= (t["confianza_ia"] or -1) <= 1
              and len(fila) == 1 and fila[0]["category"] == t["category"] and motores == ["llm", "reglas"])
        return f"{t['category']} · confianza {t['confianza_ia']} · el agente lo ve: {len(fila) == 1} · log {motores}", ok

    @caso(ctx, "TC-H5", "Manejo de errores y permisos",
          "token invalido 401; agente creando ticket 403; sin sesion no se leen tickets ni la vista del dataset")
    def _():
        malo = estado_http(lambda: api(ctx, "POST", "/create-ticket", cuerpo={"titulo": "x", "description": "y"}, token="token-invalido"))
        agente = estado_http(lambda: api(ctx, "POST", "/create-ticket", "agente", {"titulo": "x", "description": "y"}))
        anon_tickets = estado_http(lambda: rest(ctx, "tickets?select=id&limit=1", None))
        anon_vista = estado_http(lambda: rest(ctx, "dataset_tickets?select=ticket_id&limit=1", None))
        ok = malo == 401 and agente == 403 and anon_tickets in (401, 403) and anon_vista in (401, 403)
        return f"token invalido {malo} · agente {agente} · anon tickets {anon_tickets} · anon vista {anon_vista}", ok


# ---------------------------------------------------------------------------
# Aceptacion de HU-06 repetida en la nube (HU-10, CA-5)
# ---------------------------------------------------------------------------
def tickets_paridad() -> list[dict]:
    """Un ticket de examen por categoria que el prompt v2 clasifico bien en local, con su prediccion."""
    cache = {}
    for linea in (RAIZ / "evaluation" / "results" / "cache" / "clasificacion-v2.jsonl").read_text(encoding="utf-8").splitlines():
        if linea.strip():
            fila = json.loads(linea)
            cache[fila["id"]] = fila
    elegidos = []
    for categoria in CATEGORIAS_PARIDAD:
        for f in sorted(filtrar(cargar(), "examen"), key=lambda f: f["id"]):
            if f["categoria_real"] == categoria and cache.get(f["id"], {}).get("categoria") == categoria:
                elegidos.append({**f, "local": cache[f["id"]]})
                break
    return elegidos


def aceptacion(ctx: Contexto) -> None:
    @caso(ctx, "TC-A1", "HU-06 · clasificacion con el modelo, igual que en local",
          f"la nube da la misma categoria que la evaluacion local en {len(CATEGORIAS_PARIDAD)} tickets de examen")
    def _():
        resultados = []
        for f in tickets_paridad():
            t = crear_ticket(ctx, *dividir(f["texto"]))
            resultados.append((f["id"], f["local"]["categoria"], t["category"], t["clasificado_por"]))
        iguales = sum(1 for _, local, nube, motor in resultados if local == nube and motor == "llm")
        detalle = "; ".join(f"{i}: local {l} / nube {n}" for i, l, n, _ in resultados)
        return f"{iguales} de {len(resultados)} iguales ({detalle})", iguales == len(resultados) == len(CATEGORIAS_PARIDAD)

    @caso(ctx, "TC-A2", "HU-06 · revision humana con confianza baja",
          f"un ticket sin informacion queda con confianza <= {UMBRAL_REVISION} y requiere_revision true")
    def _():
        t = crear_ticket(ctx, "Consulta", "Hola, tengo una duda.")
        ok = t["clasificado_por"] == "llm" and t["confianza_ia"] <= UMBRAL_REVISION and t["requiere_revision"] is True
        return f"{t['category']} · confianza {t['confianza_ia']} · requiere_revision {t['requiere_revision']}", ok


def repliegue(ctx: Contexto) -> None:
    """Fuerza que el LLM no responda a tiempo (LLM_TIMEOUT casi cero) y comprueba que la API clasifica con reglas.

    Toca la configuracion de Render y redespliega la API dos veces: se corre a proposito, no en el workflow diario.
    """
    import render_nube as R

    servicio = R.buscar(R.API)
    commit = ctx.sha

    def fijar_timeout(valor: str) -> str:
        R.render("PUT", f"/services/{servicio['id']}/env-vars/LLM_TIMEOUT", {"value": valor})
        d = R.render("POST", f"/services/{servicio['id']}/deploys", {"clearCache": "do_not_clear", "commitId": commit})
        return R.esperar_deploy(servicio, d["id"])

    @caso(ctx, "TC-A3", "HU-06 · repliegue al motor de reglas cuando el LLM no responde",
          "con LLM_TIMEOUT=0.001 el ticket se crea igual, clasificado por reglas; al restaurar vuelve el LLM")
    def _():
        try:
            caido = fijar_timeout("0.001")
            t = crear_ticket(ctx, "Me cobraron dos veces", "En el extracto de este mes aparece dos veces el cargo de la suscripción.")
        finally:
            restaurado = fijar_timeout("20")
        t2 = crear_ticket(ctx, "Me cobraron dos veces", "En el extracto de este mes aparece dos veces el cargo de la suscripción.")
        ok = (caido == "live" and restaurado == "live" and t["clasificado_por"] == "reglas" and t["confianza_ia"] is None
              and t2["clasificado_por"] == "llm")
        return (f"caido: {t['category']} por {t['clasificado_por']} · restaurado: {t2['category']} por {t2['clasificado_por']}"
                f" · deploys {caido}/{restaurado}"), ok


def limpiar(ctx: Contexto) -> None:
    borrados = 0
    for ticket_id in ctx.creados:
        try:
            api(ctx, "DELETE", f"/tickets/{ticket_id}", "cliente")
            borrados += 1
        except ErrorAPI as e:
            print(f"No se pudo borrar el ticket {ticket_id}: {e}")
    print(f"Tickets de prueba borrados: {borrados} de {len(ctx.creados)}")


def reporte(ctx: Contexto, modo: str) -> Path:
    ahora = datetime.now(timezone.utc)
    destino = RAIZ / "deploy" / "evidencia" / ahora.astimezone(COLOMBIA).strftime("%Y-%m-%d_%H%M")
    destino.mkdir(parents=True, exist_ok=True)
    aprobados = sum(c["estado"] == "Aprobado" for c in ctx.casos)
    datos = {"fecha_utc": ahora.isoformat(timespec="seconds"),
             "fecha_colombia": ahora.astimezone(COLOMBIA).strftime("%Y-%m-%d %H:%M"),
             "modo": modo, "web": ctx.web, "api": ctx.api, "ref": ctx.ref, "commit_esperado": ctx.sha,
             "version_api": ctx.salud.get("version"), "commit_api": ctx.salud.get("commit"),
             "aprobados": aprobados, "total": len(ctx.casos), "casos": ctx.casos}
    (destino / "reporte.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lineas = [f"# Pruebas en la nube — {datos['fecha_colombia']} (hora de Colombia)", "",
              f"- Modo: {modo} · Web: {ctx.web} · API: {ctx.api}",
              f"- Version que reporta la API: {datos['version_api']} · commit {datos['commit_api']}"
              + (f" · esperado {ctx.ref} = {ctx.sha[:7]}" if ctx.sha else ""),
              f"- **{aprobados} de {len(ctx.casos)} casos aprobados**", "",
              "| Caso | Prueba | Resultado esperado | Resultado obtenido | Estado |", "|---|---|---|---|---|"]
    lineas += [f"| {c['id']} | {c['caso']} | {c['esperado']} | {c['obtenido']} | {c['estado']} |" for c in ctx.casos]
    (destino / "reporte.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return destino


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Pruebas de humo y de aceptacion en la nube")
    parser.add_argument("--solo-humo", action="store_true")
    parser.add_argument("--ref", help="tag o commit que debe estar corriendo, por ejemplo v2.0.0")
    parser.add_argument("--repliegue", action="store_true", help="incluye la prueba de repliegue (toca Render)")
    args = parser.parse_args(argv)
    if args.repliegue and not args.ref:
        parser.error("--repliegue necesita --ref: redespliega la API y debe hacerlo con el commit que ya corre")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ctx = Contexto(args)
    modo = "humo" if args.solo_humo else "humo y aceptacion"
    try:
        humo(ctx)
        if not args.solo_humo and "cliente" in ctx.tokens:
            aceptacion(ctx)
            if args.repliegue:
                modo += " con repliegue"
                repliegue(ctx)
    finally:
        if "cliente" in ctx.tokens:
            limpiar(ctx)
        destino = reporte(ctx, modo)
    aprobados = sum(c["estado"] == "Aprobado" for c in ctx.casos)
    print(f"\n{aprobados} de {len(ctx.casos)} casos aprobados · reporte en {destino.relative_to(RAIZ)}")
    return 0 if aprobados == len(ctx.casos) else 1


if __name__ == "__main__":
    sys.exit(main())
