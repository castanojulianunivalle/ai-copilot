"""
Sprint 6 · HU-09 · AISCOP-46: metricas de clasificacion.

Implementadas en Python puro y sin dependencias. Son tres razones:

1. El script de evaluacion corre siempre, tambien en una maquina donde no se
   pueda compilar scikit-learn.
2. Las formulas quedan a la vista y son citables en el articulo, en vez de
   escondidas tras una llamada de libreria.
3. La correccion se verifica cruzando los resultados contra sklearn en
   `verificar_contra_sklearn.py`, que si es opcional.

Incluye la prueba de McNemar, que es la adecuada para comparar dos
clasificadores evaluados sobre las MISMAS muestras: comparar dos intervalos de
confianza por separado no responde si la diferencia es significativa.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class MetricasClase:
    etiqueta: str
    vp: int  # verdaderos positivos
    fp: int  # falsos positivos
    fn: int  # falsos negativos
    soporte: int

    @property
    def precision(self) -> float:
        denominador = self.vp + self.fp
        return self.vp / denominador if denominador else 0.0

    @property
    def recall(self) -> float:
        denominador = self.vp + self.fn
        return self.vp / denominador if denominador else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    def as_dict(self) -> dict:
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "soporte": self.soporte,
        }


@dataclass
class Resultado:
    etiquetas: list[str]
    matriz: list[list[int]]
    por_clase: dict[str, MetricasClase]
    exactitud: float
    n: int
    aciertos: int
    correctos: list[bool] = field(default_factory=list)

    @property
    def f1_macro(self) -> float:
        """Promedio simple entre clases: cada categoria pesa igual sin importar
        cuantos tickets tenga. Es la metrica principal del estudio porque el
        historico real esta sesgado hacia 'Tecnico'."""
        if not self.por_clase:
            return 0.0
        return sum(m.f1 for m in self.por_clase.values()) / len(self.por_clase)

    @property
    def f1_ponderado(self) -> float:
        """Promedio pesado por soporte. Refleja mejor lo que siente el usuario,
        pero oculta el desempeño en las categorias raras."""
        total = sum(m.soporte for m in self.por_clase.values())
        if not total:
            return 0.0
        return sum(m.f1 * m.soporte for m in self.por_clase.values()) / total

    @property
    def precision_macro(self) -> float:
        if not self.por_clase:
            return 0.0
        return sum(m.precision for m in self.por_clase.values()) / len(self.por_clase)

    @property
    def recall_macro(self) -> float:
        if not self.por_clase:
            return 0.0
        return sum(m.recall for m in self.por_clase.values()) / len(self.por_clase)

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "aciertos": self.aciertos,
            "exactitud": round(self.exactitud, 4),
            "precision_macro": round(self.precision_macro, 4),
            "recall_macro": round(self.recall_macro, 4),
            "f1_macro": round(self.f1_macro, 4),
            "f1_ponderado": round(self.f1_ponderado, 4),
            "etiquetas": self.etiquetas,
            "matriz_confusion": self.matriz,
            "por_clase": {k: v.as_dict() for k, v in self.por_clase.items()},
        }


def evaluar(y_real: list[str], y_pred: list[str], etiquetas: list[str]) -> Resultado:
    """Matriz de confusion y metricas por clase.

    `etiquetas` fija el orden de los ejes de la matriz y se pasa completa
    (las 11 categorias) aunque alguna no aparezca en la muestra: una categoria
    que el modelo nunca predice tiene recall 0, y omitirla de la matriz
    escondería justamente ese fallo.
    """
    if len(y_real) != len(y_pred):
        raise ValueError(f"Longitudes distintas: {len(y_real)} reales vs {len(y_pred)} predichas")

    indice = {etiqueta: i for i, etiqueta in enumerate(etiquetas)}
    matriz = [[0] * len(etiquetas) for _ in etiquetas]
    correctos: list[bool] = []

    for real, pred in zip(y_real, y_pred):
        if real not in indice:
            raise ValueError(f"Etiqueta real fuera de la taxonomia: {real!r}")
        if pred not in indice:
            raise ValueError(f"Etiqueta predicha fuera de la taxonomia: {pred!r}")
        # Convencion: filas = real, columnas = predicho.
        matriz[indice[real]][indice[pred]] += 1
        correctos.append(real == pred)

    por_clase: dict[str, MetricasClase] = {}
    for etiqueta, i in indice.items():
        vp = matriz[i][i]
        fn = sum(matriz[i]) - vp                      # era esta clase, se predijo otra
        fp = sum(fila[i] for fila in matriz) - vp     # se predijo esta clase, era otra
        por_clase[etiqueta] = MetricasClase(etiqueta, vp, fp, fn, soporte=sum(matriz[i]))

    aciertos = sum(correctos)
    return Resultado(
        etiquetas=etiquetas,
        matriz=matriz,
        por_clase=por_clase,
        exactitud=aciertos / len(y_real) if y_real else 0.0,
        n=len(y_real),
        aciertos=aciertos,
        correctos=correctos,
    )


def mcnemar(correctos_a: list[bool], correctos_b: list[bool]) -> dict:
    """Prueba de McNemar exacta entre dos clasificadores sobre las mismas muestras.

    Solo informan los desacuerdos: los casos que ambos aciertan o ambos fallan
    no dicen nada sobre cual es mejor.

        b = A acierta y B falla
        c = A falla y B acierta

    Bajo H0 (los dos motores son igual de buenos) cada desacuerdo es una moneda
    justa, asi que b ~ Binomial(b+c, 0.5). Se usa la version exacta y no la
    aproximacion chi-cuadrado porque con n=66 los desacuerdos son pocos y la
    aproximacion no es fiable por debajo de ~25.
    """
    if len(correctos_a) != len(correctos_b):
        raise ValueError("Ambos motores deben evaluarse sobre las mismas muestras")

    b = sum(1 for a, bb in zip(correctos_a, correctos_b) if a and not bb)
    c = sum(1 for a, bb in zip(correctos_a, correctos_b) if not a and bb)
    n = b + c

    if n == 0:
        return {"b": 0, "c": 0, "n_desacuerdos": 0, "p_valor": 1.0, "significativo": False}

    # p de dos colas: probabilidad de un desbalance al menos tan extremo.
    k = min(b, c)
    cola = sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    p = min(1.0, 2 * cola)

    return {
        "b": b,
        "c": c,
        "n_desacuerdos": n,
        "p_valor": round(p, 6),
        "significativo": p < 0.05,
    }
