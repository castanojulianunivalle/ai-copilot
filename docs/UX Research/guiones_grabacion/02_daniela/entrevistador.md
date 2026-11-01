# Guion del entrevistador — Sesión 02 con Daniela Andrea R.

> **Para Julian.** Este es tu guion específico para conducir la entrevista a Daniela. Léelo de principio a fin antes de iniciar Google Meet. La entrevistada tiene su propio guion (`entrevistada.md`); aquí está **lo que tú dices, cuándo, y qué esperar**.

---

## Ficha de la sesión

| Campo | Valor |
|-------|-------|
| Pseudónimo | Daniela Andrea R. |
| Edad / ciudad | 31 años · Medellín |
| Perfil | Clienta avanzada — Lead de Operaciones Digitales en e-commerce |
| Madurez digital | Alta (Jira, Slack, AWS, GitHub, SQL diario) |
| Hora | 03:00 p.m. |
| Duración objetivo | **10 minutos** |
| Tono que debes mantener | **Colega de profesión, ágil, técnico.** Tutéala con confianza, puedes usar anglicismos. |
| Cosas a evitar | Explicar términos técnicos básicos (ofende su nivel), preguntas tipo encuesta cerrada, sentimentalismo |
| Verbatims clave que esperas | A02, A04, A06, A09, A12, A14 (6 frases-insight objetivo) |

---

## Reglas operativas para esta sesión

1. Confirma con Daniela que firmó el consentimiento ANTES de iniciar grabación.
2. Daniela responde rápido y concreto. **No la interrumpas**: deja que termine, anota verbatims y pasa a la siguiente.
3. Después de cada pregunta, **espera 1-2 segundos** (Daniela arranca rápido). Si la respuesta es muy técnica y queda corta, no profundices: ya ganaste el insight.
4. Si Daniela quiere debatir el diseño del producto contigo en pleno bloque 5, frénala con cortesía: *«eso me lo guardo para una sesión de feedback futura, hoy quiero capturar tu punto de vista de cliente»*.
5. **Mantén estricto el reloj**: Daniela respeta el tiempo, hazlo tú también.

---

## Bloque 1 — Apertura · 0:00 – 0:30

**Tú dices (textualmente):**
> «¡Daniela, qué más! Gracias por hacer el espacio. Tres cositas: no hay respuestas correctas, lo que me sirve es tu experiencia tal cual; puedes parar cuando quieras; la sesión se graba solo con fines académicos y aparecerás con un pseudónimo. ¿Todo bien si arrancamos?»

**Esperas que Daniela diga:** *«Todo bien, parce, dale. Ya firmé el consentimiento esta mañana.»*

**Inicia grabación.** Confirma: *«Listo, ya estoy grabando.»*

---

## Bloque 2 — Calentamiento · 0:30 – 1:30

**Tú preguntas:**
> «Cuéntame en una frase a qué te dedicas y qué tan cómoda te sientes con la tecnología en tu día a día.»

**Lo que esperas oír:** menciona Operaciones Digitales en e-commerce; viene del mundo dev; lista de herramientas larga (Jira, Slack, AWS, GitHub).

**Frase clave a fishear:** *«El reto no es aprender una herramienta nueva, es decidir cuál merece la pena»* (no es verbatim numerado pero da color al perfil).

**Si responde muy corto** («manejo Operaciones Digitales»), pídele detalle: *«¿qué herramientas te tocan en una semana típica?»*. Daniela contestará una lista larga, lo cual está bien.

---

## Bloque 3 — Comportamiento actual · 1:30 – 4:30

> **Aquí salen 2 verbatims clave (A02 y A04).** Las respuestas serán técnicas; no te asustes si suelta jerga.

**Pregunta 1 (1:30 – 3:00):**
> «La última vez que necesitaste ayuda con un sistema, ¿qué hiciste? Llévame paso a paso, brevemente.»

**Lo que esperas:** historia de la pasarela de pagos caída, severidad P1, ServiceNow. Lo importante: *«por escrito queda traza, una llamada me bloquea»* → 🟢 **A02**.

**Si Daniela se va a un detalle muy técnico** (request IDs, timestamps), déjala 30 segundos y luego: *«perfecto, eso lo entiendo. ¿Y por qué ese canal y no otro?»* — eso fuerza el A02.

**Pregunta 2 (3:00 – 4:30):**
> «¿Qué fue lo más frustrante de esa experiencia y qué fue lo que sí funcionó?»

**Lo que esperas:** lo frustrante = dropdown con 47 categorías, cae en cola "Other". Lo bueno = timeline en vivo bajó la ansiedad → 🟢 **A04** «*Pasos en tiempo real bajaron mi ansiedad*».

---

## Bloque 4 — Pain point clave · 4:30 – 5:30

**Tú preguntas:**
> «Si pudieras arreglar UNA sola cosa de cómo funciona hoy la mesa de ayuda, ¿cuál sería?»

**Lo que esperas:** API REST + webhooks → 🟢 **A12** «*Sin API ni webhooks, estoy presa*».

**Si Daniela se va a varias cosas a la vez** (fragmentación de canales, taxonomías, agentes que no leen), recuérdale: *«si tuvieras que escoger UNA, ¿cuál pesa más?»*. Es para forzarla a priorizar.

---

## Bloque 5 — Validación del concepto · 5:30 – 8:00

**Tú lees el concepto (puedes ser técnico con Daniela):**
> «Concepto: portal web donde el cliente crea tickets, un sistema clasifica automáticamente la categoría con motor de reglas como línea base, y un agente los gestiona desde un dashboard. Fase 2: integramos un LLM —Llama 3.1— que prioriza por urgencia y sentimiento. ¿Qué reacción inmediata tienes?»

**Lo que esperas (importantes):**
- Que valide la línea base con reglas vs LLM como **enfoque científico**.
- Que pida explicabilidad → 🟢 **A09** «*Una caja negra no la pongo en producción*».
- Que mencione transparencia de prioridad → 🟢 **A06** «*Si me bajas la prioridad, explícame por qué*».

**Si Daniela quiere debatir arquitectura del LLM** (on-prem vs cloud, latencia), mantenla en su rol de cliente, no de arquitecta: *«esos son temas que después tomamos; quiero saber qué te haría confiar como usuaria del producto»*.

**Pregunta de cierre del bloque (7:00 – 8:00):**
> «Si tuvieras que recomendarnos UNA funcionalidad imprescindible para la primera versión, ¿cuál?»

**Lo que esperas:** SSO + accesibilidad → 🟢 **A14** «*Accesibilidad y SSO desde el día uno*».

---

## Bloque 6 — Cierre · 8:00 – 10:00

**Pregunta 1 (8:00 – 9:00):**
> «¿Hay algo importante que no te pregunté?»

**Lo que esperas:** medir time-to-first-response como métrica reina, comentarios sobre privacidad del LLM. Cualquiera de los dos suma.

**Pregunta 2 (9:00 – 9:45):**
> «En una palabra: ¿qué debería ser este sistema para ti?»

**Lo que esperas oír:** **«Integrable.»** (Quizás dude entre «eficiente» e «integrable»; déjala escoger).

**Cierre (9:45 – 10:00):**
> «Listo Daniela, gracias. Te dejo con tu día. Detengo grabación.»

---

## Checklist post-sesión

- [ ] Detener grabación local + grabación nativa de Google Meet.
- [ ] Renombrar el video: `EUX-002_Daniela_2026-05-12.mp4`.
- [ ] Subirlo a la carpeta privada de Drive y pegar el enlace en el [README](../../README.md) sección 5.
- [ ] Cotejar la transcripción [`../../entrevistas/04_entrevista_02_cliente_avanzado.md`](../../entrevistas/04_entrevista_02_cliente_avanzado.md) con lo grabado.
- [ ] Marcar ✅ el consentimiento firmado en la ficha de la entrevista.
- [ ] Si Daniela ofreció revisar prototipos, anótalo: es una colaboradora futura valiosa.

## Si algo se sale del guion

| Situación | Qué hacer |
|-----------|-----------|
| Daniela quiere darte recomendaciones técnicas no solicitadas | Anota la idea fuera del guion: *«excelente, eso lo guardo para después»*. No la sigas |
| Pide un escenario hipotético que no preparaste | Devuélvele la pregunta a su experiencia: *«¿te ha pasado algo así? Cuéntamelo»* |
| Habla muy rápido y pierdes verbatims | Después de su respuesta repite la frase clave: *«o sea, "una caja negra no la pongo en producción", ¿correcto?»*. Eso te asegura el verbatim claro en el video |
| Te pasas de los 10 min | Bloque 6 reducido: solo P8 (palabra-síntesis) |
| Daniela menciona un proveedor por nombre | No la cortes en el momento; al editar la transcripción, anonimiza el nombre |
