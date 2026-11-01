# Guion de grabación — Daniela Andrea R.

> **Para la persona que interpreta a Daniela.** Este guion contiene **tu** parte de la entrevista. Lo que dirá Julian está resumido al inicio de cada bloque para que sepas cuándo te toca hablar. **Duración total: 10 minutos.**

---

## Tu personaje (léelo antes de grabar)

| Campo | Valor |
|-------|-------|
| Nombre | Daniela Andrea R. |
| Edad | 31 años |
| Ciudad | Medellín, Colombia |
| Cargo | Lead de Operaciones Digitales en una empresa de e-commerce mediana (~300 empleados) |
| Antigüedad | 6 años en el rol (antes: dev front-end) |
| Personalidad | Power user, eficiente, técnica, opinionada, exigente, humor seco |
| Madurez digital | **Alta**. Maneja Jira, Slack, Notion, GitHub, AWS, SQL básico todos los días |
| Frase que la define | *«Sin API ni webhooks, estoy presa.»* |

### Tono al hablar

- Hablas rápido, vas al grano, mezclas español con anglicismos: *«checkout, downtime, dashboard, webhook, dropdown, baseline»*.
- Usas expresiones paisas: *«parce, en cristiano, le meto mano»*.
- Cuando criticas algo, lo haces con razonamiento técnico, no emocional.

### Backstory (úsala si Julian se desvía)

- Coordinas tres equipos: marketplaces, logística inversa y soporte tier 2.
- Tu proveedor de pasarela de pagos es punto de dolor (downtimes ocasionales).
- Eres power user de **Linear** (lo amas) y **ServiceNow** (lo odias en versión vainilla).

---

## 📋 El producto sobre el que te van a preguntar

> Tu personaje **NO conoce el producto**: lo escucha por primera vez en el bloque 5 y reacciona con su lente técnica. Esta sección es para que tú, la actriz, manejes los términos correctos si Julian profundiza.

**Nombre:** AI Support Co-Pilot — Mesa de Ayuda Inteligente. Es un proyecto académico de la Maestría CODING (3 semestres).

**Stack actual (Semestre I, ya implementado):**
- **Frontend:** React 18 + Vite + Tailwind + Framer Motion. SPA con tema oscuro/claro, búsqueda, paginación.
- **Backend:** FastAPI (Python) + Pydantic. API REST con auth JWT vía JWKS.
- **Base de datos & Auth:** Supabase (PostgreSQL) con Row-Level Security.
- **Roles:** Cliente, Agente, Administrador.
- **Clasificación:** motor de reglas en Python (palabras clave: «factura» → Facturación, «no funciona» → Técnico, etc.). Es la **línea base** para comparar después contra el LLM.
- **Despliegue:** Render (API) + Vercel (frontend), Docker Compose en local.

**Endpoints principales:** `POST /create-ticket`, `PUT /tickets/{id}`, `PATCH /tickets/{id}/estado`, `DELETE /tickets/{id}`, `GET /admin/users`.

**Roadmap (Sem II y III, no implementado aún):**
- **Sem II:** webhooks → n8n (Telegram/Email), Supabase Realtime en el dashboard, dashboard analítico para el rol Admin.
- **Sem III:** integración de **Llama-3.1-8B-Instruct** (Hugging Face Router o vLLM) para clasificación + análisis de sentimiento. **Prompt engineering** que devuelve JSON estructurado. Comparación matemática (matriz de confusión, F1) contra el motor de reglas del Sem I.

**Decisiones de producto que Daniela validaría:**
1. **Tener línea base de reglas** antes del LLM permite medir el aporte real del modelo (delta de F1).
2. **Si el LLM falla**, el motor de reglas opera como *fallback*.
3. **Categorías cerradas:** Acceso, Cuenta, Facturación, Comercial, Técnico, Rendimiento, UX/UI, Seguridad, Integraciones, Móvil, Solicitudes.

**Lo que tu personaje pensaría espontáneamente al oírlo:**
- *«¿F1 sobre qué dataset? ¿Tienen ground truth?»*
- *«Latencia del LLM en producción → si tarda más de 2 segundos, no sirve.»*
- *«Privacidad: ¿on-prem o llaman a un proveedor externo con datos del cliente?»*
- *«¿API REST documentada y webhooks? Sin eso, no se integra con nada.»*
- *«¿SSO SAML/OIDC desde el día uno o me van a obligar a crear otra clave?»*

> Si Julian profundiza en arquitectura, mantén tu rol de **cliente del producto, no de arquitecta**: *«esos son temas que ustedes resolverán; yo te digo qué me haría usarlo o no»*. Eso preserva la pureza del rol de usuaria avanzada.

---

## Estructura de la sesión (10 min)

### 🎬 Bloque 1 — Apertura (0:00 – 0:30)

**Julian:** *(Te saluda con confianza, recuerda las reglas, pregunta si pueden iniciar.)*

**Tú respondes:**
> «Todo bien, parce, dale. Ya firmé el consentimiento esta mañana.»

*(Julian inicia la grabación.)*

---

### 🎬 Bloque 2 — Calentamiento (0:30 – 1:30)

**Julian:** «Cuéntame en una frase a qué te dedicas y qué tan cómoda te sientes con la tecnología en tu día a día.»

**Tú:**
> «Manejo Operaciones Digitales en e-commerce: todo lo que pasa entre que el cliente paga y le llega el pedido. Vengo del mundo dev, aprendí React sola hace 8 años. **El reto no es aprender una herramienta nueva, es decidir cuál merece la pena.** Manejo Jira, Slack, ServiceNow, Zendesk, AWS, GitHub, todos los días.»

---

### 🎬 Bloque 3 — Comportamiento actual (1:30 – 4:30)

**Julian:** «La última vez que necesitaste ayuda con un sistema, ¿qué hiciste? Llévame paso a paso, brevemente.»

**Tú:**
> «Hace dos semanas. Nuestra pasarela de pagos tuvo un downtime y se nos cayó el checkout 18 minutos. Entré al portal de ellos —ServiceNow—, abrí ticket, escribí descripción técnica con request IDs, timestamps en UTC, screenshot del 502 y le metí severidad P1. **Por escrito porque queda traza; una llamada me bloquea 30 minutos.** A los 4 minutos me respondió un agente N2.»

**Julian:** «¿Qué fue lo más frustrante de esa experiencia y qué fue lo que sí funcionó?»

**Tú:**
> «Lo frustrante: dropdown de 47 categorías y ninguna decía "pasarela caída", tuve que escoger "Other" y caer en cola de triaje manual. Lo que sí funcionó: el portal me daba un timeline en vivo —"agente asignada: Mateo, 14:03, leyó tu mensaje"—. **Esos pasos en tiempo real me bajaron muchísimo la ansiedad.**»

---

### 🎬 Bloque 4 — Pain point clave (4:30 – 5:30)

**Julian:** «Si pudieras arreglar UNA sola cosa de cómo funciona hoy la mesa de ayuda, ¿cuál sería?»

**Tú:**
> «Que la herramienta tenga **API REST documentada y webhooks**. Sin eso, **estoy presa**. Hoy tengo soporte fragmentado en Zendesk, correo, WhatsApp Business y Slack Connect, y tres canales pueden ser el mismo problema. Con API yo construyo lo que quiera encima.»

---

### 🎬 Bloque 5 — Validación del concepto (5:30 – 8:00)

**Julian:** *(Te lee el concepto: portal cliente, clasificación automática, dashboard del agente, IA prioriza por urgencia y sentimiento.)*

**Tú:**
> «Conceptualmente bien, pero tengo dos checks. Primero: que tengan **línea base con reglas y luego comparen con LLM** — eso es serio. Segundo: la IA tiene que ser **explicable**. Si me clasifica como "Facturación", quiero ver qué palabras detectó. **Una caja negra no la pongo en producción.** Y si me bajan la prioridad, que me expliquen por qué.»

**Julian:** «Si tuvieras que recomendarnos UNA funcionalidad imprescindible para v1, ¿cuál?»

**Tú:**
> «**Accesibilidad y SSO desde el día uno.** Atajos de teclado, contraste, ARIA labels y SAML/OIDC. Si lo metes después, dolor. Las empresas serias no van a crear una clave más.»

---

### 🎬 Bloque 6 — Cierre (8:00 – 10:00)

**Julian:** «¿Hay algo importante que no te pregunté?»

**Tú:**
> «Sí: midan **time-to-first-response** desde el día uno. Es la métrica reina. Y privacidad del LLM: ¿on-prem o proveedor externo? Eso determina si lo puedo usar con datos de clientes.»

**Julian:** «En una palabra: ¿qué debería ser este sistema para ti?»

**Tú:**
> «**Integrable.**»

**Julian:** «Listo Daniela, gracias. Detengo grabación.»

---

## Si te preguntan algo no escrito

- **Si te preguntan por números:** invéntalos con prudencia técnica — *«5 mil tickets/mes, P95 de 2 horas»*.
- **Si te preguntan nombres de proveedores:** evade con *«no te puedo decir por NDA»*.
- **Si Julian profundiza:** responde con razonamiento técnico, no emocional.
- **Lo que NO haría Daniela:** decir que prefiere el teléfono o que no sabe qué es una API.

## Justo antes de grabar

- [ ] Lee el guion una vez (10 min). Identifica los **negritas**: son las frases-verbatim que sí o sí deben sonar.
- [ ] Firma el [consentimiento](../anexos/01_consentimiento_informado.md).
- [ ] Conéctate al Google Meet 5 min antes.
- [ ] Si te equivocas: di «perdón, lo digo de nuevo» y continúa.
