"""
Sprint 6 · HU-09 · AISCOP-46: evaluacion del LLM contra el motor de reglas.

Corre ambos motores sobre el mismo conjunto etiquetado, calcula matriz de
confusion y metricas por clase, y contrasta la diferencia con la prueba de
McNemar. Escribe los resultados en JSON y en Markdown.

Uso:
    # Solo la linea base de reglas (no necesita credenciales)
    python evaluation/evaluate.py

    # Con el LLM, guardando las predicciones en cache
    export LLM_ENABLED=1 LLM_API_KEY=hf_xxx
    python evaluation/evaluate.py --llm

    # Reusando la cache, sin volver a pagar tokens
    python evaluation/evaluate.py
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "python-api"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from metricas import evaluar, mcnemar  # noqa: E402

from ai.reglas import classify_with_rules  # noqa: E402
from ai.taxonomia import CATEGORIAS  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
# El motor de reglas registra una linea por ticket; con 66 tickets tapa la
# salida util del script.
logging.getLogger("ai.reglas").setLevel(logging.WARNING)
logger = logging.getLogger("evaluate")

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tickets_etiquetados.jsonl"
SALIDA = Path(__file__).resolve().parent / "results"


def cargar_fixture(ruta: Path) -> list[dict[str, Any]]:
    filas = [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]
    fuera = {f["categoria_real"] for f in filas} - set(CATEGORIAS)
    if fuera:
        raise SystemExit(f"El fixture tiene categorias fuera de la taxonomia: {sorted(fuera)}")
    return filas


# ---------------------------------------------------------------------------
# Predicciones
# ---------------------------------------------------------------------------
def predecir_reglas(filas: list[dict]) -> list[str]:
    return [classify_with_rules(f["texto"]) for f in filas]


def cargar_cache(ruta: Path) -> dict[str, dict]:
    if not ruta.exists():
        return {}
    cache = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.strip():
            registro = json.loads(linea)
            cache[registro["id"]] = registro
    return cache


def predecir_llm(filas: list[dict], cache_ruta: Path, forzar: bool, consultar: bool) -> dict[str, dict]:
    """Devuelve {id: prediccion}. Solo llama al modelo por lo que falte en cache.

    La cache es lo que hace la evaluacion repetible sin volver a pagar tokens y,
    sobre todo, lo que permite que la cifra publicada en el articulo provenga de
    unas predicciones concretas y auditables, no de una corrida irrepetible.
    """
    cache = cargar_cache(cache_ruta)
    pendientes = [f for f in filas if forzar or f["id"] not in cache]

    if not pendientes:
        logger.info("Predicciones del LLM tomadas de cache (%d)", len(cache))
        return cache

    if not consultar:
        # Cache parcial y sin --llm: se evalua con lo que hay en vez de abortar.
        # Una cache incompleta es el estado normal despues de una corrida en la
        # que el proveedor fallo en algunos tickets.
        logger.info(
            "Cache con %d de %d predicciones; faltan %d. Usa --llm para completarlas.",
            len(cache), len(filas), len(pendientes),
        )
        return cache

    from ai.classifier import clasificar
    from ai.llm_client import ClienteLLM

    cliente = ClienteLLM()
    if not cliente.habilitado:
        raise SystemExit(
            "El LLM esta deshabilitado. Exporta LLM_ENABLED=1 y LLM_API_KEY, "
            "o corre sin --llm para evaluar solo la linea base."
        )

    logger.info("Consultando el LLM para %d tickets...", len(pendientes))
    for i, fila in enumerate(pendientes, 1):
        resultado = clasificar(fila["texto"], classify_with_rules, cliente)
        if not resultado.uso_ia:
            # No se cachea un fallback: si se guardara, una caida transitoria
            # del proveedor quedaria congelada como si fuera la prediccion del
            # modelo y contaria como error suyo en las metricas.
            logger.warning("  [%d/%d] %s cayo a reglas: %s", i, len(pendientes), fila["id"], resultado.error)
            continue
        c = resultado.clasificacion
        cache[fila["id"]] = {
            "id": fila["id"],
            "categoria": c.categoria,
            "sentimiento": c.sentimiento,
            "prioridad": c.prioridad,
            "confianza": c.confianza,
            "justificacion": c.justificacion,
            "modelo": resultado.modelo,
            "latencia_ms": resultado.latencia_ms,
        }
        if i % 10 == 0:
            logger.info("  [%d/%d]", i, len(pendientes))

    cache_ruta.parent.mkdir(parents=True, exist_ok=True)
    with cache_ruta.open("w", encoding="utf-8", newline="\n") as fh:
        for registro in cache.values():
            fh.write(json.dumps(registro, ensure_ascii=False, sort_keys=True) + "\n")
    logger.info("Cache de predicciones guardada en %s", cache_ruta)
    return cache


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------
def tabla_markdown(resultado, titulo: str) -> str:
    lineas = [
        f"### {titulo}",
        "",
        f"- **Exactitud**: {resultado.exactitud:.2%} ({resultado.aciertos}/{resultado.n})",
        f"- **F1 macro**: {resultado.f1_macro:.4f}",
        f"- **F1 ponderado**: {resultado.f1_ponderado:.4f}",
        f"- **Precisión macro**: {resultado.precision_macro:.4f}",
        f"- **Recall macro**: {resultado.recall_macro:.4f}",
        "",
        "| Categoría | Precisión | Recall | F1 | Soporte |",
        "|---|---:|---:|---:|---:|",
    ]
    for etiqueta in resultado.etiquetas:
        m = resultado.por_clase[etiqueta]
        lineas.append(f"| {etiqueta} | {m.precision:.3f} | {m.recall:.3f} | {m.f1:.3f} | {m.soporte} |")
    return "\n".join(lineas)


def matriz_markdown(resultado, titulo: str) -> str:
    corto = {e: (e[:6] + "…" if len(e) > 7 else e) for e in resultado.etiquetas}
    cabecera = "| real \\ pred | " + " | ".join(corto[e] for e in resultado.etiquetas) + " |"
    sep = "|---|" + "---:|" * len(resultado.etiquetas)
    filas = []
    for i, etiqueta in enumerate(resultado.etiquetas):
        celdas = []
        for j, valor in enumerate(resultado.matriz[i]):
            celdas.append(f"**{valor}**" if i == j and valor else (str(valor) if valor else "·"))
        filas.append(f"| **{etiqueta}** | " + " | ".join(celdas) + " |")
    return "\n".join([f"### Matriz de confusión — {titulo}", "", cabecera, sep, *filas])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evalua LLM vs motor de reglas")
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--out", type=Path, default=SALIDA)
    parser.add_argument("--llm", action="store_true", help="Consulta el LLM por lo que falte en cache")
    parser.add_argument("--forzar", action="store_true", help="Ignora la cache y vuelve a consultar")
    args = parser.parse_args(argv)

    filas = cargar_fixture(args.fixture)
    etiquetas = list(CATEGORIAS)
    y_real = [f["categoria_real"] for f in filas]
    args.out.mkdir(parents=True, exist_ok=True)
    cache_ruta = args.out / "predicciones_llm.jsonl"

    logger.info("Evaluando %d tickets sobre %d categorias", len(filas), len(etiquetas))
    res_reglas = evaluar(y_real, predecir_reglas(filas), etiquetas)
    logger.info("Reglas -> exactitud %.2f%%  F1 macro %.4f", res_reglas.exactitud * 100, res_reglas.f1_macro)

    informe: dict[str, Any] = {
        "generado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fixture": str(args.fixture.name),
        "n": len(filas),
        "etiquetas": etiquetas,
        "reglas": res_reglas.as_dict(),
    }

    cache = predecir_llm(filas, cache_ruta, args.forzar, consultar=args.llm) if (args.llm or cache_ruta.exists()) else {}
    # Solo los tickets con prediccion real del LLM entran en la comparacion.
    comparables = [f for f in filas if f["id"] in cache]
    res_llm = None

    if comparables:
        y_real_c = [f["categoria_real"] for f in comparables]
        y_llm = [cache[f["id"]]["categoria"] for f in comparables]
        y_reglas_c = [classify_with_rules(f["texto"]) for f in comparables]

        res_llm = evaluar(y_real_c, y_llm, etiquetas)
        # Se recalcula reglas sobre el mismo subconjunto: comparar el LLM sobre
        # 60 tickets contra reglas sobre 66 no seria una comparacion pareada.
        res_reglas_c = evaluar(y_real_c, y_reglas_c, etiquetas)
        prueba = mcnemar(res_reglas_c.correctos, res_llm.correctos)

        modelos = sorted({cache[f["id"]]["modelo"] for f in comparables})
        latencias = sorted(cache[f["id"]]["latencia_ms"] for f in comparables)
        informe.update({
            "cobertura_llm": {"evaluados": len(comparables), "de": len(filas)},
            "modelos": modelos,
            "latencia_ms": {
                "mediana": latencias[len(latencias) // 2],
                "p95": latencias[min(len(latencias) - 1, int(len(latencias) * 0.95))],
                "max": latencias[-1],
            },
            "reglas_subconjunto_pareado": res_reglas_c.as_dict(),
            "llm": res_llm.as_dict(),
            "mcnemar": prueba,
            "delta_f1_macro": round(res_llm.f1_macro - res_reglas_c.f1_macro, 4),
            "delta_exactitud": round(res_llm.exactitud - res_reglas_c.exactitud, 4),
        })
        logger.info("LLM    -> exactitud %.2f%%  F1 macro %.4f", res_llm.exactitud * 100, res_llm.f1_macro)
        logger.info(
            "McNemar: b=%d c=%d p=%.4f -> %s",
            prueba["b"], prueba["c"], prueba["p_valor"],
            "diferencia significativa" if prueba["significativo"] else "sin evidencia de diferencia",
        )
    else:
        logger.warning("Sin predicciones del LLM: se reporta solo la linea base. Usa --llm para compararlas.")

    (args.out / "metricas.json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    partes = [
        "# Evaluación de modelos — AI Support Co-Pilot",
        "",
        f"> Sprint 6 · HU-09 · AISCOP-46 · generado el {informe['generado_en']}",
        f"> Conjunto: `{informe['fixture']}` · {informe['n']} tickets · {len(etiquetas)} categorías",
        "",
        tabla_markdown(res_reglas, "Motor de reglas (línea base, Semestre 1)"),
        "",
        matriz_markdown(res_reglas, "motor de reglas"),
    ]
    if res_llm is not None:
        prueba = informe["mcnemar"]
        veredicto = (
            f"La diferencia **es** estadísticamente significativa (p = {prueba['p_valor']:.4f} < 0.05)."
            if prueba["significativo"]
            else f"**No** hay evidencia suficiente de diferencia (p = {prueba['p_valor']:.4f} ≥ 0.05)."
        )
        partes += [
            "",
            tabla_markdown(res_llm, f"LLM — {', '.join(informe['modelos'])}"),
            "",
            matriz_markdown(res_llm, "LLM"),
            "",
            "### Comparación pareada",
            "",
            f"- Δ exactitud: **{informe['delta_exactitud']:+.2%}**",
            f"- Δ F1 macro: **{informe['delta_f1_macro']:+.4f}**",
            f"- McNemar: reglas acierta y LLM falla en **{prueba['b']}** casos; "
            f"LLM acierta y reglas falla en **{prueba['c']}**; "
            f"{prueba['n_desacuerdos']} desacuerdos en total.",
            f"- {veredicto}",
            "",
            f"Latencia del LLM: mediana {informe['latencia_ms']['mediana']} ms · "
            f"p95 {informe['latencia_ms']['p95']} ms · máx {informe['latencia_ms']['max']} ms.",
        ]
    (args.out / "informe.md").write_text("\n".join(partes) + "\n", encoding="utf-8")

    logger.info("Resultados en %s", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
