"""
Escenario de la demostración final (Trabajo Integrador III): datos para los reportes (HU-07) y control del flujo
de n8n (HU-05) para mostrar en vivo que la notificación está desacoplada.

    python deploy/escenario_demo.py sembrar     # 40 tickets de los últimos 30 días, a nombre de cliente.demo
    python deploy/escenario_demo.py limpiar     # borra solo los tickets sembrados (marca [demo] en la descripción)
    python deploy/escenario_demo.py n8n on|off  # activa o desactiva el flujo «AISCOP · HU-05 · Ticket urgente → correo»
    python deploy/escenario_demo.py n8n estado  # dice si está activo y muestra sus últimas ejecuciones

Variables de entorno: SUPABASE_ACCESS_TOKEN (para leer las llaves del proyecto), N8N_URL y N8N_API_KEY.
Los tickets sembrados no pasan por la API: no disparan correos ni gastan cuota del LLM. Su clasificación es la que
daría el modelo y sirve para que las gráficas tengan volumen; los tickets de la demostración en vivo sí se crean
desde la aplicación.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone

from nube_comun import llaves_supabase, pedir, proyecto_supabase

MARCA = "[demo]"
FLUJO = "AISCOP · HU-05 · Ticket urgente → correo"

# (título, descripción, categoría, sentimiento, prioridad)
CASOS = [
    ("No puedo iniciar sesión", "Desde ayer la contraseña no funciona y el enlace de recuperación no llega.", "Acceso", "Frustrado", "Alta"),
    ("Cobro duplicado", "En el extracto aparecen dos cobros del mismo mes.", "Facturación", "Frustrado", "Alta"),
    ("La página carga muy lento", "El panel tarda más de un minuto en abrir los reportes.", "Rendimiento", "Neutral", "Media"),
    ("Error al exportar a Excel", "Al exportar sale un archivo vacío.", "Técnico", "Neutral", "Media"),
    ("¿Cómo cambio mi correo?", "Quiero actualizar el correo de la cuenta.", "Consultas", "Neutral", "Baja"),
    ("Inicio de sesión sospechoso", "Me llegó una alerta de acceso desde otro país.", "Seguridad", "Urgente", "Alta"),
    ("El botón de pagar no responde", "En el celular el botón de pago no hace nada.", "Móvil", "Frustrado", "Alta"),
    ("Sugerencia de modo oscuro", "Sería bueno tener modo oscuro en los reportes.", "UX/UI", "Satisfecho", "Baja"),
    ("Webhook de Slack no llega", "La integración con Slack dejó de enviar mensajes.", "Integraciones", "Neutral", "Media"),
    ("Factura con datos errados", "El NIT de la factura no corresponde.", "Facturación", "Neutral", "Media"),
    ("Excelente atención", "Gracias, el problema quedó resuelto rápido.", "Consultas", "Satisfecho", "Baja"),
    ("Caída total del servicio", "Nadie de la empresa puede entrar, es urgente.", "Técnico", "Urgente", "Alta"),
]
ESTADOS = ["Cerrado"] * 5 + ["En proceso"] * 2 + ["Abierto"] * 3


def supabase():
    ll = llaves_supabase(proyecto_supabase()["id"])
    return ll["url"], {"apikey": ll["service_role"], "Authorization": f"Bearer {ll['service_role']}",
                       "Content-Type": "application/json", "Prefer": "return=representation"}


def sembrar(_args) -> int:
    url, h = supabase()
    cliente = pedir("GET", f"{url}/rest/v1/profiles?email=eq.cliente.demo@aiscop.local&select=id", cabeceras=h)[1]
    if not cliente:
        sys.exit("No existe cliente.demo@aiscop.local en la nube.")
    azar, ahora, filas = random.Random(20261120), datetime.now(timezone.utc), []
    for i in range(40):
        titulo, desc, cat, sent, prio = CASOS[i % len(CASOS)]
        llm = azar.random() < 0.9
        confianza = round(azar.uniform(0.55, 0.97), 2) if llm else None
        filas.append({"titulo": titulo, "description": f"{desc} {MARCA}", "category": cat, "sentimiento": sent,
                      "prioridad": prio, "estado": azar.choice(ESTADOS), "created_by": cliente[0]["id"],
                      "clasificado_por": "llm" if llm else "reglas", "confianza_ia": confianza,
                      "motivo_revision": "confianza_baja" if confianza is not None and confianza < 0.6 else None,
                      "created_at": (ahora - timedelta(days=azar.randint(0, 29), hours=azar.randint(0, 20))).isoformat()})
    creadas = pedir("POST", f"{url}/rest/v1/tickets", cabeceras=h, cuerpo=filas)[1]
    print(f"Sembrados {len(creadas)} tickets de los últimos 30 días (marca {MARCA}).")
    return 0


def limpiar(_args) -> int:
    url, h = supabase()
    borradas = pedir("DELETE", f"{url}/rest/v1/tickets?description=like.*{MARCA.replace('[', '%5B').replace(']', '%5D')}",
                     cabeceras=h)[1]
    print(f"Borrados {len(borradas or [])} tickets sembrados.")
    return 0


def n8n_api(metodo: str, ruta: str, cuerpo=None):
    return pedir(metodo, os.environ["N8N_URL"].rstrip("/") + "/api/v1" + ruta, cuerpo=cuerpo,
                 cabeceras={"X-N8N-API-KEY": os.environ["N8N_API_KEY"]})[1]


def n8n(args) -> int:
    flujo = next((w for w in n8n_api("GET", "/workflows?limit=250")["data"] if w["name"] == FLUJO), None)
    if not flujo:
        sys.exit(f"No existe el flujo «{FLUJO}» en n8n.")
    if args.accion in ("on", "off"):
        n8n_api("POST", f"/workflows/{flujo['id']}/{'activate' if args.accion == 'on' else 'deactivate'}", {})
    flujo = n8n_api("GET", f"/workflows/{flujo['id']}")
    print(f"Flujo «{FLUJO}»: {'ACTIVO' if flujo['active'] else 'INACTIVO'}")
    for e in n8n_api("GET", f"/executions?workflowId={flujo['id']}&limit=5")["data"]:
        print(f"  {e['startedAt'][:19]}  {e['status']}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("sembrar").set_defaults(f=sembrar)
    sub.add_parser("limpiar").set_defaults(f=limpiar)
    s = sub.add_parser("n8n")
    s.add_argument("accion", choices=["on", "off", "estado"])
    s.set_defaults(f=n8n)
    args = p.parse_args(argv)
    return args.f(args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
