"""
Sprint 5 · HU-06 · AISCOP-42: orquestador de la clasificacion.

Une cliente + prompt + parser y garantiza la propiedad que hace desplegable el
componente inteligente: **clasificar nunca falla**. Si el LLM no responde, si
responde tarde o si responde algo ininterpretable, se cae al motor de reglas
del Semestre 1 y el ticket se crea igual. La IA mejora la clasificacion; no se
convierte en un punto unico de fallo del alta de tickets.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from .llm_client import ClienteLLM, LLMError
from .parser import Clasificacion, RespuestaInvalida, parsear
from .prompts import PROMPT_SISTEMA, VERSION_PROMPT, construir_mensaje_usuario
from .taxonomia import PRIORIDAD_POR_SENTIMIENTO

logger = logging.getLogger(__name__)

MOTOR_LLM = "llm"
MOTOR_REGLAS = "reglas"


@dataclass(frozen=True)
class ResultadoClasificacion:
    clasificacion: Clasificacion
    motor: str
    modelo: str
    latencia_ms: int
    # Por que se cayo a reglas. Se guarda para poder cuantificar en el Sprint 6
    # cuantas veces la IA no estuvo disponible, que es un resultado en si mismo.
    error: str | None = None

    @property
    def uso_ia(self) -> bool:
        return self.motor == MOTOR_LLM


def _desde_reglas(texto: str, fallback: Callable[[str], str], error: str | None) -> ResultadoClasificacion:
    categoria = fallback(texto)
    return ResultadoClasificacion(
        clasificacion=Clasificacion(
            categoria=categoria,
            sentimiento="Neutral",
            prioridad=PRIORIDAD_POR_SENTIMIENTO["Neutral"],
            # 0.0 y no 0.5: el motor de reglas no estima confianza, y marcar
            # estas filas con el valor por defecto del LLM las mezclaria en las
            # estadisticas de confianza del articulo.
            confianza=0.0,
            justificacion=None,
        ),
        motor=MOTOR_REGLAS,
        modelo=f"classify_with_rules@{VERSION_PROMPT}",
        latencia_ms=0,
        error=error,
    )


def clasificar(
    texto: str,
    fallback: Callable[[str], str],
    cliente: ClienteLLM | None = None,
) -> ResultadoClasificacion:
    """Clasifica un ticket. `fallback` es el motor de reglas del Semestre 1."""
    cliente = cliente or ClienteLLM()

    if not cliente.habilitado:
        return _desde_reglas(texto, fallback, error=None)

    try:
        respuesta = cliente.completar(PROMPT_SISTEMA, construir_mensaje_usuario(texto))
    except LLMError as exc:
        logger.warning("LLM no disponible, se usa el motor de reglas: %s", exc)
        return _desde_reglas(texto, fallback, error=str(exc)[:200])

    try:
        clasificacion = parsear(respuesta.texto)
    except RespuestaInvalida as exc:
        logger.warning("Respuesta del LLM ininterpretable, se usa el motor de reglas: %s", exc)
        return _desde_reglas(texto, fallback, error=str(exc)[:200])

    return ResultadoClasificacion(
        clasificacion=clasificacion,
        motor=MOTOR_LLM,
        # El modelo solo no basta para reproducir un resultado: la version del
        # prompt es la otra mitad del experimento del Sprint 6.
        modelo=f"{respuesta.modelo}@{VERSION_PROMPT}",
        latencia_ms=respuesta.latencia_ms,
    )
