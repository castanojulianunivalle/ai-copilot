"""
Accion acordada en la retrospectiva del Sprint 4: verificar el balance del
reparto practica/examen sobre identificadores inventados, para que un error
como el del bigint con signo falle en una prueba y no en la revision del SQL.

El reparto vive en SQL (vista dataset_tickets). Aqui se replica la regla en
Python y, para que la replica no se quede desactualizada, se comprueba tambien
que la migracion siga diciendo exactamente esa regla.
"""
from __future__ import annotations

import hashlib
import random
import re
import uuid
from pathlib import Path

MIGRACION = (Path(__file__).resolve().parents[2]
             / "supabase" / "migrations" / "20260902000000_dataset_historico.sql")

# 'cc' = 204 de 256 valores posibles del primer byte del md5.
UMBRAL = "cc"
FRACCION_ESPERADA = int(UMBRAL, 16) / 256


def split(ticket_id: str) -> str:
    """Misma regla que la vista: primeros dos hex del md5 del uuid, como texto."""
    return "train" if hashlib.md5(ticket_id.encode()).hexdigest()[:2] < UMBRAL else "test"


def ids_inventados(n: int, semilla: int = 20260924) -> list[str]:
    rng = random.Random(semilla)
    return [str(uuid.UUID(int=rng.getrandbits(128), version=4)) for _ in range(n)]


def test_la_migracion_sigue_usando_la_regla_replicada():
    sql = MIGRACION.read_text(encoding="utf-8")
    assert re.search(r"substr\(md5\(t\.id::text\),\s*1,\s*2\)\s*<\s*'cc'", sql), (
        "La regla del reparto cambio en el SQL: hay que actualizar esta replica"
    )


def test_el_reparto_es_determinista():
    for i in ids_inventados(200):
        assert split(i) == split(i)


def test_el_reparto_respeta_la_proporcion_sobre_ids_inventados():
    ids = ids_inventados(20_000)
    practica = sum(split(i) == "train" for i in ids) / len(ids)
    # Con 20 000 ids la desviacion tipica es ~0,28 pp; 1,5 pp son mas de 5 sigmas.
    assert abs(practica - FRACCION_ESPERADA) < 0.015, f"{practica:.3%} vs {FRACCION_ESPERADA:.3%}"


def test_los_dos_lados_reciben_tickets():
    lados = {split(i) for i in ids_inventados(500)}
    assert lados == {"train", "test"}


def test_el_diseno_anterior_si_se_desbalanceaba():
    """Documenta el defecto que motivo la accion: bigint con signo y modulo.

    En PostgreSQL el modulo de un negativo es negativo, asi que la condicion
    'resto < 80' acepta toda la mitad negativa y el reparto deja de ser 80/20.
    """
    def split_viejo(ticket_id: str) -> str:
        entero = int(hashlib.md5(ticket_id.encode()).hexdigest()[:16], 16)
        if entero >= 2**63:          # reinterpretado como bigint con signo
            entero -= 2**64
        resto = int(entero % 100) if entero >= 0 else -((-entero) % 100)  # semantica de Postgres
        return "train" if resto < 80 else "test"

    ids = ids_inventados(20_000)
    practica_vieja = sum(split_viejo(i) == "train" for i in ids) / len(ids)
    assert practica_vieja > 0.85  # ~90 %: la mitad negativa cae entera en train
