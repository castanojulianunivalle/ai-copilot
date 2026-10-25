"""
HU-13: atención de tickets por agentes. Tomar, liberar y reasignar; comentarios, notas internas e historial.

Corre la API FastAPI real contra una Supabase en memoria que aplica los filtros (eq, is_, in_), así que la toma
atómica se prueba de verdad: el UPDATE condicionado a «asignado_a is null» deja pasar solo al primero.
"""
from __future__ import annotations

import itertools

import pytest
from fastapi.testclient import TestClient

import main

CLIENTE, OTRO_CLIENTE, AGENTE, AGENTE_2, ADMIN = "u-cliente", "u-otro", "u-agente", "u-agente2", "u-admin"
_ids = itertools.count(1)


class _Resultado:
    def __init__(self, data):
        self.data = data


class _Consulta:
    def __init__(self, base, tabla):
        self.base, self.tabla = base, tabla
        self.filtros, self.accion, self.valores, self.orden = [], "select", None, None

    def select(self, _columnas="*"):
        return self

    def insert(self, fila):
        self.accion, self.valores = "insert", fila
        return self

    def update(self, valores):
        self.accion, self.valores = "update", valores
        return self

    def eq(self, col, valor):
        self.filtros.append(lambda f: f.get(col) == valor)
        return self

    def is_(self, col, valor):
        assert valor == "null"
        self.filtros.append(lambda f: f.get(col) is None)
        return self

    def in_(self, col, valores):
        self.filtros.append(lambda f: f.get(col) in valores)
        return self

    def order(self, col):
        self.orden = col
        return self

    def limit(self, _n):
        return self

    def execute(self):
        filas = self.base.datos.setdefault(self.tabla, [])
        if self.accion == "insert":
            fila = {"id": f"{self.tabla}-{next(_ids)}", "created_at": f"2026-10-26T00:00:{next(_ids):02d}Z",
                    "interno": False, **self.valores}
            filas.append(fila)
            return _Resultado([dict(fila)])
        elegidas = [f for f in filas if all(c(f) for c in self.filtros)]
        if self.accion == "update":
            for f in elegidas:
                f.update(self.valores)
        if self.orden:
            elegidas = sorted(elegidas, key=lambda f: f[self.orden])
        return _Resultado([dict(f) for f in elegidas])


class SupabaseMemoria:
    def __init__(self):
        self.datos = {
            "profiles": [{"id": CLIENTE, "role": "cliente", "email": "cliente@x"},
                         {"id": OTRO_CLIENTE, "role": "cliente", "email": "otro@x"},
                         {"id": AGENTE, "role": "agente", "email": "agente@x"},
                         {"id": AGENTE_2, "role": "agente", "email": "agente2@x"},
                         {"id": ADMIN, "role": "administrador", "email": "admin@x"}],
            "tickets": [{"id": "t1", "titulo": "No puedo pagar", "description": "Error al pagar", "estado": "Abierto",
                         "created_by": CLIENTE, "asignado_a": None, "created_at": "2026-10-26T00:00:00Z"}],
            "ticket_eventos": [],
        }

    def table(self, nombre):
        return _Consulta(self, nombre)

    def ticket(self):
        return self.datos["tickets"][0]

    def eventos(self, tipo=None):
        return [e for e in self.datos["ticket_eventos"] if tipo is None or e["tipo"] == tipo]


ROLES = {CLIENTE: "cliente", OTRO_CLIENTE: "cliente", AGENTE: "agente", AGENTE_2: "agente", ADMIN: "administrador"}


@pytest.fixture
def base(monkeypatch):
    memoria = SupabaseMemoria()
    monkeypatch.setattr(main, "get_supabase", lambda: memoria)
    return memoria


@pytest.fixture
def como(base):
    """como(usuario) devuelve un TestClient autenticado con ese usuario y su rol."""
    clientes = []

    def _como(usuario):
        main.app.dependency_overrides[main._verify_token] = lambda: (usuario, ROLES[usuario])
        c = TestClient(main.app)
        clientes.append(c)
        return c

    yield _como
    main.app.dependency_overrides.clear()


def test_agente_toma_ticket_libre_y_queda_en_el_historial(base, como):
    r = como(AGENTE).post("/tickets/t1/tomar")
    assert r.status_code == 200 and r.json()["asignado_a"] == AGENTE
    assert base.ticket()["asignado_a"] == AGENTE and base.ticket()["asignado_en"]
    (evento,) = base.eventos("asignacion")
    assert evento["autor_id"] == AGENTE and evento["asignado_despues"] == AGENTE


def test_segundo_agente_no_puede_tomar_un_ticket_ya_tomado(base, como):
    assert como(AGENTE).post("/tickets/t1/tomar").status_code == 200
    r = como(AGENTE_2).post("/tickets/t1/tomar")
    assert r.status_code == 409
    assert base.ticket()["asignado_a"] == AGENTE
    assert len(base.eventos("asignacion")) == 1


def test_el_cliente_no_puede_tomar_ni_cambiar_estado(como):
    cliente = como(CLIENTE)
    assert cliente.post("/tickets/t1/tomar").status_code == 403
    assert cliente.patch("/tickets/t1/estado", params={"estado": "Cerrado"}).status_code == 403
    assert cliente.put("/tickets/t1", json={"estado": "Cerrado"}).status_code == 403


def test_pasar_a_en_proceso_asigna_al_agente_y_guarda_el_comentario(base, como):
    r = como(AGENTE).patch("/tickets/t1/estado", params={"estado": "En proceso"},
                           json={"comentario": "Estamos revisando el cobro con el banco."})
    assert r.status_code == 200 and r.json()["asignado_a"] == AGENTE
    assert base.ticket()["estado"] == "En proceso" and base.ticket()["asignado_a"] == AGENTE
    (cambio,) = base.eventos("estado")
    assert (cambio["estado_antes"], cambio["estado_despues"]) == ("Abierto", "En proceso")
    assert cambio["texto"] == "Estamos revisando el cobro con el banco."


def test_el_cambio_de_estado_sin_comentario_sigue_funcionando(base, como):
    # Compatibilidad con v2.1.0 y con la prueba de humo TC-H6: PATCH ?estado= sin cuerpo.
    assert como(AGENTE).patch("/tickets/t1/estado", params={"estado": "Cerrado"}).status_code == 200
    assert base.ticket()["estado"] == "Cerrado"


def test_estado_invalido(como):
    assert como(AGENTE).patch("/tickets/t1/estado", params={"estado": "Resuelto"}).status_code == 400


def test_liberar_solo_quien_lo_tiene_o_el_administrador(base, como):
    como(AGENTE).post("/tickets/t1/tomar")
    assert como(AGENTE_2).post("/tickets/t1/liberar").status_code == 403
    assert como(AGENTE).post("/tickets/t1/liberar").status_code == 200
    assert base.ticket()["asignado_a"] is None
    como(AGENTE).post("/tickets/t1/tomar")
    assert como(ADMIN).post("/tickets/t1/liberar").status_code == 200


def test_reasignar_es_solo_del_administrador_y_a_un_agente(base, como):
    assert como(AGENTE).post("/tickets/t1/asignar", json={"agente_id": AGENTE_2}).status_code == 403
    assert como(ADMIN).post("/tickets/t1/asignar", json={"agente_id": CLIENTE}).status_code == 400
    assert como(ADMIN).post("/tickets/t1/asignar", json={"agente_id": AGENTE_2}).status_code == 200
    assert base.ticket()["asignado_a"] == AGENTE_2


def test_comentarios_y_notas_internas(base, como):
    assert como(AGENTE).post("/tickets/t1/comentarios", json={"texto": "Ya hablé con facturación."}).status_code == 200
    assert como(AGENTE).post("/tickets/t1/comentarios",
                             json={"texto": "Cliente con dos reclamos previos", "interno": True}).status_code == 200
    assert como(CLIENTE).post("/tickets/t1/comentarios", json={"texto": "Gracias, quedo atento."}).status_code == 200
    # El cliente no escribe notas internas, ni comenta tickets ajenos, ni manda comentarios vacíos.
    assert como(CLIENTE).post("/tickets/t1/comentarios", json={"texto": "x", "interno": True}).status_code == 403
    assert como(OTRO_CLIENTE).post("/tickets/t1/comentarios", json={"texto": "hola"}).status_code == 403
    assert como(AGENTE).post("/tickets/t1/comentarios", json={"texto": "   "}).status_code == 400


def test_el_cliente_ve_su_historial_sin_las_notas_internas(base, como):
    como(AGENTE).post("/tickets/t1/tomar")
    como(AGENTE).post("/tickets/t1/comentarios", json={"texto": "Nota interna", "interno": True})
    como(AGENTE).post("/tickets/t1/comentarios", json={"texto": "Respuesta al cliente"})

    del_agente = como(AGENTE).get("/tickets/t1/eventos").json()
    del_cliente = como(CLIENTE).get("/tickets/t1/eventos").json()
    assert [e["tipo"] for e in del_agente] == ["asignacion", "comentario", "comentario"]
    assert [e.get("texto") for e in del_cliente if e["tipo"] == "comentario"] == ["Respuesta al cliente"]
    assert del_agente[0]["autor"] == {"id": AGENTE, "email": "agente@x", "role": "agente"}
    assert como(OTRO_CLIENTE).get("/tickets/t1/eventos").status_code == 403


def test_lista_de_agentes_solo_para_el_equipo(como):
    agentes = como(AGENTE).get("/agentes").json()
    assert {a["id"] for a in agentes} == {AGENTE, AGENTE_2, ADMIN}
    assert como(CLIENTE).get("/agentes").status_code == 403


def test_ticket_inexistente(como):
    assert como(AGENTE).post("/tickets/no-existe/tomar").status_code == 404
