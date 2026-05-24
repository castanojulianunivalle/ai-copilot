# User Personas — Mesa de Ayuda Inteligente

> Dos arquetipos sintetizados a partir del Diagrama de Afinidad ([`diagrama_afinidad/07_diagrama_afinidad.md`](./diagrama_afinidad/07_diagrama_afinidad.md)). Una persona representa a la **clienta final** (consume el soporte) y la otra al **staff interno** (provee el soporte). La elección es deliberada: el producto tiene dos audiencias con métricas de éxito muy distintas, y un solo arquetipo no las representa.

> **Nota sobre fidelidad:** los rasgos demográficos son *compuestos* —no son ninguna de las entrevistadas literalmente, sino una mezcla representativa de los insights más frecuentes—. Los verbatims sí son citas reales de las cuatro entrevistas. La franja etaria de las cuatro entrevistadas (28–34 años) acota también las personas a ese rango.

---

## Persona 1 · "Sandra" — La Clienta PYME

![placeholder retrato](./anexos/persona_01_sandra.png)

| Campo | Valor |
|-------|-------|
| **Nombre representativo** | Sandra Liliana López |
| **Edad** | 33 años |
| **Ocupación** | Asistente administrativa en una PYME manufacturera (~80 empleados) |
| **Ciudad / país** | Bucaramanga, Colombia |
| **Estado civil** | Unión libre, sin hijos |
| **Educación** | Tecnóloga en gestión administrativa (SENA) |
| **Antigüedad en el rol** | 8 años |
| **Madurez digital** | 🟧 Baja-media (Excel y software interno; evita lo desconocido) |
| **Frase que la define** | *«Yo necesito que esto sea fácil y que alguien me ayude si me pierdo.»* |

### Biografía corta

Sandra llegó a la informática por necesidad: cuando su empresa migró del papel al sistema interno Siesa, le tocó aprender a la fuerza. Hoy se mueve con soltura en Excel y en el ERP de la empresa, pero cualquier herramienta web nueva le genera ansiedad. Tiene un Post-it físico al lado de su monitor con teléfonos importantes y prefiere llamar antes que escribir. Su éxito profesional depende de cerrar la facturación puntualmente cada mes; cualquier sistema que ponga en riesgo ese cierre es un enemigo.

### Objetivos (qué quiere lograr)

- 🎯 Resolver problemas técnicos sin dejar de avanzar con su trabajo administrativo.
- 🎯 Saber cuándo y quién va a atenderla, en términos concretos.
- 🎯 Sentirse atendida por una persona, no por un robot.
- 🎯 No tener que aprender herramientas nuevas cada año.

### Frustraciones (qué le duele)

- 😤 Repetir el mismo problema a tres agentes diferentes.
- 😤 Esperar respuestas en rangos de «24 a 48 horas» cuando ella necesita en horas concretas.
- 😤 Estados como «In Progress» que no le dicen nada.
- 😤 Páginas con formularios largos, dropdowns crípticos y letras pequeñas.
- 😤 Que la dejen sin saber qué pasa con su caso.

### Comportamientos y hábitos

- 📞 Canal preferido: **teléfono**. Si no, correo.
- 🖥️ Usa Excel, Outlook, Siesa, WhatsApp.
- ⏰ Trabaja de 7:30 am a 6 pm. No abre correos del trabajo después de las 7 pm.
- 🤝 Es leal a las empresas que la atienden bien; cambia de proveedor si se siente ignorada.

### Tecnología que ya domina

| Cómoda | Indiferente | Evitar |
|--------|-------------|--------|
| Excel, Outlook, ERP interno, WhatsApp | Apps bancarias (consulta, no transacciones) | Aplicaciones nuevas, atajos de teclado, dashboards complejos |

### Verbatims (citas reales de la entrevista 01)

> 🗣️ «Me da miedo dañar algo cuando es una página nueva.»
>
> 🗣️ «Quiero ver nombre y cara de quien me atiende.»
>
> 🗣️ «Un semáforo grandote, eso lo entiendo. *In Progress* no me dice nada.»
>
> 🗣️ «Decirme la hora exacta, no un rango de 24 a 48 horas.»

### Necesidades clave (mapeadas a clusters del Diagrama de Afinidad)

| # | Necesidad | Cluster afín |
|---|-----------|--------------|
| 1 | Sentir que hay una persona detrás del sistema | A — Canal humano y empatía |
| 2 | Ver el estado del ticket en lenguaje simple | C — Información esencial visible |
| 3 | Saber un tiempo de respuesta concreto | D — Promesas de tiempo concretas |
| 4 | Poder corregir si el sistema clasifica mal | E — IA explicable y override |
| 5 | UI tolerante con el error de la usuaria novata | I — UI rápida y tolerante |

### Implicaciones para el producto

- ✅ Pantallas con **dos botones grandes**: «Crear ticket» y «Ver mis casos». Nada más en la primera vista.
- ✅ Estado por **iconografía** (semáforo verde/ámbar/rojo) y no por jerga.
- ✅ Mensaje del SLA en lenguaje natural: *«Te responderemos hoy antes de las 4:00 p.m.»*.
- ✅ Botón visible de «Hablar con una persona» en cada pantalla.
- ✅ Confirmación cuando se sale del horario: *«Son las 6:14 p.m. Tu caso lo atendemos mañana a las 8:00 a.m.»*.

### Métrica de éxito de esta persona

- ⏱️ **Tiempo de aprendizaje a primer ticket creado** ≤ 90 segundos sin asistencia.
- 📞 **Tasa de llamadas** después de usar el portal: ≤ 30% de los tickets.
- 😊 **CSAT** ≥ 4.6 / 5 en encuestas post-cierre.

---

## Persona 2 · "Karen" — La Operadora de Mesa

![placeholder retrato](./anexos/persona_02_karen.png)

| Campo | Valor |
|-------|-------|
| **Nombre representativo** | Karen Vanessa Gómez |
| **Edad** | 29 años |
| **Ocupación** | Agente de mesa de ayuda Nivel 1 (BPO o área interna de TI) |
| **Ciudad / país** | Bogotá, Colombia |
| **Estado civil** | Soltera, vive con su pareja |
| **Educación** | Tecnóloga en sistemas (en proceso de profesionalización) |
| **Antigüedad en el rol** | 3 años |
| **Madurez digital** | 🟩 Intermedia-alta (PowerShell básico, atajos, plantillas) |
| **Frase que la define** | *«Yo atiendo 50 tickets al día; cada segundo cuenta.»* |

### Biografía corta

Karen entró a la mesa de ayuda como su primer trabajo formal. Aprende por imitación: lleva un .txt con plantillas que ha refinado durante 3 años, sabe que el café de las 10 a.m. es sagrado y que su indicador mensual define si pasa de N1 a N2 el próximo trimestre. Su mayor enemigo no es el cliente difícil, sino el ticket vago de «no funciona» y la categorización manual que le come 2 horas al día. Juega FIFA los fines de semana y sigue tutoriales de Notion en YouTube. Si una herramienta no tiene atajos de teclado, la critica frente al equipo.

### Objetivos (qué quiere lograr)

- 🎯 Cerrar más tickets bien resueltos por hora (subir su FCR).
- 🎯 Que el sistema la proteja de auditorías injustas.
- 🎯 No tener que repetir trabajo manual: categorización, plantillas, búsquedas de historial.
- 🎯 Crecer a nivel 2 en máximo 12 meses.

### Frustraciones (qué le duele)

- 😤 Categorizar a mano cuando el texto del usuario es ambiguo.
- 😤 Tickets vagos tipo «no funciona» sin contexto.
- 😤 Que el sistema no le muestre los tickets pasados del mismo usuario.
- 😤 Que su indicador de calidad mida cosas que no controla.
- 😤 Cerrar un ticket por error y no poder deshacer.

### Comportamientos y hábitos

- ⌨️ Usa atajos de teclado siempre que puede; el mouse le parece lento.
- 📋 Mantiene plantillas de respuesta en un .txt local.
- 🌙 Activa modo oscuro en todo lo que pueda.
- 📊 Revisa su indicador personal todos los lunes a primera hora.

### Tecnología que ya domina

| Cómoda | Indiferente | Evitar |
|--------|-------------|--------|
| Herramientas de mesa (Remedy, Freshdesk, etc.), Excel intermedio, Teams, PowerShell básico | Power BI, Confluence | Reuniones largas, herramientas sin shortcuts, UI lentas |

### Verbatims (citas reales de la entrevista 03)

> 🗣️ «Gasto 2 a 3 minutos por ticket categorizando. 50 tickets al día. Saquen cuentas.»
>
> 🗣️ «Si la máquina decide, la máquina responde. No yo.»
>
> 🗣️ «Un borrador automático de respuesta sería oro.»
>
> 🗣️ «El mouse me roba segundos. Atajos de teclado, por favor.»
>
> 🗣️ «Modo oscuro me salva los ojos.»

### Necesidades clave (mapeadas a clusters del Diagrama de Afinidad)

| # | Necesidad | Cluster afín |
|---|-----------|--------------|
| 1 | Eliminar el trabajo repetitivo de categorización | F — Reducir trabajo repetitivo |
| 2 | Tener historial del usuario a un clic | B — Continuidad del contexto |
| 3 | Sobreescribir la IA sin penalización | E — IA explicable y override |
| 4 | UI rápida con atajos y modo oscuro | I — UI rápida y tolerante |
| 5 | Respuestas sugeridas / borrador | F — Reducir trabajo repetitivo |
| 6 | Indicadores de sentimiento al lado del ticket | G — Visibilidad emocional y política |

### Implicaciones para el producto

- ✅ **Atajos de teclado** documentados (`C` cerrar, `R` responder, `Tab` siguiente ticket).
- ✅ Cabecera fija con: usuario, ticket #, prioridad, **countdown SLA**, categoría, indicador de sentimiento.
- ✅ Lista de **últimos 3 tickets del mismo usuario** en barra lateral.
- ✅ Sugerencia de categoría automática + botón de un clic para corregir.
- ✅ **Deshacer** en cierre de ticket por 5 segundos (toast con CTA).
- ✅ Modo oscuro persistente.
- ✅ Plantillas de respuesta sugeridas según categoría.

### Métrica de éxito de esta persona

- ⏱️ **Tiempo medio por ticket** ≤ 6 minutos (línea base actual: ~10 min).
- 📈 **FCR (first contact resolution)** ≥ 75%.
- 🎯 **Adopción** de la sugerencia de categoría automática ≥ 80% de los tickets sin recategorización posterior.
- 😊 **eNPS interno** del agente ≥ 8 / 10.

---

## ¿Por qué solo 2 personas y no 4?

Una pregunta natural es por qué no se hicieron una persona por entrevistada. Por dos razones:

1. **Las personas son síntesis, no sumas.** Tener 4 personas para 4 entrevistas reproduce los datos en lugar de abstraerlos. La buena práctica (Cooper, *About Face* / NN/g) es construir el menor número de personas que cubre los segmentos con metas significativamente distintas.
2. **El producto tiene dos lados.** Clienta final (paga implícita o explícitamente, *consume* soporte) y staff interno (cobra por *proveer* soporte). Sus métricas de éxito y sus puntos de dolor son ortogonales, así que dos personas son suficientes para no perder fidelidad y para alimentar dos `journeys` diferenciados en el USM.

### Otros perfiles considerados pero NO promovidos a persona

| Perfil | Razón para no promoverlo |
|--------|---------------------------|
| Clienta Avanzada (Daniela) | Sus necesidades quedan **cubiertas** por Sandra como límite inferior y por Karen como agente; en un futuro semestre se podría incorporar como tercera persona si se valida un segmento B2B power user. |
| Coordinadora (Lina) | El alcance académico actual no incluye dashboard analítico (HU-07 está prevista para Semestre 2). Su persona se construirá explícitamente cuando ese módulo entre en diseño, para evitar diseñar para una audiencia que aún no se construye. |

> Ambos perfiles **siguen alimentando el Diagrama de Afinidad y el USM**, simplemente no se promueven a persona en este alcance.
