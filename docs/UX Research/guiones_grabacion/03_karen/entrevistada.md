# Guion de grabación — Karen Vanessa G.

> **Para la persona que interpreta a Karen.** Este guion contiene **tu** parte de la entrevista. Lo que dirá Julian está resumido al inicio de cada bloque para que sepas cuándo te toca hablar. **Duración total: 10 minutos.**

---

## Tu personaje (léelo antes de grabar)

| Campo | Valor |
|-------|-------|
| Nombre | Karen Vanessa G. |
| Edad | 28 años |
| Ciudad | Bogotá, Colombia |
| Cargo | Agente de Mesa de Ayuda Nivel 1 — BPO con cliente del sector financiero (un banco) |
| Antigüedad | 3 años |
| Personalidad | Pragmática, eficiente, humor de "trinchera", se queja con razón pero también propone soluciones |
| Madurez digital | **Intermedia-alta**. PowerShell básico, atajos de teclado, plantillas, modo oscuro everywhere |
| Frase que la define | *«Yo atiendo 50 tickets al día; cada segundo cuenta.»* |

### Tono al hablar

- Hablas con jerga de oficina y dev: *«parce, hermana, crack, pegada (a la herramienta), no le pares bolas»*.
- Cuando te frustras, ironía: *«Saquen cuentas», «el man»*.
- Te entusiasmas con cosas técnicas: *«eso sería oro», «me salva los ojos»*.

### Backstory (úsala si Julian se desvía)

- Eres agente N1 hace 3 años; primer trabajo formal.
- Tu líder: **Mauro** (super exigente con indicadores).
- Tu compañera de turno: **Yuli**.
- La herramienta del cliente bancario: **BMC Remedy**.
- Meta: subir a N2 en 12 meses.

---

## 📋 El producto sobre el que te van a preguntar

> Tu personaje **NO conoce el producto**: lo escucha por primera vez en el bloque 5 y reacciona desde la trinchera del agente. Esta sección es para que tú entiendas qué hace la herramienta y puedas comparar con tu Remedy si Julian profundiza.

**Nombre:** AI Support Co-Pilot — Mesa de Ayuda Inteligente. Va a competir con herramientas como **Freshdesk, BMC Remedy, ServiceNow o Zendesk**, pero más liviana.

**¿Qué tendría tu pantalla de agente?** *(esto es lo que más te interesa porque es donde vivirías 8 horas al día)*

- **Lista de tickets** ordenable por prioridad, estado y antigüedad. Búsqueda y paginación.
- **Cabecera de cada ticket** con: usuario, ticket #, prioridad, **categoría sugerida automáticamente**, estado (Abierto/Cerrado), fecha de creación.
- **Categoría sugerida** = la viene calculada por el sistema. Hoy con palabras clave (si el cliente escribió «factura», lo marca como Facturación). En el futuro, con un modelo de IA (Llama-3.1) que **lee** el ticket completo.
- **Botón para sobreescribir** la categoría con un clic si crees que está mal clasificado.
- **Estados:** Abierto / Cerrado. Cambiar estado es `PATCH /tickets/{id}/estado`.
- **Modo oscuro** persistente.
- **Tema con gradientes y animaciones suaves** (Framer Motion + Lucide React).
- **A futuro (Sem II):** alertas vía Telegram/Email cuando entra un ticket urgente, vista en tiempo real (Supabase Realtime) sin tener que refrescar.
- **A futuro (Sem III):** indicador de **sentimiento del cliente** (frustrado, neutral, positivo) al lado del ticket, y **borrador automático de respuesta** sugerido por la IA.

**Categorías existentes:** Acceso, Cuenta, Facturación, Comercial, Técnico, Rendimiento, UX/UI, Seguridad, Integraciones, Móvil, Solicitudes. *Son 11, no 80 como las de Remedy.*

**Lo que NO existe (y Karen pediría):**
- Atajos de teclado (`C`, `R`, `Tab`).
- Plantillas de respuesta sugeridas según categoría.
- Vista del **historial del usuario** (los últimos 3 tickets que el mismo cliente ha mandado).
- Botón "deshacer cierre" durante 5 segundos.
- Indicador visible de **carga** del agente (cuántos tickets tiene asignados, vs el resto).

**Lo que tu personaje pensaría espontáneamente al oírlo:**
- *«11 categorías está bien — Remedy tiene 80, una locura.»*
- *«Si la IA me clasifica mal y mi líder me audita, ¿quién paga el pato?»*
- *«¿Atajos de teclado? Si no los hay, esto va a ser lento.»*
- *«¿Modo oscuro? Por favor, mis ojos.»*
- *«¿Borrador de respuesta sugerido por IA? Eso sería oro.»*

> Si Julian te pregunta por algo técnico que no aparece arriba, contesta como agente: *«eso lo decide el equipo de TI; yo lo único que sé es que tiene que cargar rápido y tener los datos a la mano»*. Eso preserva tu rol operativo.

---

## Estructura de la sesión (10 min)

### 🎬 Bloque 1 — Apertura (0:00 – 0:30)

**Julian:** *(Te saluda con confianza, recuerda las reglas, pregunta si estás lista.)*

**Tú respondes:**
> «Lista. Una sola cosa: si suena la diadema es que me cayó un ticket; no le pares bolas, sigamos.»

*(Julian inicia la grabación.)*

---

### 🎬 Bloque 2 — Calentamiento (0:30 – 1:30)

**Julian:** «Cuéntame en una frase a qué te dedicas y qué tan cómoda te sientes con la tecnología.»

**Tú:**
> «Soy agente N1 hace 3 años, atiendo a empleados internos de un banco — VPN caída, contraseñas, impresoras, lo que sea. Estudié sistemas dos semestres, hago scripts en PowerShell cuando puedo. En BMC Remedy ya soy ágil porque vivo pegada ahí.»

---

### 🎬 Bloque 3 — Comportamiento actual (1:30 – 4:30)

**Julian:** «Llévame por un día típico tuyo en pocas frases: cómo te llegan los tickets y cómo los priorizas.»

**Tú:**
> «7:30 entro. **Tres logins solo para empezar**: VPN, Remedy, CRM del banco. Abro la cola con 30 a 60 tickets entre los pendientes y los nuevos. Los ordeno **manualmente** por prioridad y antigüedad — empiezo por P1 más viejo porque los SLA me corren. Cierro 50 al día. Termino 5:30 y dejo notas para el turno noche.»

**Julian:** «¿Cuál es la parte del proceso que más tiempo te roba sin agregar valor?»

**Tú:**
> «**Categorizar.** Tengo un dropdown con 80 categorías. Muchas veces el usuario describe mal el problema y me toca adivinar. Si me equivoco, mi líder me lo audita y me baja el indicador. **Gasto 2 a 3 minutos por ticket categorizando, son 50 al día. Saquen cuentas.** La segunda parte que me roba tiempo: redactar respuestas. El 60% de los tickets son cosas repetidas y tengo plantillas en un .txt en mi escritorio que copio y pego.»

---

### 🎬 Bloque 4 — Pain point clave (4:30 – 5:30)

**Julian:** «Si pudieras arreglar UNA sola cosa de cómo funciona hoy la mesa de ayuda, ¿cuál sería?»

**Tú:**
> «Que el sistema me redacte un primer borrador de respuesta y me sugiera la categoría con porcentaje de confianza. Yo edito y mando. **Eso sería oro.** Y por favor: que la cabecera del agente sea fija con cinco datos —usuario, ticket, prioridad, SLA, categoría— y al lado los últimos 3 tickets del mismo usuario. Hoy me toca buscarlo a mano.»

---

### 🎬 Bloque 5 — Validación del concepto (5:30 – 8:00)

**Julian:** *(Te lee el concepto: portal cliente, clasificación automática, dashboard del agente, IA prioriza por urgencia y sentimiento.)*

**Tú:**
> «Yo soy la cliente del dashboard. Lo primero: tiene que ser **rápido**. Si abrir un ticket toma 4 segundos cargar, x50 al día son 3 minutos perdidos. Y de la IA: que me deje **sobreescribir sin penalización**. Si yo veo que se equivocó y cambio, listo. **Si la máquina decide, la máquina responde, no yo.** Si por su error me bajan el indicador a mí, prefiero hacerlo a mano.»

**Julian:** «Si tuvieras que recomendarnos UNA funcionalidad imprescindible para la primera versión, ¿cuál sería?»

**Tú:**
> «**Atajos de teclado.** `C` para cerrar, `R` para responder, `Tab` entre tickets. **El mouse me roba 5 segundos** cada vez. Y modo oscuro, por favor. Las 4 de la tarde con 40 tickets atendidos, los ojos arden. **El modo oscuro me salva los ojos.**»

---

### 🎬 Bloque 6 — Cierre (8:00 – 10:00)

**Julian:** «¿Hay algo importante que no te pregunté?»

**Tú:**
> «Sí: que la interfaz **perdone errores**. Si cierro un ticket sin querer, déjame deshacer 5 segundos. Y que el sentimiento se vea **al lado del ticket** como un emoji, así calibro el tono antes de leer.»

**Julian:** «En una sola palabra: ¿qué debería ser este sistema para ti?»

**Tú:** *(con energía)*
> «**Rápido.**»

**Julian:** «Listo, gracias parce. Detengo grabación.»

---

## Si te preguntan algo no escrito

- **Si te piden números:** mantén la métrica de "50 tickets al día" como ancla.
- **Si te preguntan por sueldo o condiciones:** evade con humor — *«Mejor hablamos de tickets, eso es secreto»*.
- **Si te preguntan por casos difíciles:** menciona problemas comunes — VPN caída, contraseñas bloqueadas, impresoras sin red.
- **Lo que NO haría Karen:** decir que prefiere el call center, evitar atajos.

## Justo antes de grabar

- [ ] Lee el guion una vez (10 min). Subraya los **negritas**.
- [ ] Firma el [consentimiento](../anexos/01_consentimiento_informado.md).
- [ ] Conéctate al Google Meet 5 min antes.
- [ ] Si te equivocas: di «perdón, lo digo de nuevo» y continúa.
