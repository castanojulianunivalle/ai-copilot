"""
HU-10 · AISCOP-53: el proyecto de Supabase de la demo, reproducible desde el repositorio.

    python deploy/supabase_nube.py estado                # que hay en la nube; no cambia nada
    python deploy/supabase_nube.py crear                 # crea el proyecto si no existe y espera a que este sano
    python deploy/supabase_nube.py migrar [--hasta V]    # aplica en orden las migraciones pendientes (hasta V)
    python deploy/supabase_nube.py auth --sitio URL      # Auth apunta al frontend de Render
    python deploy/supabase_nube.py usuarios              # usuarios de demostracion con su rol

Variables de entorno:
    SUPABASE_ACCESS_TOKEN                        token personal de la Management API
    DEMO_CLIENTE_PASSWORD, DEMO_AGENTE_PASSWORD  solo para `usuarios`

Las migraciones quedan registradas en supabase_migrations.schema_migrations, la misma tabla que usa
la CLI de Supabase, asi que `supabase db push` reconoceria las ya aplicadas.
"""
from __future__ import annotations

import argparse
import secrets
import sys
import time

from nube_comun import RAIZ, PROYECTO_SUPABASE, ErrorAPI, llaves_supabase, pedir, proyecto_supabase, supabase_mgmt, variable

REGION = "us-east-1"
MIGRACIONES = RAIZ / "supabase" / "migrations"
USUARIOS_DEMO = [("cliente.demo@aiscop.local", "cliente", "DEMO_CLIENTE_PASSWORD"),
                 ("agente.demo@aiscop.local", "agente", "DEMO_AGENTE_PASSWORD")]
BITACORA = """
create schema if not exists supabase_migrations;
create table if not exists supabase_migrations.schema_migrations (
  version text primary key, statements text[], name text);
"""


def sql(ref: str, consulta: str) -> list:
    """Ejecuta SQL como postgres mediante la Management API (no hace falta la contrasena de la base)."""
    return supabase_mgmt("POST", f"/v1/projects/{ref}/database/query", {"query": consulta}) or []


def exigir_proyecto() -> dict:
    proyecto = proyecto_supabase()
    if not proyecto:
        sys.exit(f"No existe el proyecto {PROYECTO_SUPABASE}: corre `crear` primero.")
    return proyecto


def esperar_sano(ref: str, limite_s: int = 900) -> None:
    inicio, ultimo = time.time(), None
    while time.time() - inicio < limite_s:
        estado = supabase_mgmt("GET", f"/v1/projects/{ref}").get("status")
        if estado != ultimo:
            print(f"   {ref}: {estado} ({int(time.time() - inicio)} s)")
            ultimo = estado
        if estado == "ACTIVE_HEALTHY":
            return
        time.sleep(10)
    sys.exit(f"El proyecto {ref} no quedo sano en {limite_s} s.")


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------
def estado(_args) -> int:
    proyecto = proyecto_supabase()
    if not proyecto:
        print(f"{PROYECTO_SUPABASE}: no existe")
        return 0
    ref = proyecto["id"]
    print(f"{PROYECTO_SUPABASE}: {ref} · {proyecto.get('status')} · {proyecto.get('region')} · https://{ref}.supabase.co")
    try:
        aplicadas = [f["version"] for f in sql(ref, "select version from supabase_migrations.schema_migrations order by 1")]
    except ErrorAPI:
        aplicadas = []
    for ruta in sorted(MIGRACIONES.glob("*.sql")):
        print(f"   {'aplicada ' if ruta.stem.split('_')[0] in aplicadas else 'PENDIENTE'} {ruta.name}")
    auth = supabase_mgmt("GET", f"/v1/projects/{ref}/config/auth")
    print(f"   auth: site_url {auth.get('site_url')} · autoconfirmacion {auth.get('mailer_autoconfirm')}")
    for fila in sql(ref, "select u.email, p.role from auth.users u left join public.profiles p on p.id = u.id order by 1"):
        print(f"   usuario {fila['email']}: {fila['role']}")
    return 0


def crear(_args) -> int:
    proyecto = proyecto_supabase()
    if proyecto:
        print(f"Ya existe {PROYECTO_SUPABASE}: {proyecto['id']} ({proyecto.get('status')})")
    else:
        organizaciones = supabase_mgmt("GET", "/v1/organizations")
        if not organizaciones:
            sys.exit("El token no tiene ninguna organizacion de Supabase.")
        # La contrasena de la base no se guarda: la Management API no la necesita y se puede
        # restablecer desde el panel si algun dia hace falta conectarse con psql.
        proyecto = supabase_mgmt("POST", "/v1/projects", {
            "name": PROYECTO_SUPABASE, "organization_id": organizaciones[0]["id"],
            "region": REGION, "db_pass": secrets.token_urlsafe(32)})
        print(f"Creado {PROYECTO_SUPABASE}: {proyecto['id']} en {REGION}")
    esperar_sano(proyecto["id"])
    return 0


def migrar(args) -> int:
    ref = exigir_proyecto()["id"]
    sql(ref, BITACORA)
    aplicadas = {f["version"] for f in sql(ref, "select version from supabase_migrations.schema_migrations")}
    for ruta in sorted(MIGRACIONES.glob("*.sql")):
        version, _, nombre = ruta.stem.partition("_")
        if args.hasta and version > args.hasta:
            print(f"se deja pendiente {ruta.name} (--hasta {args.hasta})")
            continue
        if version in aplicadas:
            print(f"ya aplicada {ruta.name}")
            continue
        texto = ruta.read_text(encoding="utf-8")
        if "$migracion$" in texto:
            sys.exit(f"{ruta.name} contiene el delimitador reservado $migracion$.")
        # Migracion y registro en una sola transaccion: o queda todo, o no queda nada.
        sql(ref, f"begin;\n{texto}\n;\ninsert into supabase_migrations.schema_migrations (version, name, statements) "
                 f"values ('{version}', '{nombre}', array[$migracion${texto}$migracion$]);\ncommit;")
        print(f"aplicada {ruta.name}")
    return 0


def auth(args) -> int:
    ref = exigir_proyecto()["id"]
    sitio = args.sitio.rstrip("/")
    supabase_mgmt("PATCH", f"/v1/projects/{ref}/config/auth", {
        "site_url": sitio,
        "uri_allow_list": f"{sitio}/**,http://localhost:5173/**",
        # Demo sin confirmacion por correo: el SMTP gratuito de Supabase solo entrega a los miembros
        # del equipo del proyecto. Con SMTP propio se vuelve a activar (decision de HU-10).
        "mailer_autoconfirm": True,
    })
    print(f"Auth: site_url {sitio}; redirecciones a {sitio}/** y a localhost:5173; sin confirmacion por correo")
    return 0


def usuarios(_args) -> int:
    ref = exigir_proyecto()["id"]
    llaves = llaves_supabase(ref)
    cab = {"apikey": llaves["service_role"]}
    base = f"{llaves['url']}/auth/v1/admin/users"
    existentes = {u["email"]: u["id"] for u in
                  pedir("GET", f"{base}?per_page=200", token=llaves["service_role"], cabeceras=cab)[1].get("users", [])}
    for correo, rol, var in USUARIOS_DEMO:
        datos = {"password": variable(var), "email_confirm": True}
        if correo in existentes:
            uid = existentes[correo]
            pedir("PUT", f"{base}/{uid}", token=llaves["service_role"], cabeceras=cab, cuerpo=datos)
        else:
            uid = pedir("POST", base, token=llaves["service_role"], cabeceras=cab, cuerpo={"email": correo, **datos})[1]["id"]
        # El trigger handle_new_user crea el perfil como cliente; el rol se fija aqui.
        sql(ref, f"update public.profiles set role = '{rol}' where id = '{uid}'")
        print(f"{correo}: {rol}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Proyecto de Supabase de la demo")
    sub = parser.add_subparsers(dest="comando", required=True)
    for nombre, fn in (("estado", estado), ("crear", crear), ("usuarios", usuarios)):
        sub.add_parser(nombre).set_defaults(fn=fn)
    p = sub.add_parser("migrar")
    p.add_argument("--hasta", help="aplica solo hasta esa versión (p. ej. 20260924000000), para verificar una migración "
                                   "con evidencia de antes y después")
    p.set_defaults(fn=migrar)
    p = sub.add_parser("auth")
    p.add_argument("--sitio", required=True, help="URL publica del frontend")
    p.set_defaults(fn=auth)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
