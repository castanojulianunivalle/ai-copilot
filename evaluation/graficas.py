"""
Sprint 6 · HU-09 · AISCOP-47: figuras de la evaluacion.

Tres figuras por particion, en PNG y SVG:
- resumen:         exactitud, F1 macro y F1 ponderado de cada motor;
- comparativa_f1:  F1 por categoria, ordenado por la ventaja de la ultima version del prompt;
- matriz_<motor>:  matriz de confusion de cada motor (filas = real, columnas = predicho).

matplotlib es opcional a proposito: evaluate.py produce metricas.json e informe.md sin el.

Decisiones de diseño (para un documento impreso, como en el prototipo del 1 de septiembre):
- Las reglas van en gris neutro y las versiones del modelo en dos tonos de un mismo azul: v1 claro,
  la ultima oscuro. Ademas del color, la ultima version lleva trama diagonal, porque en una copia en
  blanco y negro el color no sobrevive y la trama si.
- La matriz usa una rampa secuencial de un solo tono, no un arcoiris: la magnitud se lee como orden.
- Se rotula la diferencia por categoria, que es el hallazgo; los valores exactos estan en metricas.json.
"""
from __future__ import annotations

from pathlib import Path

TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
REJILLA = "#e1e0d9"
EJE = "#c3c2b7"
SERIE_REGLAS = "#a3a29b"
SERIES_MODELO = ["#86b6ef", "#1c5cab"]           # versiones del prompt: anterior, ultima
MEJORA, EMPEORA = "#1c5cab", "#b4530a"
RAMPA_AZUL = ["#f4f8fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def _plt():
    import matplotlib

    matplotlib.use("Agg")                            # sin interfaz grafica: corre en CI y en servidor
    import matplotlib.pyplot as plt

    plt.rcParams.update({"axes.formatter.use_locale": False})
    plt.rcParams.update({
        "font.family": "sans-serif", "font.size": 10, "axes.edgecolor": EJE, "axes.labelcolor": TINTA,
        "xtick.color": TINTA_SECUNDARIA, "ytick.color": TINTA, "axes.spines.top": False,
        "axes.spines.right": False, "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white",
        # Ids fijos en el SVG: sin esto cada corrida cambia el archivo aunque la figura sea la misma.
        "svg.hashsalt": "aiscop-hu09",
    })
    return plt


def _guardar(fig, base: Path) -> list[Path]:
    rutas = [base.with_suffix(".png"), base.with_suffix(".svg")]
    for ruta in rutas:
        # Sin fecha en los metadatos, por la misma razon: una figura solo cambia si cambian los datos.
        fig.savefig(ruta, metadata={"Date": None} if ruta.suffix == ".svg" else None)
    return rutas


def _coma(x: float, d: int = 2) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def _formato_coma():
    from matplotlib.ticker import FuncFormatter

    return FuncFormatter(lambda v, _: _coma(v, 1) if v <= 1.0001 else "")


def _series(res_reglas, resultados: dict) -> list[tuple[str, object, str, str | None]]:
    """(nombre, resultado, color, trama) en orden: reglas y luego cada version del prompt."""
    series = [("Motor de reglas", res_reglas, SERIE_REGLAS, None)]
    versiones = list(resultados.items())[-2:]
    for k, (version, res) in enumerate(versiones):
        ultima = k == len(versiones) - 1
        color = SERIES_MODELO[-1] if ultima else SERIES_MODELO[0]
        series.append((f"LLM {version.replace('clasificacion-', '')}", res, color, "///" if ultima else None))
    return series


def resumen(series, particion: str, n: int, destino: Path) -> list[Path]:
    plt = _plt()
    claves = [("exactitud", "Exactitud"), ("f1_macro", "F1 macro"), ("f1_ponderado", "F1 ponderado")]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ancho = 0.8 / len(series)
    for i, (nombre, res, color, trama) in enumerate(series):
        valores = [getattr(res, c) for c, _ in claves]
        xs = [j + (i - (len(series) - 1) / 2) * ancho for j in range(len(claves))]
        barras = ax.bar(xs, valores, ancho * 0.94, color=color, hatch=trama, edgecolor="white", label=nombre)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.015, _coma(v), ha="center", fontsize=9, color=TINTA)
    ax.set_xticks(range(len(claves)), [t for _, t in claves])
    ax.set_ylim(0, 1.08)
    ax.yaxis.set_major_formatter(_formato_coma())
    ax.yaxis.grid(True, color=REJILLA)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncols=len(series), loc="lower left", bbox_to_anchor=(0, 1.0))
    ax.set_title(f"Partición {particion} · {n} tickets", loc="left", pad=28, fontsize=11, color=TINTA_SECUNDARIA)
    rutas = _guardar(fig, destino / "resumen")
    plt.close(fig)
    return rutas


def comparativa_f1(series, destino: Path) -> list[Path]:
    plt = _plt()
    etiquetas = series[0][1].etiquetas
    ultima = series[-1][1]
    orden = sorted(etiquetas, key=lambda e: ultima.por_clase[e].f1 - series[0][1].por_clase[e].f1, reverse=True)
    fig, ax = plt.subplots(figsize=(8.5, 6.4))
    alto = 0.8 / len(series)
    for i, (nombre, res, color, trama) in enumerate(series):
        ys = [j + (i - (len(series) - 1) / 2) * alto for j in range(len(orden))]
        ax.barh(ys, [res.por_clase[e].f1 for e in orden], alto * 0.94, color=color, hatch=trama,
                edgecolor="white", label=nombre)
    for j, e in enumerate(orden):
        d = ultima.por_clase[e].f1 - series[0][1].por_clase[e].f1
        ax.text(1.17, j, ("+" if d > 0 else "−" if d < 0 else "±") + _coma(abs(d)), va="center", ha="right",
                fontsize=9.5, fontweight="bold", color=MEJORA if d > 0 else EMPEORA if d < 0 else TINTA_SECUNDARIA)
    ax.set_yticks(range(len(orden)), orden)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.18)
    ax.xaxis.set_major_formatter(_formato_coma())
    ax.set_xlabel("F1 por categoría")
    ax.xaxis.grid(True, color=REJILLA)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncols=len(series), loc="lower left", bbox_to_anchor=(0, 1.0))
    ax.text(1.17, -0.9, f"{series[-1][0]} − reglas", ha="right", fontsize=8.5, color=TINTA_SECUNDARIA)
    rutas = _guardar(fig, destino / "comparativa_f1")
    plt.close(fig)
    return rutas


def matriz_confusion(res, titulo: str, base: Path) -> list[Path]:
    plt = _plt()
    from matplotlib.colors import LinearSegmentedColormap

    m, etiquetas = res.matriz, res.etiquetas
    k = len(etiquetas)
    tope = max(max(fila) for fila in m) or 1
    fig, ax = plt.subplots(figsize=(7.6, 6.6))
    ax.imshow(m, cmap=LinearSegmentedColormap.from_list("azul", RAMPA_AZUL), vmin=0, vmax=tope)
    for i in range(k):
        for j in range(k):
            if m[i][j]:
                ax.text(j, i, str(m[i][j]), ha="center", va="center", fontsize=10,
                        color="white" if m[i][j] > tope * 0.55 else TINTA, fontweight="bold" if i == j else "normal")
    ax.set_xticks(range(k), etiquetas, rotation=40, ha="right")
    ax.set_yticks(range(k), etiquetas)
    ax.set_xlabel("Categoría predicha")
    ax.set_ylabel("Categoría real")
    for lado in ax.spines.values():
        lado.set_visible(False)
    ax.set_title(f"{titulo} · {res.aciertos} de {res.n} aciertos", loc="left", fontsize=11, color=TINTA)
    rutas = _guardar(fig, base)
    plt.close(fig)
    return rutas


def generar(informe: dict, res_reglas, resultados: dict, destino: Path) -> list[Path]:
    """Todas las figuras de una particion. `resultados`: {version del prompt: Resultado}."""
    series = _series(res_reglas, resultados)
    rutas = resumen(series, informe["particion"], informe["n"], destino) + comparativa_f1(series, destino)
    rutas += matriz_confusion(res_reglas, "Motor de reglas", destino / "matriz_reglas")
    for version, res in resultados.items():
        corto = version.replace("clasificacion-", "")
        rutas += matriz_confusion(res, f"LLM {corto}", destino / f"matriz_llm_{corto}")
    return rutas
