"""
Sprint 5 · HU-06 · AISCOP-42: taxonomia cerrada del componente inteligente.

Un unico sitio donde viven las etiquetas validas. El prompt las enumera, el
parser valida contra ellas, la migracion las restringe con CHECK y la
evaluacion del Sprint 6 las usa como ejes de la matriz de confusion. Si se
duplicaran en cuatro lugares, cualquier desincronizacion aparecería como una
caida de accuracy que no es del modelo sino del codigo.
"""
from __future__ import annotations

import unicodedata

# Las mismas 11 categorias del motor de reglas del Semestre 1
# (`classify_with_rules`). Comparar IA contra reglas exige que ambos motores
# escojan del mismo conjunto.
CATEGORIAS: tuple[str, ...] = (
    "Técnico",
    "Facturación",
    "Comercial",
    "Acceso",
    "Cuenta",
    "Rendimiento",
    "UX/UI",
    "Seguridad",
    "Integraciones",
    "Móvil",
    "Solicitudes",
)

SENTIMIENTOS: tuple[str, ...] = ("Frustrado", "Urgente", "Neutral", "Satisfecho")

PRIORIDADES: tuple[str, ...] = ("Alta", "Media", "Baja")

# HU-09: el ticket sube de prioridad cuando el tono lo justifica.
PRIORIDAD_POR_SENTIMIENTO: dict[str, str] = {
    "Urgente": "Alta",
    "Frustrado": "Alta",
    "Neutral": "Media",
    "Satisfecho": "Baja",
}


def _plegar(valor: str) -> str:
    """minusculas y sin tildes, para comparar 'Facturacion' con 'Facturación'."""
    sin_tildes = unicodedata.normalize("NFKD", valor)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return sin_tildes.strip().lower()


def _indice(valores: tuple[str, ...]) -> dict[str, str]:
    return {_plegar(v): v for v in valores}


_IDX_CATEGORIAS = _indice(CATEGORIAS)
_IDX_SENTIMIENTOS = _indice(SENTIMIENTOS)
_IDX_PRIORIDADES = _indice(PRIORIDADES)

# El modelo a veces devuelve una variante razonable en vez de la etiqueta exacta.
# Mapearlas es preferible a descartar la prediccion y perder la fila: un
# descarte contaria como error del modelo en la evaluacion cuando en realidad
# acerto la clase y fallo la ortografia.
_SINONIMOS_CATEGORIA: dict[str, str] = {
    "tecnico": "Técnico",
    "soporte tecnico": "Técnico",
    "facturacion": "Facturación",
    "billing": "Facturación",
    "pagos": "Facturación",
    "ventas": "Comercial",
    "login": "Acceso",
    "autenticacion": "Acceso",
    "usuario": "Cuenta",
    "perfil": "Cuenta",
    "performance": "Rendimiento",
    "ui": "UX/UI",
    "ux": "UX/UI",
    "ux / ui": "UX/UI",
    "ux-ui": "UX/UI",
    "interfaz": "UX/UI",
    "integracion": "Integraciones",
    "api": "Integraciones",
    "movil": "Móvil",
    "mobile": "Móvil",
    "solicitud": "Solicitudes",
    "feature request": "Solicitudes",
}


def normalizar_categoria(valor: str | None) -> str | None:
    if not valor:
        return None
    clave = _plegar(valor)
    return _IDX_CATEGORIAS.get(clave) or _SINONIMOS_CATEGORIA.get(clave)


def normalizar_sentimiento(valor: str | None) -> str | None:
    if not valor:
        return None
    return _IDX_SENTIMIENTOS.get(_plegar(valor))


def normalizar_prioridad(valor: str | None) -> str | None:
    if not valor:
        return None
    return _IDX_PRIORIDADES.get(_plegar(valor))
