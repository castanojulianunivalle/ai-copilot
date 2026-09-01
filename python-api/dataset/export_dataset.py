"""
Sprint 4 · HU-08 · AISCOP-38: exportacion del dataset historico de tickets.

Extrae la vista `dataset_tickets` de Supabase, normaliza y anonimiza el texto,
reparte en train/test respetando el split determinista que ya calcula la vista y
escribe los artefactos versionables (JSONL + CSV + metadata).

El dataset resultante es el insumo del Sprint 5 (clasificacion con LLM) y del
Sprint 6 (evaluacion IA vs motor de reglas).

Uso:
    python export_dataset.py --out ../../data/dataset            # desde Supabase
    python export_dataset.py --from-file muestra.json --out ./out  # sin red
    python export_dataset.py --out ./out --solo-etiquetados      # solo ground truth
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("export_dataset")

VISTA = "dataset_tickets"
PAGINA = 1000  # PostgREST corta en 1000 filas por peticion

# Campos que viajan al dataset. El orden fija el de las columnas del CSV.
CAMPOS = [
    "ticket_id",
    "created_at",
    "titulo",
    "description",
    "texto",
    "estado",
    "categoria_reglas",
    "categoria_llm",
    "sentimiento_llm",
    "prioridad_llm",
    "confianza_llm",
    "modelo_llm",
    "latencia_llm_ms",
    "categoria_real",
    "sentimiento_real",
    "prioridad_real",
    "etiquetado",
    "split",
]

# ---------------------------------------------------------------------------
# Anonimizacion
# ---------------------------------------------------------------------------
# Los tickets son texto libre escrito por clientes: traen correos, telefonos y
# a veces numeros de documento. El dataset se versiona en el repositorio, asi
# que se redacta antes de escribir, no despues.
# El orden importa: la URL se redacta primero para que el patron de correo no
# se coma un fragmento de una direccion web que contenga '@'. El '+' del
# telefono queda fuera del \b, que solo casa entre caracter de palabra y no.
_PATRONES_PII = [
    (re.compile(r"\bhttps?://\S+"), "<URL>"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<EMAIL>"),
    (re.compile(r"\+?\b(?:\d{1,3}[ -]?)?(?:\d[ -]?){9,14}\b"), "<TELEFONO>"),
]


def anonimizar(texto: str) -> str:
    for patron, reemplazo in _PATRONES_PII:
        texto = patron.sub(reemplazo, texto)
    return texto


def normalizar(texto: str | None) -> str:
    """Colapsa espacios y saltos de linea. No baja a minusculas: el LLM y el
    analisis de sentimiento pierden senal si se destruyen mayusculas y signos."""
    if not texto:
        return ""
    return re.sub(r"\s+", " ", texto).strip()


# ---------------------------------------------------------------------------
# Origen de datos
# ---------------------------------------------------------------------------
def leer_supabase() -> list[dict[str, Any]]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise SystemExit(
            "Faltan SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY. "
            "Exportalas o usa --from-file para trabajar sin red."
        )
    try:
        from supabase import create_client
    except ImportError:
        raise SystemExit("Falta el paquete 'supabase' (pip install -r requirements.txt)")

    cliente = create_client(url, key)
    filas: list[dict[str, Any]] = []
    desde = 0
    while True:
        lote = (
            cliente.table(VISTA)
            .select("*")
            .order("created_at")
            .range(desde, desde + PAGINA - 1)
            .execute()
        )
        if not lote.data:
            break
        filas.extend(lote.data)
        if len(lote.data) < PAGINA:
            break
        desde += PAGINA
    logger.info("Leidas %d filas de %s", len(filas), VISTA)
    return filas


def leer_archivo(ruta: Path) -> list[dict[str, Any]]:
    contenido = json.loads(ruta.read_text(encoding="utf-8"))
    filas = contenido["data"] if isinstance(contenido, dict) else contenido
    logger.info("Leidas %d filas de %s", len(filas), ruta)
    return filas


# ---------------------------------------------------------------------------
# Transformacion
# ---------------------------------------------------------------------------
def transformar(filas: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    salida = []
    for fila in filas:
        titulo = anonimizar(normalizar(fila.get("titulo")))
        descripcion = anonimizar(normalizar(fila.get("description")))
        if not titulo and not descripcion:
            continue  # sin texto no hay nada que clasificar

        registro = {campo: fila.get(campo) for campo in CAMPOS}
        registro["titulo"] = titulo
        registro["description"] = descripcion
        # `texto` es exactamente lo que consumen el motor de reglas y el LLM:
        # se materializa aqui para que entrenamiento y produccion vean lo mismo.
        registro["texto"] = f"{titulo} {descripcion}".strip()
        registro["etiquetado"] = bool(fila.get("categoria_real"))
        salida.append(registro)
    return salida


def baseline_reglas(registros: list[dict[str, Any]]) -> dict[str, Any]:
    """Exactitud del motor de reglas sobre lo que si tiene ground truth.
    Es la cifra contra la que se compara el LLM en el Sprint 6."""
    evaluables = [
        r for r in registros if r.get("categoria_real") and r.get("categoria_reglas")
    ]
    if not evaluables:
        return {"evaluables": 0, "aciertos": 0, "exactitud": None}
    aciertos = sum(1 for r in evaluables if r["categoria_reglas"] == r["categoria_real"])
    return {
        "evaluables": len(evaluables),
        "aciertos": aciertos,
        "exactitud": round(aciertos / len(evaluables), 4),
    }


def _commit_actual() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).resolve().parent,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, OSError):
        return None


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------
def escribir_jsonl(ruta: Path, registros: list[dict[str, Any]]) -> str:
    sha = hashlib.sha256()
    with ruta.open("w", encoding="utf-8", newline="\n") as fh:
        for registro in registros:
            linea = json.dumps(registro, ensure_ascii=False, sort_keys=True)
            fh.write(linea + "\n")
            sha.update(linea.encode("utf-8"))
    return sha.hexdigest()


def escribir_csv(ruta: Path, registros: list[dict[str, Any]]) -> None:
    with ruta.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=CAMPOS, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(registros)


def distribucion(registros: list[dict[str, Any]], campo: str) -> dict[str, int]:
    conteo = Counter(r[campo] for r in registros if r.get(campo))
    return dict(sorted(conteo.items(), key=lambda kv: (-kv[1], kv[0])))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exporta el dataset historico de tickets")
    parser.add_argument("--out", required=True, type=Path, help="Directorio de salida")
    parser.add_argument("--from-file", type=Path, help="Lee de un JSON local en vez de Supabase")
    parser.add_argument(
        "--solo-etiquetados",
        action="store_true",
        help="Exporta unicamente los tickets con ground truth",
    )
    args = parser.parse_args(argv)

    filas = leer_archivo(args.from_file) if args.from_file else leer_supabase()
    registros = transformar(filas)
    if args.solo_etiquetados:
        registros = [r for r in registros if r["etiquetado"]]
    if not registros:
        logger.error("No hay registros que exportar")
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    particiones = {"train": [], "test": []}
    for registro in registros:
        particiones.get(registro.get("split") or "train", particiones["train"]).append(registro)

    checksums = {}
    for nombre, subconjunto in particiones.items():
        if not subconjunto:
            continue
        checksums[nombre] = escribir_jsonl(args.out / f"{nombre}.jsonl", subconjunto)
        escribir_csv(args.out / f"{nombre}.csv", subconjunto)

    fechas = sorted(r["created_at"] for r in registros if r.get("created_at"))
    metadata = {
        "generado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": _commit_actual(),
        "origen": str(args.from_file) if args.from_file else f"supabase:{VISTA}",
        "total": len(registros),
        "particiones": {k: len(v) for k, v in particiones.items() if v},
        "etiquetados": sum(1 for r in registros if r["etiquetado"]),
        "rango_fechas": {"desde": fechas[0], "hasta": fechas[-1]} if fechas else None,
        "distribucion_categoria_real": distribucion(registros, "categoria_real"),
        "distribucion_categoria_reglas": distribucion(registros, "categoria_reglas"),
        "baseline_reglas": baseline_reglas(registros),
        "checksums_sha256": checksums,
        "anonimizacion": [p.pattern for p, _ in _PATRONES_PII],
    }
    (args.out / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    logger.info(
        "Exportados %d registros (%s) -> %s",
        len(registros),
        ", ".join(f"{k}={len(v)}" for k, v in particiones.items() if v),
        args.out,
    )
    base = metadata["baseline_reglas"]
    if base["exactitud"] is not None:
        logger.info(
            "Linea base motor de reglas: %.2f%% (%d/%d etiquetados)",
            base["exactitud"] * 100,
            base["aciertos"],
            base["evaluables"],
        )
    else:
        logger.warning("Sin tickets etiquetados: no hay linea base que medir todavia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
