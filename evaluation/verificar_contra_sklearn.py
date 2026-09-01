"""
Sprint 6 · HU-09 · AISCOP-47: verificacion de `metricas.py` contra referencias.

`metricas.py` implementa las metricas a mano para no depender de scikit-learn en
tiempo de ejecucion y para que las formulas sean citables en el articulo. El
precio de esa decision es tener que demostrar que la implementacion es correcta,
y eso es lo que hace este script: compara contra scikit-learn y scipy sobre
muestras aleatorias.

No forma parte del flujo de evaluacion. Se corre cuando se toca metricas.py.

    pip install scikit-learn scipy
    python evaluation/verificar_contra_sklearn.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python-api"))

from metricas import evaluar, mcnemar  # noqa: E402

from ai.taxonomia import CATEGORIAS  # noqa: E402

TOLERANCIA = 1e-12


def main() -> int:
    try:
        from scipy.stats import binomtest
        from sklearn.metrics import (
            accuracy_score,
            confusion_matrix,
            f1_score,
            precision_recall_fscore_support,
        )
    except ImportError:
        print("Faltan scikit-learn y scipy: pip install scikit-learn scipy")
        return 2

    etiquetas = list(CATEGORIAS)
    random.seed(11)
    todo_ok = True

    print("== Metricas de clasificacion vs scikit-learn ==")
    for _ in range(10):
        n = random.randint(40, 400)
        y_real = [random.choice(etiquetas) for _ in range(n)]
        # Prediccion correlacionada con la real: ruido puro no ejercita las
        # celdas de la diagonal ni los casos de division por cero.
        y_pred = [r if random.random() < 0.6 else random.choice(etiquetas) for r in y_real]

        mio = evaluar(y_real, y_pred, etiquetas)
        p, r, f, s = precision_recall_fscore_support(
            y_real, y_pred, labels=etiquetas, zero_division=0
        )
        comprobaciones = {
            "matriz": mio.matriz == confusion_matrix(y_real, y_pred, labels=etiquetas).tolist(),
            "exactitud": abs(mio.exactitud - accuracy_score(y_real, y_pred)) < TOLERANCIA,
            "f1_macro": abs(
                mio.f1_macro
                - f1_score(y_real, y_pred, labels=etiquetas, average="macro", zero_division=0)
            ) < TOLERANCIA,
            "f1_ponderado": abs(
                mio.f1_ponderado
                - f1_score(y_real, y_pred, labels=etiquetas, average="weighted", zero_division=0)
            ) < TOLERANCIA,
            "precision": all(abs(mio.por_clase[e].precision - p[i]) < TOLERANCIA for i, e in enumerate(etiquetas)),
            "recall": all(abs(mio.por_clase[e].recall - r[i]) < TOLERANCIA for i, e in enumerate(etiquetas)),
            "f1_clase": all(abs(mio.por_clase[e].f1 - f[i]) < TOLERANCIA for i, e in enumerate(etiquetas)),
            "soporte": all(mio.por_clase[e].soporte == s[i] for i, e in enumerate(etiquetas)),
        }
        ok = all(comprobaciones.values())
        todo_ok &= ok
        fallos = [k for k, v in comprobaciones.items() if not v]
        print(f"  {'OK  ' if ok else 'FALLA'} n={n:3}  {'coinciden las 8 metricas' if ok else fallos}")

    print("\n== McNemar exacto vs scipy.stats.binomtest ==")
    for b, c in [(10, 3), (3, 10), (0, 0), (5, 5), (1, 0), (20, 7), (2, 9), (50, 30)]:
        a_correctos = [True] * b + [False] * c
        b_correctos = [False] * b + [True] * c
        mio = mcnemar(a_correctos, b_correctos)
        referencia = (
            min(1.0, binomtest(min(b, c), b + c, 0.5, alternative="two-sided").pvalue)
            if b + c else 1.0
        )
        ok = abs(mio["p_valor"] - referencia) < 1e-6
        todo_ok &= ok
        print(f"  {'OK  ' if ok else 'FALLA'} b={b:2} c={c:2}  propio={mio['p_valor']:.6f}  scipy={referencia:.6f}")

    print("\nTODO CORRECTO" if todo_ok else "\nHAY DIFERENCIAS: revisar metricas.py")
    return 0 if todo_ok else 1


if __name__ == "__main__":
    sys.exit(main())
