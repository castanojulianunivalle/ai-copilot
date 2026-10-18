"""AISCOP-46: las metricas propias dan lo que deben en casos calculados a mano."""
import math

import pytest

from metricas import evaluar, mcnemar

ETIQUETAS = ["a", "b", "c"]


def test_matriz_filas_reales_columnas_predichas():
    r = evaluar(["a", "a", "b", "c"], ["a", "b", "b", "a"], ETIQUETAS)
    assert r.matriz == [[1, 1, 0], [0, 1, 0], [1, 0, 0]]
    assert r.aciertos == 2 and r.exactitud == 0.5


def test_precision_recall_f1_por_clase():
    r = evaluar(["a", "a", "b", "c"], ["a", "b", "b", "a"], ETIQUETAS)
    a, b, c = (r.por_clase[e] for e in ETIQUETAS)
    assert (a.precision, a.recall) == (0.5, 0.5)
    assert (b.precision, b.recall) == (0.5, 1.0)
    assert math.isclose(b.f1, 2 / 3)
    assert (c.precision, c.recall, c.f1) == (0.0, 0.0, 0.0)   # nunca predicha: cuenta, no se omite
    assert math.isclose(r.f1_macro, (0.5 + 2 / 3 + 0.0) / 3)


def test_f1_ponderado_pesa_por_soporte():
    r = evaluar(["a", "a", "b", "c"], ["a", "b", "b", "a"], ETIQUETAS)
    assert math.isclose(r.f1_ponderado, (0.5 * 2 + (2 / 3) * 1 + 0.0 * 1) / 4)


def test_f1_micro_coincide_con_la_exactitud():
    # 2 VP, 2 FP y 2 FN: cada error es un FP de la clase predicha y un FN de la real (AISCOP-58).
    r = evaluar(["a", "a", "b", "c"], ["a", "b", "b", "a"], ETIQUETAS)
    assert math.isclose(r.f1_micro, 2 * 2 / (2 * 2 + 2 + 2)) and math.isclose(r.f1_micro, r.exactitud)


def test_etiqueta_fuera_de_la_taxonomia():
    with pytest.raises(ValueError):
        evaluar(["a"], ["z"], ETIQUETAS)


def test_mcnemar_cuenta_solo_los_desacuerdos():
    reglas = [True, True, False, False, True]
    llm = [True, False, True, True, True]
    p = mcnemar(reglas, llm)
    assert (p["b"], p["c"], p["n_desacuerdos"]) == (1, 2, 3)
    assert math.isclose(p["p_valor"], 1.0)          # 1 frente a 2 es perfectamente compatible con el azar


def test_mcnemar_exacta_reproduce_el_avance_2():
    # Avance 2: 5 tickets solo los acertaban las reglas y 24 solo el modelo.
    reglas = [True] * 5 + [False] * 24
    llm = [False] * 5 + [True] * 24
    p = mcnemar(reglas, llm)
    esperado = 2 * sum(math.comb(29, i) for i in range(6)) / 2 ** 29
    assert math.isclose(p["p_valor"], round(esperado, 6))
    assert p["p_valor"] == 0.000546 and p["significativo"]


def test_mcnemar_sin_desacuerdos():
    assert mcnemar([True, False], [True, False])["p_valor"] == 1.0
