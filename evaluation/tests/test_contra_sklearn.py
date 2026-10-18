"""AISCOP-47: metricas.py da lo mismo que scikit-learn y McNemar lo mismo que scipy.stats.binomtest.

metricas.py implementa las formulas a mano, sin dependencias y citables en el articulo. El precio de
esa decision es demostrar que son correctas: aqui se contrastan sobre las predicciones reales de cada
version del prompt en cada particion, y sobre muestras aleatorias.
"""
import random

import pytest

sk = pytest.importorskip("sklearn.metrics")
stats = pytest.importorskip("scipy.stats")

import evaluate as E  # noqa: E402
from metricas import evaluar, mcnemar  # noqa: E402
from particion import cargar, filtrar  # noqa: E402

ETIQUETAS = list(E.CATEGORIAS)
TOLERANCIA = 1e-12


def casos_reales():
    for particion in ("examen", "practica", "todo"):
        filas = filtrar(cargar(), particion)
        yield f"{particion}-reglas", [f["categoria_real"] for f in filas], E.predecir_reglas(filas)
        for ruta in sorted(E.CACHE.glob("*.jsonl")):
            cache = E.leer_cache(ruta)
            comunes = [f for f in filas if f["id"] in cache]
            yield f"{particion}-{ruta.stem}", [f["categoria_real"] for f in comunes], [cache[f["id"]]["categoria"] for f in comunes]


def casos_aleatorios(n=40):
    azar = random.Random(20261017)
    for k in range(n):
        tam = azar.randint(5, 80)
        yield f"azar-{k}", [azar.choice(ETIQUETAS) for _ in range(tam)], [azar.choice(ETIQUETAS) for _ in range(tam)]


@pytest.mark.parametrize("nombre,y_real,y_pred", list(casos_reales()) + list(casos_aleatorios()))
def test_metricas_iguales_a_sklearn(nombre, y_real, y_pred):
    r = evaluar(y_real, y_pred, ETIQUETAS)
    assert r.matriz == sk.confusion_matrix(y_real, y_pred, labels=ETIQUETAS).tolist()
    assert abs(r.exactitud - sk.accuracy_score(y_real, y_pred)) < TOLERANCIA
    p, rc, f1, soporte = sk.precision_recall_fscore_support(y_real, y_pred, labels=ETIQUETAS, zero_division=0)
    for i, e in enumerate(ETIQUETAS):
        m = r.por_clase[e]
        assert abs(m.precision - p[i]) < TOLERANCIA and abs(m.recall - rc[i]) < TOLERANCIA
        assert abs(m.f1 - f1[i]) < TOLERANCIA and m.soporte == soporte[i]
    assert abs(r.f1_macro - sk.f1_score(y_real, y_pred, labels=ETIQUETAS, average="macro", zero_division=0)) < TOLERANCIA
    assert abs(r.f1_ponderado - sk.f1_score(y_real, y_pred, labels=ETIQUETAS, average="weighted", zero_division=0)) < TOLERANCIA


@pytest.mark.parametrize("b,c", [(5, 24), (4, 16), (2, 17), (2, 5), (1, 8), (0, 9), (3, 3), (0, 1), (10, 30)])
def test_mcnemar_igual_a_binomtest(b, c):
    p = mcnemar([True] * b + [False] * c, [False] * b + [True] * c)
    referencia = stats.binomtest(min(b, c), b + c, 0.5, alternative="two-sided").pvalue
    assert p["p_valor"] == round(min(1.0, referencia), 6)
