"""
Sprint 6 · HU-09 · AISCOP-51: evaluacion del umbral de revision humana (0.5 frente a 0.9).

Un ticket va a revision humana cuando la confianza que declara el modelo no supera el umbral
(CONFIANZA_REVISION_HUMANA en python-api/ai/parser.py). Este script responde dos preguntas:

1. Cual umbral separa mejor los errores del modelo: para cada umbral cuenta cuantos tickets van a
   revision y cuantos de los errores atrapa. Se elige mirando la particion de practica y se reporta
   sobre la de examen y sobre los 66 (AISCOP-58). Tambien mide una senal alternativa: que el modelo
   y las reglas discrepen.
2. Si el umbral sigue cumpliendo su proposito: los tickets sin informacion suficiente
   (fixtures/sondas_revision.jsonl) deben quedar marcados para revision.

Uso:
    python evaluation/umbral.py           # con lo que haya en cache
    python evaluation/umbral.py --llm     # consulta las sondas que falten con el prompt actual
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "python-api"))
sys.path.insert(0, str(AQUI))

import evaluate as E  # noqa: E402
from particion import cargar, filtrar  # noqa: E402

from ai.parser import CONFIANZA_REVISION_HUMANA  # noqa: E402

UMBRALES = [0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95]
TITULOS = {"practica": "Práctica", "examen": "Examen", "todo": "Los 66 (práctica y examen)"}
SONDAS = AQUI / "fixtures" / "sondas_revision.jsonl"
CACHE_SONDAS = E.CACHE / "sondas"
DESTINO = E.RESULTADOS / "umbral"


def tabla_umbrales(filas: list[dict], cache: dict[str, dict]) -> dict:
    casos = [(cache[f["id"]]["confianza"], cache[f["id"]]["categoria"] == f["categoria_real"],
              cache[f["id"]]["categoria"] != E.classify_with_rules(f["texto"])) for f in filas if f["id"] in cache]
    errores = sum(not ok for _, ok, _ in casos)
    filas_tabla = []
    for u in UMBRALES:
        marcados = [ok for c, ok, _ in casos if c <= u]
        atrapados = sum(not ok for ok in marcados)
        filas_tabla.append({"umbral": u, "a_revision": len(marcados), "carga": round(len(marcados) / len(casos), 4),
                            "errores_atrapados": atrapados, "de_errores": errores})
    discrepan = [ok for _, ok, d in casos if d]
    return {"n": len(casos), "errores": errores,
            "confianza_en_errores": sorted(c for c, ok, _ in casos if not ok),
            "confianza_minima_en_aciertos": min((c for c, ok, _ in casos if ok), default=None),
            "umbrales": filas_tabla,
            "senal_discrepancia_con_reglas": {"a_revision": len(discrepan), "carga": round(len(discrepan) / len(casos), 4),
                                               "errores_atrapados": sum(not ok for ok in discrepan), "de_errores": errores}}


def sondas(consultar: bool, version: str) -> list[dict]:
    filas = [json.loads(l) for l in SONDAS.read_text(encoding="utf-8").splitlines() if l.strip()]
    ruta = CACHE_SONDAS / f"{version}.jsonl"
    cache = E.leer_cache(ruta)
    if consultar and any(f["id"] not in cache for f in filas):
        from dotenv import load_dotenv

        load_dotenv(AQUI.parent / "python-api" / ".env")
        from ai.classifier import clasificar
        from ai.llm_client import ClienteLLM

        cliente = ClienteLLM()
        for f in filas:
            if f["id"] in cache:
                continue
            r = clasificar(f["texto"], E.classify_with_rules, cliente)
            if r.uso_ia:
                c = r.clasificacion
                cache[f["id"]] = {"id": f["id"], "categoria": c.categoria, "confianza": c.confianza,
                                  "justificacion": c.justificacion, "modelo": r.modelo, "latencia_ms": r.latencia_ms}
        E.escribir_cache(ruta, cache)
    return [{"id": f["id"], "texto": f["texto"], "esperado": f["esperado"],
             "confianza": cache.get(f["id"], {}).get("confianza"),
             "a_revision": (cache[f["id"]]["confianza"] <= CONFIANZA_REVISION_HUMANA) if f["id"] in cache else None}
            for f in filas]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evalua el umbral de revision humana")
    parser.add_argument("--llm", action="store_true", help="consulta las sondas que falten con el prompt actual")
    parser.add_argument("--version", default="clasificacion-v2")
    args = parser.parse_args(argv)

    cache = E.leer_cache(E.CACHE / f"{args.version}.jsonl")
    todas = cargar()
    resultado = {
        **E.commit_actual(), "version": args.version, "umbral_vigente": CONFIANZA_REVISION_HUMANA,
        "practica": tabla_umbrales(filtrar(todas, "practica"), cache),
        "examen": tabla_umbrales(filtrar(todas, "examen"), cache),
        "todo": tabla_umbrales(todas, cache),
        "sondas": sondas(args.llm, args.version),
    }
    DESTINO.mkdir(parents=True, exist_ok=True)
    (DESTINO / "umbral.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lineas = [f"# Umbral de revisión humana — {args.version}", "",
              f"> Sprint 6 · AISCOP-51 · commit `{resultado['commit']}` · umbral vigente {CONFIANZA_REVISION_HUMANA}", ""]
    for particion, titulo in TITULOS.items():
        t = resultado[particion]
        lineas += [f"## {titulo}: {t['n']} tickets, {t['errores']} errores del modelo", "",
                   f"Confianza en los errores: {t['confianza_en_errores']} · mínima en los aciertos: "
                   f"{t['confianza_minima_en_aciertos']}", "",
                   "| Umbral | A revisión | Carga | Errores atrapados |", "|---:|---:|---:|---:|"]
        lineas += [f"| ≤ {u['umbral']} | {u['a_revision']} | {u['carga']:.0%} | {u['errores_atrapados']} de {u['de_errores']} |"
                   for u in t["umbrales"]]
        s = t["senal_discrepancia_con_reglas"]
        lineas += ["", f"Señal alternativa, el modelo y las reglas discrepan: {s['a_revision']} a revisión "
                       f"({s['carga']:.0%}), {s['errores_atrapados']} de {s['de_errores']} errores atrapados.", ""]
    lineas += ["## Sondas: tickets sin información suficiente", "", "| Ticket | Confianza | ¿A revisión? |", "|---|---:|---|"]
    lineas += [f"| {s['texto']} | {s['confianza']} | {'sí' if s['a_revision'] else 'no'} |" for s in resultado["sondas"]]
    (DESTINO / "informe.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # en Windows, con la salida redirigida, cp1252 no tiene el signo menor o igual
    print("\n".join(lineas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
