#!/usr/bin/env python3
"""
TEST: Upload reducido a JIRA — 1 sprint, 2 epics, todas asignadas a un solo usuario.
Para validar que la estructura se crea correctamente antes de subir todo.

Usage:
  python scripts/upload_to_jira_test.py              # dry-run
  python scripts/upload_to_jira_test.py --execute    # carga real
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
PROJECT_KEY = os.getenv("JIRA_UPLOAD_PROJECT_KEY", "SCRUM")
BOARD_ID = int(os.getenv("JIRA_UPLOAD_BOARD_ID", "0"))

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

STORY_POINTS_FIELD = "customfield_10016"

# Todas las tareas asignadas a este usuario para la prueba
TEST_USER_EMAIL = "andresdfxyz@gmail.com"

# ---------------------------------------------------------------------------
# 1 Sprint de prueba
# ---------------------------------------------------------------------------
SPRINTS = [
    {
        "name": "Sprint Test - Infra+CRUD",
        "startDate": "2026-02-23T08:00:00.000-05:00",
        "endDate": "2026-03-08T18:00:00.000-05:00",
    },
]

# ---------------------------------------------------------------------------
# 2 Epics reducidos con 2 stories cada uno (subset del plan real)
# ---------------------------------------------------------------------------
EPICS = [
    {
        "summary": "Epic 0 — Infraestructura y configuración base",
        "description": "Setup técnico: React PWA + Django REST Framework + PostgreSQL, autenticación JWT.",
        "stories": [
            {
                "summary": "HU-0.1 — Setup del proyecto y estructura base",
                "description": (
                    "Como desarrollador, quiero tener el proyecto configurado con la estructura base "
                    "(React PWA + Django + PostgreSQL), para comenzar a desarrollar funcionalidades.\n\n"
                    "Criterios de aceptación:\n"
                    "- Proyecto React inicializado con PWA habilitado\n"
                    "- Proyecto Django inicializado con DRF\n"
                    "- PostgreSQL configurado\n"
                    "- Docker Compose para entorno local\n"
                    "- README con instrucciones de setup"
                ),
                "points": 5,
                "subtasks": [
                    {"summary": "[FE] Setup proyecto React + PWA + estructura de carpetas"},
                    {"summary": "[BE] Setup Django + DRF + PostgreSQL + Docker Compose"},
                ],
            },
            {
                "summary": "HU-0.2 — Autenticación y gestión de roles",
                "description": (
                    "Como usuario del sistema, quiero iniciar sesión con mis credenciales y acceder "
                    "solo a las funcionalidades de mi rol.\n\n"
                    "Criterios de aceptación:\n"
                    "- Login con email/contraseña + JWT\n"
                    "- Modelo de usuario con campo rol\n"
                    "- Permisos DRF por rol\n"
                    "- Pantalla de login responsive React\n"
                    "- Protección de rutas frontend"
                ),
                "points": 8,
                "subtasks": [
                    {"summary": "[BE] Django Auth + JWT + permisos por rol + endpoints"},
                    {"summary": "[FE] Pantalla login + PrivateRoute + manejo de tokens React"},
                ],
            },
        ],
    },
    {
        "summary": "Epic 1 — Planificación y gestión de visitas",
        "description": "CRUD de visitas: crear, editar, cancelar y reprogramar.",
        "stories": [
            {
                "summary": "HU-1.1 — Crear visita empresarial",
                "description": (
                    "Como administrador, quiero crear una visita asignando asesor, empresa, tipo, "
                    "fecha y hora.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: POST /api/visitas/\n"
                    "- Validación de solapamiento\n"
                    "- Estado inicial: Programada\n"
                    "- Formulario React"
                ),
                "points": 5,
                "subtasks": [
                    {"summary": "[BE] API POST /api/visitas/ + validaciones de negocio"},
                    {"summary": "[FE] Formulario crear visita React + integración API"},
                ],
            },
            {
                "summary": "HU-1.2 — Editar y cancelar visitas programadas",
                "description": (
                    "Como administrador, quiero editar o cancelar visitas programadas.\n\n"
                    "Criterios de aceptación:\n"
                    "- API: PUT + PATCH cancelar\n"
                    "- Modelo HistorialVisita\n"
                    "- UI edición + modal cancelación"
                ),
                "points": 5,
                "subtasks": [
                    {"summary": "[BE] API PUT + PATCH cancelar + modelo HistorialVisita"},
                    {"summary": "[FE] UI edición + modal cancelación React"},
                ],
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# JIRA API helpers (same as upload_to_jira.py)
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

    def _get(self, path: str, params: dict | None = None) -> dict:
        resp = self.session.get(f"{self.base_url}{path}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: dict) -> dict:
        if self.dry_run:
            print(f"  [DRY-RUN] POST {path}")
            return {"id": "dry-id", "key": f"{PROJECT_KEY}-DRY"}
        resp = self.session.post(f"{self.base_url}{path}", json=body, timeout=30)
        if resp.status_code >= 400:
            print(f"  [ERROR] POST {path} → {resp.status_code}: {resp.text[:500]}")
            resp.raise_for_status()
        return resp.json()

    def _text_to_adf(self, text: str) -> dict:
        paragraphs = []
        for line in text.split("\n"):
            if line.strip():
                paragraphs.append({"type": "paragraph", "content": [{"type": "text", "text": line}]})
            else:
                paragraphs.append({"type": "paragraph", "content": []})
        return {"type": "doc", "version": 1, "content": paragraphs}

    def resolve_account_id(self, email: str) -> str | None:
        try:
            users = self._get("/rest/api/3/user/search", params={"query": email})
            for u in users:
                if (u.get("emailAddress") or "").lower() == email.lower():
                    print(f"  [user] {email} → {u['accountId']}")
                    return u["accountId"]
            if users:
                aid = users[0]["accountId"]
                print(f"  [user] {email} → {aid} (best match: {users[0].get('displayName', '?')})")
                return aid
        except Exception as e:
            print(f"  [WARN] Could not resolve {email}: {e}")
        return None

    def detect_board_id(self) -> int | None:
        try:
            boards = self._get("/rest/agile/1.0/board", params={"projectKeyOrId": PROJECT_KEY})
            board_list = boards.get("values", [])
            if board_list:
                bid = board_list[0]["id"]
                print(f"  [OK] Board: id={bid}, name='{board_list[0].get('name', '')}'")
                return bid
        except Exception as e:
            print(f"  [ERROR] Board detection failed: {e}")
        return None

    def create_sprint(self, sprint_data: dict, board_id: int) -> str:
        print(f"\n[sprint] Creating: {sprint_data['name']}")
        body = {
            "name": sprint_data["name"],
            "startDate": sprint_data["startDate"],
            "endDate": sprint_data["endDate"],
            "originBoardId": board_id,
        }
        result = self._post("/rest/agile/1.0/sprint", body)
        sid = str(result.get("id", "dry-id"))
        print(f"  [OK] Sprint: id={sid}")
        return sid

    def move_to_sprint(self, sprint_id: str, issue_keys: list[str]) -> None:
        if not issue_keys:
            return
        print(f"  [sprint] Moving {len(issue_keys)} issues → sprint {sprint_id}")
        if self.dry_run:
            return
        resp = self.session.post(
            f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
            json={"issues": issue_keys},
            timeout=30,
        )
        if resp.status_code >= 400:
            print(f"  [WARN] Move failed: {resp.status_code}: {resp.text[:300]}")

    def create_epic(self, summary: str, description: str) -> str:
        print(f"\n[epic] {summary}")
        body = {"fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": self._text_to_adf(description),
            "issuetype": {"name": "Epic"},
        }}
        result = self._post("/rest/api/3/issue", body)
        key = result.get("key", "DRY-KEY")
        print(f"  [OK] → {key}")
        time.sleep(0.3)
        return key

    def create_story(self, summary: str, description: str, epic_key: str, points: float | None) -> str:
        print(f"  [story] {summary}")
        fields: dict = {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": self._text_to_adf(description),
            "issuetype": {"name": "Story"},
            "parent": {"key": epic_key},
        }
        if points is not None:
            fields[STORY_POINTS_FIELD] = points
        result = self._post("/rest/api/3/issue", {"fields": fields})
        key = result.get("key", "DRY-KEY")
        print(f"    [OK] → {key} ({points} pts)")
        time.sleep(0.3)
        return key

    def create_subtask(self, summary: str, parent_key: str, assignee_id: str | None) -> str:
        print(f"    [subtask] {summary}")
        fields: dict = {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "issuetype": {"name": "Sub-task"},
            "parent": {"key": parent_key},
        }
        if assignee_id:
            fields["assignee"] = {"accountId": assignee_id}
        result = self._post("/rest/api/3/issue", {"fields": fields})
        key = result.get("key", "DRY-KEY")
        print(f"      [OK] → {key}")
        time.sleep(0.2)
        return key


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    execute = "--execute" in sys.argv
    dry_run = not execute

    if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("[error] Faltan: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        return 1

    mode = "EJECUCIÓN REAL" if execute else "DRY-RUN (usa --execute para crear)"
    print("=" * 60)
    print(f"  TEST UPLOAD — {mode}")
    print(f"  Proyecto: {PROJECT_KEY} | Usuario: {TEST_USER_EMAIL}")
    print("=" * 60)

    up = JiraUploader(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, dry_run=dry_run)

    # Board
    board_id = BOARD_ID
    if board_id == 0:
        print("\n[step 0] Detectando board...")
        board_id = up.detect_board_id()
        if not board_id:
            print("  No se encontró board. Configura JIRA_UPLOAD_BOARD_ID")
            return 1

    # User
    print(f"\n[step 1] Resolviendo usuario: {TEST_USER_EMAIL}")
    account_id = up.resolve_account_id(TEST_USER_EMAIL)
    if not account_id and not dry_run:
        print("  [WARN] No se pudo resolver el usuario. Subtasks quedarán sin asignar.")

    # Sprint
    print("\n[step 2] Creando sprint de prueba")
    sprint_id = up.create_sprint(SPRINTS[0], board_id=board_id)

    # Epics + Stories + Subtasks
    print("\n[step 3] Creando Epics → Stories → Subtasks")
    all_story_keys: list[str] = []

    for epic_data in EPICS:
        epic_key = up.create_epic(epic_data["summary"], epic_data["description"])

        for story in epic_data["stories"]:
            story_key = up.create_story(
                summary=story["summary"],
                description=story["description"],
                epic_key=epic_key,
                points=story.get("points"),
            )
            all_story_keys.append(story_key)

            for subtask in story.get("subtasks", []):
                up.create_subtask(
                    summary=subtask["summary"],
                    parent_key=story_key,
                    assignee_id=account_id,
                )

    # Move to sprint
    print("\n[step 4] Asignando stories al sprint")
    up.move_to_sprint(sprint_id, all_story_keys)

    # Summary
    total_stories = sum(len(e["stories"]) for e in EPICS)
    total_subtasks = sum(len(s.get("subtasks", [])) for e in EPICS for s in e["stories"])
    print("\n" + "=" * 60)
    print(f"  RESUMEN: {len(EPICS)} Epics, {total_stories} Stories, {total_subtasks} Subtasks")
    print(f"  Sprint: 1 | Asignado a: {TEST_USER_EMAIL}")
    if dry_run:
        print("\n  >>> python scripts/upload_to_jira_test.py --execute <<<")
    else:
        print("\n  Carga de prueba completada.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
