"""
HU-10 · AISCOP-56: busca secretos en el repositorio, en el árbol actual y en todo el historial de git.

    python deploy/revisar_secretos.py

Patrones: llaves secretas y de servicio de Supabase (incluido un JWT con rol service_role), tokens personales de
Supabase, Render, GitHub y Atlassian, llaves de Groq y de Hugging Face, y llaves privadas. La llave anon de Supabase
no cuenta: es pública por diseño y la protegen las políticas RLS.

Nunca imprime un secreto: de cada hallazgo muestra el tipo, dónde está, los primeros caracteres y la longitud.
Termina con código 1 si encuentra algo.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# Hallazgos revisados y aceptados: huella SHA-256 del secreto (nunca el secreto) y por qué no es un riesgo.
EXCEPCIONES = {
    "97c302ac06e1292d33165c409454bb2e80e599684ae072f9b117f4dcd6c55d21":
        "llave service_role del Supabase del Semestre 1 (ref flhgweikfrprnhompkcm), en el historial desde el 21 de marzo "
        "de 2026; el proyecto fue eliminado y su dominio no resuelve (comprobado el 17 de octubre de 2026). AISCOP-61.",
}
PATRONES = {
    "llave secreta de Supabase": r"sb_secret_[A-Za-z0-9_-]{20,}",
    "token personal de Supabase": r"sbp_[A-Za-z0-9]{20,}",
    "llave de la API de Render": r"rnd_[A-Za-z0-9]{20,}",
    "llave de Groq": r"gsk_[A-Za-z0-9]{20,}",
    "token de Hugging Face": r"hf_[A-Za-z0-9]{30,}",
    "token de GitHub": r"(?:ghp|gho|ghu|ghs)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}",
    "token de Atlassian": r"ATATT[A-Za-z0-9_\-=]{30,}",
    "llave privada": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
}
JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.(eyJ[A-Za-z0-9_-]{10,})\.[A-Za-z0-9_-]{10,}")


def rol_de_jwt(carga: str) -> str | None:
    try:
        return json.loads(base64.urlsafe_b64decode(carga + "=" * (-len(carga) % 4))).get("role")
    except (ValueError, json.JSONDecodeError):
        return None


def hallazgos(texto: str):
    for tipo, patron in PATRONES.items():
        for m in re.finditer(patron, texto):
            yield tipo, m.group(0)
    for m in JWT.finditer(texto):
        if rol_de_jwt(m.group(1)) == "service_role":
            yield "JWT de Supabase con rol service_role", m.group(0)


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=True).stdout


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    encontrados = []
    archivos = [a for a in git("ls-files").splitlines() if a]
    yo = Path(__file__).resolve().relative_to(RAIZ).as_posix()
    for archivo in archivos:
        if archivo == yo:          # los patrones de este mismo script no son secretos
            continue
        ruta = RAIZ / archivo
        try:
            texto = ruta.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        encontrados += [("árbol", archivo, t, s) for t, s in hallazgos(texto)]
    commits = git("rev-list", "--all").split()
    historial = git("log", "--all", "-p", "--no-color", "--format=@@commit %H", "--", ".", f":(exclude){yo}")
    actual = None
    for linea in historial.splitlines():
        if linea.startswith("@@commit "):
            actual = linea.split()[1][:7]
            continue
        if linea.startswith("+") and not linea.startswith("+++"):
            encontrados += [("historial", actual, t, s) for t, s in hallazgos(linea)]
    vistos, revisados = set(), set()
    for donde, ubicacion, tipo, secreto in encontrados:
        huella = hashlib.sha256(secreto.encode()).hexdigest()
        if huella in EXCEPCIONES:
            if huella not in revisados:
                print(f"Excepción revisada · {tipo} · {donde} {ubicacion} · {EXCEPCIONES[huella]}")
            revisados.add(huella)
            continue
        clave = (donde, ubicacion, tipo, huella)
        if clave in vistos:
            continue
        vistos.add(clave)
        print(f"HALLAZGO · {tipo} · {donde} {ubicacion} · {secreto[:6]}… ({len(secreto)} caracteres)")
    resumen = f"{len(archivos)} archivos del árbol y {len(commits)} commits del historial"
    if not vistos:
        extra = f" (y {len(revisados)} excepción revisada)" if revisados else ""
        print(f"Sin hallazgos en {resumen}{extra}.")
        return 0
    print(f"{len(vistos)} hallazgos en {resumen}.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
