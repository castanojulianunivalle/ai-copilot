from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from urllib.parse import urlencode

import requests

from ..http_utils import parse_json, raise_for_status, request_with_retries


@dataclass(frozen=True)
class JiraIssue:
    key: str
    url: str
    summary: str
    issue_type: str
    status: str
    assignee: str | None
    created: datetime | None
    updated: datetime | None
    due_date: date | None
    original_estimate_seconds: int | None
    story_points: float | None
    project_key: str | None


def _parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except Exception:
        return None


def _parse_date(val: str | None) -> date | None:
    if not val:
        return None
    try:
        return date.fromisoformat(val)
    except Exception:
        return None


class JiraClient:
    def __init__(self, *, base_url: str, email: str, api_token: str, timeout_s: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
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

    def _post(self, path: str, json_body: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"

        def _do() -> requests.Response:
            return self.session.post(url, json=json_body, timeout=self.timeout_s)

        resp = request_with_retries(_do)
        raise_for_status(resp, context=f"POST {path}")
        return parse_json(resp)

    def board_issues(
        self,
        *,
        board_id: int,
        jql: str,
        max_results: int = 200,
    ) -> list[JiraIssue]:
        """
        Uses Jira Agile API to fetch issues visible in a board, with an additional JQL filter.
        """
        start_at = 0
        out: list[JiraIssue] = []
        fields_param = "*all"

        while True:
            payload = self._get(
                f"/rest/agile/1.0/board/{board_id}/issue",
                params={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": max_results,
                    "fields": fields_param,
                },
            )
            issues = payload.get("issues", [])
            for raw in issues:
                out.append(self._to_issue(raw))

            if payload.get("isLast", False):
                break
            start_at = payload.get("startAt", 0) + payload.get("maxResults", max_results)
            if start_at >= payload.get("total", 0):
                break

        return out

    def search_issues(
        self,
        *,
        jql: str,
        max_results: int = 200,
    ) -> list[JiraIssue]:
        """
        Uses JIRA REST API search to fetch issues by JQL (any query, not board-specific).
        Uses /rest/api/3/search/jql (migrated from deprecated /rest/api/3/search).
        """
        start_at = 0
        out: list[JiraIssue] = []
        fields_param = "*all"

        while True:
            payload = self._get(
                "/rest/api/3/search/jql",
                params={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": max_results,
                    "fields": fields_param,
                },
            )
            issues = payload.get("issues", [])
            for raw in issues:
                out.append(self._to_issue(raw))

            total = payload.get("total", 0)
            if start_at + len(issues) >= total:
                break
            start_at += len(issues)
            if len(issues) == 0:
                break

        return out

    def _extract_comment_text(self, body: Any) -> str:
        if isinstance(body, str):
            return body
        if not isinstance(body, dict):
            return str(body)
        content_parts = []

        def _extract_from_content(obj: Any) -> None:
            if isinstance(obj, dict):
                if "text" in obj:
                    content_parts.append(obj["text"])
                if "content" in obj and isinstance(obj["content"], list):
                    for item in obj["content"]:
                        _extract_from_content(item)
                elif "plain" in obj:
                    content_parts.append(obj["plain"])
            elif isinstance(obj, list):
                for item in obj:
                    _extract_from_content(item)

        _extract_from_content(body)
        return " ".join(content_parts).strip()

    def get_issue_comments(self, issue_key: str, since_date: date | None = None) -> list[dict[str, Any]]:
        try:
            payload = self._get(f"/rest/api/3/issue/{issue_key}/comment")
            comments = payload.get("comments", []) or []

            if since_date:
                filtered = []
                for comment in comments:
                    created_str = comment.get("created")
                    if created_str:
                        try:
                            created_dt = _parse_dt(created_str)
                            if created_dt and created_dt.date() == since_date:
                                body_raw = comment.get("body", "")
                                body_text = self._extract_comment_text(body_raw)
                                filtered.append({
                                    "body": body_text,
                                    "created": created_dt,
                                    "author": (comment.get("author") or {}).get("displayName", "Unknown"),
                                })
                        except Exception:
                            pass
                return filtered

            result = []
            for c in comments:
                body_raw = c.get("body", "")
                body_text = self._extract_comment_text(body_raw)
                result.append({
                    "body": body_text,
                    "created": _parse_dt(c.get("created")),
                    "author": (c.get("author") or {}).get("displayName", "Unknown"),
                })
            return result
        except Exception as e:
            print(f"[jira] Failed to get comments for {issue_key}: {e}")
            return []

    def _to_issue(self, raw: dict[str, Any]) -> JiraIssue:
        key = raw.get("key", "")
        fields: dict[str, Any] = raw.get("fields", {}) or {}

        issue_type = (fields.get("issuetype") or {}).get("name") or ""
        status = (fields.get("status") or {}).get("name") or ""
        assignee_obj = fields.get("assignee")
        assignee = None
        if isinstance(assignee_obj, dict):
            assignee = assignee_obj.get("displayName") or assignee_obj.get("emailAddress")

        timetracking = fields.get("timetracking") or {}
        original_estimate_seconds = (
            timetracking.get("originalEstimateSeconds")
            or fields.get("timeoriginalestimate")
            or None
        )

        story_points = None
        common_story_point_fields = {"customfield_10016", "customfield_10020", "customfield_10026", "customfield_10021"}
        for k, v in fields.items():
            if isinstance(k, str) and k.lower() in common_story_point_fields:
                if isinstance(v, (int, float)) and v is not None:
                    story_points = float(v)
                    break
                elif isinstance(v, dict) and 'value' in v:
                    val = v.get('value')
                    if isinstance(val, (int, float)) and val is not None:
                        story_points = float(val)
                        break

        if story_points is None:
            for k, v in fields.items():
                if not isinstance(k, str) or not k.startswith("customfield_"):
                    continue
                if isinstance(v, (int, float)) and v is not None and v > 0:
                    if 0.5 <= float(v) <= 100:
                        story_points = float(v)
                        break
                elif isinstance(v, dict) and "value" in v:
                    val = v.get("value")
                    if isinstance(val, (int, float)) and val is not None and val > 0:
                        if 0.5 <= float(val) <= 100:
                            story_points = float(val)
                            break

        project_key = None
        project = fields.get("project")
        if isinstance(project, dict):
            project_key = project.get("key")

        return JiraIssue(
            key=key,
            url=f"{self.base_url}/browse/{key}",
            summary=fields.get("summary") or "",
            issue_type=issue_type,
            status=status,
            assignee=assignee,
            created=_parse_dt(fields.get("created")),
            updated=_parse_dt(fields.get("updated")),
            due_date=_parse_date(fields.get("duedate")),
            original_estimate_seconds=int(original_estimate_seconds) if original_estimate_seconds else None,
            story_points=story_points,
            project_key=project_key,
        )


def default_dev_jql(today: date, assignee_filter: str | None = None) -> str:
    from datetime import timedelta
    today_str = today.isoformat()
    next_day = (today + timedelta(days=1)).isoformat()
    base_query = "statusCategory != Done "

    if assignee_filter:
        assignee_escaped = assignee_filter.replace('"', '\\"')
        base_query += f"AND assignee is not EMPTY "
        base_query += f"AND assignee != \"{assignee_escaped}\" "
        five_days_ago = (today - timedelta(days=5)).isoformat()
        base_query += f"AND (updated >= '{today_str}' AND updated < '{next_day}' "
        base_query += f"OR (created >= '{five_days_ago}' AND created < '{next_day}'))"
    else:
        base_query += "AND assignee is not EMPTY "
        base_query += f"AND (updated >= '{today_str}' OR created >= '{today_str}')"

    return base_query


def default_qa_jql(today: date, assignee_filter: str | None = None) -> str:
    from datetime import timedelta
    today_str = today.isoformat()
    next_day = (today + timedelta(days=1)).isoformat()
    base_query = "issuetype = Epic AND statusCategory != Done "

    if assignee_filter:
        assignee_escaped = assignee_filter.replace('"', '\\"')
        base_query += f"AND assignee is not EMPTY "
        base_query += f"AND assignee != \"{assignee_escaped}\" "
        five_days_ago = (today - timedelta(days=5)).isoformat()
        base_query += f"AND (updated >= '{today_str}' AND updated < '{next_day}' "
        base_query += f"OR (created >= '{five_days_ago}' AND created < '{next_day}'))"
    else:
        base_query += "AND assignee is not EMPTY "
        base_query += f"AND (updated >= '{today_str}' OR created >= '{today_str}')"

    return base_query
