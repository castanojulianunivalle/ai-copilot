"""AISCOP-45: el conjunto de examen esta congelado y la particion es estratificada y estable."""
import json
from collections import Counter

import particion as P


def test_conjunto_balanceado_y_etiquetado():
    filas = P.cargar()
    assert len(filas) == 66
    assert set(Counter(f["categoria_real"] for f in filas).values()) == {6}
    assert all(f["categoria_real"] and f["sentimiento_real"] and f["prioridad_real"] for f in filas)


def test_particion_estratificada():
    filas = P.cargar()
    practica, examen = P.filtrar(filas, "practica"), P.filtrar(filas, "examen")
    assert (len(practica), len(examen)) == (22, 44)
    assert set(Counter(f["categoria_real"] for f in practica).values()) == {2}
    assert set(Counter(f["categoria_real"] for f in examen).values()) == {4}
    assert not {f["id"] for f in practica} & {f["id"] for f in examen}


def test_particion_no_depende_del_orden_del_archivo():
    filas = P.cargar()
    assert P.particionar(filas) == P.particionar(list(reversed(filas)))


def test_coincide_con_la_congelada():
    congelada = json.loads(P.CONGELADA.read_text(encoding="utf-8"))
    asignacion = P.particionar(P.cargar())
    assert congelada["sha256_fixture"] == P.huella_archivo(), "el conjunto de examen cambio despues de congelarse"
    assert congelada["practica"] == sorted(i for i, p in asignacion.items() if p == "practica")
    assert congelada["examen"] == sorted(i for i, p in asignacion.items() if p == "examen")
