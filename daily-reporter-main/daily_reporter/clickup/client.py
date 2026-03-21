from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import requests

from ..http_utils import parse_json, raise_for_status, request_with_retries


@dataclass(frozen=True)
class ClickUpTask:
    id: str
    name: str
    description: str | None
    markdown_description: str | None
    status: str | None
    url: str | None


class ClickUpClient:
    def __init__(self, *, token: str, timeout_s: float = 30.0):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        self.base_url = "https://api.clickup.com/api/v2"
        self.timeout_s = timeout_s

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"

        def _do() -> requests.Response:
            return self.session.get(url, timeout=self.timeout_s)

        resp = request_with_retries(_do)
        raise_for_status(resp, context=f"GET {path}")
        return parse_json(resp)

    def _post(self, path: str, *, params: dict[str, Any] | None = None, json_body: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"

        def _do() -> requests.Response:
            return self.session.post(url, json=json_body or {}, timeout=self.timeout_s)

        resp = request_with_retries(_do)
        raise_for_status(resp, context=f"POST {path}")
        return parse_json(resp)

    def _put(self, path: str, *, json_body: dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"

        def _do() -> requests.Response:
            return self.session.put(url, json=json_body, timeout=self.timeout_s)

        resp = request_with_retries(_do)
        raise_for_status(resp, context=f"PUT {path}")
        return parse_json(resp)

    def get_authorized_user(self) -> dict[str, Any]:
        """
        Returns the authorized user for the current token.
        """
        return self._get("/user")

    def create_task_comment(self, *, task_id: str, comment_text: str, notify_all: bool = False) -> Any:
        """
        Create a comment on a task. This is the safest way to preserve rich template formatting,
        since it doesn't require updating the task description.
        Endpoint commonly supported by ClickUp API v2:
          POST /task/{task_id}/comment
        Body:
          { "comment_text": "...", "notify_all": false }
        """
        return self._post(
            f"/task/{task_id}/comment",
            json_body={"comment_text": comment_text, "notify_all": notify_all},
        )

    def get_task(self, task_id: str) -> ClickUpTask:
        # Some workspaces only return `markdown_description` when explicitly requested.
        raw = self._get(f"/task/{task_id}", params={"include_markdown_description": "true"})
        return self._to_task(raw)

    def delete_task(self, task_id: str) -> None:
        """
        Delete a task from ClickUp.
        Endpoint: DELETE /task/{task_id}
        """
        self._delete(f"/task/{task_id}")

    def _delete(self, path: str) -> None:
        url = f"{self.base_url}{path}"

        def _do() -> requests.Response:
            return self.session.delete(url, timeout=self.timeout_s)

        resp = request_with_retries(_do)
        raise_for_status(resp, context=f"DELETE {path}")

    def list_tasks_find_by_name(self, *, list_id: str, task_name: str, max_pages: int = 6) -> ClickUpTask | None:
        """
        ClickUp list tasks API supports pagination. Some workspaces support `search` param,
        but to be robust we scan pages and match `name` exactly.
        """
        for page in range(max_pages):
            payload = self._get(
                f"/list/{list_id}/task",
                params={
                    "archived": "false",
                    "page": page,
                    "order_by": "updated",
                    "reverse": "true",
                    "subtasks": "false",
                    "include_closed": "true",
                },
            )
            tasks = payload.get("tasks", []) or []
            for t in tasks:
                if (t.get("name") or "").strip() == task_name.strip():
                    return self._to_task(t)
            if len(tasks) == 0:
                break
        return None

    def list_tasks_find_by_pattern(self, *, list_id: str, name_pattern: str, max_pages: int = 10) -> list[ClickUpTask]:
        """
        Find all tasks matching a name pattern (partial match).
        Returns list of matching tasks.
        """
        matches: list[ClickUpTask] = []
        for page in range(max_pages):
            payload = self._get(
                f"/list/{list_id}/task",
                params={
                    "archived": "false",
                    "page": page,
                    "order_by": "updated",
                    "reverse": "true",
                    "subtasks": "false",
                    "include_closed": "true",
                },
            )
            tasks = payload.get("tasks", []) or []
            for t in tasks:
                task_name = (t.get("name") or "").strip()
                if name_pattern in task_name:
                    matches.append(self._to_task(t))
            if len(tasks) == 0:
                break
        return matches

    def copy_task_to_list(self, *, template_task_id: str, list_id: str, new_name: str) -> ClickUpTask:
        """
        Copies an existing task (template) into the target list.
        """
        payload = self._post(
            f"/task/{template_task_id}/copy",
            params={"list_id": list_id, "name": new_name},
            json_body={},
        )
        # API responses vary; try common shapes
        new_task_id = payload.get("id") or payload.get("task_id") or payload.get("task", {}).get("id")
        if not new_task_id:
            # Some accounts return { "task": { ... } } or just empty; fall back to searching by name.
            found = self.list_tasks_find_by_name(list_id=list_id, task_name=new_name, max_pages=10)
            if not found:
                raise RuntimeError("ClickUp copy task succeeded but could not determine new task id")
            return found
        return self.get_task(str(new_task_id))

    def create_task_from_template(
        self,
        *,
        list_id: str,
        task_template_id: str,
        new_name: str,
        assignees: list[int] | None = None,
    ) -> ClickUpTask:
        """
        Creates a task from a ClickUp Task Template.

        NOTE: ClickUp's API reference lists 'Create Task From Template' under Tasks.
        Workspaces commonly support:
          POST /list/{list_id}/taskTemplate/{task_template_id}
        """
        body: dict[str, Any] = {"name": new_name}
        if assignees is not None:
            body["assignees"] = assignees

        payload = self._post(
            f"/list/{list_id}/taskTemplate/{task_template_id}",
            json_body=body,
        )
        task_id = payload.get("id") or payload.get("task", {}).get("id") or payload.get("task_id")
        if not task_id:
            raise RuntimeError("Create task from template: could not determine created task id from response")
        return self.get_task(str(task_id))

    def get_teams(self) -> list[dict[str, Any]]:
        """
        Returns authorized workspaces/teams for the token.
        """
        data = self._get("/team")
        return data.get("teams", []) or []

    def get_task_templates(self, *, team_id: str) -> list[dict[str, Any]]:
        """
        Lists task templates for a team/workspace.
        Many workspaces expose:
          GET /team/{team_id}/taskTemplate
        """
        data = self._get(f"/team/{team_id}/taskTemplate")
        # Shape varies: sometimes 'templates', sometimes 'task_templates'
        return data.get("templates") or data.get("task_templates") or []

    def create_task(
        self,
        *,
        list_id: str,
        name: str,
        description: str | None = None,
        status: str | None = None,
    ) -> ClickUpTask:
        """
        Create a new task in the specified list.
        """
        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["markdown_content"] = description
        if status is not None:
            body["status"] = status
        
        payload = self._post(f"/list/{list_id}/task", json_body=body)
        task_id = payload.get("id") or (payload.get("task", {}) or {}).get("id")
        if not task_id:
            raise RuntimeError("Create task: could not determine created task id from response")
        return self.get_task(str(task_id))

    def merge_tasks(self, *, target_task_id: str, source_task_ids: list[str]) -> None:
        """
        Merge multiple source tasks into a target task.
        The target task keeps its title and properties, but descriptions, comments, attachments, etc.
        from source tasks are merged into it.
        """
        if not source_task_ids:
            return
        self._post(
            f"/task/{target_task_id}/merge",
            json_body={"source_task_ids": source_task_ids},
        )

    def update_task(
        self,
        *,
        task_id: str,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        assignees: list[int] | None = None,
        due_date_ts: int | None = None,
        followers: list[int] | None = None,
    ) -> None:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        # Update Task supports markdown via `markdown_content` (official docs).
        # https://developer.clickup.com/reference/updatetask
        if description is not None:
            body["markdown_content"] = description
        if status is not None:
            body["status"] = status
        # assignees can be None (don't change), [] (remove all), or [id, ...] (set specific)
        # Use explicit check for list type to allow empty list to remove assignees
        if isinstance(assignees, list):
            body["assignees"] = assignees
        elif assignees is not None:
            body["assignees"] = assignees
        if due_date_ts is not None:
            body["due_date"] = due_date_ts
        if isinstance(followers, list):
            body["followers"] = followers
        if not body:
            return
        self._put(f"/task/{task_id}", json_body=body)

    @staticmethod
    def _to_task(raw: dict[str, Any]) -> ClickUpTask:
        status = None
        st = raw.get("status")
        if isinstance(st, dict):
            status = st.get("status") or st.get("name")
        elif isinstance(st, str):
            status = st

        return ClickUpTask(
            id=str(raw.get("id") or ""),
            name=raw.get("name") or "",
            description=raw.get("description"),
            markdown_description=raw.get("markdown_description"),
            status=status,
            url=raw.get("url"),
        )
