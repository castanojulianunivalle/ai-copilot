"""
Motor de clasificacion por reglas (Semestre 1, HU-04).

Vive en su propio modulo desde el Sprint 6 por una razon concreta: el script de
evaluacion tiene que ejercitar EXACTAMENTE esta funcion y no una copia, y
haciendo `from main import classify_with_rules` arrastraria FastAPI, Supabase y
la verificacion de JWT al entorno de evaluacion. main.py lo reexporta, asi que
su superficie publica no cambia.

La logica es la del Semestre 1, intacta: es la linea base contra la que se
compara el LLM, y tocarla invalidaria la comparacion.
"""
import logging

logger = logging.getLogger(__name__)


def classify_with_rules(text: str) -> str:
    """HU-04: Clasificación por palabras clave (motor de reglas)."""
    text_lower = (text or "").lower()
    category = "Técnico"

    category_rules = [
        ("Facturación", ["factura", "billing", "cobro", "pago", "suscripción", "reembolso"]),
        ("Acceso", ["login", "inicio de sesión", "contraseña", "bloqueo", "2fa", "otp"]),
        ("Cuenta", ["perfil", "cuenta", "usuario", "registro", "alta", "baja"]),
        ("Integraciones", ["api", "webhook", "zapier", "slack", "integración", "integraciones"]),
        ("Rendimiento", ["lento", "latencia", "demora", "performance", "rendimiento"]),
        ("UX/UI", ["diseño", "ui", "ux", "interfaz", "botón", "boton", "pantalla"]),
        ("Seguridad", ["phishing", "fraude", "seguridad", "vulnerabilidad", "hack"]),
        ("Solicitudes", ["quiero", "me gustaría", "feature", "mejorar", "solicitud"]),
        ("Comercial", ["precio", "plan", "cotización", "ventas", "comercial"]),
        ("Móvil", ["android", "ios", "móvil", "movil", "celular"]),
        ("Técnico", ["error", "fallo", "bug", "no funciona", "no sirve", "crash", "internet"]),
    ]

    for name, keywords in category_rules:
        if any(k in text_lower for k in keywords):
            category = name
            break

    logger.info(f"Classification: {category} (reglas)")
    return category
