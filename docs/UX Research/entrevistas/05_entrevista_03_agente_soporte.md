# Entrevista 03 — Agente de Soporte

> **Transcripción completa (entrevistador + entrevistada)** · Duración real: **10 min**. Sirve como transcripción de referencia para la grabación en video y como insumo del Diagrama de Afinidad.

---

## Ficha de la sesión

| Campo | Valor |
|-------|-------|
| ID de entrevista | EUX-003 |
| Pseudónimo | **Karen Vanessa G.** |
| Edad | 28 años |
| Cargo | Agente de Mesa de Ayuda Nivel 1 — BPO con cliente del sector financiero |
| Ciudad | Bogotá, Colombia |
| Nivel digital declarado | **Intermedio-alto** |
| Tiempo en el rol | 3 años |
| Modalidad | Google Meet |
| Fecha | 13/05/2026, 11:00 a.m. |
| Duración real | **10 minutos** |
| Consentimiento firmado | ✅ (PDF en Drive privado) |

---

## Bloque 1 — Apertura (0:00 – 0:30)

**E:** Karen, parce, qué nota. Tres cositas: no hay respuestas correctas, lo que me sirve es lo que vives en tu día a día como agente; puedes parar cuando quieras; la grabación es solo para mi profesor y aparecerás con un pseudónimo. ¿Lista?

**K:** Lista. Una sola cosa: si suena la diadema es que me cayó un ticket; no le pares bolas, sigamos.

*(Inicio grabación.)*

---

## Bloque 2 — Calentamiento (0:30 – 1:30)

**E:** Cuéntame en una frase a qué te dedicas y qué tan cómoda te sientes con la tecnología.

**K:** Soy agente N1 hace 3 años, atiendo a empleados internos de un banco — VPN caída, contraseñas, impresoras, lo que sea. Estudié sistemas dos semestres, hago scripts en PowerShell cuando puedo. En BMC Remedy ya soy ágil porque vivo pegada ahí.

---

## Bloque 3 — Comportamiento actual (1:30 – 4:30)

**E:** Llévame por un día típico tuyo en pocas frases: cómo te llegan los tickets y cómo los priorizas.

**K:** 7:30 entro. Tres logins solo para empezar: VPN, Remedy, CRM del banco. Abro la cola con 30 a 60 tickets entre los pendientes y los nuevos. Los ordeno **manualmente** por prioridad y antigüedad — empiezo por P1 más viejo porque los SLA me corren. Cierro 50 al día. Termino 5:30 y dejo notas para el turno noche.

**E:** ¿Cuál es la parte del proceso que más tiempo te roba sin agregar valor?

**K:** **Categorizar.** Tengo un dropdown con 80 categorías. Muchas veces el usuario describe mal el problema y me toca adivinar. Si me equivoco, mi líder me lo audita y me baja el indicador. **Gasto 2 a 3 minutos por ticket categorizando, son 50 al día. Saquen cuentas.** La segunda parte que me roba tiempo: redactar respuestas. El 60% de los tickets son cosas repetidas y tengo plantillas en un .txt en mi escritorio que copio y pego.

> 🔴 **G04:** «*2-3 minutos categorizando, 50 al día — saquen cuentas*» — taxonomía como overhead.
>
> 🟢 **G11:** «*Plantillas en un .txt que copio y pego*» — falta de respuestas sugeridas.

---

## Bloque 4 — Pain point clave (4:30 – 5:30)

**E:** Si pudieras arreglar UNA sola cosa de cómo funciona hoy la mesa de ayuda, ¿cuál sería?

**K:** Que el sistema me redacte un primer borrador de respuesta y me sugiera la categoría con porcentaje de confianza. Yo edito y mando. **Eso sería oro.** Y por favor: que la cabecera del agente sea fija con cinco datos —usuario, ticket, prioridad, SLA, categoría— y al lado los últimos 3 tickets del mismo usuario. Hoy me toca buscarlo a mano.

> 🟢 **G07:** «*Cabecera fija: usuario, ticket, prioridad, SLA, categoría*» — UI mínima del agente.

---

## Bloque 5 — Validación del concepto (5:30 – 8:00)

**E:** Estamos diseñando un portal donde el cliente crea ticket, sistema clasifica solo, agente gestiona desde dashboard. Después, IA prioriza por urgencia y sentimiento. ¿Reacción inmediata?

**K:** Yo soy la cliente del dashboard. Lo primero: tiene que ser **rápido**. Si abrir un ticket toma 4 segundos cargar, x50 al día son 3 minutos perdidos. Y de la IA: que me deje **sobreescribir sin penalización**. Si yo veo que se equivocó y cambio, listo. **Si la máquina decide, la máquina responde, no yo.** Si por su error me bajan el indicador a mí, prefiero hacerlo a mano.

> 🔴 **G09:** «*Si la máquina decide, la máquina responde. No yo*» — responsabilidad operativa clara.

**E:** Si tuvieras que recomendarnos UNA funcionalidad imprescindible para la primera versión, ¿cuál sería?

**K:** **Atajos de teclado.** `C` para cerrar, `R` para responder, `Tab` entre tickets. **El mouse me roba 5 segundos** cada vez. Y modo oscuro, por favor. Las 4 de la tarde con 40 tickets atendidos, los ojos arden. **El modo oscuro me salva los ojos.**

> 🟢 **G13:** «*Atajos de teclado: el mouse me roba segundos*» — eficiencia / power user.
>
> 🟢 **G15:** «*Modo oscuro me salva los ojos*» — accesibilidad / fatiga.

---

## Bloque 6 — Cierre (8:00 – 10:00)

**E:** ¿Hay algo importante que no te pregunté?

**K:** Sí: que la interfaz **perdone errores**. Si cierro un ticket sin querer, déjame deshacer 5 segundos. Y que el sentimiento se vea **al lado del ticket** como un emoji, así calibro el tono antes de leer.

**E:** En una sola palabra: ¿qué debería ser este sistema para ti?

**K:** **Rápido.**

**E:** Listo, gracias parce. Detengo grabación.

---

## Anexos: insights destacados (para alimentar el Diagrama de Afinidad)

| ID | Verbatim / Insight | Tema preliminar |
|----|---------------------|-----------------|
| G04 | «2-3 minutos categorizando, 50 tickets al día — saquen cuentas» | Categorización manual costosa |
| G07 | «Cabecera fija: usuario, ticket, prioridad, SLA, categoría» | UI mínima del agente |
| G09 | «Si la máquina decide, la máquina responde, no yo» | Responsabilidad operativa |
| G11 | «Plantillas en un .txt que copio y pego» | Asistente de redacción / KB ad-hoc |
| G13 | «Atajos de teclado, el mouse me roba segundos» | Eficiencia / power user |
| G15 | «Modo oscuro me salva los ojos» | Accesibilidad / fatiga |

**Palabra-síntesis (one-word recap):** *Rápido.*
