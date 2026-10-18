"""
Sprint 6 · HU-09 · AISCOP-46: evaluacion del LLM contra el motor de reglas.

Corre el motor de reglas sobre una particion del conjunto etiquetado, toma las
predicciones del LLM de la cache de cada version de prompt (o consulta al modelo
por las que falten, con --llm) y compara siempre sobre los mismos tickets:
matriz de confusion, metricas por clase y prueba de McNemar exacta. Si hay mas
de una version de prompt en cache, tambien compara la ultima con la anterior.

Uso:
    python evaluation/evaluate.py                        # examen, con lo que haya en cache
    python evaluation/evaluate.py --particion practica   # lo unico que se mira al ajustar el prompt
    python evaluation/evaluate.py --particion todo       # los 66, comparable con el Avance 2
    python evaluation/evaluate.py --llm                  # completa la cache de la version actual del prompt

Con --llm hacen falta LLM_ENABLED=1 y LLM_API_KEY en el entorno (python-api/.env sirve).
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "python-api"))
sys.path.insert(0, str(AQUI))

from metricas import evaluar, mcnemar  # noqa: E402
from particion import FIXTURE, cargar, filtrar, huella_archivo  # noqa: E402

from ai.reglas import classify_with_rules  # noqa: E402
from ai.taxonomia import CATEGORIAS  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
# El motor de reglas registra una linea por ticket y tapa la salida util.
logging.getLogger("ai.reglas").setLevel(logging.WARNING)
logger = logging.getLogger("evaluate")

RESULTADOS = AQUI / "results"
CACHE = RESULTADOS / "cache"


# ---------------------------------------------------------------------------
# Predicciones
# ---------------------------------------------------------------------------
def predecir_reglas(filas: list[dict]) -> list[str]:
    return [classify_with_rules(f["texto"]) for f in filas]


def leer_cache(ruta: Path) -> dict[str, dict]:
    if not ruta.exists():
        return {}
    registros = (json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip())
    return {r["id"]: r for r in registros}


def escribir_cache(ruta: Path, cache: dict[str, dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="\n") as fh:
        for registro in sorted(cache.values(), key=lambda r: r["id"]):
            fh.write(json.dumps(registro, ensure_ascii=False, sort_keys=True) + "\n")


def consultar_llm(filas: list[dict], pausa: float) -> str:
    """Completa la cache de la version ACTUAL del prompt. Devuelve esa version.

    Un repliegue a reglas nunca se guarda como prediccion del modelo: congelaria
    una caida del proveedor como si fuera un error del modelo.
    """
    from dotenv import load_dotenv

    load_dotenv(RAIZ / "python-api" / ".env")
    from ai.classifier import clasificar
    from ai.llm_client import ClienteLLM
    from ai.prompts import VERSION_PROMPT

    cliente = ClienteLLM()
    if not cliente.habilitado:
        raise SystemExit("El LLM esta deshabilitado: hacen falta LLM_ENABLED=1 y LLM_API_KEY.")
    ruta = CACHE / f"{VERSION_PROMPT}.jsonl"
    cache = leer_cache(ruta)
    pendientes = [f for f in filas if f["id"] not in cache]
    logger.info("Prompt %s: %d en cache, %d por consultar", VERSION_PROMPT, len(cache), len(pendientes))
    for i, fila in enumerate(pendientes, 1):
        resultado = clasificar(fila["texto"], classify_with_rules, cliente)
        if not resultado.uso_ia:
            logger.warning("  [%d/%d] %s cayo a reglas: %s", i, len(pendientes), fila["id"], resultado.error)
            continue
        c = resultado.clasificacion
        cache[fila["id"]] = {
            "id": fila["id"], "categoria": c.categoria, "sentimiento": c.sentimiento,
            "prioridad": c.prioridad, "confianza": c.confianza, "justificacion": c.justificacion,
            "modelo": resultado.modelo, "latencia_ms": resultado.latencia_ms,
        }
        escribir_cache(ruta, cache)          # se guarda en cada paso: una caida no pierde lo ya pagado
        time.sleep(pausa)                    # respeta el limite de solicitudes por minuto del proveedor
    return VERSION_PROMPT


# ---------------------------------------------------------------------------
# Comparacion
# ---------------------------------------------------------------------------
def latencias(predicciones: list[dict]) -> dict[str, int]:
    valores = sorted(p["latencia_ms"] for p in predicciones)
    return {"mediana": valores[len(valores) // 2],
            "p95": valores[min(len(valores) - 1, int(len(valores) * 0.95))],
            "max": valores[-1]}


def comparar_version(filas: list[dict], cache: dict[str, dict], etiquetas: list[str]) -> dict[str, Any] | None:
    comparables = [f for f in filas if f["id"] in cache]
    if not comparables:
        return None
    y_real = [f["categoria_real"] for f in comparables]
    res_llm = evaluar(y_real, [cache[f["id"]]["categoria"] for f in comparables], etiquetas)
    # Reglas sobre el MISMO subconjunto: comparar el LLM sobre 40 tickets contra
    # reglas sobre 44 no seria una comparacion pareada.
    res_reglas = evaluar(y_real, predecir_reglas(comparables), etiquetas)
    prueba = mcnemar(res_reglas.correctos, res_llm.correctos)
    return {
        "cobertura": {"evaluados": len(comparables), "de": len(filas)},
        "modelos": sorted({cache[f["id"]]["modelo"] for f in comparables}),
        "latencia_ms": latencias([cache[f["id"]] for f in comparables]),
        "llm": res_llm.as_dict(),
        "reglas_pareado": res_reglas.as_dict(),
        "mcnemar_vs_reglas": prueba,
        "delta_f1_macro": round(res_llm.f1_macro - res_reglas.f1_macro, 4),
        "delta_exactitud": round(res_llm.exactitud - res_reglas.exactitud, 4),
        "_resultado": res_llm,
        "_ids": [f["id"] for f in comparables],
    }


def comparar_entre_versiones(filas, caches, anterior, actual, etiquetas) -> dict[str, Any] | None:
    comunes = [f for f in filas if f["id"] in caches[anterior] and f["id"] in caches[actual]]
    if not comunes:
        return None
    y_real = [f["categoria_real"] for f in comunes]
    a = evaluar(y_real, [caches[anterior][f["id"]]["categoria"] for f in comunes], etiquetas)
    b = evaluar(y_real, [caches[actual][f["id"]]["categoria"] for f in comunes], etiquetas)
    return {"de": anterior, "a": actual, "n": len(comunes), "mcnemar": mcnemar(a.correctos, b.correctos),
            "delta_f1_macro": round(b.f1_macro - a.f1_macro, 4),
            "delta_exactitud": round(b.exactitud - a.exactitud, 4)}


def commit_actual() -> dict[str, Any]:
    """El commit que produce las cifras, para poder citarlas."""
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                             text=True, check=True).stdout.strip()
        sucio = subprocess.run(["git", "status", "--porcelain", "--", "evaluation", "python-api/ai"], cwd=RAIZ,
                               capture_output=True, text=True, check=True).stdout.strip()
        return {"commit": sha, "arbol_limpio": not sucio}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "arbol_limpio": None}


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------
def tabla_markdown(r: dict, titulo: str) -> str:
    lineas = [f"### {titulo}", "",
              f"- **Exactitud**: {r['exactitud']:.2%} ({r['aciertos']}/{r['n']})",
              f"- **F1 macro**: {r['f1_macro']:.4f} · F1 ponderado {r['f1_ponderado']:.4f}",
              f"- **Precisión macro**: {r['precision_macro']:.4f} · **Recall macro**: {r['recall_macro']:.4f}",
              "", "| Categoría | Precisión | Recall | F1 | Soporte |", "|---|---:|---:|---:|---:|"]
    for etiqueta in r["etiquetas"]:
        m = r["por_clase"][etiqueta]
        lineas.append(f"| {etiqueta} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['soporte']} |")
    return "\n".join(lineas)


def matriz_markdown(r: dict, titulo: str) -> str:
    corto = {e: (e[:6] + "…" if len(e) > 7 else e) for e in r["etiquetas"]}
    filas = [f"### Matriz de confusión — {titulo}", "",
             "| real \\ pred | " + " | ".join(corto[e] for e in r["etiquetas"]) + " |",
             "|---|" + "---:|" * len(r["etiquetas"])]
    for i, etiqueta in enumerate(r["etiquetas"]):
        celdas = [(f"**{v}**" if i == j and v else (str(v) if v else "·")) for j, v in enumerate(r["matriz_confusion"][i])]
        filas.append(f"| **{etiqueta}** | " + " | ".join(celdas) + " |")
    return "\n".join(filas)


def escribir_informe(informe: dict, destino: Path) -> None:
    partes = ["# Evaluación de modelos — AI Support Co-Pilot", "",
              f"> Sprint 6 · HU-09 · generado el {informe['generado_en']} · commit `{informe['commit']}`",
              f"> Partición **{informe['particion']}** · {informe['n']} tickets · huella del conjunto "
              f"`{informe['sha256_fixture'][:12]}`", "",
              tabla_markdown(informe["reglas"], "Motor de reglas (línea base, Semestre 1)"), "",
              matriz_markdown(informe["reglas"], "motor de reglas")]
    for version, v in informe["versiones"].items():
        p = v["mcnemar_vs_reglas"]
        veredicto = ("**es** estadísticamente significativa" if p["significativo"] else "**no** es estadísticamente significativa")
        partes += ["", tabla_markdown(v["llm"], f"LLM · {version} · {', '.join(v['modelos'])}"), "",
                   matriz_markdown(v["llm"], f"LLM {version}"), "",
                   f"**Frente a las reglas, sobre los mismos {v['cobertura']['evaluados']} tickets:** "
                   f"Δ exactitud {v['delta_exactitud']:+.2%}, Δ F1 macro {v['delta_f1_macro']:+.4f}. "
                   f"McNemar: las reglas aciertan y el LLM falla en {p['b']}; el LLM acierta y las reglas fallan en "
                   f"{p['c']}; p = {p['p_valor']:.4f}: la diferencia {veredicto}.", "",
                   f"Latencia: mediana {v['latencia_ms']['mediana']} ms · p95 {v['latencia_ms']['p95']} ms · "
                   f"máx {v['latencia_ms']['max']} ms."]
    c = informe.get("comparacion_versiones")
    if c:
        partes += ["", f"### {c['a']} frente a {c['de']}", "",
                   f"Sobre {c['n']} tickets: Δ exactitud {c['delta_exactitud']:+.2%}, Δ F1 macro {c['delta_f1_macro']:+.4f}. "
                   f"McNemar: {c['de']} acierta y {c['a']} falla en {c['mcnemar']['b']}; al revés, en {c['mcnemar']['c']}; "
                   f"p = {c['mcnemar']['p_valor']:.4f}."]
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evalua el LLM contra el motor de reglas")
    parser.add_argument("--particion", choices=["examen", "practica", "todo"], default="examen")
    parser.add_argument("--llm", action="store_true", help="consulta el modelo por lo que falte en la cache de la version actual")
    parser.add_argument("--pausa", type=float, default=3.0, help="segundos entre consultas al modelo")
    parser.add_argument("--graficas", action="store_true", help="genera las figuras (requiere matplotlib)")
    args = parser.parse_args(argv)

    filas = filtrar(cargar(), args.particion)
    etiquetas = list(CATEGORIAS)
    if args.llm:
        consultar_llm(filas, args.pausa)

    res_reglas = evaluar([f["categoria_real"] for f in filas], predecir_reglas(filas), etiquetas)
    logger.info("Particion %s (%d tickets) · reglas: exactitud %.2f%%, F1 macro %.4f",
                args.particion, len(filas), res_reglas.exactitud * 100, res_reglas.f1_macro)

    caches = {r.stem: leer_cache(r) for r in sorted(CACHE.glob("*.jsonl"))}
    versiones = {}
    for version, cache in caches.items():
        comparacion = comparar_version(filas, cache, etiquetas)
        if comparacion:
            versiones[version] = comparacion
            p = comparacion["mcnemar_vs_reglas"]
            logger.info("%s: exactitud %.2f%%, F1 macro %.4f · McNemar b=%d c=%d p=%.4f", version,
                        comparacion["llm"]["exactitud"] * 100, comparacion["llm"]["f1_macro"], p["b"], p["c"], p["p_valor"])

    informe: dict[str, Any] = {
        "generado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **commit_actual(),
        "particion": args.particion, "fixture": FIXTURE.name, "sha256_fixture": huella_archivo(),
        "n": len(filas), "etiquetas": etiquetas, "reglas": res_reglas.as_dict(),
        "versiones": {k: {c: v for c, v in d.items() if not c.startswith("_")} for k, d in versiones.items()},
    }
    nombres = list(versiones)
    if len(nombres) >= 2:
        informe["comparacion_versiones"] = comparar_entre_versiones(filas, caches, nombres[-2], nombres[-1], etiquetas)

    destino = RESULTADOS / args.particion
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "metricas.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    escribir_informe(informe, destino / "informe.md")

    if args.graficas:
        from graficas import generar
        generar(informe, res_reglas, {k: d["_resultado"] for k, d in versiones.items()}, destino)

    logger.info("Resultados en %s", destino)
    return 0


if __name__ == "__main__":
    sys.exit(main())
