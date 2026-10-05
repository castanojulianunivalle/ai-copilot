"""
Sprint 5 · HU-06 · AISCOP-42: prompt de clasificacion.

El prompt es un artefacto de investigacion, no una cadena de texto cualquiera:
es la variable independiente del experimento del Sprint 6. Se versiona con
`VERSION_PROMPT` y ese valor viaja hasta `classification_log.modelo`, de modo
que cualquier cifra del articulo se puede atribuir al prompt exacto que la
produjo.

Reglas de diseño aplicadas:
1. Taxonomia cerrada y enumerada; el modelo no puede inventar categorias.
2. Desambiguacion explicita de los pares que el motor de reglas confunde.
3. Few-shot corto y adversarial: los ejemplos son casos limite, no casos faciles.
4. Contrato de salida JSON estricto, sin prosa alrededor.
5. Se le pide declarar confianza baja en vez de adivinar, para poder enrutar a
   revision humana los casos dudosos.
"""
from __future__ import annotations

from .taxonomia import CATEGORIAS, PRIORIDADES, SENTIMIENTOS

VERSION_PROMPT = "clasificacion-v1"

# Los pares que mas se confunden. Se derivan de mirar donde falla el motor de
# reglas del Semestre 1: comparten palabras clave y el if/else se queda con la
# primera que casa, sin mirar la intencion.
_DESAMBIGUACION = """\
Distinciones que importan (son los pares que mas se confunden):
- Acceso vs Cuenta: "Acceso" es no poder entrar (contraseña, 2FA, bloqueo).
  "Cuenta" es gestionar datos ya estando dentro (perfil, correo, baja).
- Facturación vs Comercial: "Facturación" es un cobro ya ocurrido (factura,
  reembolso, cargo duplicado). "Comercial" es antes de comprar (precio, plan,
  cotización).
- Técnico vs Rendimiento: "Rendimiento" es que funciona pero lento. "Técnico"
  es que no funciona (error, caída, dato incorrecto).
- Solicitudes vs UX/UI: "Solicitudes" pide algo que no existe todavía. "UX/UI"
  se queja de algo que existe y estorba.
- Integraciones vs Técnico: "Integraciones" solo si el problema está en la
  frontera con un sistema externo (API, webhook, Slack).
- Seguridad: prevalece sobre cualquier otra si hay phishing, fraude, acceso no
  autorizado o fuga de datos, aunque el ticket también hable de otra cosa.

No uses "Técnico" como cajón de sastre: es la categoría correcta solo si el
problema es un fallo del producto que no encaja mejor en otra."""

_EJEMPLOS = [
    (
        "Cargo duplicado. Me cobraron el plan dos veces este mes y ya envié el "
        "soporte hace 5 días. Nadie responde. Esto es inaceptable.",
        {
            "categoria": "Facturación",
            "sentimiento": "Frustrado",
            "prioridad": "Alta",
            "confianza": 0.95,
            "justificacion": "Cobro duplicado ya ocurrido; el tono señala reclamo reiterado sin respuesta.",
        },
    ),
    (
        "Buenas, quisiera saber cuánto cuesta el plan empresarial y si incluye "
        "más usuarios. Gracias.",
        {
            "categoria": "Comercial",
            "sentimiento": "Neutral",
            "prioridad": "Baja",
            "confianza": 0.92,
            "justificacion": "Consulta de precio previa a la compra, no un cobro existente.",
        },
    ),
    (
        "El reporte tarda como 40 segundos en abrir desde ayer. Funciona, pero "
        "es desesperante con el cliente en el teléfono.",
        {
            "categoria": "Rendimiento",
            "sentimiento": "Frustrado",
            "prioridad": "Alta",
            "confianza": 0.9,
            "justificacion": "El módulo responde pero con latencia alta; no es una falla funcional.",
        },
    ),
    (
        "Me llegó un correo pidiendo mi contraseña con el logo de ustedes. No la "
        "di, pero quiero reportarlo.",
        {
            "categoria": "Seguridad",
            "sentimiento": "Neutral",
            "prioridad": "Alta",
            "confianza": 0.97,
            "justificacion": "Intento de phishing: Seguridad prevalece aunque mencione contraseña (Acceso).",
        },
    ),
]


def _bloque_ejemplos() -> str:
    import json

    partes = []
    for texto, salida in _EJEMPLOS:
        partes.append(
            f"Ticket: {texto}\nJSON: {json.dumps(salida, ensure_ascii=False)}"
        )
    return "\n\n".join(partes)


PROMPT_SISTEMA = f"""\
Eres un clasificador de tickets de soporte técnico en español. Analizas el
ticket y devuelves únicamente un objeto JSON.

Categorías permitidas (elige exactamente una, escrita igual que aquí):
{", ".join(CATEGORIAS)}

Sentimiento del cliente (exactamente uno):
{", ".join(SENTIMIENTOS)}

Prioridad (exactamente una):
{", ".join(PRIORIDADES)}

{_DESAMBIGUACION}

Prioridad: "Alta" si el cliente está Frustrado o el asunto es Urgente, si hay
riesgo de seguridad o si el cliente está bloqueado sin poder trabajar. "Baja"
si es una consulta informativa o una sugerencia. "Media" en los demás casos.

Formato de salida — solo este JSON, sin texto antes ni después, sin ```:
{{"categoria": "...", "sentimiento": "...", "prioridad": "...", "confianza": 0.0, "justificacion": "..."}}

- "confianza": número entre 0 y 1. Si el ticket es ambiguo o le falta
  información, baja la confianza en lugar de adivinar con seguridad falsa.
  Un valor por debajo de 0.5 marca el ticket para revisión humana.
- "justificacion": una sola frase, máximo 20 palabras, en español.

Ejemplos:

{_bloque_ejemplos()}"""


def construir_mensaje_usuario(texto: str, max_caracteres: int = 4000) -> str:
    """Envuelve el ticket. Se trunca por el final: en un ticket largo el
    planteamiento del problema suele estar al principio, y truncar acota tanto
    el costo por token como el riesgo de inyeccion de instrucciones al final."""
    limpio = (texto or "").strip()
    if len(limpio) > max_caracteres:
        limpio = limpio[:max_caracteres] + " […truncado]"
    return f"Ticket: {limpio}\nJSON:"
