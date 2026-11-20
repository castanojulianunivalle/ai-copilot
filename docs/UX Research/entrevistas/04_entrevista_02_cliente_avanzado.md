# Entrevista 02 — Cliente Avanzada

> **Transcripción completa (entrevistador + entrevistada)** · Duración real: **10 min**. Sirve como transcripción de referencia para la grabación en video y como insumo del Diagrama de Afinidad.

---

## Ficha de la sesión

| Campo | Valor |
|-------|-------|
| ID de entrevista | EUX-002 |
| Pseudónimo | **Daniela Andrea R.** |
| Edad | 31 años |
| Cargo | Lead de Operaciones Digitales — empresa de e-commerce mediana (≈300 empleados) |
| Ciudad | Medellín, Colombia |
| Nivel digital declarado | **Alto / Power user** |
| Tiempo en el rol | 6 años (antes: dev front-end en una startup) |
| Modalidad | Google Meet |
| Fecha | 12/05/2026, 03:00 p.m. |
| Duración real | **10 minutos** |
| Consentimiento firmado | ✅ (PDF en Drive privado) |

---

## Bloque 1 — Apertura (0:00 – 0:30)

**E:** ¡Daniela, qué más! Tres cositas: no hay respuestas correctas, lo que me sirve es tu experiencia tal cual la vives; puedes parar cuando quieras; la sesión se graba solo con fines académicos y vas a aparecer con un pseudónimo. ¿Todo bien si arrancamos?

**D:** Todo bien, parce, dale. Ya firmé el consentimiento esta mañana.

*(Inicio grabación.)*

---

## Bloque 2 — Calentamiento (0:30 – 1:30)

**E:** Cuéntame en una frase a qué te dedicas y qué tan cómoda te sientes con la tecnología en tu día a día.

**D:** Manejo Operaciones Digitales en e-commerce: todo lo que pasa entre que el cliente paga y le llega el pedido. Vengo del mundo dev, aprendí React sola hace 8 años. **El reto no es aprender una herramienta nueva, es decidir cuál merece la pena.** Manejo Jira, Slack, ServiceNow, Zendesk, AWS, GitHub, todos los días.

---

## Bloque 3 — Comportamiento actual (1:30 – 4:30)

**E:** La última vez que necesitaste ayuda con un sistema, ¿qué hiciste? Llévame paso a paso, brevemente.

**D:** Hace dos semanas. Nuestra pasarela de pagos tuvo un downtime y se nos cayó el checkout 18 minutos. Entré al portal de ellos —ServiceNow—, abrí ticket, escribí descripción técnica con request IDs, timestamps en UTC, screenshot del 502 y le metí severidad P1. **Por escrito porque queda traza; una llamada me bloquea 30 minutos.** A los 4 minutos me respondió un agente N2.

> 🟢 **A02:** «*Por escrito queda traza; una llamada me bloquea*» — preferencia por canal asíncrono.

**E:** ¿Qué fue lo más frustrante de esa experiencia y qué fue lo que sí funcionó?

**D:** Lo frustrante: dropdown de 47 categorías y ninguna decía "pasarela caída", tuve que escoger "Other" y caer en cola de triaje manual. Lo que sí funcionó: el portal me daba un timeline en vivo —*"agente asignada: Mateo, 14:03, leyó tu mensaje"*—. **Esos pasos en tiempo real me bajaron muchísimo la ansiedad.**

> 🟢 **A04:** «*Pasos en tiempo real bajaron mi ansiedad*» — feedback continuo / timeline.

---

## Bloque 4 — Pain point clave (4:30 – 5:30)

**E:** Si pudieras arreglar UNA sola cosa de cómo funciona hoy la mesa de ayuda, ¿cuál sería?

**D:** Que la herramienta tenga **API REST documentada y webhooks**. Sin eso, **estoy presa**. Hoy tengo soporte fragmentado en Zendesk, correo, WhatsApp Business y Slack Connect, y tres canales pueden ser el mismo problema. Con API yo construyo lo que quiera encima.

> 🟢 **A12:** «*Sin API ni webhooks, estoy presa*» — necesidad de extensibilidad.

---

## Bloque 5 — Validación del concepto (5:30 – 8:00)

**E:** Estamos diseñando una mesa de ayuda donde el cliente crea tickets desde un portal web; un sistema clasifica automáticamente y un agente gestiona desde un dashboard. En segunda fase, una IA prioriza por urgencia y sentimiento. ¿Qué reacción inmediata tienes?

**D:** Conceptualmente bien, pero tengo dos checks. Primero: que tengan **línea base con reglas y luego comparen con LLM** — eso es serio. Segundo: la IA tiene que ser **explicable**. Si me clasifica como "Facturación", quiero ver qué palabras detectó. **Una caja negra no la pongo en producción.** Y si me bajan la prioridad, que me expliquen por qué.

> 🟢 **A09:** «*Una caja negra no la pongo en producción*» — explicabilidad como requisito.
>
> 🟢 **A06:** «*Si me bajas la prioridad, explícame por qué*» — transparencia algorítmica.

**E:** Si tuvieras que recomendarnos UNA funcionalidad imprescindible para la primera versión, ¿cuál sería?

**D:** **Accesibilidad y SSO desde el día uno.** Atajos de teclado, contraste, ARIA labels y SAML/OIDC. Si lo metes después, dolor. Las empresas serias no van a crear una clave más.

> 🟢 **A14:** «*Accesibilidad y SSO desde el día uno*» — requisitos no funcionales como hard requirement.

---

## Bloque 6 — Cierre (8:00 – 10:00)

**E:** ¿Hay algo importante que no te pregunté?

**D:** Sí: midan **time-to-first-response** desde el día uno. Es la métrica reina. Y privacidad del LLM: ¿on-prem o proveedor externo? Eso determina si lo puedo usar con datos de clientes.

**E:** En una sola palabra: ¿qué debería ser este sistema para ti?

**D:** **Integrable.**

**E:** Listo Daniela, gracias. Detengo grabación.

---

## Anexos: insights destacados (para alimentar el Diagrama de Afinidad)

| ID | Verbatim / Insight | Tema preliminar |
|----|---------------------|-----------------|
| A02 | «Por escrito queda traza, una llamada me bloquea» | Asincronía / paralelización |
| A04 | «Pasos en tiempo real bajaron mi ansiedad» | Feedback continuo / timeline |
| A06 | «Si me bajas la prioridad, explícame por qué» | Transparencia de decisiones |
| A09 | «Una caja negra no la pongo en producción» | Explicabilidad de IA |
| A12 | «Sin API ni webhooks, estoy presa» | Extensibilidad / integraciones |
| A14 | «Accesibilidad y SSO desde el día uno» | Requisitos no funcionales |

**Palabra-síntesis (one-word recap):** *Integrable.*
