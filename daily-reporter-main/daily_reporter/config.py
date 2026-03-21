from __future__ import annotations

import os
from dataclasses import dataclass


def _getenv(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    if val is None or val == "":
        return default
    return val


def _getenv_bool(name: str, default: bool = False) -> bool:
    raw = _getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    clickup_token: str
    clickup_list_id: str
    # Preferred: a ClickUp Task Template ID (not a task id)
    clickup_task_template_id: str | None
    # Optional legacy fallback: a task id used as a "template task" for copy-based creation
    clickup_template_task_id: str | None

    jira_base_url: str
    jira_email: str
    jira_api_token: str

    jira_dev_frontend_board_id: int
    jira_dev_backend_board_id: int
    jira_qa_board_id: int

    jira_dev_jql: str | None
    jira_qa_jql: str | None
    # If set, exclude issues assigned to this Jira user (displayName or emailAddress)
    jira_exclude_user: str | None

    run_phase: str | None
    force_date: str | None
    force_run: bool

    # ClickUp write mode:
    # - comment: keep the template description untouched (preserves rich blocks) and post report as a comment
    # - description: try to update the description via API (may lose rich block formatting)
    # - merge: use merge strategy (create small tasks and merge into header tasks, then into target)
    clickup_write_mode: str
    # If set, assign created daily tasks to this ClickUp user id.
    # If empty, we auto-detect the authorized user from the token via GET /user.
    clickup_owner_id: int | None
    # If true, in the close phase we remove DR markers from the description, leaving only final content.
    clickup_strip_markers_on_close: bool
    # Merge strategy: Task IDs for header sections (Planning, Daily Summary, Final Summary)
    # If all three are set, merge strategy will be used when clickup_write_mode=merge
    clickup_header_planning_task_id: str | None
    clickup_header_daily_summary_task_id: str | None
    clickup_header_final_summary_task_id: str | None
    # Empty task template ID for merge mode (task must be empty, assigned to token owner)
    # Used to duplicate content and objective tasks instead of creating new ones
    clickup_empty_task_template_id: str | None


def load_settings() -> Settings:
    clickup_token = _getenv("CLICKUP_TOKEN")
    clickup_list_id = _getenv("CLICKUP_LIST_ID")
    clickup_task_template_id = _getenv("CLICKUP_TASK_TEMPLATE_ID")
    clickup_template_task_id = _getenv("CLICKUP_TEMPLATE_TASK_ID")

    jira_base_url = _getenv("JIRA_BASE_URL")
    jira_email = _getenv("JIRA_EMAIL")
    jira_api_token = _getenv("JIRA_API_TOKEN")

    dev_fe = _getenv("JIRA_DEV_FRONTEND_BOARD_ID")
    dev_be = _getenv("JIRA_DEV_BACKEND_BOARD_ID")
    qa = _getenv("JIRA_QA_BOARD_ID")

    missing_pairs = [
        ("CLICKUP_TOKEN", clickup_token),
        ("CLICKUP_LIST_ID", clickup_list_id),
        ("JIRA_BASE_URL", jira_base_url),
        ("JIRA_EMAIL", jira_email),
        ("JIRA_API_TOKEN", jira_api_token),
        ("JIRA_DEV_FRONTEND_BOARD_ID", dev_fe),
        ("JIRA_DEV_BACKEND_BOARD_ID", dev_be),
        ("JIRA_QA_BOARD_ID", qa),
    ]
    missing = [name for name, value in missing_pairs if value is None]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    # Require at least one creation source: task template (preferred) or legacy template task id.
    if not clickup_task_template_id and not clickup_template_task_id:
        raise RuntimeError(
            "Missing ClickUp template configuration: set CLICKUP_TASK_TEMPLATE_ID (preferred) "
            "or CLICKUP_TEMPLATE_TASK_ID (legacy)"
        )

    owner_raw = _getenv("CLICKUP_OWNER_ID")
    owner_id = int(owner_raw) if owner_raw else None

    return Settings(
        clickup_token=clickup_token,  # type: ignore[arg-type]
        clickup_list_id=clickup_list_id,  # type: ignore[arg-type]
        clickup_task_template_id=clickup_task_template_id,
        clickup_template_task_id=clickup_template_task_id,
        jira_base_url=jira_base_url.rstrip("/"),  # type: ignore[union-attr]
        jira_email=jira_email,  # type: ignore[arg-type]
        jira_api_token=jira_api_token,  # type: ignore[arg-type]
        jira_dev_frontend_board_id=int(dev_fe),  # type: ignore[arg-type]
        jira_dev_backend_board_id=int(dev_be),  # type: ignore[arg-type]
        jira_qa_board_id=int(qa),  # type: ignore[arg-type]
        jira_dev_jql=_getenv("JIRA_DEV_JQL"),
        jira_qa_jql=_getenv("JIRA_QA_JQL"),
        jira_exclude_user=_getenv("JIRA_EXCLUDE_USER"),
        run_phase=_getenv("RUN_PHASE"),
        force_date=_getenv("FORCE_DATE"),
        force_run=_getenv_bool("FORCE_RUN", default=False),
        clickup_write_mode=(_getenv("CLICKUP_WRITE_MODE", "comment") or "comment").strip().lower(),
        clickup_owner_id=owner_id,
        clickup_strip_markers_on_close=_getenv_bool("CLICKUP_STRIP_MARKERS_ON_CLOSE", default=False),
        clickup_header_planning_task_id=_getenv("CLICKUP_HEADER_PLANNING_TASK_ID"),
        clickup_header_daily_summary_task_id=_getenv("CLICKUP_HEADER_DAILY_SUMMARY_TASK_ID"),
        clickup_header_final_summary_task_id=_getenv("CLICKUP_HEADER_FINAL_SUMMARY_TASK_ID"),
        clickup_empty_task_template_id=_getenv("CLICKUP_EMPTY_TASK_TEMPLATE_ID"),
    )


