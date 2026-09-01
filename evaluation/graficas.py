"""
Sprint 6 · HU-09 · AISCOP-47: figuras de la evaluacion.

Genera las dos figuras que van al articulo: la matriz de confusion y la
comparativa de F1 por clase entre el motor de reglas y el LLM.

matplotlib es opcional a proposito: `evaluate.py` corre y produce metricas.json
e informe.md sin el. Solo las figuras requieren instalarlo
(`pip install -r evaluation/requirements.txt`).

Decisiones de diseño (para un documento impreso, no para pantalla):
- Paleta validada: azul #2a78d6 y naranja #eb6834 como series categoricas.
  Separacion CVD Delta-E 24.7 (protanopia) y 33.6 en vision normal, ambas muy
  por encima de los umbrales de 8 y 15; contraste >= 3:1 sobre el fondo.
- Ademas del color, la serie del LLM lleva trama diagonal: en una tesis impresa
  en blanco y negro el color no sobrevive, la trama si.
- La matriz usa una rampa secuencial de un solo tono (azul claro -> oscuro), no
  un arcoiris: la magnitud tiene que leerse como orden, y un arcoiris no lo es.
- En la comparativa no se rotula cada barra. Se rotula la diferencia por clase,
  que es el hallazgo; los valores exactos ya estan en informe.md y metricas.json.
- Un solo modo (claro). Son figuras para imprimir, no un tablero interactivo.
"""
from __future__ import annotations

from pathlib import Path

# Paleta (ver referencia de diseño). Los roles se nombran para no repartir hex
# sueltos por el codigo.
SUPERFICIE = "#fcfcfb"
TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_TENUE = "#898781"
REJILLA = "#e1e0d9"
EJE = "#c3c2b7"
SERIE_REGLAS = "#2a78d6"   # slot categorico 1 (azul)
SERIE_LLM = "#eb6834"      # slot categorico 2 (naranja)

# Rampa secuencial azul 100 -> 700, tal cual la referencia.
RAMPA_AZUL = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]


class MatplotlibAusente(RuntimeError):
    pass


def _preparar():
    try:
        import matplotlib
    except ImportError as exc:  # pragma: no cover
        raise MatplotlibAusente(
            "Las figuras necesitan matplotlib: pip install -r evaluation/requirements.txt"
        ) from exc
    matplotlib.use("Agg")  # sin interfaz grafica: esto corre en CI y en servidor
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
        "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE,
        "savefig.facecolor": SUPERFICIE,
        "text.color": TINTA_PRIMARIA,
        "axes.labelcolor": TINTA_SECUNDARIA,
        "xtick.color": TINTA_TENUE,
        "ytick.color": TINTA_TENUE,
        "axes.edgecolor": EJE,
    })
    return plt


def _guardar(fig, ruta: Path) -> list[Path]:
    """PNG para leer en pantalla y en el repositorio, SVG para maquetar la tesis
    sin que las figuras se pixelen al escalarlas."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    salidas = []
    for extension in ("png", "svg"):
        destino = ruta.with_suffix(f".{extension}")
        fig.savefig(destino, dpi=200, bbox_inches="tight")
        salidas.append(destino)
    return salidas


def matriz_confusion(resultado, titulo: str, ruta: Path) -> list[Path]:
    plt = _preparar()
    from matplotlib.colors import LinearSegmentedColormap

    etiquetas = resultado.etiquetas
    matriz = resultado.matriz
    cmap = LinearSegmentedColormap.from_list("azules", RAMPA_AZUL)
    # Una celda en cero es ausencia de dato, no la magnitud mas baja: se pinta
    # del color del fondo para que la señal quede en las celdas que si tienen
    # conteo. `set_under` con vmin=0.5 manda todos los ceros ahi.
    cmap.set_under(SUPERFICIE)
    maximo = max((max(fila) for fila in matriz), default=1) or 1

    fig, ax = plt.subplots(figsize=(8.5, 7.2))
    ax.imshow(matriz, cmap=cmap, vmin=0.5, vmax=maximo, aspect="equal")

    ax.set_xticks(range(len(etiquetas)), etiquetas, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(etiquetas)), etiquetas, fontsize=9)
    ax.set_xlabel("Categoría predicha", fontsize=10, labelpad=10)
    ax.set_ylabel("Categoría real", fontsize=10, labelpad=10)
    ax.set_title(titulo, fontsize=12, color=TINTA_PRIMARIA, pad=30, loc="left")
    # La nota va entre el titulo y la cuadricula. Debajo del eje X chocaria con
    # las etiquetas rotadas y con el label del eje.
    ax.text(0, 1.015,
            "La diagonal son los aciertos. Cada fila suma el total real de esa categoría.",
            transform=ax.transAxes, fontsize=8, color=TINTA_TENUE, va="bottom")

    # Separacion de 2px entre celdas: los bordes hacen legible la cuadricula sin
    # necesidad de una rejilla encima.
    ax.set_xticks([x - 0.5 for x in range(1, len(etiquetas))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(etiquetas))], minor=True)
    ax.grid(which="minor", color=SUPERFICIE, linewidth=2)
    ax.tick_params(which="minor", length=0)
    for lado in ax.spines.values():
        lado.set_visible(False)

    for i in range(len(etiquetas)):
        for j in range(len(etiquetas)):
            valor = matriz[i][j]
            if not valor:
                continue
            # Texto claro sobre celda oscura: por encima de ~55% del maximo la
            # rampa ya no deja leer tinta negra.
            color = "#ffffff" if valor > maximo * 0.55 else TINTA_PRIMARIA
            ax.text(j, i, str(valor), ha="center", va="center",
                    fontsize=9, color=color,
                    fontweight="bold" if i == j else "normal")

    salidas = _guardar(fig, ruta)
    plt.close(fig)
    return salidas


def comparativa_f1(res_reglas, res_llm, ruta: Path) -> list[Path]:
    plt = _preparar()

    etiquetas = res_reglas.etiquetas
    # Ordenado por la mejora que aporta la IA: la figura responde de un vistazo
    # "donde ayuda mas el LLM", que es la pregunta del articulo.
    orden = sorted(
        etiquetas,
        key=lambda e: res_llm.por_clase[e].f1 - res_reglas.por_clase[e].f1,
    )
    f1_reglas = [res_reglas.por_clase[e].f1 for e in orden]
    f1_llm = [res_llm.por_clase[e].f1 for e in orden]

    y = range(len(orden))
    alto = 0.38
    fig, ax = plt.subplots(figsize=(9, 6.4))

    ax.barh([v + alto / 2 for v in y], f1_reglas, height=alto,
            color=SERIE_REGLAS, label="Motor de reglas", zorder=3)
    ax.barh([v - alto / 2 for v in y], f1_llm, height=alto,
            color=SERIE_LLM, label="LLM", hatch="///", edgecolor=SUPERFICIE,
            linewidth=0.6, zorder=3)

    ax.set_yticks(list(y), orden, fontsize=9)
    ax.set_xlim(0, 1.18)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "0,25", "0,50", "0,75", "1,0"], fontsize=9)
    ax.set_xlabel("F1 por categoría", fontsize=10, labelpad=8)
    ax.set_title("Dónde mejora el LLM sobre el motor de reglas", fontsize=12,
                 color=TINTA_PRIMARIA, pad=14, loc="left")

    ax.xaxis.grid(True, color=REJILLA, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(EJE)
    ax.tick_params(length=0)

    # Solo se rotula la diferencia, que es el hallazgo. Los valores exactos
    # estan en informe.md; un numero sobre cada una de las 22 barras seria ruido.
    for i, etiqueta in enumerate(orden):
        delta = res_llm.por_clase[etiqueta].f1 - res_reglas.por_clase[etiqueta].f1
        signo = "+" if delta > 0 else ("±" if delta == 0 else "−")
        ax.text(1.02, i, f"{signo}{abs(delta):.2f}", va="center", fontsize=8.5,
                color=TINTA_SECUNDARIA if delta else TINTA_TENUE,
                fontweight="bold" if abs(delta) >= 0.3 else "normal")
    ax.text(1.02, len(orden) - 0.4, "Δ F1", va="center", fontsize=8.5,
            color=TINTA_TENUE, style="italic")

    # Arriba a la derecha, fuera del area de datos: en "lower right" tapaba las
    # barras de la ultima categoria.
    leyenda = ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.005),
                        frameon=False, fontsize=9, ncol=2)
    for texto in leyenda.get_texts():
        texto.set_color(TINTA_SECUNDARIA)

    salidas = _guardar(fig, ruta)
    plt.close(fig)
    return salidas
