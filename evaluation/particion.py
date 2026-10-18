"""
Sprint 6 · HU-09 · AISCOP-45: particion de practica y examen del conjunto etiquetado.

El prompt v2 (AISCOP-50) se ajusta mirando tickets; si esos tickets fueran los
mismos con los que se mide, la evaluacion dejaria de ser ciega. Por eso los 66
tickets se reparten en dos particiones que no se tocan:

- practica: 2 por categoria (22). Es lo unico que se mira al ajustar el prompt.
- examen:   4 por categoria (44). Solo se usa para medir, una vez congelado el
  prompt.

El reparto es estratificado y determinista: dentro de cada categoria los tickets
se ordenan por md5(id) y los dos primeros van a practica. No depende de
random() ni del orden del archivo, asi que el mismo ticket cae siempre en la
misma particion.

`fixtures/particion_congelada.json` guarda el reparto y la huella SHA-256 del
conjunto. Las pruebas comprueban que lo calculado coincide con lo congelado:
si alguien edita un ticket de examen o cambia la regla, fallan.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tickets_etiquetados.jsonl"
CONGELADA = Path(__file__).resolve().parent / "fixtures" / "particion_congelada.json"
PRACTICA_POR_CATEGORIA = 2
PARTICIONES = ("practica", "examen")


def huella_id(ticket_id: str) -> str:
    return hashlib.md5(ticket_id.encode("utf-8")).hexdigest()


def huella_archivo(ruta: Path = FIXTURE) -> str:
    # Sobre el texto con finales de linea LF: Git en Windows puede escribir CRLF,
    # y la huella tiene que ser la misma en cualquier maquina y en la CI.
    texto = ruta.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def cargar(ruta: Path = FIXTURE) -> list[dict[str, Any]]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def particionar(filas: list[dict[str, Any]]) -> dict[str, str]:
    """{id: 'practica' | 'examen'}, estratificado por categoria."""
    por_categoria: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fila in filas:
        por_categoria[fila["categoria_real"]].append(fila)
    asignacion = {}
    for filas_categoria in por_categoria.values():
        for k, fila in enumerate(sorted(filas_categoria, key=lambda f: huella_id(f["id"]))):
            asignacion[fila["id"]] = "practica" if k < PRACTICA_POR_CATEGORIA else "examen"
    return asignacion


def filtrar(filas: list[dict[str, Any]], particion: str) -> list[dict[str, Any]]:
    """Las filas de una particion; 'todo' devuelve el conjunto completo."""
    if particion == "todo":
        return list(filas)
    if particion not in PARTICIONES:
        raise ValueError(f"Particion desconocida: {particion}")
    asignacion = particionar(filas)
    return [f for f in filas if asignacion[f["id"]] == particion]


def congelar(ruta_fixture: Path = FIXTURE, destino: Path = CONGELADA) -> dict[str, Any]:
    """Escribe el reparto congelado. Se corre una sola vez, al cerrar AISCOP-45."""
    filas = cargar(ruta_fixture)
    asignacion = particionar(filas)
    registro = {
        "fixture": ruta_fixture.name,
        "sha256_fixture": huella_archivo(ruta_fixture),
        "regla": f"por categoria, orden md5(id); los {PRACTICA_POR_CATEGORIA} primeros a practica",
        "practica": sorted(i for i, p in asignacion.items() if p == "practica"),
        "examen": sorted(i for i, p in asignacion.items() if p == "examen"),
    }
    destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return registro


if __name__ == "__main__":
    r = congelar()
    print(f"practica: {len(r['practica'])} · examen: {len(r['examen'])} · sha256 {r['sha256_fixture'][:12]}")
