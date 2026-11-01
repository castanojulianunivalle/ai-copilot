# Guion de presentación — Arquitectura de información (10–15 minutos)

**Uso:** lectura en voz alta para grabación en video.  
**Duración orientativa:** ~10–12 min a ritmo moderado; puedes extender con ejemplos hasta ~15 min.

---

## Introducción (≈ 1 min)

Buenos días / Buenas tardes. En esta presentación resumo el proceso de **Arquitectura de la información** que realicé para el proyecto de curso, que está alineado con mi proyecto integrador: **AI Support Co-Pilot**, una aplicación web de mesa de ayuda con soporte eventual de capacidades inteligentes.

La actividad pedía definir el **mapa del sitio**, las **taxonomías y metadatos**, la **navegabilidad** y los **mecanismos de búsqueda**. Voy a explicar cada parte y **por qué** tomé esas decisiones, no solo qué dibujé en el diagrama.

---

## Qué problema ordena la arquitectura de información (≈ 1 min)

Sin una IA clara, una app con clientes, agentes y administradores mezcla pantallas y rutas y el usuario se pierde o accede a lo que no debe. Por eso organicé la información en **tres grandes mundos**: lo **público** —landing, login y registro—, el **área cliente** —mis tickets, nuevo ticket, detalle—, y el **área operativa** —dashboard del agente y, más adelante, administración y reportes.

Esa separación no es solo visual: coincide con los **roles** y con la idea de que cada persona ve solo lo que le corresponde, especialmente en los datos sensibles de los tickets.

---

## Mapa del sitio (≈ 3 min)

El **mapa del sitio** que propongo tiene un nivel raíz público y luego ramas por rol.

Desde **inicio** el usuario puede ir a **iniciar sesión** o **registrarse** como cliente. Tras autenticarse, la aplicación lo lleva según su rol: el **cliente** a **mis tickets**, el **agente** al **dashboard** de todos los tickets, y el **administrador** hacia la **gestión de usuarios** o reportes cuando esas pantallas existan en el producto.

En el área **cliente**, la jerarquía es: lista **mis tickets**, desde ahí **nuevo ticket**, y **detalle** de cada ticket por identificador en la URL. No hay más profundidad de la necesaria: tres niveles habituales —área, lista, detalle— para que sea fácil de aprender.

Para el **agente**, el dashboard es la tabla principal y desde cada fila o acción se entra al **detalle** para cambiar estado y ver clasificación. Justifico esta forma porque replica el flujo mental: primero veo la **cola**, luego **profundizo** en un caso.

El diagrama completo está en el documento de entrega; aquí la idea clave es **pocas ramas, bien etiquetadas**, y URLs estables como `/mis-tickets` y `/dashboard` que ya están alineadas con el desarrollo del integrador.

---

## Taxonomías y metadatos (≈ 3 min)

La pieza central del contenido es el **ticket**. Definí metadatos que sirven tanto para la **interfaz** como para la **inteligencia** del sistema más adelante.

Son obligatorios el **identificador**, el **título**, la **descripción**, el **estado** —por ejemplo abierto y cerrado, extensible si el negocio lo pide— y las **marcas de tiempo** de creación y actualización para ordenar y auditar. El ticket está ligado al **usuario solicitante** para poder mostrar “solo los míos” al cliente.

La **categoría** no tiene por qué ser obligatoria al crear el ticket desde el formulario: puede **rellenarse** después con el motor de reglas o con el modelo de lenguaje. Eso reduce fricción en el cliente y mantiene datos **estructurados** para filtros y reportes. Propongo una taxonomía **cerrada** de categorías —técnico, facturación, acceso, general u otro— para que las gráficas y los filtros sean coherentes y para facilitar el entrenamiento o la evaluación de la IA.

Opcionalmente aparecen **prioridad** y **sentimiento** cuando el producto evolucione; quedan definidos como metadatos para no rediseñar la taxonomía desde cero.

Para **usuarios**, la taxonomía de **roles** es fija: cliente, agente y administrador. Esa decisión gobierna qué ve el menú y qué consultas puede hacer cada uno en búsqueda: lo desarrollo en el siguiente bloque.

Justifico las taxonomías cerradas porque abiertas infinitas rompen filtros, dashboards y la consistencia entre pantalla y base de datos.

---

## Navegabilidad (≈ 2 min)

La **navegabilidad** une el mapa con la taxonomía de roles.

Cada rol tiene un **conjunto pequeño de enlaces persistentes** —por ejemplo el cliente: mis tickets, nuevo ticket, cerrar sesión— sin mezclar el dashboard global. Tras el login, la **redirección automática** según rol evita que el agente aterrice en una pantalla de cliente.

En pantallas de **detalle** uso **migas de pan** o equivalente —por ejemplo: inicio, mis tickets, ticket número— para que siempre se sepa dónde uno está. Un botón de **volver a la lista** reduce la dependencia del botón atrás del navegador.

Si alguien intenta entrar a una ruta sin permiso, la navegación debe responder con **redirección o mensaje claro**, no con una página vacía: eso cierra el círculo entre seguridad y arquitectura de la información.

---

## Mecanismos de búsqueda (≈ 2 min)

La **búsqueda** también respeta roles.

El **cliente** solo busca y filtra dentro de **sus propios tickets**, por texto en título o descripción y opcionalmente por estado. Así no hay riesgo de filtrar información de otros usuarios en la interfaz.

El **agente** sí necesita **búsqueda global** sobre los tickets que la política de seguridad le permite ver, más **filtros** por estado, categoría y fechas para priorizar trabajo real.

Cuando no hay resultados, el sistema debe mostrar un **estado vacío claro** —“no hay coincidencias”— para no confundir con un error de red. El orden por defecto por **fecha descendente** es el más útil en mesas de ayuda: primero lo más reciente.

En el futuro, la IA podría sumar búsqueda semántica o sugerencias; la base que dejamos —texto más metadatos— ya soporta ese salto sin rediseñar todo.

---

## Cierre y decisiones globales (≈ 1–2 min)

En resumen: **separé el sitio por roles**, definí **metadatos del ticket** pensando en listados, filtros y clasificación automática, organicé la **navegación** para que sea mínima y coherente con permisos, y diseñé la **búsqueda** como restringida para el cliente y potente para el agente.

Las decisiones buscan **simplicidad para el usuario ocasional** —el que abre un ticket— y **eficiencia para el operador** que gestiona muchos casos al día.

El detalle con diagramas y tablas está en el documento escrito de entrega; esta presentación solo condensa el **proceso de arquitectura de información** y las **justificaciones** principales.

Muchas gracias.

---

### Notas para quien graba

- **Ritmo:** pausar después de cada sección grande; si te pasas de 12 minutos, acorta el bloque “taxonomías” con una frase por metadato clave.  
- **Visual:** si muestras diapositivas, una slide por sección (mapa, taxonomía, navegación, búsqueda, cierre) coincide con los tiempos indicados.  
- **Total:** ~1400–1700 palabras; a ~140 palabras/min ≈ **10–12 min**.
