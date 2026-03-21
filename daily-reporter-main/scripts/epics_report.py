#!/usr/bin/env python3
"""
Script rápido: mensaje con todos los Epics en progreso (estados distintos de Done)
del tablero de Epics, con la info de cada Epic y las tareas asociadas.

Requiere: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN
Opcional: JIRA_EPICS_PROJECT (ej: AIMMSCICD) - preferido, busca por proyecto.
          JIRA_EPICS_BOARD_ID o JIRA_QA_BOARD_ID - fallback, usa board API.

Uso:
  python scripts/epics_report.py
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

# Add project root for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(override=False)


def _getenv(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    if val is None or val == "":
        return default
    return val.strip()


def main() -> int:
    from daily_reporter.jira import JiraClient, JiraIssue

    base_url = _getenv("JIRA_BASE_URL")
    email = _getenv("JIRA_EMAIL")
    api_token = _getenv("JIRA_API_TOKEN")
    epics_project = _getenv("JIRA_EPICS_PROJECT")
    epics_board = _getenv("JIRA_EPICS_BOARD_ID") or _getenv("JIRA_QA_BOARD_ID")

    missing = []
    if not base_url:
        missing.append("JIRA_BASE_URL")
    if not email:
        missing.append("JIRA_EMAIL")
    if not api_token:
        missing.append("JIRA_API_TOKEN")
    if not epics_project and not epics_board:
        missing.append("JIRA_EPICS_PROJECT (ej: AIMMSCICD) o JIRA_EPICS_BOARD_ID")
    if missing:
        print(f"[error] Faltan variables: {', '.join(missing)}")
        return 1

    jira = JiraClient(base_url=base_url, email=email, api_token=api_token)

    # Epics en progreso: todos los estados excepto Done
    epics_jql = "issuetype = Epic AND statusCategory != Done"
    if epics_project:
        # Buscar por proyecto (más fiable que board API para backlogs de Epics)
        epics = jira.search_issues(jql=f"project = {epics_project} AND {epics_jql}")
    else:
        epics = jira.board_issues(board_id=int(epics_board), jql=epics_jql)
    if not epics:
        msg = "No hay Epics en progreso en el tablero."
        print(msg)
        return 0

    lines: list[str] = []
    lines.append(f"## Epics en progreso ({date.today().isoformat()})\n")
    lines.append(f"Total: {len(epics)} Epic(s)\n")

    for epic in sorted(epics, key=lambda e: (e.status or "", e.key)):
        lines.append(f"### [{epic.key}]({epic.url}) — {epic.summary}")
        lines.append(f"- **Estado:** {epic.status}")
        lines.append(f"- **Asignado:** {epic.assignee or 'Sin asignar'}")
        if epic.story_points is not None:
            lines.append(f"- **Story Points:** {epic.story_points}")
        if epic.due_date:
            lines.append(f"- **Fecha límite:** {epic.due_date.isoformat()}")

        # Tareas asociadas: parentEpic (Jira Cloud) o parent (fallback)
        children: list[JiraIssue] = []
        try:
            children = jira.search_issues(jql=f'parentEpic = "{epic.key}"')
        except Exception:
            try:
                children = jira.search_issues(jql=f'parent = "{epic.key}"')
            except Exception as e:
                lines.append(f"- **Tareas:** (error: {e})")
                lines.append("")
                continue

        if children:
            lines.append("- **Tareas asociadas:**")
            for t in sorted(children, key=lambda x: (x.status or "", x.key)):
                assignee = t.assignee or "Sin asignar"
                sp = f" ({t.story_points} pts)" if t.story_points else ""
                lines.append(f"  - [{t.key}]({t.url}) — {t.summary} | {t.status} | {assignee}{sp}")
        else:
            lines.append("- **Tareas asociadas:** (ninguna)")

        lines.append("")

    message = "\n".join(lines)
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
