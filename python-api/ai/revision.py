"""
Sprint 7 · HU-11 · AISCOP-67: por qué un ticket va a revisión humana.

La confianza que declara el modelo atrapa los tickets sin información (AISCOP-51), pero no sus errores:
estos llegan con 0,95, igual que los aciertos. Por eso la revisión ya no es solo «confianza ≤ 0,5».
Ahora lleva un motivo, y suma el caso que la confianza no veía: un ticket urgente sin detalle del problema
(la sonda «Urgente: necesito que me llamen hoy» salía con 0,95).

La discrepancia con el motor de reglas también se midió (evaluation/umbral.py): atrapa 5 de 6 errores
del examen, pero manda el 50 % de los tickets a revisión. Ninguna variante barata baja de ese 25 % de
carga que pedía el CA-1, así que no se activa. La decisión está en evaluation/README.md.
"""
from __future__ import annotations

MOTIVO_CONFIANZA_BAJA = "confianza_baja"
MOTIVO_URGENTE_SIN_DETALLE = "urgente_sin_detalle"
MOTIVOS = (MOTIVO_CONFIANZA_BAJA, MOTIVO_URGENTE_SIN_DETALLE)

# Los 66 tickets del conjunto tienen 11 palabras o más; una urgencia de menos de 10 no dice cuál es el problema.
PALABRAS_MINIMAS = 10


def es_urgente(texto: str, sentimiento: str | None, prioridad: str | None) -> bool:
    return prioridad == "Alta" or sentimiento == "Urgente" or "urgente" in texto.lower()


def motivo_revision(texto: str, sentimiento: str | None, prioridad: str | None, confianza: float | None,
                    requiere_por_confianza: bool) -> str | None:
    """Motivo por el que una persona debe revisar la clasificación del modelo, o None si no hace falta."""
    if confianza is None:  # lo clasificó el motor de reglas: no hay predicción del modelo que revisar
        return None
    if requiere_por_confianza:
        return MOTIVO_CONFIANZA_BAJA
    if es_urgente(texto, sentimiento, prioridad) and len(texto.split()) < PALABRAS_MINIMAS:
        return MOTIVO_URGENTE_SIN_DETALLE
    return None
