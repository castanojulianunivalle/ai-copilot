Plan Maestro: AI Support Co-Pilot (Mesa de Ayuda Inteligente)
Programa: Maestría en Computación para el Desarrollo de Aplicaciones Inteligentes (CODING)
Rol: Solo Developer
📅 SEMESTRE 1: Arquitectura Base y Gestión de Tickets (Sin IA)
Fase: Fundamentación y CRUD Transaccional.
Objetivo: Establecer la infraestructura cloud, seguridad y flujo básico de tickets.
Historias de Usuario (HU) Refinadas
HU-01 (Autenticación): Como usuario, quiero registrarme e iniciar sesión con roles (Cliente/Agente) para acceder a un panel personalizado.
HU-02 (CRUD Cliente): Como cliente, quiero crear tickets con título y descripción para recibir asistencia técnica.
HU-03 (CRUD Agente): Como agente, quiero visualizar todos los tickets y actualizar su estado (Abierto/Cerrado) para gestionar el soporte.
HU-04 (Clasificación Fallback): Como sistema, quiero asignar categorías basadas en palabras clave (ej. "internet", "error") para tener una línea base de comparación.
Plan de Sprints (Sprint 0 + 3 sprints x 3 semanas)
Sprint 0: Kickoff, definición de entorno, repositorio, Jira y documentación inicial (2 semanas).
Sprint 1: Configuración de Supabase (Tablas, RLS), Setup de FastAPI + React e implementación de Auth y Perfiles de Usuario.
Sprint 2: Desarrollo del panel de creación y listado de tickets para el Cliente.
Sprint 3: Dashboard del Agente y motor de reglas de clasificación básico (Python if/else).
📊 SEMESTRE 2: Automatización de Flujos y Analítica (Sin IA)
Fase: Integración de Servicios y Preparación de Datos.
Objetivo: Conectar el sistema con flujos externos y generar visibilidad sobre el rendimiento del soporte.
Historias de Usuario (HU) Refinadas
HU-05 (Notificaciones Externas): Como agente, quiero que el sistema dispare un flujo en n8n para enviarme un correo cuando se cree un ticket de alta prioridad.
HU-06 (Real-time Updates): Como agente, quiero ver los nuevos tickets aparecer en mi pantalla sin refrescar la página para atenderlos de inmediato.
HU-07 (Dashboard Analítico): Como administrador, quiero visualizar métricas de tickets resueltos vs. pendientes para medir la eficiencia del equipo.
Plan de Sprints (3 sprints x 3 semanas = 9 semanas)
Sprint 4: Configuración de Webhooks en FastAPI, integración con n8n (Email/Telegram) e implementación de Supabase Realtime en el Dashboard.
Sprint 5: Creación de vistas de reportes y gráficas estadísticas (Recharts) y armado de Dataset histórico.
Sprint 6: Ingeniería de Datos: log histórico de tickets para entrenamiento y validación futura.
🧠 SEMESTRE 3: Inteligencia Artificial y Evaluación (Con IA)
Fase: Implementación de NLP y Validación Científica.
Objetivo: Inyectar el LLM (Llama 3.1) para clasificación, análisis de sentimiento y generar el artículo de grado.
Historias de Usuario (HU) Refinadas
HU-08 (Clasificación con LLM): Como sistema, quiero usar un modelo de lenguaje para categorizar tickets complejos que el motor de reglas no identifica.
HU-09 (Análisis de Sentimiento): Como agente, quiero que los tickets se prioricen automáticamente si el LLM detecta un tono "Frustrado" o "Urgente" en el texto del cliente.
HU-10 (Asistente de Respuesta): Como agente, quiero que la IA me sugiera una respuesta basada en la base de conocimientos para reducir mi tiempo de redacción.
Plan de Sprints (3 sprints x 3 semanas = 9 semanas)
Sprint 7: Integración de la API de Llama-3.1 (Hugging Face Router o vLLM) e implementación de Prompt Engineering para extracción de entidades y análisis de sentimiento.
Sprint 8: Evaluación de Modelos: comparación matemática del accuracy de la IA vs. motor de reglas del Semestre 1 (Matriz de Confusión).
Sprint 9: Redacción del artículo final, conclusiones de rendimiento y preparación de la sustentación.
📝 Resumen de Entregables Técnicos
Semestre 1: Repositorio con App Web + Supabase + CRUD funcional.
Semestre 2: Flujos de n8n activos + Dashboard con analítica descriptiva.
Semestre 3: Implementación de IA + Informe de Métricas (F1-Score, Recall) + Artículo de Investigación.
