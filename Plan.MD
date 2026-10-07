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
📊 SEMESTRE 2: Componente Inteligente (Con IA)
Fase: Datos, NLP y Validación Científica.
Objetivo: Construir el dataset base, inyectar un LLM de pesos abiertos para clasificación y análisis de sentimiento, y medir su rendimiento frente al motor de reglas del Semestre 1. El plan partía de Llama 3.1 con Hugging Face Router; desde el 5 de octubre de 2026 el modelo es gpt-oss-20b servido por Groq, porque se agotaron los créditos gratuitos de Hugging Face (AISCOP-49).
Calendario Trabajo Integrador 2 — cada sprint cierra con su evento de sustentación: Evento 1 (semana 3) 18 sep · Evento 2 (semana 6) 9 oct · Evento 3 (semana 9) 30 oct.
Historias de Usuario (HU) Refinadas
HU-08 (Dataset Histórico): Como investigador, quiero un log histórico etiquetado de tickets y la línea base del motor de reglas medida, para poder evaluar la IA contra un referente.
HU-06 (Clasificación con LLM): Como sistema, quiero usar un modelo de lenguaje para categorizar tickets complejos que el motor de reglas no identifica.
HU-09 (Evaluación de Modelos): Como investigador, quiero comparar la IA contra el motor de reglas con matriz de confusión, F1-Score y recall para sustentar los resultados.
Plan de Sprints (3 sprints x 3 semanas = 9 semanas)
Sprint 4 — Dataset IA (2026-08-31 → 2026-09-18, cierra en Evento 1): diseño del esquema del dataset, script de exportación/ETL, metadatos versionados en el repo y medición de la línea base de reglas. Cerrado: HU-08, 13 de 13 puntos.
Sprint 5 — LLM Clasificación (2026-09-21 → 2026-10-08, cierra en Evento 2): cliente del LLM compatible con OpenAI (Hugging Face Router, Groq, vLLM u Ollama), prompt engineering, parsing JSON, persistencia de entidades/sentimiento y repliegue al motor de reglas. Cerrado: HU-06, 13 de 13 puntos; medido sobre los 66 tickets etiquetados con gpt-oss-20b en Groq.
Sprint 6 — Evaluación IA (2026-10-12 → 2026-10-29, cierra en Evento 3): conjunto de evaluación etiquetado, script de métricas, matriz de confusión y exportación de gráficas versionadas.

⚙️ SEMESTRE 3: Automatización de Flujos y Analítica (Sin IA)
Fase: Integración de Servicios y Visibilidad Operativa.
Objetivo: Conectar el sistema con flujos externos y exponer la analítica del soporte, ya enriquecida con las salidas de la IA del Semestre 2.
Historias de Usuario (HU) Refinadas
HU-05 (Notificaciones Externas): Como agente, quiero que el sistema dispare un flujo en n8n para notificarme cuando se cree un ticket de alta prioridad.
HU-06b (Real-time Updates): Como agente, quiero ver los nuevos tickets aparecer en mi pantalla sin refrescar la página para atenderlos de inmediato.
HU-07 (Dashboard Analítico): Como administrador, quiero visualizar métricas de tickets resueltos vs. pendientes —y el desempeño de la clasificación IA— para medir la eficiencia del equipo.
Plan de Sprints
Sprint 7 — n8n y Realtime (2026-11-02 → 2026-11-20): webhooks en FastAPI, flujo n8n (Email/Telegram), Supabase Realtime en el dashboard y prueba end-to-end.
Sprint 8 — Reportes y cierre (2026-11-23 → 2026-12-11): endpoints agregados/vistas SQL, componentes de gráficas (Recharts), integración en el dashboard y artículo final.

📝 Resumen de Entregables Técnicos
Semestre 1: Repositorio con App Web + Supabase + CRUD funcional + motor de reglas (línea base).
Semestre 2: Dataset histórico + Implementación de IA (gpt-oss-20b en Groq) + Informe de Métricas (F1-Score, Recall, matriz de confusión).
Semestre 3: Flujos de n8n activos + Realtime + Dashboard con analítica descriptiva + Artículo de Investigación.
