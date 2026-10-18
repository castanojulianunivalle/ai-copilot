"""AISCOP-46: el script integrado reproduce exactamente las cifras presentadas en el Avance 2.

La corrida del 5 de octubre (gpt-oss-20b en Groq, prompt clasificacion-v1) quedo en la cache; la
comparacion se recalcula desde ahi sin consultar al modelo.
"""
import evaluate as E
from particion import cargar, filtrar


def test_reproduce_el_avance_2():
    filas = filtrar(cargar(), "todo")
    v = E.comparar_version(filas, E.leer_cache(E.CACHE / "clasificacion-v1.jsonl"), list(E.CATEGORIAS))
    assert v["cobertura"] == {"evaluados": 66, "de": 66}
    assert (v["llm"]["aciertos"], v["reglas_pareado"]["aciertos"]) == (54, 35)
    assert (v["llm"]["f1_macro"], v["reglas_pareado"]["f1_macro"]) == (0.8043, 0.5271)
    p = v["mcnemar_vs_reglas"]
    assert (p["b"], p["c"], p["p_valor"]) == (5, 24, 0.000546)
