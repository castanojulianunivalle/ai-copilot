"""
Sprint 7 · HU-05 · AISCOP-31: prueba end-to-end de la notificacion.

Levanta un receptor HTTP local que se hace pasar por n8n, dispara el modulo de
notificacion como lo haria la API y comprueba la cadena completa: filtro por
prioridad, forma del payload, y firma HMAC validada como la validaria el nodo de
n8n (reserializando el cuerpo ya parseado, que es donde estuvo el bug).

No necesita Supabase, ni un LLM, ni una instancia de n8n. Corre en cualquier
maquina con la libreria estandar y httpx.

    python python-api/pruebas/prueba_e2e_notificacion.py
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.ERROR)

SECRETO = "secreto-de-prueba"
RECIBIDOS: list[dict] = []


class ReceptorN8N(BaseHTTPRequestHandler):
    """Se comporta como el flujo de n8n: valida la firma y guarda el evento."""

    def do_POST(self):  # noqa: N802
        largo = int(self.headers.get("Content-Length", 0))
        crudo = self.rfile.read(largo)
        firma = self.headers.get("X-Signature-256", "")

        # Reproduce el nodo "Verificar firma HMAC": n8n NO ve los bytes crudos,
        # ve el cuerpo ya parseado y lo vuelve a serializar. Si la API y n8n no
        # coinciden en el formato, la firma falla aqui.
        cuerpo = json.loads(crudo)
        reserializado = json.dumps(
            cuerpo, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        esperada = "sha256=" + hmac.new(SECRETO.encode(), reserializado, hashlib.sha256).hexdigest()

        RECIBIDOS.append({
            "payload": cuerpo,
            "firma_recibida": firma,
            "firma_valida": hmac.compare_digest(firma, esperada),
            "bytes_identicos": crudo == reserializado,
        })
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *args):  # silencia el log del servidor
        pass


def main() -> int:
    servidor = HTTPServer(("127.0.0.1", 0), ReceptorN8N)
    puerto = servidor.server_address[1]
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()

    os.environ.update(
        N8N_WEBHOOK_URL=f"http://127.0.0.1:{puerto}/webhook/aiscop",
        N8N_WEBHOOK_SECRET=SECRETO,
        N8N_PRIORIDADES="Alta",
        APP_URL="https://mesa.example.com",
    )

    from notificaciones import notificar_ticket

    base = {
        "ticket_id": "e2e-001",
        "titulo": "Cobro duplicado en la factura de septiembre",
        "description": "Me cobraron dos veces y nadie responde. Está mal.",
        "category": "Facturación",
        "sentimiento": "Frustrado",
        "prioridad": "Alta",
        "confianza_ia": 0.94,
        "clasificado_por": "llm",
        "requiere_revision": False,
    }

    fallos = []

    def comprobar(nombre: str, condicion: bool, detalle: str = "") -> None:
        print(f"  {'OK  ' if condicion else 'FALLA'} {nombre}" + (f"  -> {detalle}" if detalle and not condicion else ""))
        if not condicion:
            fallos.append(nombre)

    print("Prueba end-to-end de la notificacion a n8n\n")

    print("1. Ticket de prioridad Alta")
    notificar_ticket(base)
    comprobar("llego al receptor", len(RECIBIDOS) == 1, f"recibidos={len(RECIBIDOS)}")
    if RECIBIDOS:
        evento = RECIBIDOS[-1]
        p = evento["payload"]
        comprobar("firma HMAC valida", evento["firma_valida"])
        comprobar("bytes identicos tras reserializar", evento["bytes_identicos"])
        comprobar("evento correcto", p.get("evento") == "ticket.prioritario")
        comprobar("conserva la categoria con tilde", p.get("categoria") == "Facturación", str(p.get("categoria")))
        comprobar("incluye el tono detectado", p.get("sentimiento") == "Frustrado")
        comprobar("incluye la confianza de la IA", p.get("confianza_ia") == 0.94)
        comprobar("enlace accionable al ticket", p.get("url", "").endswith("/?ticket=e2e-001"), str(p.get("url")))

    print("\n2. Ticket de prioridad Media (no debe disparar)")
    antes = len(RECIBIDOS)
    notificar_ticket({**base, "ticket_id": "e2e-002", "prioridad": "Media"})
    comprobar("no se notifica", len(RECIBIDOS) == antes)

    print("\n3. Clasificado por reglas (la IA no estaba disponible)")
    notificar_ticket({**base, "ticket_id": "e2e-003", "clasificado_por": "reglas",
                      "confianza_ia": None, "requiere_revision": False})
    if len(RECIBIDOS) > antes:
        p = RECIBIDOS[-1]["payload"]
        comprobar("firma valida tambien con nulos", RECIBIDOS[-1]["firma_valida"])
        comprobar("marca que no fue la IA", p.get("clasificado_por") == "reglas")

    print("\n4. n8n caido (la API no debe romperse)")
    servidor.shutdown()
    try:
        notificar_ticket({**base, "ticket_id": "e2e-004"})
        comprobar("no propaga excepcion", True)
    except Exception as exc:  # noqa: BLE001
        comprobar("no propaga excepcion", False, str(exc))

    print("\n" + ("TODO CORRECTO" if not fallos else f"FALLAN {len(fallos)}: {fallos}"))
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
