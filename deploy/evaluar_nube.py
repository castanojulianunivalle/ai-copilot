"""
HU-10 · AISCOP-57: la evaluacion formal de HU-09, repetida contra la version desplegada.

Manda los 44 tickets de examen a POST /create-ticket de la nube, como el cliente de demostracion, y mide
la latencia de punta a punta: API en Render, Groq y Supabase. Responde si el componente inteligente
mantiene su desempeno despues de desplegarse:

- metricas de la nube contra la etiqueta humana, las mismas de evaluate.py;
- coincidencia ticket a ticket con la evaluacion local del mismo prompt (results/cache/clasificacion-v2.jsonl);
- tasa de exito, repliegues a reglas y latencia (mediana y p95).

    python deploy/evaluar_nube.py      # deja evaluation/results/nube/: metricas.json, informe.md, predicciones.jsonl

Variables: AISCOP_API_URL, SUPABASE_URL, SUPABASE_ANON_KEY, DEMO_CLIENTE_PASSWORD. Borra los tickets al terminar.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone

from nube_comun import RAIZ, ErrorAPI, pedir, variable
from pruebas_nube import CLIENTE, COLOMBIA, dividir

import evaluate as E  # noqa: E402  (pruebas_nube ya puso evaluation/ y python-api/ en sys.path)
from metricas import evaluar, mcnemar  # noqa: E402
from particion import cargar, filtrar, huella_archivo  # noqa: E402

VERSION_LOCAL = "clasificacion-v2"
DESTINO = RAIZ / "evaluation" / "results" / "nube"


def percentiles(valores: list[int]) -> dict:
    v = sorted(valores)
    return {"mediana": v[len(v) // 2], "p95": v[min(len(v) - 1, int(len(v) * 0.95))], "max": v[-1]} if v else {}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evaluacion del examen contra la API desplegada")
    parser.add_argument("--pausa", type=float, default=3.0, help="segundos entre tickets (limite de Groq)")
    parser.add_argument("--espera-final", type=float, default=0, help="segundos a esperar la reclasificación (HU-12)")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    api = variable("AISCOP_API_URL").rstrip("/")
    supabase = variable("SUPABASE_URL").rstrip("/")
    salud = pedir("GET", api + "/health", timeout=150, reintentos=4)[1]
    token = pedir("POST", f"{supabase}/auth/v1/token?grant_type=password", cabeceras={"apikey": variable("SUPABASE_ANON_KEY")},
                  cuerpo={"email": CLIENTE, "password": variable("DEMO_CLIENTE_PASSWORD")})[1]["access_token"]
    print(f"API {api}: version {salud.get('version')} · commit {salud.get('commit')} · {salud['clasificacion'].get('modelo')}")

    filas = filtrar(cargar(), "examen")
    predicciones, creados, finales = [], [], {}
    inicio_corrida = datetime.now(timezone.utc)
    try:
        for i, f in enumerate(filas, 1):
            titulo, descripcion = dividir(f["texto"])
            inicio = time.perf_counter()
            try:
                r = pedir("POST", api + "/create-ticket", token=token, cuerpo={"titulo": titulo, "description": descripcion},
                          timeout=60, reintentos=1)[1]
                creados.append(r["ticket_id"])
                predicciones.append({"id": f["id"], "ok": True, "categoria": r["category"], "confianza": r["confianza_ia"],
                                     "clasificado_por": r["clasificado_por"], "requiere_revision": r["requiere_revision"],
                                     "latencia_ms": int((time.perf_counter() - inicio) * 1000)})
            except ErrorAPI as e:
                predicciones.append({"id": f["id"], "ok": False, "error": e.estado,
                                     "latencia_ms": int((time.perf_counter() - inicio) * 1000)})
            p = predicciones[-1]
            print(f"{i:2}/{len(filas)} {f['id']}: {p.get('categoria', 'ERROR')} ({p.get('clasificado_por', p.get('error'))}) "
                  f"{p['latencia_ms']} ms")
            time.sleep(args.pausa)
        # HU-12: los que cayeron a reglas se reclasifican en segundo plano; se espera y se lee su estado final.
        pendientes = [p for p in predicciones if p.get("clasificado_por") == "reglas"]
        if pendientes and args.espera_final:
            print(f"{len(pendientes)} tickets en reglas; espera de {args.espera_final} s para la reclasificación")
            time.sleep(args.espera_final)
            ids = {c: p["id"] for c, p in zip(creados, [x for x in predicciones if x.get("ok")])}
            for ticket_id, ev_id in ids.items():
                fila = pedir("GET", f"{supabase}/rest/v1/tickets?id=eq.{ticket_id}&select=category,clasificado_por,"
                                    "confianza_ia,reclasificar", token=token,
                             cabeceras={"apikey": variable("SUPABASE_ANON_KEY")})[1]
                if fila:
                    finales[ev_id] = fila[0]
    finally:
        borrados = 0
        for ticket_id in creados:
            try:
                pedir("DELETE", f"{api}/tickets/{ticket_id}", token=token, reintentos=1)
                borrados += 1
            except ErrorAPI:
                pass
        print(f"Tickets borrados: {borrados} de {len(creados)}")

    por_id = {p["id"]: p for p in predicciones}
    local = E.leer_cache(E.CACHE / f"{VERSION_LOCAL}.jsonl")
    etiquetas = list(E.CATEGORIAS)
    validas = [f for f in filas if por_id[f["id"]]["ok"]]
    y_real = [f["categoria_real"] for f in validas]
    res_nube = evaluar(y_real, [por_id[f["id"]]["categoria"] for f in validas], etiquetas)
    comparables = [f for f in validas if f["id"] in local]
    res_local = evaluar([f["categoria_real"] for f in comparables], [local[f["id"]]["categoria"] for f in comparables], etiquetas)
    nube_ok = [por_id[f["id"]]["categoria"] == f["categoria_real"] for f in comparables]
    local_ok = [local[f["id"]]["categoria"] == f["categoria_real"] for f in comparables]
    distintas = [{"id": f["id"], "real": f["categoria_real"], "local": local[f["id"]]["categoria"],
                  "nube": por_id[f["id"]]["categoria"], "clasificado_por": por_id[f["id"]]["clasificado_por"]}
                 for f in comparables if por_id[f["id"]]["categoria"] != local[f["id"]]["categoria"]]
    resultado = {
        "generado_en": inicio_corrida.isoformat(timespec="seconds"),
        "fecha_colombia": inicio_corrida.astimezone(COLOMBIA).strftime("%Y-%m-%d %H:%M"),
        "api": api, "version_api": salud.get("version"), "commit_api": salud.get("commit"),
        "modelo": salud["clasificacion"].get("modelo"), "sha256_fixture": huella_archivo(), "particion": "examen",
        "n": len(filas), "respuestas_ok": len(validas),
        "clasificados_por_llm": sum(p.get("clasificado_por") == "llm" for p in predicciones),
        "repliegues_a_reglas": sum(p.get("clasificado_por") == "reglas" for p in predicciones),
        "fallas_http": len(filas) - len(validas),
        "a_revision": sum(bool(p.get("requiere_revision")) for p in predicciones),
        "latencia_ms_punta_a_punta": percentiles([p["latencia_ms"] for p in predicciones if p["ok"]]),
        "nube": res_nube.as_dict(),
        "local": {"version": VERSION_LOCAL, **res_local.as_dict()},
        "coincidencia_con_local": {"iguales": len(comparables) - len(distintas), "de": len(comparables), "distintas": distintas},
        "mcnemar_local_vs_nube": mcnemar(local_ok, nube_ok),
    }
    if finales:
        fin = [finales.get(f["id"], {}).get("category", por_id[f["id"]].get("categoria")) for f in validas]
        res_fin = evaluar(y_real, fin, etiquetas)
        resultado["despues_de_reclasificar"] = {
            "en_reglas_al_final": sum(1 for v in finales.values() if v.get("clasificado_por") == "reglas"),
            "pendientes": sum(1 for v in finales.values() if v.get("reclasificar")),
            "exactitud": round(res_fin.exactitud, 4), "f1_macro": round(res_fin.f1_macro, 4),
            "iguales_a_local": sum(1 for f, c in zip(validas, fin) if c == local.get(f["id"], {}).get("categoria"))}
        print("Después de reclasificar:", resultado["despues_de_reclasificar"])
    DESTINO.mkdir(parents=True, exist_ok=True)
    (DESTINO / "metricas.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (DESTINO / "predicciones.jsonl").open("w", encoding="utf-8", newline="\n") as salida:
        for p in predicciones:
            salida.write(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n")

    c, lat, m = resultado["coincidencia_con_local"], resultado["latencia_ms_punta_a_punta"], resultado["mcnemar_local_vs_nube"]
    lineas = [
        "# Evaluación del examen contra la versión desplegada", "",
        f"> HU-10 · AISCOP-57 · {resultado['fecha_colombia']} (Colombia) · API {api} · versión {resultado['version_api']} "
        f"· commit `{resultado['commit_api']}` · {resultado['modelo']}", "",
        f"- **Respuestas:** {len(validas)} de {len(filas)} · por el LLM {resultado['clasificados_por_llm']} · "
        f"repliegues a reglas {resultado['repliegues_a_reglas']} · fallas HTTP {resultado['fallas_http']}",
        f"- **En la nube:** exactitud {res_nube.exactitud:.2%} · F1 macro {res_nube.f1_macro:.4f} · F1 micro {res_nube.f1_micro:.4f}",
        f"- **Local, mismo prompt ({VERSION_LOCAL}), mismos tickets:** exactitud {res_local.exactitud:.2%} · "
        f"F1 macro {res_local.f1_macro:.4f}",
        f"- **Misma categoría que en local:** {c['iguales']} de {c['de']}. McNemar local frente a nube: b = {m['b']}, "
        f"c = {m['c']}, p = {m['p_valor']:.4f}",
        f"- **Latencia de punta a punta** (cliente → Render → Groq → Supabase): mediana {lat.get('mediana')} ms · "
        f"p95 {lat.get('p95')} ms · máx {lat.get('max')} ms",
        f"- **A revisión humana:** {resultado['a_revision']} de {len(filas)}", ""]
    if distintas:
        lineas += ["| Ticket | Real | Local | Nube |", "|---|---|---|---|"]
        lineas += [f"| {d['id']} | {d['real']} | {d['local']} | {d['nube']} ({d['clasificado_por']}) |" for d in distintas]
    lineas += ["", E.tabla_markdown(res_nube.as_dict(), "Métricas en la nube"), "", E.matriz_markdown(res_nube.as_dict(), "nube")]
    (DESTINO / "informe.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas[:9]))
    return 0 if resultado["fallas_http"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
