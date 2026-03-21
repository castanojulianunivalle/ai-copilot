#!/usr/bin/env python3
"""
Upload Story Mapping to JIRA:
  1. Creates 3 sprints on the board
  2. Creates 7 Epics
  3. Creates Stories under each Epic
  4. Creates Subtasks under each Story with developer assignments
  5. Sets story points and assigns stories to sprints

Usage:
  python scripts/upload_to_jira.py              # dry-run (muestra lo que haría)
  python scripts/upload_to_jira.py --execute    # ejecuta la carga real
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(override=False)

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Proyecto y board: según URL .../jira/software/projects/SR/boards/1/backlog
PROJECT_KEY = os.getenv("JIRA_UPLOAD_PROJECT_KEY", "SR")
BOARD_ID = int(os.getenv("JIRA_UPLOAD_BOARD_ID", "1"))  # 0 = auto-detect

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# Story points custom field (most common in Jira Cloud)
STORY_POINTS_FIELD = "customfield_10016"

# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------
TEAM = {
    "jimmy": "jimmy.villegas@correunivalle.edu.co",
    "eider": "eider.matallana@correounivalle.edu.co",
    "jhonathan": "jhonathan.delgado@correounivalle.edu.co",
    "juan": "males.juan@correounivalle.edu.co",
    "andres": "andres.fabian.urrea@correounivalle.edu.co",
}

# ---------------------------------------------------------------------------
# Sprints
# ---------------------------------------------------------------------------
SPRINTS = [
    {
        "name": "Sprint 1 - Infra+CRUD",
        "startDate": "2026-02-23T08:00:00.000-05:00",
        "endDate": "2026-03-08T18:00:00.000-05:00",
    },
    {
        "name": "Sprint 2 - Agenda+Ejecución",
        "startDate": "2026-03-09T08:00:00.000-05:00",
        "endDate": "2026-03-22T18:00:00.000-05:00",
    },
    {
        "name": "Sprint 3 - Ruta+Analítica",
        "startDate": "2026-03-23T08:00:00.000-05:00",
        "endDate": "2026-04-01T18:00:00.000-05:00",
    },
]

# ---------------------------------------------------------------------------
# Epics & Stories data
# ---------------------------------------------------------------------------
EPICS = [
    {
        "summary": "Epic 0 — Infraestructura y configuración base",
        "description": "Setup técnico: proyecto React PWA + Django REST Framework + PostgreSQL, autenticación JWT, modelos de datos base.",
        "stories": [
            {
                "summary": "HU-0.1 — Setup del proyecto y estructura base",
                "description": (
                    "Como desarrollador, quiero tener el proyecto configurado con la estructura base "
                    "(React PWA + Django + PostgreSQL), para comenzar a desarrollar funcionalidades.\n\n"
                    "Criterios de aceptación:\n"
                    "- Proyecto React inicializado con PWA habilitado (manifest.json, service worker)\n"
                    "- Proyecto Django inicializado con DRF y estructura de apps (core, visits, users, reports)\n"
                    "- PostgreSQL configurado con settings de Django (dev/prod)\n"
                    "- Docker Compose para entorno local (React + Django + PostgreSQL)\n"
                    "- CORS configurado entre React y Django\n"
                    "- README con instrucciones de setup local"
                ),
                "points": 5,
                "sprint": 1,
                "subtasks": [
                    {"summary": "Setup proyecto React + PWA + estructura de carpetas", "assignee": "juan"},
                    {"summary": "Setup Django + DRF + PostgreSQL + Docker Compose", "assignee": "jimmy"},
                ],
            },
            {
                "summary": "HU-0.2 — Autenticación y gestión de roles",
                "description": (
                    "Como usuario del sistema, quiero iniciar sesión con mis credenciales y acceder solo "
                    "a las funcionalidades de mi rol, para garantizar la seguridad.\n\n"
                    "Criterios de aceptación:\n"
                    "- Login con email/contraseña usando Django Auth + JWT (simplejwt)\n"
                    "- Modelo de usuario extendido con campo rol (Administrador, Asesor, Empresa)\n"
                    "- Permisos DRF por rol (IsAdmin, IsAsesor, IsEmpresa)\n"
                    "- Endpoint POST /api/auth/login (retorna access + refresh token)\n"
                    "- Endpoint POST /api/auth/register con asignación de rol\n"
                    "- Pantalla de login responsive en React\n"
                    "- Protección de rutas React con PrivateRoute según rol\n"
                    "- Logout y expiración de sesión"
                ),
                "points": 8,
                "sprint": 1,
                "subtasks": [
                    {"summary": "Django Auth + JWT + permisos por rol + endpoints", "assignee": "eider"},
                    {"summary": "Pantalla login + PrivateRoute + manejo de tokens React", "assignee": "andres"},
                ],
            },
            {
                "summary": "HU-0.3 — Modelo de datos y CRUD de entidades base",
                "description": (
                    "Como desarrollador, quiero tener los modelos de Empresa, Asesor, Zona y Visita "
                    "en la base de datos, para soportar toda la lógica de negocio.\n\n"
                    "Criterios de aceptación:\n"
                    "- Modelo Empresa (nombre, NIT, dirección, contacto, coordenadas lat/lng, zona FK)\n"
                    "- Modelo Asesor (user FK, teléfono, zona asignada FK, estado activo/inactivo)\n"
                    "- Modelo Zona (nombre, descripción)\n"
                    "- Modelo Visita (asesor FK, empresa FK, tipo, estado, fecha_programada, fecha_ejecución, observaciones, resultado)\n"
                    "- Migraciones Django ejecutables y management command de seed\n"
                    "- Serializers + ViewSets CRUD para Empresas y Asesores (solo admin)\n"
                    "- Admin Django configurado para todas las entidades"
                ),
                "points": 8,
                "sprint": 1,
                "subtasks": [
                    {"summary": "Modelos Django + migraciones + admin + seed", "assignee": "jimmy"},
                    {"summary": "Serializers + ViewSets CRUD Empresas y Asesores", "assignee": "jhonathan"},
                ],
            },
        ],
    },
    {
        "summary": "Epic 1 — Planificación y gestión de visitas empresariales",
        "description": "Permite al administrador crear, editar, cancelar y reprogramar visitas asignando asesor, empresa, tipo, fecha y hora.",
        "stories": [
            {
                "summary": "HU-1.1 — Crear visita empresarial",
                "description": (
                    "Como administrador, quiero crear una visita asignando asesor, empresa, tipo de visita "
                    "(promoción o control), fecha y hora, para planificar la agenda de visitas.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: POST /api/visitas/ con validaciones de negocio\n"
                    "- Validación: no se permite solapamiento de horario para el mismo asesor\n"
                    "- Validación: no se permite visita duplicada a la misma empresa el mismo día\n"
                    "- Al crear, la visita queda en estado Programada\n"
                    "- Formulario React con campos: asesor, empresa, tipo, fecha, hora inicio, hora fin\n"
                    "- Se muestra confirmación y la visita aparece en el listado"
                ),
                "points": 5,
                "sprint": 1,
                "subtasks": [
                    {"summary": "API POST /api/visitas/ + validaciones de negocio", "assignee": "jimmy"},
                    {"summary": "Formulario crear visita React + integración API", "assignee": "juan"},
                ],
            },
            {
                "summary": "HU-1.2 — Editar y cancelar visitas programadas",
                "description": (
                    "Como administrador, quiero editar o cancelar visitas programadas, para ajustar la planificación.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: PUT /api/visitas/:id/ permite cambiar fecha, hora, asesor o empresa (estado=Programada)\n"
                    "- API: PATCH /api/visitas/:id/cancelar/ cambia estado a Cancelada, motivo obligatorio\n"
                    "- No se puede editar/cancelar una visita Realizada\n"
                    "- Modelo HistorialVisita para registrar cambios\n"
                    "- UI: formulario de edición + modal de cancelación con motivo"
                ),
                "points": 5,
                "sprint": 1,
                "subtasks": [
                    {"summary": "API PUT + PATCH cancelar + modelo HistorialVisita", "assignee": "eider"},
                    {"summary": "UI edición + modal cancelación React", "assignee": "andres"},
                ],
            },
            {
                "summary": "HU-1.3 — Reprogramar visitas solicitadas",
                "description": (
                    "Como administrador, quiero reprogramar visitas solicitadas por la empresa o por necesidad operativa.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: PATCH /api/visitas/:id/reprogramar/ nueva fecha/hora + motivo obligatorio\n"
                    "- Flujo: Programada → Reprogramada → Programada (nueva fecha)\n"
                    "- Trazabilidad en HistorialVisita\n"
                    "- Validación de solapamiento al reprogramar\n"
                    "- UI: opción reprogramar desde detalle + formulario nueva fecha/motivo"
                ),
                "points": 3,
                "sprint": 1,
                "subtasks": [
                    {"summary": "API PATCH reprogramar + validaciones + historial", "assignee": "jhonathan"},
                    {"summary": "UI reprogramar visita React", "assignee": "juan"},
                ],
            },
        ],
    },
    {
        "summary": "Epic 2 — Visualización y control de la agenda de visitas",
        "description": "Calendario global para administradores y agenda personal para asesores, con filtros por fecha, asesor, empresa y estado.",
        "stories": [
            {
                "summary": "HU-2.1 — Calendario global de visitas (Administrador)",
                "description": (
                    "Como administrador, quiero visualizar todas las visitas en un calendario general.\n\n"
                    "Criterios de aceptación:\n"
                    "- Componente React con react-big-calendar o FullCalendar\n"
                    "- Modos: día, semana, mes\n"
                    "- Cada evento muestra: empresa, asesor, hora, estado (color diferenciado)\n"
                    "- Click en visita abre modal de detalle\n"
                    "- API: GET /api/visitas/ con filtros por rango de fechas\n"
                    "- Responsive: funciona en desktop y tablet"
                ),
                "points": 8,
                "sprint": 2,
                "subtasks": [
                    {"summary": "API GET /api/visitas/ con filtros por rango de fechas", "assignee": "jimmy"},
                    {"summary": "Componente calendario React + integración API", "assignee": "juan"},
                ],
            },
            {
                "summary": "HU-2.2 — Filtrar visitas por asesor, estado o fecha",
                "description": (
                    "Como administrador, quiero filtrar visitas por asesor, estado, fecha o empresa.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: GET /api/visitas/ con query params: asesor, estado, fecha_desde, fecha_hasta, empresa\n"
                    "- Django-filter integrado en ViewSet\n"
                    "- Panel de filtros React: multi-select, date picker, búsqueda\n"
                    "- Filtros en tiempo real sobre calendario y lista\n"
                    "- URL refleja filtros (deep linking)"
                ),
                "points": 5,
                "sprint": 2,
                "subtasks": [
                    {"summary": "Django-filter en ViewSet + query params API", "assignee": "eider"},
                    {"summary": "Panel de filtros React + deep linking URL", "assignee": "andres"},
                ],
            },
            {
                "summary": "HU-2.3 — Agenda personal del asesor",
                "description": (
                    "Como asesor, quiero ver mi agenda diaria y semanal con las visitas asignadas.\n\n"
                    "Criterios de aceptación:\n"
                    "- Vista de agenda diaria con lista de visitas ordenadas por hora\n"
                    "- Vista semanal con resumen por día\n"
                    "- Cada visita muestra: empresa, dirección, hora, tipo, estado\n"
                    "- Solo muestra visitas del asesor autenticado\n"
                    "- Optimizada para móvil"
                ),
                "points": 5,
                "sprint": 2,
                "subtasks": [
                    {"summary": "API filtro visitas por asesor autenticado (request.user)", "assignee": "jhonathan"},
                    {"summary": "Componente agenda diaria/semanal React mobile-first", "assignee": "juan"},
                ],
            },
        ],
    },
    {
        "summary": "Epic 3 — Ejecución y registro de visitas por asesores",
        "description": "El asesor registra inicio/fin de la visita, resultado, observaciones y consulta su historial.",
        "stories": [
            {
                "summary": "HU-3.1 — Registrar inicio y fin de una visita (check-in / check-out)",
                "description": (
                    "Como asesor, quiero registrar el inicio y fin de una visita.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: PATCH /api/visitas/:id/checkin/ registra hora inicio + geolocalización\n"
                    "- API: PATCH /api/visitas/:id/checkout/ registra hora fin, estado → Realizada\n"
                    "- Validación: solo si fecha es hoy y estado es Programada/En ejecución\n"
                    "- No se puede iniciar si hay otra visita En ejecución\n"
                    "- Campos: hora_inicio_real, hora_fin_real, latitud_checkin, longitud_checkin\n"
                    "- Botones React con captura de geolocalización"
                ),
                "points": 5,
                "sprint": 2,
                "subtasks": [
                    {"summary": "API checkin/checkout + validaciones + campos modelo", "assignee": "jimmy"},
                    {"summary": "Botones checkin/checkout React + geolocalización", "assignee": "andres"},
                ],
            },
            {
                "summary": "HU-3.2 — Registrar resultado y observaciones de la visita",
                "description": (
                    "Como asesor, quiero registrar el resultado y observaciones de la visita.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: PUT /api/visitas/:id/resultado/ campos: resultado, observaciones (max 1000)\n"
                    "- Campo opcional: evidencia fotográfica (max 3 fotos, upload a storage)\n"
                    "- Modelo Evidencia con FileField\n"
                    "- Formulario React post-visita\n"
                    "- Validación: no se puede guardar sin resultado seleccionado"
                ),
                "points": 5,
                "sprint": 2,
                "subtasks": [
                    {"summary": "API resultado + modelo Evidencia + upload archivos", "assignee": "eider"},
                    {"summary": "Formulario resultado React + upload fotos", "assignee": "andres"},
                ],
            },
            {
                "summary": "HU-3.3 — Historial de visitas realizadas (asesor)",
                "description": (
                    "Como asesor, quiero consultar el historial de mis visitas realizadas.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: GET /api/visitas/?asesor=me&estado=realizada con paginación\n"
                    "- Filtro por rango de fechas\n"
                    "- Lista paginada React con empresa, fecha, resultado\n"
                    "- Click en visita abre detalle completo (con fotos)\n"
                    "- Ordenable por fecha (más reciente primero)"
                ),
                "points": 3,
                "sprint": 2,
                "subtasks": [
                    {"summary": "API paginación + filtro asesor autenticado", "assignee": "jhonathan"},
                    {"summary": "Lista historial React + detalle con fotos", "assignee": "juan"},
                ],
            },
        ],
    },
    {
        "summary": "Epic 4 — Optimización de la ruta diaria del asesor",
        "description": "Visualización en mapa de las visitas del día.",
        "stories": [
            {
                "summary": "HU-4.1 — Visualizar ruta del día en mapa",
                "description": (
                    "Como asesor, quiero visualizar la ruta del día con todas mis visitas en un mapa.\n\n"
                    "Criterios de aceptación:\n"
                    "- Mapa interactivo con React Leaflet (OpenStreetMap)\n"
                    "- Marcadores por visita: nombre empresa, hora, estado (color)\n"
                    "- Ubicación actual del asesor en tiempo real (GPS)\n"
                    "- Ruta trazada entre ubicación actual y visitas pendientes\n"
                    "- Click en marcador: popup con detalle + botón navegar (Google Maps/Waze)\n"
                    "- Funcional en móvil con pantalla completa"
                ),
                "points": 8,
                "sprint": 3,
                "subtasks": [
                    {"summary": "API visitas del día con coordenadas para asesor", "assignee": "jimmy"},
                    {"summary": "Componente mapa React Leaflet + marcadores + ruta", "assignee": "juan"},
                ],
            },
        ],
    },
    {
        "summary": "Epic 5 — Gestión de visitas desde la empresa visitada",
        "description": "Portal para que la empresa visualice visitas programadas, solicite reprogramaciones y confirme visitas realizadas.",
        "stories": [
            {
                "summary": "HU-5.1 — Visualizar visitas programadas (empresa)",
                "description": (
                    "Como empresa, quiero visualizar las visitas programadas para estar informada.\n\n"
                    "Criterios de aceptación:\n"
                    "- Dashboard React con lista de visitas programadas (próximas primero)\n"
                    "- Cada visita: fecha, hora, asesor, tipo, estado\n"
                    "- Filtrable por estado y rango de fechas\n"
                    "- Indicador de próxima visita destacado\n"
                    "- Solo muestra visitas de la empresa autenticada"
                ),
                "points": 3,
                "sprint": 2,
                "subtasks": [
                    {"summary": "API filtro visitas por empresa autenticada", "assignee": "jhonathan"},
                    {"summary": "Dashboard empresa React", "assignee": "andres"},
                ],
            },
            {
                "summary": "HU-5.2 — Solicitar reprogramación de visita (empresa)",
                "description": (
                    "Como empresa, quiero solicitar la reprogramación de una visita.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: POST /api/visitas/:id/solicitar-reprogramacion/\n"
                    "- Modelo SolicitudReprogramacion (visita FK, fecha_preferida, motivo, estado)\n"
                    "- Estado visita cambia a Pendiente de reprogramación\n"
                    "- Admin puede aprobar/rechazar\n"
                    "- UI: botón solicitar reprogramación + estado solicitud"
                ),
                "points": 5,
                "sprint": 2,
                "subtasks": [
                    {"summary": "Modelo SolicitudReprogramacion + API solicitar + resolver", "assignee": "eider"},
                    {"summary": "UI solicitar reprogramación + estado solicitud React", "assignee": "juan"},
                ],
            },
            {
                "summary": "HU-5.3 — Confirmar visita realizada (empresa)",
                "description": (
                    "Como empresa, quiero confirmar que la visita fue realizada.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: PATCH /api/visitas/:id/confirmar-empresa/ valoración 1-5, comentario opcional\n"
                    "- Campos: confirmada_empresa, valoracion_empresa, comentario_empresa\n"
                    "- Después de checkout del asesor, empresa ve opción confirmar\n"
                    "- Management command auto-confirmar visitas sin respuesta tras 48h\n"
                    "- UI: botón confirmar con estrellas + comentario"
                ),
                "points": 3,
                "sprint": 3,
                "subtasks": [
                    {"summary": "API confirmar + auto-confirmación 48h (management command)", "assignee": "eider"},
                    {"summary": "UI confirmación con estrellas React", "assignee": "juan"},
                ],
            },
        ],
    },
    {
        "summary": "Epic 6 — Análisis y seguimiento de visitas",
        "description": "Dashboard con indicadores, estadísticas de cumplimiento y reportes exportables.",
        "stories": [
            {
                "summary": "HU-6.1 — Estadísticas de visitas programadas vs realizadas",
                "description": (
                    "Como administrador, quiero ver estadísticas de visitas programadas vs realizadas.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: GET /api/reportes/cumplimiento/ Django ORM aggregations por semana\n"
                    "- KPIs: tasa de cumplimiento, canceladas, reprogramadas\n"
                    "- Filtros: fecha_desde, fecha_hasta, zona\n"
                    "- Dashboard React con gráficos recharts/chart.js: barras y torta\n"
                    "- Datos actualizados al cambiar filtros"
                ),
                "points": 5,
                "sprint": 3,
                "subtasks": [
                    {"summary": "API reportes/cumplimiento + aggregations Django ORM", "assignee": "eider"},
                    {"summary": "Dashboard gráficos React (recharts/chart.js)", "assignee": "andres"},
                ],
            },
            {
                "summary": "HU-6.2 — Indicadores de desempeño por asesor",
                "description": (
                    "Como administrador, quiero visualizar indicadores por asesor.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: GET /api/reportes/desempeno-asesores/ aggregations por asesor\n"
                    "- Filtro por período y zona\n"
                    "- Tabla React de asesores ordenable por columna\n"
                    "- Click en asesor muestra detalle con historial gráfico semanal"
                ),
                "points": 5,
                "sprint": 3,
                "subtasks": [
                    {"summary": "API desempeño-asesores + aggregations por asesor", "assignee": "jimmy"},
                    {"summary": "Tabla desempeño React + detalle asesor", "assignee": "juan"},
                ],
            },
            {
                "summary": "HU-6.3 — Histórico de visitas por empresa",
                "description": (
                    "Como administrador, quiero consultar el histórico de visitas por empresa.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: GET /api/reportes/historico-empresa/:id/ timeline de visitas\n"
                    "- Resumen: total visitas, última visita, frecuencia promedio\n"
                    "- Exportación a Excel/CSV (openpyxl)\n"
                    "- Búsqueda de empresa con autocompletado React (debounced)\n"
                    "- Timeline de visitas recibidas en UI"
                ),
                "points": 3,
                "sprint": 3,
                "subtasks": [
                    {"summary": "API histórico-empresa + exportación Excel/CSV", "assignee": "jhonathan"},
                    {"summary": "Búsqueda empresa + timeline React", "assignee": "andres"},
                ],
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# JIRA API helpers
# ---------------------------------------------------------------------------
class JiraUploader:
    def __init__(self, base_url: str, email: str, token: str, dry_run: bool = True):
        self.base_url = base_url
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.auth = (email, token)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        self._account_cache: dict[str, str] = {}
        self._subtask_issuetype_id: str | None = None

    def _get_subtask_issuetype_id(self) -> str:
        """Obtiene el ID del tipo de incidencia 'subtask' del proyecto (vía API, válido para Jira en español)."""
        if self._subtask_issuetype_id is not None:
            return self._subtask_issuetype_id
        data = self._get(
            f"/rest/api/3/issue/createmeta/{PROJECT_KEY}/issuetypes"
        )
        types = data.get("issueTypes") or data.get("values") or []
        for it in types:
            if it.get("subtask") is True:
                self._subtask_issuetype_id = str(it["id"])
                print(f"  [config] Tipo subtarea del proyecto: id={self._subtask_issuetype_id} ({it.get('name', '')})")
                return self._subtask_issuetype_id
        # Fallback: intentar por nombre (inglés o español)
        for it in types:
            name = (it.get("name") or "").lower()
            if "sub" in name and "task" in name or "tarea" in name:
                self._subtask_issuetype_id = str(it["id"])
                print(f"  [config] Tipo subtarea (por nombre): id={self._subtask_issuetype_id} ({it.get('name', '')})")
                return self._subtask_issuetype_id
        raise RuntimeError(
            "No se encontró un tipo de incidencia 'subtask' en el proyecto. "
            "Revisa la configuración del proyecto en Jira."
        )

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self.base_url}{path}"
        if self.dry_run:
            print(f"  [DRY-RUN] POST {path}")
            print(f"            body keys: {list(body.get('fields', body).keys())}")
            return {"id": "dry-run-id", "key": f"{PROJECT_KEY}-DRY"}
        resp = self.session.post(url, json=body, timeout=30)
        if resp.status_code >= 400:
            print(f"  [ERROR] POST {path} → {resp.status_code}: {resp.text[:500]}")
            resp.raise_for_status()
        return resp.json()

    def _text_to_adf(self, text: str) -> dict:
        """Convert plain text to Atlassian Document Format."""
        paragraphs = []
        for line in text.split("\n"):
            if line.strip():
                paragraphs.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": line}],
                })
            else:
                paragraphs.append({"type": "paragraph", "content": []})
        return {"type": "doc", "version": 1, "content": paragraphs}

    # -- Users --
    def resolve_account_id(self, email: str) -> str | None:
        if email in self._account_cache:
            return self._account_cache[email]
        try:
            users = self._get("/rest/api/3/user/search", params={"query": email})
            for u in users:
                if (u.get("emailAddress") or "").lower() == email.lower():
                    aid = u["accountId"]
                    self._account_cache[email] = aid
                    print(f"  [user] {email} → {aid}")
                    return aid
            if users:
                aid = users[0]["accountId"]
                self._account_cache[email] = aid
                print(f"  [user] {email} → {aid} (best match)")
                return aid
        except Exception as e:
            print(f"  [WARN] Could not resolve user {email}: {e}")
        return None

    # -- Sprints --
    def create_sprint(self, sprint_data: dict, board_id: int) -> str:
        print(f"\n[sprint] Creating: {sprint_data['name']}")
        body = {
            "name": sprint_data["name"],
            "startDate": sprint_data["startDate"],
            "endDate": sprint_data["endDate"],
            "originBoardId": board_id,
        }
        if self.dry_run:
            print(f"  [DRY-RUN] POST /rest/agile/1.0/sprint → {sprint_data['name']}")
            return "dry-run-sprint-id"
        resp = self.session.post(
            f"{self.base_url}/rest/agile/1.0/sprint",
            json=body,
            timeout=30,
        )
        if resp.status_code >= 400:
            print(f"  [ERROR] {resp.status_code}: {resp.text[:500]}")
            resp.raise_for_status()
        data = resp.json()
        sprint_id = str(data["id"])
        print(f"  [OK] Sprint created: id={sprint_id}")
        return sprint_id

    def move_to_sprint(self, sprint_id: str, issue_keys: list[str]) -> None:
        if not issue_keys:
            return
        print(f"  [sprint] Moving {len(issue_keys)} issues to sprint {sprint_id}")
        if self.dry_run:
            print(f"  [DRY-RUN] Issues: {issue_keys}")
            return
        body = {"issues": issue_keys}
        resp = self.session.post(
            f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
            json=body,
            timeout=30,
        )
        if resp.status_code >= 400:
            print(f"  [WARN] Move to sprint failed: {resp.status_code}: {resp.text[:300]}")

    # -- Issues --
    def create_epic(self, summary: str, description: str) -> str:
        print(f"\n[epic] Creating: {summary}")
        body = {
            "fields": {
                "project": {"key": PROJECT_KEY},
                "summary": summary,
                "description": self._text_to_adf(description),
                "issuetype": {"name": "Epic"},
            }
        }
        result = self._post("/rest/api/3/issue", body)
        key = result.get("key", "DRY-KEY")
        print(f"  [OK] Epic: {key}")
        time.sleep(0.3)
        return key

    def create_story(
        self,
        summary: str,
        description: str,
        epic_key: str,
        story_points: float | None = None,
    ) -> str:
        print(f"  [story] Creating: {summary}")
        fields: dict = {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": self._text_to_adf(description),
            "issuetype": {"name": "Story"},
            "parent": {"key": epic_key},
        }
        if story_points is not None:
            fields[STORY_POINTS_FIELD] = story_points
        result = self._post("/rest/api/3/issue", {"fields": fields})
        key = result.get("key", "DRY-KEY")
        print(f"    [OK] Story: {key} ({story_points} pts)")
        time.sleep(0.3)
        return key

    def create_subtask(
        self,
        summary: str,
        parent_key: str,
        assignee_account_id: str | None = None,
    ) -> str:
        print(f"    [subtask] Creating: {summary}")
        subtask_type_id = self._get_subtask_issuetype_id() if not self.dry_run else "10000"
        fields: dict = {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "issuetype": {"id": subtask_type_id},
            "parent": {"key": parent_key},
        }
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        result = self._post("/rest/api/3/issue", {"fields": fields})
        key = result.get("key", "DRY-KEY")
        assignee_info = f" → {assignee_account_id}" if assignee_account_id else ""
        print(f"      [OK] Subtask: {key}{assignee_info}")
        time.sleep(0.2)
        return key


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    execute = "--execute" in sys.argv
    dry_run = not execute

    if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("[error] Faltan variables: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        return 1

    if dry_run:
        print("=" * 60)
        print("  DRY-RUN MODE — no se creará nada en JIRA")
        print("  Usa --execute para ejecutar la carga real")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  EJECUTANDO CARGA REAL EN JIRA")
        print(f"  Proyecto: {PROJECT_KEY} | Board: {BOARD_ID}")
        print("=" * 60)

    uploader = JiraUploader(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, dry_run=dry_run)

    # 0. Auto-detect board ID if not set
    board_id = BOARD_ID
    if board_id == 0:
        print("\n" + "=" * 40)
        print("PASO 0: Auto-detectar Board ID")
        print("=" * 40)
        try:
            boards = uploader._get("/rest/agile/1.0/board", params={"projectKeyOrId": PROJECT_KEY})
            board_list = boards.get("values", [])
            if board_list:
                board_id = board_list[0]["id"]
                print(f"  [OK] Board detectado: id={board_id}, name='{board_list[0].get('name', '')}'")
            else:
                print(f"  [ERROR] No se encontró board para proyecto {PROJECT_KEY}")
                return 1
        except Exception as e:
            print(f"  [ERROR] No se pudo detectar board: {e}")
            print("  Configura JIRA_UPLOAD_BOARD_ID en tu .env")
            return 1

    # 1. Resolve team account IDs
    print("\n" + "=" * 40)
    print("PASO 1: Resolver usuarios del equipo")
    print("=" * 40)
    account_ids: dict[str, str | None] = {}
    for alias, email in TEAM.items():
        aid = uploader.resolve_account_id(email)
        account_ids[alias] = aid
        if not aid:
            print(f"  [WARN] No se encontró accountId para {email}")

    # 2. Create sprints
    print("\n" + "=" * 40)
    print("PASO 2: Crear sprints")
    print("=" * 40)
    sprint_ids: dict[int, str] = {}
    for i, sprint_data in enumerate(SPRINTS, start=1):
        sprint_id = uploader.create_sprint(sprint_data, board_id=board_id)
        sprint_ids[i] = sprint_id

    # 3. Create Epics, Stories, Subtasks
    print("\n" + "=" * 40)
    print("PASO 3: Crear Epics → Stories → Subtasks")
    print("=" * 40)
    issues_by_sprint: dict[int, list[str]] = {1: [], 2: [], 3: []}

    for epic_data in EPICS:
        epic_key = uploader.create_epic(epic_data["summary"], epic_data["description"])

        for story in epic_data["stories"]:
            story_key = uploader.create_story(
                summary=story["summary"],
                description=story["description"],
                epic_key=epic_key,
                story_points=story.get("points"),
            )

            sprint_num = story.get("sprint", 1)
            issues_by_sprint.setdefault(sprint_num, []).append(story_key)

            for subtask in story.get("subtasks", []):
                alias = subtask["assignee"]
                assignee_id = account_ids.get(alias)
                uploader.create_subtask(
                    summary=subtask["summary"],
                    parent_key=story_key,
                    assignee_account_id=assignee_id,
                )

    # 4. Move stories to sprints
    print("\n" + "=" * 40)
    print("PASO 4: Asignar stories a sprints")
    print("=" * 40)
    for sprint_num, issue_keys in sorted(issues_by_sprint.items()):
        sprint_id = sprint_ids.get(sprint_num)
        if sprint_id and issue_keys:
            print(f"\n  Sprint {sprint_num}: {len(issue_keys)} stories")
            uploader.move_to_sprint(sprint_id, issue_keys)

    # Summary
    total_epics = len(EPICS)
    total_stories = sum(len(e["stories"]) for e in EPICS)
    total_subtasks = sum(len(s.get("subtasks", [])) for e in EPICS for s in e["stories"])
    print("\n" + "=" * 60)
    print(f"  RESUMEN: {total_epics} Epics, {total_stories} Stories, {total_subtasks} Subtasks")
    print(f"  Sprints: {len(SPRINTS)}")
    if dry_run:
        print("\n  >>> Ejecuta con --execute para crear todo en JIRA <<<")
    else:
        print("\n  Carga completada exitosamente.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
