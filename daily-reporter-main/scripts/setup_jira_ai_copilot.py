#!/usr/bin/env python3
"""
Setup JIRA para AI Support Co-Pilot desde docs de ai-ticket-processor.

Crea automaticamente en JIRA (plan gratuito):
  - Sprints (con fechas 2026)
  - Publicaciones/Versiones (una por sprint; Fix Version en Epics, Stories y Subtareas)
  - Epics
  - Stories (Historias de Usuario) y Subtareas con descripcion
  - Fix Version por sprint (9 sprints; ver 6.release_plan_agilismo.md)
Uso:
  python scripts/setup_jira_ai_copilot.py                    # dry-run (no toca Jira)
  python scripts/setup_jira_ai_copilot.py --execute          # crea sprints, versiones, epics, stories
  python scripts/setup_jira_ai_copilot.py --execute --clean  # primero borra issues/versiones/sprints del
                                                             # proyecto y tablero, luego crea todo de nuevo

  --clean solo tiene efecto con --execute (destructivo). Opcional: --yes o JIRA_CLEAN_SKIP_CONFIRM=1 para no pedir Enter.

Si create sprint da 400: el tablero debe ser SCRUM (no Kanban). Habilita sprints en Jira:
  Board > Configurar (engranaje) > General > Sprints.
"""

from __future__ import annotations

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
PROJECT_KEY = os.getenv("JIRA_UPLOAD_PROJECT_KEY", "AICOP")
BOARD_ID = int(os.getenv("JIRA_UPLOAD_BOARD_ID", "0"))
# Asignee por defecto para todas las Stories (email Jira)
ASSIGNEE_EMAIL = os.getenv("JIRA_ASSIGNEE_EMAIL", "castano.julian@correounivalle.edu.co")
# Si True: usa Epic Link (customfield_10014). Si False: usa parent (jerarquia Epic-Story)
USE_EPIC_LINK = os.getenv("JIRA_USE_EPIC_LINK", "false").lower() in ("1", "true", "yes")

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

STORY_POINTS_FIELD = "customfield_10016"

# ---------------------------------------------------------------------------
# Sprints: 9 iteraciones (Sprint 0..8), cada una 3 semanas (~21 dias).
# Sprint 0 termina 4 abr 2026; sin tareas de documentos de entrega academica (solo desarrollo).
# Ver docs/Entrega I/6.release_plan_agilismo.md
# ---------------------------------------------------------------------------
# Formato fechas: ISO 8601 con offset -05:00 (Colombia). Jira acepta tambien .000Z
# Nombres de sprint: Jira Cloud exige **menos de 30 caracteres** (max 29).
SPRINTS = [
    {"name": "Sprint 0 - Doc y mockups", "startDate": "2026-03-15T09:00:00.000-05:00", "endDate": "2026-04-04T18:00:00.000-05:00"},
    {"name": "Sprint 1 - Auth y Perfiles", "startDate": "2026-04-05T09:00:00.000-05:00", "endDate": "2026-04-25T18:00:00.000-05:00"},
    {"name": "Sprint 2 - Panel Cliente", "startDate": "2026-04-26T09:00:00.000-05:00", "endDate": "2026-05-16T18:00:00.000-05:00"},
    {"name": "Sprint 3 - Dashboard y Reglas", "startDate": "2026-05-17T09:00:00.000-05:00", "endDate": "2026-06-06T18:00:00.000-05:00"},
    {"name": "Sprint 4 - n8n y Realtime", "startDate": "2026-06-07T09:00:00.000-05:00", "endDate": "2026-06-27T18:00:00.000-05:00"},
    {"name": "Sprint 5 - Reportes", "startDate": "2026-06-28T09:00:00.000-05:00", "endDate": "2026-07-18T18:00:00.000-05:00"},
    {"name": "Sprint 6 - Dataset", "startDate": "2026-07-19T09:00:00.000-05:00", "endDate": "2026-08-08T18:00:00.000-05:00"},
    {"name": "Sprint 7 - LLM", "startDate": "2026-08-09T09:00:00.000-05:00", "endDate": "2026-08-29T18:00:00.000-05:00"},
    {"name": "Sprint 8 - Evaluacion", "startDate": "2026-08-30T09:00:00.000-05:00", "endDate": "2026-09-19T18:00:00.000-05:00"},
]

# Una publicacion (Version) por cada sprint (para progreso en Releases)
ALL_SPRINT_VERSION_INDICES = tuple(range(9))
# Sprints con seguimiento de tiempo (original estimate)
SPRINTS_WITH_TIME_TRACKING = (0, 1, 2, 3)
# 1 Story Point = 4 horas (docs: 4-6h efectivas)
HOURS_PER_STORY_POINT = 4

# Subtareas: (summary, description)
def _subs(*items: tuple[str, str]) -> list[dict[str, str]]:
    return [{"summary": s, "description": d} for s, d in items]


# ---------------------------------------------------------------------------
# Epics & Stories - Backlog (docs 5.backlog_historias)
# ---------------------------------------------------------------------------
EPICS = [
    {
        "summary": "Epic 1: Autenticacion y Arquitectura Base",
        "description": "Prioridad: Alta. Responsable: Desarrollador (Estudiante).",
        "stories": [
            {
                "summary": "HU-00: Documentacion tecnica, mockups y preparacion de entorno",
                "description": "Como desarrollador, quiero documentacion tecnica en el repo, mockups de pantallas y entorno listo para desarrollo, sin incluir redaccion de documentos de entrega academica.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Diagrama o notas de arquitectura (ADR/stack) en el repositorio.\n"
                "2. Mockups o wireframes en repo (assets/ o docs/tecnicos).\n"
                "3. README con setup local, variables de entorno y ramas base (develop).",
                "points": 2,
                "sprint": 0,
                "original_estimate": "8h",
                "subtasks": _subs(
                    ("Notas tecnicas de arquitectura en repo",
                     "Documentar decision de arquitectura (ADR) o notas sobre el stack tecnico (FastAPI, React, Supabase) en el repositorio para referencia del equipo."),
                    ("Mockups / wireframes en assets o docs tecnicos",
                     "Crear wireframes o mockups de las pantallas principales y guardarlos en assets/ o docs/tecnicos del repo."),
                    ("README: entorno, env y flujo de ramas",
                     "Actualizar README con instrucciones de setup local, variables de entorno (.env.example) y convencion de ramas (develop, main)."),
                ),
            },
            {
                "summary": "HU-01: Registro de Usuarios (Clientes)",
                "description": "Como usuario cliente, quiero registrarme en la plataforma usando mi correo y contrasena, para poder acceder al sistema y solicitar soporte tecnico.\n\n"
                "Criterios de Aceptacion:\n"
                "1. El formulario debe validar el formato del correo.\n"
                "2. La contrasena debe tener minimo 8 caracteres.\n"
                "3. El usuario debe crearse en Supabase Auth y asignarse el rol Cliente por defecto.",
                "points": 3,
                "sprint": 1,  # Sprint 1: Auth y Perfiles
                "original_estimate": "12h",  # 3 SP * 4h
                "subtasks": _subs(
                    ("API / auth Supabase registro",
                     "Implementar endpoint o integracion con Supabase Auth para registro de usuarios; persistir perfil con rol Cliente por defecto."),
                    ("Formulario registro React + validacion",
                     "Crear formulario de registro en React con validacion de email (formato) y contrasena (min 8 caracteres)."),
                    ("Pruebas E2E flujo registro",
                     "Automatizar prueba end-to-end del flujo completo de registro (Playwright/Cypress o similar)."),
                ),
            },
            {
                "summary": "HU-02: Inicio de Sesion y Redireccion por Rol",
                "description": "Como usuario (Cliente, Agente o Administrador), quiero iniciar sesion de forma segura, para acceder a mi panel correspondiente segun mis permisos.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Login exitoso genera un token JWT valido.\n"
                "2. Si es Cliente se redirige a /mis-tickets.\n"
                "3. Si es Agente se redirige a /dashboard.\n"
                "4. Si es Administrador puede acceder a gestion de usuarios (panel Admin).",
                "points": 2,
                "sprint": 1,
                "original_estimate": "8h",  # 2 SP * 4h
                "subtasks": _subs(
                    ("Login JWT + Supabase",
                     "Integrar inicio de sesion con Supabase Auth; gestionar token JWT y sesion en frontend."),
                    ("Redireccion por rol en frontend",
                     "Tras login, redirigir a /mis-tickets (Cliente), /dashboard (Agente) o panel Admin segun el rol del usuario."),
                    ("Pruebas rutas protegidas",
                     "Verificar que rutas protegidas requieren autenticacion y rechacen acceso no autorizado."),
                ),
            },
        ],
        "original_estimate": "28h",  # Epic 1: HU-00 + HU-01 + HU-02
    },
    {
        "summary": "Epic 2: Gestion Integral de Tickets (CRUD)",
        "description": "Prioridad: Alta. Responsable: Desarrollador (Estudiante).",
        "stories": [
            {
                "summary": "HU-03: Creacion de Ticket de Soporte",
                "description": "Como usuario cliente, quiero un formulario para crear un nuevo ticket con un titulo y descripcion, para solicitar ayuda al equipo de soporte.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Campos Titulo y Descripcion son obligatorios.\n"
                "2. El registro debe persistirse en la tabla tickets de Supabase.\n"
                "3. El estado inicial debe ser Abierto.",
                "points": 5,
                "sprint": 2,
                "original_estimate": "20h",  # 5 SP * 4h
                "subtasks": _subs(
                    ("Modelo tickets Supabase + RLS",
                     "Crear tabla tickets en Supabase con RLS para que clientes vean solo sus tickets y agentes todos."),
                    ("API crear ticket FastAPI",
                     "Endpoint POST /tickets en FastAPI que reciba titulo y descripcion, valide y persista en Supabase."),
                    ("UI formulario y listado cliente",
                     "Formulario de creacion de ticket y listado de tickets del cliente en React."),
                ),
            },
            {
                "summary": "HU-04: Dashboard de Agente y Cambio de Estado",
                "description": "Como agente de soporte, quiero ver una tabla con todos los tickets del sistema y poder editarlos, para priorizarlos y marcarlos como Cerrado.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Vista protegida por Rol (RLS en Supabase).\n"
                "2. Endpoint PATCH /tickets/{id} funcional.\n"
                "3. El estado se actualiza en la base de datos y se refleja en la UI (Abierto <-> Cerrado).",
                "points": 5,
                "sprint": 3,
                "original_estimate": "20h",  # 5 SP * 4h
                "subtasks": _subs(
                    ("Endpoint PATCH tickets + permisos",
                     "Implementar PATCH /tickets/{id} para cambio de estado (Abierto/Cerrado) con validacion de rol agente."),
                    ("Tabla dashboard agente React",
                     "Vista tabular de todos los tickets con filtros y boton para cambiar estado."),
                    ("Pruebas cambio de estado",
                     "Pruebas E2E o unitarias del flujo de cambio de estado por un agente."),
                ),
            },
            {
                "summary": "HU-04b: Clasificacion por Reglas (Sistema)",
                "description": "Como sistema, quiero asignar categorias basadas en palabras clave cuando se crea o edita un ticket, para tener una linea base de comparacion para el motor IA (Semestre 3).\n\n"
                "Criterios de Aceptacion:\n"
                "1. Motor de reglas (Python if/else) analiza titulo y descripcion.\n"
                "2. Se asigna una categoria valida (Tecnico, Facturacion, Acceso, etc.).\n"
                "3. La categoria se persiste junto con el ticket.",
                "points": 3,
                "sprint": 3,
                "original_estimate": "12h",  # 3 SP * 4h
                "subtasks": _subs(
                    ("Motor de reglas Python",
                     "Implementar logica if/else o expresiones que mapeen palabras clave (internet, error, facturacion, etc.) a categorias."),
                    ("Persistir categoria en ticket",
                     "Guardar la categoria asignada en el registro del ticket al crear o actualizar."),
                    ("Pruebas reglas con casos ejemplo",
                     "Script o tests que verifiquen la clasificacion para tickets de ejemplo con distintas palabras clave."),
                ),
            },
        ],
        "original_estimate": "52h",  # Epic 2
    },
    {
        "summary": "Epic 3: Inteligencia Artificial y Automatizacion (Sem 2-3)",
        "description": "Prioridad: Media-Alta (S2-S3). Desarrollo: n8n, reportes, dataset, LLM, evaluacion. Entregables academicos fuera del backlog de desarrollo.",
        "stories": [
            {
                "summary": "HU-05: Notificaciones Automatizadas (n8n)",
                "description": "Como administrador del sistema, quiero conectar la creacion de tickets con un webhook, para enviar un mensaje a Telegram cuando ingrese una solicitud urgente.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Webhook configurado en FastAPI.\n"
                "2. Flujo de n8n recibe el payload y envia el mensaje de Telegram exitosamente.",
                "points": 3,
                "sprint": 4,
                "subtasks": _subs(
                    ("Webhook FastAPI",
                     "Endpoint que reciba eventos de creacion de ticket (o payload externo) y dispare notificacion."),
                    ("Flujo n8n Telegram",
                     "Workflow en n8n que reciba el webhook y envie mensaje a canal/grupo de Telegram."),
                    ("Prueba end-to-end",
                     "Verificar que al crear ticket prioritario se reciba notificacion en Telegram."),
                ),
            },
            {
                "summary": "HU-07: Dashboard analitico y reportes (Recharts)",
                "description": "Como agente o administrador, quiero vistas de reportes y graficas estadisticas, para analizar volumen y estado de tickets.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Vistas con Recharts (o similar) en React.\n"
                "2. Datos agregados desde API o Supabase.\n"
                "3. Filtros basicos por fecha o estado.",
                "points": 5,
                "sprint": 5,
                "subtasks": _subs(
                    ("Endpoints agregados o vistas SQL",
                     "API o vistas materializadas que expongan datos agregados (por estado, fecha, etc.)."),
                    ("Componentes graficas Recharts",
                     "Graficas (barras, lineas, pie) con Recharts usando datos de la API."),
                    ("Integracion en dashboard",
                     "Incorporar las graficas en la vista del dashboard de agente o administrador."),
                ),
            },
            {
                "summary": "HU-08: Dataset historico e ingenieria de datos",
                "description": "Como sistema, quiero consolidar un historial de tickets para entrenamiento y analisis futuro, para soportar el modelo IA en semestres posteriores.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Export o pipeline de datos historico.\n"
                "2. Formato utilizable (CSV/JSON) documentado.\n"
                "3. Log o trazabilidad de origen.",
                "points": 5,
                "sprint": 6,
                "subtasks": _subs(
                    ("Diseno esquema dataset",
                     "Definir estructura del dataset (columnas, tipos, etiquetas) para exportacion de tickets historicos."),
                    ("Script exportacion / ETL basico",
                     "Script (Python o SQL) que exporte datos de tickets a CSV/JSON con trazabilidad de origen."),
                    ("README tecnico y metadatos del dataset en repo",
                     "Documentar el dataset: formato, esquema, origen y uso previsto en el repo."),
                ),
            },
            {
                "summary": "HU-06: Clasificacion mediante IA (LLM)",
                "description": "Como sistema, quiero utilizar el modelo Llama-3.1 para procesar el titulo y descripcion del ticket, para clasificar automaticamente la categoria y el sentimiento sin intervencion humana.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Prompt estructurado para devolver formato JSON.\n"
                "2. FastAPI se comunica con Hugging Face / vLLM correctamente.\n"
                "3. Las entidades extraidas (Categoria, Sentimiento) se guardan en la DB junto con el ticket.",
                "points": 8,
                "sprint": 7,
                "subtasks": _subs(
                    ("Integracion API LLM / vLLM",
                     "Conectar FastAPI con Hugging Face Router, vLLM o API externa para inferencia del modelo."),
                    ("Prompt engineering + parsing JSON",
                     "Diseñar prompt que devuelva JSON con categoria y sentimiento; parsear y validar la respuesta."),
                    ("Persistencia entidades en DB",
                     "Guardar categoria y sentimiento extraidos en la base de datos junto con el ticket."),
                ),
            },
            {
                "summary": "HU-09: Evaluacion de modelos (metricas F1, matriz confusion)",
                "description": "Como desarrollador, quiero scripts y salidas reproducibles de evaluacion del modelo (F1, matriz de confusion), para medir calidad del clasificador en codigo.\n\n"
                "Criterios de Aceptacion:\n"
                "1. Matriz de confusion y F1-score (u otras metricas) en scripts/notebooks.\n"
                "2. Resultados exportables en repo (csv/json o figuras generadas).\n"
                "3. Comparacion reproducible con baseline/reglas.",
                "points": 5,
                "sprint": 8,
                "subtasks": _subs(
                    ("Conjunto de evaluacion etiquetado o fixture",
                     "Preparar dataset con tickets etiquetados (ground truth) para evaluar el clasificador."),
                    ("Script metricas y matrices en repo",
                     "Script que calcule F1-score, recall, precision y genere matriz de confusion."),
                    ("Exportar metricas y graficas versionadas",
                     "Guardar resultados (JSON/CSV) y figuras en el repo con version asociada para trazabilidad."),
                ),
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# JIRA API helpers
# ---------------------------------------------------------------------------
class JiraUploader:
    def __init__(self, base_url: str, email: str, token: str, project_key: str, dry_run: bool = True):
        self.base_url = base_url
        self.project_key = project_key
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.auth = (email, token)
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        self._account_cache: dict[str, str] = {}
        self._subtask_issuetype_id: str | None = None

    def _get_subtask_issuetype_id(self) -> str:
        if self._subtask_issuetype_id is not None:
            return self._subtask_issuetype_id
        if self.dry_run:
            return "10000"
        data = self._get(f"/rest/api/3/issue/createmeta/{self.project_key}/issuetypes")
        types = data.get("issueTypes") or data.get("values") or []
        for it in types:
            if it.get("subtask") is True:
                self._subtask_issuetype_id = str(it["id"])
                return self._subtask_issuetype_id
        for it in types:
            name = (it.get("name") or "").lower()
            if "sub" in name and "task" in name or "subtarea" in name:
                self._subtask_issuetype_id = str(it["id"])
                return self._subtask_issuetype_id
        raise RuntimeError("No se encontro tipo Subtarea en el proyecto.")

    def resolve_account_id(self, email: str) -> str | None:
        """Obtiene accountId de Jira a partir del email."""
        if email in self._account_cache:
            return self._account_cache[email]
        try:
            users = self._get("/rest/api/3/user/search", params={"query": email})
            for u in users:
                if (u.get("emailAddress") or "").lower() == email.lower():
                    aid = u["accountId"]
                    self._account_cache[email] = aid
                    return aid
            if users:
                aid = users[0]["accountId"]
                self._account_cache[email] = aid
                return aid
        except Exception as e:
            print(f"  [WARN] No se pudo resolver usuario {email}: {e}")
        return None

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self.base_url}{path}"
        if self.dry_run:
            print(f"  [DRY-RUN] POST {path}")
            return {"id": "dry-run", "key": f"{self.project_key}-DRY"}
        resp = self.session.post(url, json=body, timeout=30)
        if resp.status_code >= 400:
            print(f"  [ERROR] POST {path} -> {resp.status_code}: {resp.text[:400]}")
            resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> bool:
        """DELETE; devuelve True si OK o 404."""
        url = f"{self.base_url}{path}"
        if self.dry_run:
            print(f"  [DRY-RUN] DELETE {path}")
            return True
        resp = self.session.delete(url, timeout=30)
        if resp.status_code in (200, 204):
            return True
        if resp.status_code == 404:
            return True
        print(f"  [WARN] DELETE {path} -> {resp.status_code}: {resp.text[:200]}")
        return False

    @staticmethod
    def _issue_delete_priority(issuetype_name: str) -> int:
        """0 = primero (subtareas), 1 = medio, 2 = epic al final."""
        n = (issuetype_name or "").lower()
        if "epic" in n:
            return 2
        if ("sub" in n and "task" in n) or "subtarea" in n:
            return 0
        return 1

    def search_all_issue_keys(self) -> list[str]:
        """Lista todas las keys del proyecto, ordenadas para borrado seguro."""
        keys_with_pri: list[tuple[int, str]] = []
        start = 0
        page = 50
        while True:
            data = self._get(
                "/rest/api/3/search",
                params={
                    "jql": f'project = "{self.project_key}" ORDER BY key ASC',
                    "startAt": start,
                    "maxResults": page,
                    "fields": "issuetype",
                },
            )
            issues = data.get("issues", [])
            total = data.get("total", 0)
            for iss in issues:
                it = (iss.get("fields") or {}).get("issuetype") or {}
                name = it.get("name") or ""
                pri = self._issue_delete_priority(name)
                keys_with_pri.append((pri, iss["key"]))
            start += len(issues)
            if start >= total or not issues:
                break
        keys_with_pri.sort(key=lambda x: (x[0], x[1]))
        return [k for _, k in keys_with_pri]

    def delete_issue(self, issue_key: str, delete_subtasks: bool = True) -> bool:
        qs = f"?deleteSubtasks={'true' if delete_subtasks else 'false'}"
        path = f"/rest/api/3/issue/{issue_key}{qs}"
        return self._delete(path)

    def list_project_versions(self) -> list[dict]:
        data = self._get(f"/rest/api/3/project/{self.project_key}/versions")
        return data if isinstance(data, list) else []

    def delete_version(self, version_id: str) -> bool:
        return self._delete(f"/rest/api/3/version/{version_id}")

    def list_board_sprints(self, board_id: int) -> list[dict]:
        """Sprints asociados al tablero (paginado)."""
        all_vals: list[dict] = []
        start = 0
        page = 50
        while True:
            data = self._get(
                f"/rest/agile/1.0/board/{board_id}/sprint",
                params={"startAt": start, "maxResults": page},
            )
            values = data.get("values", [])
            all_vals.extend(values)
            if not values:
                break
            if data.get("isLast", True):
                break
            start += len(values)
        return all_vals

    def delete_sprint(self, sprint_id: int | str) -> bool:
        return self._delete(f"/rest/agile/1.0/sprint/{sprint_id}")

    def clean_project_board(self, board_id: int) -> None:
        """
        Borra issues del proyecto, versiones y sprints del tablero.
        Los sprints ya completados en Jira Cloud a veces no se pueden borrar por API (se omite con aviso).
        """
        print("\n[PASO CLEAN] Limpiar proyecto y tablero")
        print(f"  Proyecto: {self.project_key} | Board: {board_id}")

        keys = self.search_all_issue_keys()
        print(f"  Issues a eliminar: {len(keys)}")
        for i, key in enumerate(keys):
            ok = self.delete_issue(key, delete_subtasks=True)
            if ok and not self.dry_run:
                print(f"    [{i + 1}/{len(keys)}] {key}")
            time.sleep(0.15)

        versions = self.list_project_versions()
        print(f"  Versiones a eliminar: {len(versions)}")
        for v in versions:
            vid = str(v.get("id", ""))
            name = v.get("name", vid)
            if self.dry_run:
                print(f"    [DRY-RUN] version: {name}")
            else:
                if self.delete_version(vid):
                    print(f"    [OK] version: {name}")
                time.sleep(0.15)

        sprints = self.list_board_sprints(board_id)
        print(f"  Sprints a eliminar: {len(sprints)}")
        for sp in sprints:
            sid = sp.get("id")
            name = sp.get("name", sid)
            state = sp.get("state", "")
            if self.dry_run:
                print(f"    [DRY-RUN] sprint: {name} ({state})")
            else:
                if self.delete_sprint(sid):
                    print(f"    [OK] sprint: {name} ({state})")
                else:
                    print(f"    [SKIP] sprint no borrado (puede estar cerrado o en uso): {name}")
                time.sleep(0.2)

        print("  [OK] Limpieza finalizada (revisa avisos arriba).")

    def _text_to_adf(self, text: str) -> dict:
        paragraphs = []
        for line in text.split("\n"):
            if line.strip():
                paragraphs.append({"type": "paragraph", "content": [{"type": "text", "text": line}]})
            else:
                paragraphs.append({"type": "paragraph", "content": []})
        return {"type": "doc", "version": 1, "content": paragraphs}

    @staticmethod
    def _jira_error_text(resp: requests.Response) -> str:
        """Extrae mensaje util de un error Jira (a veces errorMessages viene vacio)."""
        raw = (resp.text or "").strip()
        try:
            err = resp.json()
        except Exception:
            return raw[:2000] if raw else "(sin cuerpo)"
        msgs = err.get("errorMessages") or []
        field_errs = err.get("errors") or {}
        parts: list[str] = []
        if msgs:
            parts.extend(str(m) for m in msgs)
        if field_errs:
            parts.append(str(field_errs))
        if parts:
            return " | ".join(parts)
        return raw[:2000] if raw else str(err)

    def create_sprint(self, sprint_data: dict, board_id: int) -> str:
        # Jira Cloud: nombre de sprint < 30 caracteres
        _MAX_SPRINT_NAME = 29
        name = (sprint_data.get("name") or "").strip()
        if len(name) > _MAX_SPRINT_NAME:
            name = name[:_MAX_SPRINT_NAME]
            print(f"\n[sprint] Creando (nombre acortado a {_MAX_SPRINT_NAME} chars): {name!r}")
        else:
            print(f"\n[sprint] Creando: {name}")
        body_full = {
            "name": name,
            "originBoardId": board_id,
        }
        if sprint_data.get("startDate"):
            body_full["startDate"] = sprint_data["startDate"]
        if sprint_data.get("endDate"):
            body_full["endDate"] = sprint_data["endDate"]
        if self.dry_run:
            print(f"  [DRY-RUN] POST /rest/agile/1.0/sprint")
            return "dry-run-sprint"

        url = f"{self.base_url}/rest/agile/1.0/sprint"
        resp = self.session.post(url, json=body_full, timeout=30)
        if resp.status_code == 400:
            print(f"  [ERROR] 400 - {self._jira_error_text(resp)}")
            # Reintento: solo nombre + tablero (fechas opcionales; algunos tenants rechazan el formato)
            body_min = {"name": name, "originBoardId": board_id}
            print(f"  [INFO] Reintentando sin startDate/endDate...")
            resp = self.session.post(url, json=body_min, timeout=30)
            if resp.status_code >= 400:
                print(f"  [ERROR] Reintento fallo: {resp.status_code} - {self._jira_error_text(resp)}")
                resp.raise_for_status()
        elif resp.status_code >= 400:
            print(f"  [ERROR] {resp.status_code} - {self._jira_error_text(resp)}")
            resp.raise_for_status()
        data = resp.json()
        print(f"  [OK] Sprint creado: id={data['id']}")
        return str(data["id"])

    def move_to_sprint(self, sprint_id: str, issue_keys: list[str]) -> None:
        if not issue_keys or self.dry_run:
            return
        resp = self.session.post(
            f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
            json={"issues": issue_keys},
            timeout=30,
        )
        if resp.status_code >= 400:
            print(f"  [WARN] Mover a sprint fallo: {resp.status_code}")

    def create_version(
        self,
        name: str,
        description: str = "",
        start_date: str | None = None,
        release_date: str | None = None,
    ) -> str:
        """Crea una publicacion/version en el proyecto."""
        print(f"\n[version] Creando: {name}")
        body = {"project": self.project_key, "name": name}
        if description:
            body["description"] = description
        if start_date:
            body["startDate"] = start_date[:10]  # YYYY-MM-DD
        if release_date:
            body["releaseDate"] = release_date[:10]
        if self.dry_run:
            print(f"  [DRY-RUN] POST /rest/api/3/version")
            return "dry-run-version-id"
        resp = self.session.post(f"{self.base_url}/rest/api/3/version", json=body, timeout=30)
        if resp.status_code >= 400:
            print(f"  [ERROR] {resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()
        data = resp.json()
        vid = str(data["id"])
        print(f"  [OK] Version: {name} (id={vid})")
        time.sleep(0.2)
        return vid

    def create_epic(
        self,
        summary: str,
        description: str,
        assignee_account_id: str | None = None,
        original_estimate: str | None = None,
        fix_version_ids: list[str] | None = None,
    ) -> str:
        print(f"\n[epic] Creando: {summary}")
        fields = {
            "project": {"key": self.project_key},
            "summary": summary,
            "description": self._text_to_adf(description),
            "issuetype": {"name": "Epic"},
        }
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        if original_estimate:
            fields["timetracking"] = {"originalEstimate": original_estimate, "remainingEstimate": original_estimate}
        if fix_version_ids:
            fields["fixVersions"] = [{"id": vid} for vid in fix_version_ids if vid and vid != "dry-run-version-id"]
        result = self._post("/rest/api/3/issue", {"fields": fields})
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
        assignee_account_id: str | None = None,
        fix_version_id: str | None = None,
        original_estimate: str | None = None,
    ) -> str:
        print(f"  [story] Creando: {summary}")
        fields = {
            "project": {"key": self.project_key},
            "summary": summary,
            "description": self._text_to_adf(description),
            "issuetype": {"name": "Story"},
        }
        if USE_EPIC_LINK:
            fields["customfield_10014"] = epic_key  # Epic Link (Jira Scrum)
        else:
            fields["parent"] = {"key": epic_key}   # Jerarquia Epic-Story
        if story_points is not None:
            fields[STORY_POINTS_FIELD] = story_points
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        if fix_version_id and fix_version_id != "dry-run-version-id":
            fields["fixVersions"] = [{"id": fix_version_id}]
        if original_estimate:
            fields["timetracking"] = {"originalEstimate": original_estimate, "remainingEstimate": original_estimate}
        result = self._post("/rest/api/3/issue", {"fields": fields})
        key = result.get("key", "DRY-KEY")
        print(f"    [OK] Story: {key} ({story_points} pts)")
        time.sleep(0.3)
        return key

    def create_subtask(
        self,
        summary: str,
        parent_key: str,
        description: str = "",
        assignee_account_id: str | None = None,
        fix_version_id: str | None = None,
    ) -> str:
        print(f"      [subtask] {summary}")
        sub_id = self._get_subtask_issuetype_id()
        fields: dict = {
            "project": {"key": self.project_key},
            "summary": summary,
            "issuetype": {"id": sub_id},
            "parent": {"key": parent_key},
        }
        if description:
            fields["description"] = self._text_to_adf(description)
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        if fix_version_id and fix_version_id != "dry-run-version-id":
            fields["fixVersions"] = [{"id": fix_version_id}]
        result = self._post("/rest/api/3/issue", {"fields": fields})
        key = result.get("key", "DRY-SUB")
        time.sleep(0.15)
        return key


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return 0

    execute = "--execute" in sys.argv
    clean = "--clean" in sys.argv
    skip_clean_confirm = "--yes" in sys.argv or os.getenv("JIRA_CLEAN_SKIP_CONFIRM", "").lower() in (
        "1",
        "true",
        "yes",
    )
    dry_run = not execute

    if clean and not execute:
        print("[error] --clean solo puede usarse junto con --execute (borra issues, versiones y sprints del proyecto).")
        return 1

    if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("[error] Faltan: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        print("Configura .env (copia env.example y completa)")
        return 1

    if dry_run:
        print("=" * 60)
        print("  DRY-RUN - No se creara nada en JIRA")
        print("  Usa --execute para ejecutar")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  SETUP JIRA - AI Support Co-Pilot")
        print(f"  Proyecto: {PROJECT_KEY} | Board: {BOARD_ID}")
        if clean:
            print("  Modo: --clean (se borra el tablero/proyecto antes de crear)")
        print("=" * 60)

    uploader = JiraUploader(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, PROJECT_KEY, dry_run=dry_run)

    # 0. Resolver accountId del asignee
    assignee_id: str | None = None
    if ASSIGNEE_EMAIL:
        print(f"\n[PASO 0a] Resolver asignee: {ASSIGNEE_EMAIL}")
        assignee_id = uploader.resolve_account_id(ASSIGNEE_EMAIL)
        if assignee_id:
            print(f"  [OK] accountId: {assignee_id}")
        else:
            print(f"  [WARN] No se encontro usuario. Las tareas quedaran sin asignar.")

    # 1. Auto-detect board
    board_id = BOARD_ID
    if board_id == 0:
        print("\n[PASO 1] Auto-detectar Board ID")
        try:
            boards = uploader._get("/rest/agile/1.0/board", params={"projectKeyOrId": PROJECT_KEY})
            values = boards.get("values", [])
            if values:
                board_id = values[0]["id"]
                print(f"  Board: id={board_id}, name={values[0].get('name', '')}")
            else:
                print(f"  [ERROR] No hay board para proyecto {PROJECT_KEY}")
                print("  Crea un board Scrum en JIRA o configura JIRA_UPLOAD_BOARD_ID")
                return 1
        except Exception as e:
            print(f"  [ERROR] {e}")
            return 1

    # 1b. Datos del tablero y compatibilidad con sprints (solo en execute)
    if execute and not dry_run:
        try:
            board_info = uploader._get(f"/rest/agile/1.0/board/{board_id}")
            board_type = (board_info.get("type") or "").lower()
            board_name = board_info.get("name", "")
            loc = board_info.get("location") or {}
            loc_key = loc.get("projectKey") or loc.get("projectKeyOrId")
            if not loc_key and loc.get("projectId") is not None:
                try:
                    pj = uploader._get(f"/rest/api/3/project/{loc['projectId']}")
                    loc_key = pj.get("key")
                except Exception:
                    loc_key = None
            print(f"\n[PASO 1b] Tablero id={board_id}: '{board_name}' | tipo API: {board_type or '?'}")
            if loc_key is not None:
                print(f"  Proyecto asociado al tablero (location): {loc_key}")
                if str(loc_key).upper() != str(PROJECT_KEY).upper():
                    print(
                        f"\n  [ERROR] El tablero {board_id} no pertenece al proyecto {PROJECT_KEY} "
                        f"(esta ligado a {loc_key}). Ajusta JIRA_UPLOAD_BOARD_ID o el project key."
                    )
                    return 1
            if board_type == "kanban":
                print("\n  [ERROR] El tablero es tipo KANBAN. Los sprints solo existen en tableros SCRUM.")
                print(f"  Crea un tablero Scrum para {PROJECT_KEY} o usa el ID del tablero Scrum correcto.")
                return 1
            # Team Managed: tipo "simple" — comprobar feature Sprints
            try:
                feat_resp = uploader._get(f"/rest/agile/1.0/board/{board_id}/features")
                features = feat_resp.get("features", [])
                sprint_feat = next((f for f in features if (f.get("boardFeature") or "").lower() == "sprints"), None)
                if sprint_feat is not None:
                    en = sprint_feat.get("enablement", "")
                    print(f"  Feature Sprints en tablero: {en}")
                    if en == "disabled":
                        print("\n  [ERROR] Sprints deshabilitados en este tablero (Team-managed).")
                        print("  En Jira: Board > Configurar (engranaje) > Features > activar Sprints.")
                        return 1
            except Exception:
                pass
        except Exception as e:
            print(f"\n  [WARN] No se pudo verificar tablero: {e}")

    if execute and clean:
        print("\n" + "!" * 60)
        print("  ATENCION: Se eliminaran todos los issues del proyecto,")
        print("  las versiones (releases) y los sprints de este tablero.")
        print("  Los sprints ya cerrados pueden no borrarse por API (ver avisos).")
        print("!" * 60)
        if not skip_clean_confirm:
            try:
                input("Pulsa Enter para continuar o Ctrl+C para cancelar... ")
            except KeyboardInterrupt:
                print("\n  Cancelado.")
                return 1
        uploader.clean_project_board(board_id)

    # 2. Crear Sprints
    print("\n[PASO 2] Crear Sprints")
    sprint_ids: dict[int, str] = {}
    for i, s in enumerate(SPRINTS):
        sprint_ids[i] = uploader.create_sprint(s, board_id=board_id)

    # 2b. Crear Publicaciones/Versiones (una por sprint, progreso en Releases)
    print("\n[PASO 2b] Crear Publicaciones (Versiones) - todos los sprints")
    version_ids: dict[int, str] = {}
    for i in ALL_SPRINT_VERSION_INDICES:
        s = SPRINTS[i]
        start = s["startDate"][:10] if s.get("startDate") else None
        end = s["endDate"][:10] if s.get("endDate") else None
        version_ids[i] = uploader.create_version(
            name=s["name"],
            description="AI Support Co-Pilot - issues con Fix Version enlazan el progreso aqui.",
            start_date=start,
            release_date=end,
        )

    # 3. Crear Epics y Stories (con DoD, Fix Version, subtareas)
    print("\n[PASO 3] Crear Epics, Stories y Subtareas (con descripcion)")
    issues_by_sprint: dict[int, list[str]] = {}

    for epic_data in EPICS:
        epic_estimate = epic_data.get("original_estimate") if any(
            s.get("sprint") in SPRINTS_WITH_TIME_TRACKING for s in epic_data["stories"]
        ) else None
        # Fix Versions del Epic = union de versiones de sus sprints (progreso en Releases)
        epic_sprint_nums = {s.get("sprint", 1) for s in epic_data["stories"]}
        epic_fix_vids = [
            version_ids[s] for s in sorted(epic_sprint_nums) if s in version_ids and version_ids[s]
        ]
        epic_key = uploader.create_epic(
            epic_data["summary"],
            epic_data["description"],
            assignee_account_id=assignee_id,
            original_estimate=epic_estimate,
            fix_version_ids=epic_fix_vids if epic_fix_vids else None,
        )
        for story in epic_data["stories"]:
            sprint_num = story.get("sprint", 1)
            fix_vid = version_ids.get(sprint_num)
            story_estimate = story.get("original_estimate") if sprint_num in SPRINTS_WITH_TIME_TRACKING else None
            story_key = uploader.create_story(
                summary=story["summary"],
                description=story["description"],
                epic_key=epic_key,
                story_points=story.get("points"),
                assignee_account_id=assignee_id,
                fix_version_id=fix_vid,
                original_estimate=story_estimate,
            )
            issues_by_sprint.setdefault(sprint_num, []).append(story_key)
            for st in story.get("subtasks", []):
                sub_key = uploader.create_subtask(
                    summary=st["summary"],
                    parent_key=story_key,
                    description=st.get("description", ""),
                    assignee_account_id=assignee_id,
                    fix_version_id=fix_vid,
                )
                issues_by_sprint.setdefault(sprint_num, []).append(sub_key)

    # 4. Asignar Stories y Subtareas a Sprints
    print("\n[PASO 4] Asignar issues a Sprints")
    for sn, keys in sorted(issues_by_sprint.items()):
        sid = sprint_ids.get(sn)
        if sid and keys and not uploader.dry_run:
            uploader.move_to_sprint(sid, keys)
            print(f"  Sprint {sn}: {len(keys)} issues (stories + subtareas)")

    total_epics = len(EPICS)
    total_stories = sum(len(e["stories"]) for e in EPICS)
    total_subtasks = sum(
        len(s.get("subtasks", [])) for e in EPICS for s in e["stories"]
    )
    print("\n" + "=" * 60)
    print(f"  RESUMEN: {total_epics} Epics, {total_stories} Stories, {total_subtasks} Subtareas")
    print(f"  Sprints: {len(SPRINTS)}")
    print(f"  Publicaciones (versiones): {len(ALL_SPRINT_VERSION_INDICES)}")
    print(f"  Timetracking: Epics y Stories de Sprints 0-3")
    if dry_run:
        print("\n  >>> Ejecuta con --execute para crear en JIRA <<<")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
