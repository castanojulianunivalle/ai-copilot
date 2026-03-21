from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date

from .calendar_utils import business_day_reason, is_business_day_colombia
from .clickup import ClickUpClient, ClickUpTask
from .config import Settings
from .http_utils import HttpError
from .jira import JiraClient, JiraIssue, default_dev_jql, default_qa_jql
from .report_builder import (
    BuiltReport,
    build_daily_summary_section,
    build_final_summary_section,
    build_planning_rows_preserving_rep1,
    build_report_description,
    strip_dr_markers,
)
from .runtime import RunContext, daily_task_title


@dataclass(frozen=True)
class RunResult:
    phase: str
    today: date
    clickup_task_id: str
    clickup_task_url: str | None
    clickup_status: str
    clickup_payload_sent: dict


def _parse_emails(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


def _resolve_clickup_users_by_email(clickup: ClickUpClient, emails: list[str]) -> tuple[list[int], dict[str, str]]:
    """
    Resolve ClickUp user ids and usernames given a list of emails by inspecting team members.
    Returns tuple: (list of user ids, dict mapping email to username)
    """
    if not emails:
        return [], {}

    email_set = {e.lower() for e in emails if e}
    found_ids: dict[str, int] = {}
    found_names: dict[str, str] = {}

    try:
        teams = clickup.get_teams()
    except Exception as exc:  # noqa: BLE001
        print(f"[clickup] Warning: could not fetch teams to resolve followers: {exc}")
        return [], {}

    for team in teams:
        members = team.get("members") or team.get("users") or []
        for m in members:
            user = m.get("user") if isinstance(m, dict) else None
            if user is None and isinstance(m, dict):
                user = m
            if not isinstance(user, dict):
                continue
            email = (user.get("email") or "").strip().lower()
            uid = user.get("id")
            username = user.get("username") or user.get("name") or email.split("@")[0]
            if email and email in email_set and uid is not None:
                try:
                    found_ids[email] = int(uid)
                    found_names[email] = username
                except Exception:
                    continue

    missing = sorted(email_set - set(found_ids.keys()))
    if missing:
        print(f"[clickup] Warning: could not resolve follower ids for emails: {missing}")

    return list(found_ids.values()), found_names


def _resolve_clickup_user_ids_by_email(clickup: ClickUpClient, emails: list[str]) -> list[int]:
    """
    Resolve ClickUp user ids given a list of emails by inspecting team members.
    """
    ids, _ = _resolve_clickup_users_by_email(clickup, emails)
    return ids


def _ensure_followers(clickup: ClickUpClient, task_id: str, follower_ids: list[int]) -> None:
    """
    Ensure the given follower_ids are set on the task.
    """
    if not follower_ids:
        return
    try:
        clickup.update_task(task_id=task_id, followers=[int(fid) for fid in follower_ids])
        print(f"[clickup] Ensured followers on task {task_id}: {follower_ids}")
    except Exception as exc:  # noqa: BLE001
        print(f"[clickup] Warning: failed to set followers on task {task_id}: {exc}")


def _run_merge_strategy(
    *,
    clickup: ClickUpClient,
    settings: Settings,
    ctx: RunContext,
    task: ClickUpTask,
    dev_fe: list[JiraIssue],
    dev_be: list[JiraIssue],
    qa: list[JiraIssue],
    me_id: int | None,
    follower_names: dict[str, str] | None = None,
) -> None:
    """
    Execute merge strategy: create small content tasks, duplicate header tasks,
    merge content into duplicated headers, then merge all into target task.
    """
    # Map section names to header task IDs from settings
    section_to_header_task: dict[str, str] = {}
    if settings.clickup_header_planning_task_id:
        section_to_header_task["Planning"] = settings.clickup_header_planning_task_id
    if settings.clickup_header_daily_summary_task_id:
        section_to_header_task["Daily Summary"] = settings.clickup_header_daily_summary_task_id
    if settings.clickup_header_final_summary_task_id:
        section_to_header_task["Final Summary"] = settings.clickup_header_final_summary_task_id

    if not section_to_header_task:
        raise RuntimeError(
            "Merge strategy requires at least one header task ID. "
            "Set CLICKUP_HEADER_PLANNING_TASK_ID, CLICKUP_HEADER_DAILY_SUMMARY_TASK_ID, "
            "and/or CLICKUP_HEADER_FINAL_SUMMARY_TASK_ID"
        )

    print("[clickup] Using merge strategy to update task")
    print(f"[clickup] Header tasks configured: {list(section_to_header_task.keys())}")

    # Build sections
    issues_all = dev_fe + dev_be + qa
    sections: list[tuple[str, str]] = []

    # Planning section
    if "Planning" in section_to_header_task:
        # For report2 in merge mode, build both reports using current state
        # (we cleared the description above, so no need to extract existing Rep #1)
        existing_by_key: dict[str, tuple[str, str, str]] = {}
        if ctx.phase == "report2":
            # For report2, use current Jira state for both report1 and report2
            # (both will show the same state since we don't have historical data)
            # Pass empty existing_by_key so it builds from scratch
            existing_by_key = {}
            print("[clickup] Building Planning section for report2: will use current Jira state for both reports")
        elif ctx.phase == "close":
            # For close, try to extract existing Rep #1 from task
            try:
                current_task = clickup.get_task(task.id)
                current_description = current_task.markdown_description or current_task.description or ""
                if current_description:
                    existing_by_key = _extract_rep1_from_merged_tables(current_description, issues_all)
                    print(f"[clickup] Extracted Rep #1 data for {len(existing_by_key)} issues from existing task")
            except Exception as e:
                print(f"[clickup] Warning: Could not extract Rep #1 data from existing task: {e}")
                existing_by_key = {}

        planning_content = build_planning_rows_preserving_rep1(
            today=ctx.today,
            phase=ctx.phase,
            issues=issues_all,
            existing_rows_by_key=existing_by_key,
            for_merge=True,
        )
        if planning_content and planning_content.strip():
            sections.append(("Planning", planning_content))
            print(f"[clickup] Built Planning section: {len(planning_content)} chars")

    # Daily Summary section
    if "Daily Summary" in section_to_header_task:
        summary_content = build_daily_summary_section(today=ctx.today, issues_all=issues_all, for_merge=True)
        if summary_content and summary_content.strip():
            sections.append(("Daily Summary", summary_content))
            print(f"[clickup] Built Daily Summary section: {len(summary_content)} chars")

    # Final Summary section (include for all phases in merge strategy)
    if "Final Summary" in section_to_header_task:
        # Get JIRA client for comments (we need to access it from settings)
        from .jira import JiraClient
        jira_client = JiraClient(
            base_url=settings.jira_base_url,
            email=settings.jira_email,
            api_token=settings.jira_api_token,
        )
        final_content = build_final_summary_section(
            when_local=ctx.now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
            issues_all=issues_all,
            today=ctx.today,
            jira_client=jira_client,
            for_merge=True,
            qa_issues=qa,
            follower_names=follower_names,
        )
        if final_content and final_content.strip():
            sections.append(("Final Summary", final_content))
            print(f"[clickup] Built Final Summary section: {len(final_content)} chars")

    if not sections:
        raise RuntimeError("No sections were built for merge strategy")

    print(f"[clickup] Total sections to merge: {len(sections)}")

    # Step 1: Create small tasks with dynamic content only
    print("[clickup] [STEP 1] Creating content tasks...")
    content_task_ids: list[tuple[str, str]] = []
    # me_id is already passed as parameter from run() function

    for section_name, content in sections:
        task_name = f"[CONTENT] {section_name} - {ctx.today.isoformat()}"
        try:
            # In merge mode, duplicate from empty task template (assigned to token owner) then update with content
            if settings.clickup_empty_task_template_id:
                print(f"[clickup] Duplicating content task from empty template {settings.clickup_empty_task_template_id}")
                temp_task = clickup.copy_task_to_list(
                    template_task_id=settings.clickup_empty_task_template_id,
                    list_id=settings.clickup_list_id,
                    new_name=task_name,
                )
                # Update the duplicated task with name (ensure it's correct), content, and status
                # Note: Content tasks should NOT be assigned to anyone per user request
                clickup.update_task(
                    task_id=temp_task.id,
                    name=task_name,  # Ensure name is correct
                    description=content,
                    status="Report #1",
                    assignees=[],  # Remove all assignees (empty list removes assignments)
                )
                print(f"[clickup] Duplicated and updated content task: {temp_task.id} ({section_name}), removed all assignees")
            else:
                # Fallback: create new task if no template configured
                temp_task = clickup.create_task(
                    list_id=settings.clickup_list_id,
                    name=task_name,
                    description=content,
                    status="Report #1",
                )
                print(f"[clickup] Created content task: {temp_task.id} ({section_name})")
            # Content tasks inherit assignment from template (assigned to token owner)
            content_task_ids.append((section_name, temp_task.id))
        except Exception as e:
            print(f"[clickup] Failed to create content task for {section_name}: {e}")
            raise

    # Step 2: Duplicate header tasks and merge content into copies
    print("[clickup] [STEP 2] Duplicating header tasks and merging content...")
    header_task_ids: list[str] = []

    for section_name, content_task_id in content_task_ids:
        if section_name not in section_to_header_task:
            print(f"[clickup] Warning: No header task ID for {section_name}, skipping")
            continue

        original_header_task_id = section_to_header_task[section_name]
        try:
            # Get original header task
            original_header_task = clickup.get_task(original_header_task_id)
            print(f"[clickup] Found header task: {original_header_task_id} ({section_name})")

            # Check for existing duplicate header tasks from previous runs (same day)
            duplicate_name = f"[{ctx.today.isoformat()}] {section_name} - {original_header_task.name}"
            existing_duplicates = clickup.list_tasks_find_by_pattern(
                list_id=settings.clickup_list_id,
                name_pattern=f"[{ctx.today.isoformat()}] {section_name}",
            )
            # Filter to exact matches and delete them
            for existing_task in existing_duplicates:
                if existing_task.name == duplicate_name:
                    try:
                        clickup.delete_task(existing_task.id)
                        print(f"[clickup] Deleted previous duplicate header task: {existing_task.id} ({existing_task.name})")
                    except Exception as exc:
                        print(f"[clickup] Warning: Failed to delete previous duplicate {existing_task.id}: {exc}")

            # Duplicate the header task (should maintain assignments from original)
            duplicate_header_task = clickup.copy_task_to_list(
                template_task_id=original_header_task_id,
                list_id=settings.clickup_list_id,
                new_name=duplicate_name,
            )
            print(f"[clickup] Duplicated header task: {duplicate_header_task.id}")

            # Merge content task into duplicate header task
            # Note: The duplicate header task should already be assigned to the user (from original)
            clickup.merge_tasks(
                target_task_id=duplicate_header_task.id,
                source_task_ids=[content_task_id],
            )
            print(f"[clickup] Merged content into duplicate header task")
            
            # Ensure duplicate header task maintains assignment after merge
            # (merge might have removed assignments if source task had none)
            if me_id is not None:
                import time
                time.sleep(0.5)  # Brief wait for merge to process
                clickup.update_task(task_id=duplicate_header_task.id, assignees=[me_id])
                print(f"[clickup] Ensured duplicate header task {duplicate_header_task.id} is assigned to user_id={me_id}")

            header_task_ids.append(duplicate_header_task.id)
        except Exception as e:
            print(f"[clickup] Failed to process header task for {section_name}: {e}")
            raise

    if not header_task_ids:
        raise RuntimeError("No header tasks were created. Cannot proceed with final merge.")

    # Step 3: Merge all duplicated header tasks into target task
    # Note: Header tasks duplicated from original headers should already be assigned to the user.
    # The merge operation will preserve assignees from the merged tasks, so the target task
    # should automatically be assigned to the user after merge.
    print(f"[clickup] [STEP 3] Merging {len(header_task_ids)} header tasks into target task...")
    try:
        # Store target task ID to ensure we reference the correct task
        target_task_id = task.id
        print(f"[clickup] Target task ID for merge: {target_task_id}")
        
        # Clear target task description first to avoid duplicate content
        # We'll replace it with empty content, then merge will add the merged content
        clickup.update_task(task_id=target_task_id, description="")
        print("[clickup] Cleared target task description before merge")
        
        # Perform the merge - header tasks are already assigned to user, so target will inherit assignment
        clickup.merge_tasks(
            target_task_id=target_task_id,
            source_task_ids=header_task_ids,
        )
        print("[clickup] Final merge completed successfully!")
        
        # Ensure task name is correct (merge might have changed it)
        import time
        time.sleep(1.0)  # Brief wait for merge to process
        title = daily_task_title(ctx.today, phase=ctx.phase)
        clickup.update_task(task_id=target_task_id, name=title)
        print(f"[clickup] Updated target task name to: {title}")
    except Exception as e:
        print(f"[clickup] Failed to merge header tasks into target: {e}")
        raise


def run(settings: Settings, ctx: RunContext) -> RunResult:
    if not settings.force_run:
        if not is_business_day_colombia(ctx.today):
            reason = business_day_reason(ctx.today) or "Non-business day"
            print(f"[skip] {ctx.today.isoformat()} is not a business day in Colombia: {reason}")
            raise SystemExit(0)

    jira = JiraClient(base_url=settings.jira_base_url, email=settings.jira_email, api_token=settings.jira_api_token)
    dev_jql = (settings.jira_dev_jql or "").strip() or default_dev_jql(ctx.today)
    qa_jql = (settings.jira_qa_jql or "").strip() or default_qa_jql(ctx.today)

    print(f"[jira] Fetching issues. dev_jql={dev_jql!r} qa_jql={qa_jql!r}")
    dev_fe = jira.board_issues(board_id=settings.jira_dev_frontend_board_id, jql=dev_jql)
    dev_be = jira.board_issues(board_id=settings.jira_dev_backend_board_id, jql=dev_jql)
    qa = jira.board_issues(board_id=settings.jira_qa_board_id, jql=qa_jql)
    print(f"[jira] Got issues: dev_fe={len(dev_fe)} dev_be={len(dev_be)} qa={len(qa)}")

    clickup = ClickUpClient(token=settings.clickup_token)
    # In merge mode, always use the authorized user from token (not CLICKUP_OWNER_ID)
    # to ensure tasks are assigned to the token owner
    me_id: int | None = None
    try:
        me = clickup.get_authorized_user()
        user = me.get("user") or {}
        me_id = int(user.get("id")) if user.get("id") is not None else None
        print(f"[clickup] Resolved authorized user id from token: {me_id}")
    except Exception as exc:  # noqa: BLE001
        print(f"[clickup] Failed to resolve authorized user id: {exc}")
    # Fallback to CLICKUP_OWNER_ID only if we can't get it from token
    if me_id is None:
        me_id = settings.clickup_owner_id

    follower_emails = _parse_emails(os.getenv("LOW_LOAD_MENTION_USERS"))
    follower_ids, follower_names = _resolve_clickup_users_by_email(clickup, follower_emails)

    mode = (settings.clickup_write_mode or "comment").strip().lower()
    if mode not in {"comment", "description", "merge"}:
        mode = "comment"

    # For close phase: find and close both AM and PM tasks
    if ctx.phase == "close" and mode == "merge":
        title_am = daily_task_title(ctx.today, phase="report1")
        title_pm = daily_task_title(ctx.today, phase="report2")
        task_am = clickup.list_tasks_find_by_name(list_id=settings.clickup_list_id, task_name=title_am)
        task_pm = clickup.list_tasks_find_by_name(list_id=settings.clickup_list_id, task_name=title_pm)
        
        # Close AM task if exists
        if task_am:
            print(f"[clickup] Closing AM task: {task_am.id} ({task_am.url})")
            _ensure_followers(clickup, task_am.id, follower_ids)
            try:
                clickup.update_task(task_id=task_am.id, status="Closed")
                print("[clickup] AM task status updated to Closed")
            except HttpError as exc:
                print(f"[clickup] Failed to close AM task: {exc}")
        
        # Close PM task if exists
        if task_pm:
            print(f"[clickup] Closing PM task: {task_pm.id} ({task_pm.url})")
            _ensure_followers(clickup, task_pm.id, follower_ids)
            try:
                clickup.update_task(task_id=task_pm.id, status="Closed")
                print("[clickup] PM task status updated to Closed")
            except HttpError as exc:
                print(f"[clickup] Failed to close PM task: {exc}")
            # Return using PM task as primary
            return RunResult(
                phase=ctx.phase,
                today=ctx.today,
                clickup_task_id=task_pm.id if task_pm else (task_am.id if task_am else ""),
                clickup_task_url=task_pm.url if task_pm else (task_am.url if task_am else None),
                clickup_status="Closed",
                clickup_payload_sent={"status": "Closed", "mode": "merge"},
            )
        elif task_am:
            return RunResult(
                phase=ctx.phase,
                today=ctx.today,
                clickup_task_id=task_am.id,
                clickup_task_url=task_am.url,
                clickup_status="Closed",
                clickup_payload_sent={"status": "Closed", "mode": "merge"},
            )
        else:
            print("[clickup] Warning: No AM or PM task found to close")
            raise RuntimeError("No task found to close")
    
    # For report1 and report2: use phase-specific title (AM/PM)
    title = daily_task_title(ctx.today, phase=ctx.phase)
    existing = clickup.list_tasks_find_by_name(list_id=settings.clickup_list_id, task_name=title)
    
    if existing:
        task = existing
        print(f"[clickup] Found existing daily task: {task.id} ({task.url})")
    else:
        # In merge mode, duplicate from empty task template (assigned to token owner)
        if mode == "merge":
            if settings.clickup_empty_task_template_id:
                print(f"[clickup] Daily task not found. Duplicating from empty task template {settings.clickup_empty_task_template_id} for merge mode")
                task = clickup.copy_task_to_list(
                    template_task_id=settings.clickup_empty_task_template_id,
                    list_id=settings.clickup_list_id,
                    new_name=title,
                )
                # Update name explicitly (in case copy didn't use new_name correctly) and ensure assignment
                if me_id is not None:
                    clickup.update_task(task_id=task.id, name=title, assignees=[me_id])
                    print(f"[clickup] Duplicated empty task: {task.id}, updated name and assigned to user_id={me_id}")
                else:
                    clickup.update_task(task_id=task.id, name=title)
                    print(f"[clickup] Duplicated empty task: {task.id}, updated name (could not assign: me_id is None)")
            else:
                print(f"[clickup] Daily task not found. Creating empty task for merge mode (no CLICKUP_EMPTY_TASK_TEMPLATE_ID configured)")
                task = clickup.create_task(
                    list_id=settings.clickup_list_id,
                    name=title,
                    description="",  # Empty task for merge strategy
                    status=None,
                )
                # Assign to owner immediately
                if me_id is not None:
                    try:
                        clickup.update_task(task_id=task.id, assignees=[me_id])
                        print(f"[clickup] Assigned empty task to user_id={me_id}")
                    except HttpError as exc:
                        print(f"[clickup] Failed to assign empty task. err={exc}")
        else:
            # Non-merge mode: use template
            if settings.clickup_task_template_id:
                print(
                    f"[clickup] Daily task not found. Creating from TASK TEMPLATE {settings.clickup_task_template_id} into list {settings.clickup_list_id}"
                )
                task = clickup.create_task_from_template(
                    list_id=settings.clickup_list_id,
                    task_template_id=settings.clickup_task_template_id,
                    new_name=title,
                    assignees=[me_id] if me_id is not None else None,
                )
            elif settings.clickup_template_task_id:
                print(
                    f"[clickup] Daily task not found. Copying task {settings.clickup_template_task_id} into list {settings.clickup_list_id}"
                )
                task = clickup.copy_task_to_list(
                    template_task_id=settings.clickup_template_task_id,
                    list_id=settings.clickup_list_id,
                    new_name=title,
                )
            else:
                raise RuntimeError(
                    "No ClickUp template configured. Set CLICKUP_TASK_TEMPLATE_ID (preferred) or CLICKUP_TEMPLATE_TASK_ID."
                )
            print(f"[clickup] Created daily task: {task.id} ({task.url})")

        # Ensure the daily task is assigned ONLY to us (remove template default assignees).
        # This also prevents notifying the template's default assignee (if the API respects assignees override).
        if me_id is not None:
            try:
                clickup.update_task(task_id=task.id, assignees=[me_id])
                print(f"[clickup] Forced assignee to user_id={me_id}")
            except HttpError as exc:
                print(f"[clickup] Failed to force assignee. err={exc}")
        
        # Ensure followers are added immediately after task creation
        if follower_ids:
            _ensure_followers(clickup, task.id, follower_ids)

    # Merge strategy: create small tasks and merge into header tasks
    if mode == "merge":
        _run_merge_strategy(
            clickup=clickup,
            settings=settings,
            ctx=ctx,
            task=task,
            dev_fe=dev_fe,
            dev_be=dev_be,
            qa=qa,
            me_id=me_id,
            follower_names=follower_names,
        )
    else:
        # Standard approach: build report and update description or post as comment
        # Use the current daily task description as the base (keeps ClickUp's rich formatting from the template copy).
        # If for any reason it is empty (rare), fall back to the template description.
        daily_task_fresh = clickup.get_task(task.id)
        base_description = daily_task_fresh.markdown_description or daily_task_fresh.description or ""
        if not base_description:
            # Fallback only if legacy template task id exists.
            if settings.clickup_template_task_id:
                template_task = clickup.get_task(settings.clickup_template_task_id)
                base_description = template_task.markdown_description or template_task.description or ""
        
        built: BuiltReport = build_report_description(
            phase=ctx.phase,
            today=ctx.today,
            when_local=ctx.now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
            base_description=base_description,
            dev_frontend=dev_fe,
            dev_backend=dev_be,
            qa=qa,
            follower_names=follower_names,
        )

        payload = {"name": title, "markdown_description": built.description, "status": built.clickup_status}
        print("[clickup] Updating task with payload:")
        print(json.dumps(payload, ensure_ascii=False)[:4000])
        print(f"[clickup] markdown_content_length={len(built.description or '')}")

        def _post_comment() -> None:
            print("[clickup] Posting report as a task comment (preserves template formatting).")
            clickup.create_task_comment(task_id=task.id, comment_text=built.report_body, notify_all=False)

        if mode == "comment":
            _post_comment()
        else:
            # Try updating description, but fall back to comment on ClickUp internal errors.
            try:
                final_desc = built.description
                if ctx.phase == "close" and settings.clickup_strip_markers_on_close:
                    final_desc = strip_dr_markers(final_desc)
                clickup.update_task(task_id=task.id, name=title, description=final_desc)
            except HttpError as exc:
                print(f"[clickup] Description update failed, falling back to comment. err={exc}")
                _post_comment()

    # Ensure followers (Manual + Moises) are added to the daily task.
    _ensure_followers(clickup, task.id, follower_ids)

    # Always attempt status transition separately.
    try:
        # Get status from built report (for standard mode) or determine from phase (for merge mode)
        if mode == "merge":
            status_map = {"report1": "Report #1", "report2": "Report #2", "close": "Closed"}
            clickup_status = status_map.get(ctx.phase, "Report #1")
        else:
            clickup_status = built.clickup_status
        clickup.update_task(task_id=task.id, status=clickup_status)
    except HttpError as exc:
        print(f"[clickup] Status update failed: err={exc}")
        raise
    # Build payload for result (use appropriate status)
    if mode == "merge":
        status_map = {"report1": "Report #1", "report2": "Report #2", "close": "Closed"}
        clickup_status = status_map.get(ctx.phase, "Report #1")
        payload = {"name": title, "status": clickup_status, "mode": "merge"}
    else:
        clickup_status = built.clickup_status
        payload = {"name": title, "markdown_description": built.description, "status": built.clickup_status}

    return RunResult(
        phase=ctx.phase,
        today=ctx.today,
        clickup_task_id=task.id,
        clickup_task_url=task.url,
        clickup_status=clickup_status,
        clickup_payload_sent=payload,
    )


def _extract_rep1_from_merged_tables(description: str, issues: list[JiraIssue]) -> dict[str, tuple[str, str, str]]:
    """
    Extract Rep #1 content from merged task description.
    The merged description contains individual tables per issue in this format:
    
    | **Issue Link** – 📝 | **Status Rep. #1** – 🛠️ | **Status Rep. #2** – |
    | :--- | :--- | :--- |
    | [ISSUE-KEY](url)<br>Assignee<br>`date` `est` | 🛠️ **Status** | |
    
    Returns dict: {ISSUE_KEY: (issue_cell, rep1_cell, rep2_cell)}
    """
    import re

    result: dict[str, tuple[str, str, str]] = {}
    
    # Split description into lines
    lines = description.splitlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for table header row (contains "Issue Link" and "Status Rep")
        if "**Issue Link**" in line and "**Status Rep. #1**" in line and "**Status Rep. #2**" in line:
            # Next line should be separator (| :--- | ...)
            if i + 1 < len(lines) and "| :---" in lines[i + 1]:
                # Next line should be data row
                if i + 2 < len(lines):
                    data_line = lines[i + 2].strip()
                    if data_line.startswith("|") and data_line.endswith("|"):
                        # Parse the data row
                        parts = [p.strip() for p in data_line.strip("|").split("|")]
                        if len(parts) >= 3:
                            issue_cell, rep1_cell, rep2_cell = parts[0], parts[1], parts[2]
                            
                            # Extract issue key from issue_cell
                            # Format: [Summary](url) where url contains /browse/ISSUE-KEY
                            issue_key = None
                            
                            # First, try to extract from URL in markdown link: [text](url)
                            url_match = re.search(r'\]\(([^)]+)\)', issue_cell)
                            if url_match:
                                url = url_match.group(1)
                                # Extract issue key from URL (format: .../browse/ISSUE-KEY)
                                browse_match = re.search(r'/browse/([A-Z0-9-]+)', url)
                                if browse_match:
                                    potential_key = browse_match.group(1)
                                    # Verify it's in our issues list
                                    if any(issue.key == potential_key for issue in issues):
                                        issue_key = potential_key
                            
                            # Fallback: try to find issue key directly in cell text
                            if not issue_key:
                                for issue in issues:
                                    if issue.key in issue_cell:
                                        issue_key = issue.key
                                        break
                            
                            # Last resort: try to extract from markdown link text
                            if not issue_key:
                                match = re.search(r'\[([A-Z0-9-]+)\]', issue_cell)
                                if match:
                                    potential_key = match.group(1)
                                    # Verify it's actually an issue key from our list
                                    if any(issue.key == potential_key for issue in issues):
                                        issue_key = potential_key
                            
                            if issue_key:
                                result[issue_key] = (issue_cell, rep1_cell, rep2_cell)
                                print(f"[clickup] Extracted Rep #1 for {issue_key}: {rep1_cell[:50]}...")
            
            # Skip separator and data row
            i += 3
        else:
            i += 1
    
    return result


