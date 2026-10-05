"""
Sprint 5 · HU-06 · AISCOP-42: parsing y validacion de la respuesta del LLM.

Aunque se pida `response_format: json_object`, en la practica los modelos
abiertos servidos por routers devuelven a veces el JSON envuelto en ``` o
precedido de una frase. Descartar esas respuestas contaria como error del
modelo en la evaluacion del Sprint 6 cuando en realidad es un problema de
formato, asi que aqui se recupera lo recuperable y se falla solo cuando el
contenido no es interpretable.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass

from .taxonomia import (
    PRIORIDAD_POR_SENTIMIENTO,
    normalizar_categoria,
    normalizar_prioridad,
    normalizar_sentimiento,
)

logger = logging.getLogger(__name__)

CONFIANZA_REVISION_HUMANA = 0.5


class RespuestaInvalida(ValueError):
    """El texto del LLM no contiene una clasificacion utilizable."""


@dataclass(frozen=True)
class Clasificacion:
    categoria: str
    sentimiento: str
    prioridad: str
    confianza: float
    justificacion: str | None = None

    @property
    def requiere_revision(self) -> bool:
        # Comparacion inclusiva a proposito: el umbral exacto es tambien el
        # valor que se asigna cuando el modelo no declara confianza, y en ese
        # caso no hay evidencia de que estuviera seguro. Un 0.5 declarado es
        # ademas, por definicion, un empate que conviene que mire una persona.
        return self.confianza <= CONFIANZA_REVISION_HUMANA

    def as_dict(self) -> dict:
        return asdict(self)


_VALLA = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def _extraer_objeto(texto: str) -> str:
    """Devuelve el primer objeto JSON balanceado del texto.

    Se cuentan llaves ignorando las que aparecen dentro de cadenas, porque una
    justificacion puede contener '{' y un recorte por la ultima '}' del texto
    partiria el objeto por el sitio equivocado.
    """
    inicio = texto.find("{")
    if inicio == -1:
        raise RespuestaInvalida(f"Sin objeto JSON en la respuesta: {texto[:120]!r}")

    profundidad = 0
    en_cadena = False
    escapado = False
    for pos in range(inicio, len(texto)):
        char = texto[pos]
        if en_cadena:
            if escapado:
                escapado = False
            elif char == "\\":
                escapado = True
            elif char == '"':
                en_cadena = False
            continue
        if char == '"':
            en_cadena = True
        elif char == "{":
            profundidad += 1
        elif char == "}":
            profundidad -= 1
            if profundidad == 0:
                return texto[inicio : pos + 1]

    raise RespuestaInvalida(f"Objeto JSON sin cerrar: {texto[:120]!r}")


def _a_float(valor: object) -> float | None:
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        try:
            return float(valor.strip().replace("%", ""))
        except ValueError:
            return None
    return None


def parsear(texto: str) -> Clasificacion:
    crudo = _VALLA.sub("", texto or "").strip()
    bruto = _extraer_objeto(crudo)

    try:
        datos = json.loads(bruto)
    except json.JSONDecodeError as exc:
        # Ultimo recurso: coma sobrante antes de } o ], que es el error de
        # sintaxis mas comun en JSON generado por un modelo.
        reparado = re.sub(r",\s*([}\]])", r"\1", bruto)
        try:
            datos = json.loads(reparado)
            logger.warning("JSON del LLM reparado (coma sobrante)")
        except json.JSONDecodeError:
            raise RespuestaInvalida(f"JSON invalido: {exc.msg}") from exc

    if not isinstance(datos, dict):
        raise RespuestaInvalida(f"Se esperaba un objeto, llego {type(datos).__name__}")

    # La categoria es el unico campo sin recuperacion posible: es la variable
    # que se mide en el Sprint 6, inventarle un valor por defecto falsearia el
    # resultado. Los demas campos si admiten un default defendible.
    categoria = normalizar_categoria(datos.get("categoria") or datos.get("category"))
    if not categoria:
        raise RespuestaInvalida(f"Categoria no reconocida: {datos.get('categoria')!r}")

    sentimiento = normalizar_sentimiento(datos.get("sentimiento") or datos.get("sentiment"))
    if not sentimiento:
        logger.warning("Sentimiento no reconocido (%r), se asume Neutral", datos.get("sentimiento"))
        sentimiento = "Neutral"

    prioridad = normalizar_prioridad(datos.get("prioridad") or datos.get("priority"))
    if not prioridad:
        # HU-09: si el modelo no da prioridad, se deriva del tono detectado.
        prioridad = PRIORIDAD_POR_SENTIMIENTO.get(sentimiento, "Media")

    confianza = _a_float(datos.get("confianza") if "confianza" in datos else datos.get("confidence"))
    if confianza is None:
        # Sin confianza declarada se asume el umbral de revision, no 1.0: no
        # hay evidencia de que el modelo estuviera seguro.
        confianza = CONFIANZA_REVISION_HUMANA
    elif confianza > 1:
        # Algunos modelos responden 85 en vez de 0.85.
        confianza = confianza / 100 if confianza <= 100 else 1.0
    confianza = max(0.0, min(1.0, confianza))

    justificacion = datos.get("justificacion") or datos.get("justification")
    if isinstance(justificacion, str):
        justificacion = justificacion.strip()[:300] or None
    else:
        justificacion = None

    return Clasificacion(
        categoria=categoria,
        sentimiento=sentimiento,
        prioridad=prioridad,
        confianza=round(confianza, 3),
        justificacion=justificacion,
    )
