from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

try:
    import boto3
    from botocore.exceptions import ClientError
except Exception:  # noqa: BLE001
    boto3 = None
    ClientError = Exception  # type: ignore[assignment]
from .jira import JiraIssue


AUTO_START = ""
AUTO_END = ""

# Marker-based template slots (recommended)
PLANNING_START = ""
PLANNING_END = ""
SUMMARY_START = ""
SUMMARY_END = ""
REP1_START = ""
REP1_END = ""
REP2_START = ""
REP2_END = ""
FINAL_START = ""
FINAL_END = ""


@dataclass(frozen=True)
class BuiltReport:
    description: str
    clickup_status: str  # Report #1 | Report #2 | Closed
    report_body: str  # content to post as a comment (markdown/plain)


def _format_hours(seconds: int | None) -> float:
    if not seconds:
        return 0.0
    return round(seconds / 3600.0, 2)


def _format_estimate_short(seconds: int | None) -> str:
    """Format estimate as short string: 30m, 1h, 2h, etc."""
    if not seconds:
        return ""
    hours = seconds / 3600.0
    if hours < 1:
        minutes = round(seconds / 60.0)
        return f"{minutes}m"
    if hours == int(hours):
        return f"{int(hours)}h"
    return f"{round(hours, 1)}h"


def _format_estimate_hours_from_story_points(story_points: float | None) -> str:
    """
    Format estimate as hours based on story points ONLY.
    Each story point = 30 minutes = 0.5 hours.
    Returns format: 2h (lowercase)
    """
    if story_points is None or story_points <= 0:
        return ""
    
    # Calculate from story points: 1 point = 30 minutes = 0.5 hours
    hours = story_points * 0.5
    
    if hours <= 0:
        return ""
    
    # Round to nearest integer for hours format
    hours_int = round(hours)
    if hours_int == 0 and hours > 0:
        hours_int = 1  # At least 1h if there's any time
    return f"{hours_int}h" if hours_int > 0 else ""


def _is_overdue(issue: JiraIssue, today: date) -> bool:
    return issue.due_date is not None and issue.due_date < today


def _status_symbol(issue: JiraIssue, today: date) -> str:
    """
    Map Jira status to icon.
    - "confirmed" -> Not started (⏳)
    - "qa review"/"qa-review-testing" -> Pending review (📝)
    - "blocked"/similar -> Stalled (🛑)
    - "done"/"promoted"/"qa-approved": count as Accepted (✅) only if updated today
    - Default: In progress (🛠️) else Not started (⏳)
    """
    s = (issue.status or "").lower()

    if "confirmed" in s:
        return "⏳"

    # Pending review
    if any(
        x in s
        for x in [
            "qa review",
            "qa-review",
            "qa-review-testing",
            "pending review",
            "code review",
            "review",
            "pr",
        ]
    ):
        return "📝"

    if any(x in s for x in ["blocked", "stalled", "on hold", "imped", "halt"]):
        return "🛑"

    # Accepted only if the transition happened today (based on updated date)
    def _updated_today() -> bool:
        if not issue.updated:
            return False
        try:
            return issue.updated.date() == today
        except Exception:
            return False

    if any(x in s for x in ["qa-approved", "qa approved", "promoted", "done", "accepted", "closed", "released", "qa passed", "resolved"]):
        if _updated_today():
            return "✅"
        # If not updated today, treat as in progress (so it doesn't count as Accepted today)
        return "🛠️"

    if any(x in s for x in ["in progress", "doing", "development", "dev", "implement", "testing"]):
        return "🛠️"

    return "⏳"


def _status_label(symbol: str) -> str:
    return {
        "⏳": "Not started",
        "🛠️": "In progress",
        "🛑": "Stalled",
        "📝": "Pending review",
        "✅": "Accepted",
    }.get(symbol, "Not started")


def _format_issue_block(issue: JiraIssue, *, today: date, phase: str) -> str:
    """
    Format a single issue in the Planning & Execution section.
    Format matches the template: Issue Link section with Status Rep columns.
    """
    initial_symbol = _status_symbol(issue, today)
    overdue_mark = " 🕒" if _is_overdue(issue, today) else ""
    created_date = issue.created.date().isoformat() if issue.created else ""
    est_short = _format_estimate_short(issue.original_estimate_seconds)
    assignee = issue.assignee or "Unassigned"
    
    # Format matches template:
    # Issue Link –{symbol}
    # [Issue Title]
    # Assignee
    # YYYY-MM-DD{est}
    # 
    # Status Rep. #1 –{symbol}{overdue}
    # 
    # Status Rep. #2 – 
    parts = []
    parts.append(f"Issue Link –{initial_symbol}{overdue_mark}")
    url = (issue.url or "").replace("https:://", "https://").replace("http:://", "http://")
    parts.append(f"[{issue.key}]({url}) {issue.summary}")
    parts.append(assignee)
    # Format date+estimate together: "2025-12-0330m" or "2025-12-031h"
    date_est = f"{created_date}{est_short}" if created_date and est_short else (created_date or "")
    parts.append(date_est + "  " if date_est else "")
    parts.append("")
    
    # Status Rep columns based on phase (we write the current snapshot symbol)
    current_symbol = _status_symbol(issue, today)
    current_overdue = " 🕒" if _is_overdue(issue, today) else ""
    
    if phase in ("report1", "report2", "close"):
        parts.append(f"Status Rep. #1 –{current_symbol}{current_overdue}")
        parts.append("")
        parts.append("")
    else:
        parts.append("Status Rep. #1 –")
        parts.append("")
    
    parts.append("Status Rep. #2 – ")
    parts.append("")
    parts.append("")
    
    return "\n".join(parts)


def _planning_table_row(issue: JiraIssue, *, today: date, phase: str) -> str:
    """
    Returns ONE markdown table row with 3 columns:
      Issue Link | Status Rep. #1 | Status Rep. #2

    This is meant to be inserted inside a pre-existing table in your template,
    between DR markers (dynamic number of rows).
    """
    symbol = _status_symbol(issue, today)
    overdue_mark = " 🕒" if _is_overdue(issue, today) else ""
    url = (issue.url or "").replace("https:://", "https://").replace("http:://", "http://")

    created_date = issue.created.date().isoformat() if issue.created else ""
    est_short = _format_estimate_short(issue.original_estimate_seconds)
    owner = issue.assignee or "Unassigned"
    meta = " ".join(x for x in [created_date, est_short] if x).strip()

    issue_cell = (
        f"**Issue Link –**{symbol}{overdue_mark}<br>"
        f"[{issue.key}]({url}) {issue.summary}<br>"
        f"{owner}<br>"
        f"{meta}"
    )

    # For now we keep rep cells as "current snapshot" for the run phase.
    rep1_cell = f"**Status Rep. #1 –**{symbol}{overdue_mark}"
    rep2_cell = "**Status Rep. #2 –**"
    if phase in {"report2", "close"}:
        rep2_cell = f"**Status Rep. #2 –**{symbol}{overdue_mark}"

    return f"| {issue_cell} | {rep1_cell} | {rep2_cell} |"


def _group_by_assignee(issues: Iterable[JiraIssue]) -> dict[str, list[JiraIssue]]:
    out: dict[str, list[JiraIssue]] = {}
    for i in issues:
        key = i.assignee or "Unassigned"
        out.setdefault(key, []).append(i)
    return out


def build_planning_execution_section(
    *,
    today: date,
    phase: str,
    dev_frontend: list[JiraIssue],
    dev_backend: list[JiraIssue],
    qa: list[JiraIssue],
) -> str:
    """
    Build Planning & Execution section matching the template format.
    Each issue has: Issue Link section, Status Rep #1, Status Rep #2 columns.
    """
    parts: list[str] = []
    # IMPORTANT: Do NOT rebuild the instructional / styled header from scratch.
    # This function should only generate the "issues content" that gets inserted into the template markers.
    all_issues = dev_frontend + dev_backend + qa
    if not all_issues:
        return "(No issues found for this run)\n"

    # We return table rows (1 per issue) so the template can keep its table header/format.
    for issue in sorted(all_issues, key=lambda x: (x.assignee or "Unassigned", x.key)):
        parts.append(_planning_table_row(issue, today=today, phase=phase))

    return "\n".join(parts).rstrip() + "\n"


def _extract_between(text: str, start_marker: str, end_marker: str) -> str | None:
    if start_marker not in text or end_marker not in text:
        return None
    _, rest = text.split(start_marker, 1)
    mid, _ = rest.split(end_marker, 1)
    return mid.strip("\n")


def _parse_planning_rows(rows_text: str) -> dict[str, tuple[str, str, str]]:
    """
    Parse existing 3-col markdown table rows:
      | issue_cell | rep1_cell | rep2_cell |
    Returns {ISSUE_KEY: (issue_cell, rep1_cell, rep2_cell)}
    """
    out: dict[str, tuple[str, str, str]] = {}
    if not rows_text:
        return out

    for line in rows_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        parts = [p.strip() for p in s.strip("|").split("|")]
        if len(parts) < 3:
            continue
        issue_cell, rep1_cell, rep2_cell = parts[0], parts[1], parts[2]
        # Extract key from markdown link inside issue_cell (we generate: [KEY](url) ...)
        key = None
        if "[" in issue_cell and "](" in issue_cell:
            try:
                key = issue_cell.split("[", 1)[1].split("](", 1)[0].strip()
            except Exception:
                key = None
        if key:
            out[key] = (issue_cell, rep1_cell, rep2_cell)
    return out


def build_planning_rows_preserving_rep1(
    *,
    today: date,
    phase: str,
    issues: list[JiraIssue],
    existing_rows_by_key: dict[str, tuple[str, str, str]],
    for_merge: bool = False,
) -> str:
    """
    Builds Planning & Execution section with individual tables per issue.
    Each issue gets its own table with headers, matching the example format.
    - report1: initializes Rep #1 snapshot, keeps Rep #2 empty
    - report2/close: preserves Rep #1 exactly as-is (if present), updates Rep #2 snapshot
    If for_merge is True, omits any title/header text (header tasks already have it).
    """
    lines: list[str] = []
    sorted_issues = sorted(issues, key=lambda x: (x.assignee or "Unassigned", x.key))
    
    for issue in sorted_issues:
        symbol = _status_symbol(issue, today)
        overdue = _is_overdue(issue, today)
        overdue_mark = " 🕒" if overdue else ""
        url = (issue.url or "").replace("https:://", "https://").replace("http:://", "http://")
        created_date = issue.created.date().isoformat() if issue.created else ""
        est_short = _format_estimate_short(issue.original_estimate_seconds)
        owner = issue.assignee or "Unassigned"
        
        # Determine header icon based on issue type (Story = 📝, others = 🛠️)
        issue_type_lower = (issue.issue_type or "").lower()
        if "story" in issue_type_lower:
            header_icon = "📝"
        else:
            header_icon = "🛠️"
        
        # Build Issue Link cell content (using <br> for line breaks)
        # Format: [Summary](url)<br>Owner<br>YYYY-MM-DD - Xh (date + hours estimate based ONLY on story_points)
        # Calculate hours ONLY from story_points (1 point = 30 min = 0.5h), NOT from original_estimate_seconds
        issue_cell_parts = [
            f"[{issue.summary}]({url})",
            owner,
        ]
        # Combine date and hours estimate with space and dash separator
        # Use story_points ONLY (not original_estimate_seconds)
        est_hours = _format_estimate_hours_from_story_points(issue.story_points)
        
        if created_date:
            if est_hours:
                # Format: 2025-11-19 - 2h
                issue_cell_parts.append(f"{created_date} - {est_hours}")
            else:
                issue_cell_parts.append(created_date)
        elif est_hours:
            # Only hours, no date
            issue_cell_parts.append(est_hours)
        
        issue_cell = "<br>".join(issue_cell_parts)
        
        # Build Status Rep. #1 cell content (use mapped status label, not raw status)
        status_label = _status_label(symbol)
        rep1_status_symbol = symbol
        rep1_overdue_mark = " 🕒" if overdue else ""
        
        if phase == "report1":
            rep1_cell = f"{rep1_status_symbol}{rep1_overdue_mark} **{status_label}**"
            rep2_cell = ""  # Empty for report1
        else:
            # For report2/close: check if we should preserve existing Rep #1 or use current state
            if existing_rows_by_key and issue.key in existing_rows_by_key:
                # Extract just the content part (remove any prefix if present)
                existing_rep1 = existing_rows_by_key[issue.key][1]
                # Remove common prefixes and check if it contains status label or raw status
                for prefix in ["**Status Rep. #1 –**", "**Status Rep. #1** –"]:
                    if prefix in existing_rep1:
                        existing_rep1 = existing_rep1.replace(prefix, "").strip()
                # If existing content looks valid, use it; otherwise use current state
                if existing_rep1 and any(x in existing_rep1 for x in ["**", status_label]):
                    rep1_cell = existing_rep1
                else:
                    # Use current state if existing doesn't look right
                    rep1_cell = f"{rep1_status_symbol}{rep1_overdue_mark} **{status_label}**"
            else:
                # No existing data or rebuilding from scratch: use current state for both reports
                rep1_cell = f"{rep1_status_symbol}{rep1_overdue_mark} **{status_label}**"
            
            # Build Status Rep. #2 cell (always use current state)
            rep2_status_symbol = symbol
            rep2_overdue_mark = " 🕒" if overdue else ""
            rep2_cell = f"{rep2_status_symbol}{rep2_overdue_mark} **{status_label}**"
        
        # Build header row with overdue icon in header if needed
        header_overdue = " 🕒" if overdue else ""
        
        # Each issue gets its own table with headers (matching the example format)
        # Headers include icons and overdue mark
        lines.append(f"| **Issue Link** – {header_icon}{header_overdue} | **Status Rep. #1** – {symbol}{header_overdue} | **Status Rep. #2** – |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(f"| {issue_cell} | {rep1_cell} | {rep2_cell} |")
        lines.append("")  # Empty line between tables

    return "\n".join(lines).rstrip() + "\n"


def _get_status_counts(issues: list[JiraIssue], today: date) -> str:
    """Returns: Pending / Review / Done (e.g., 2/0/1) using status symbols."""
    pending = review = done = 0
    for issue in issues:
        sym = _status_symbol(issue, today)
        if sym == "✅":
            done += 1
        elif sym == "📝":
            review += 1
        else:
            pending += 1
    return f"{pending}/{review}/{done}"


def _get_blocker_counts(issues: list[JiraIssue], today: date) -> str:
    """Returns: Overdue / Stalled (e.g., 1/0)"""
    overdue = stalled = 0
    for issue in issues:
        is_done = (issue.status or "").lower() in ["done", "accepted", "closed", "resolved"]
        if issue.due_date and issue.due_date < today and not is_done:
            overdue += 1
        if _status_symbol(issue, today) == "🛑":
            stalled += 1
    return f"{overdue}/{stalled}"


def _load_last_low_load_date(bucket: str | None, key: str | None) -> date | None:
    if not bucket or not key:
        return None
    if boto3 is None:
        return None
    try:
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj.get("Body")
        if not body:
            return None
        data = json.loads(body.read().decode("utf-8"))
        last = data.get("last_date")
        return date.fromisoformat(last) if last else None
    except ClientError as exc:
        # Most likely NoSuchKey on first run; ignore gracefully
        if exc.response["Error"]["Code"] not in {"NoSuchKey", "AccessDenied", "404"}:
            print(f"[low_load] Failed to load state from s3://{bucket}/{key}: {exc}")
        return None
    except Exception as exc:  # noqa: BLE001
        print(f"[low_load] Unexpected error reading state: {exc}")
        return None


def _save_last_low_load_date(bucket: str | None, key: str | None, today: date) -> None:
    if not bucket or not key:
        return
    if boto3 is None:
        return
    try:
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps({"last_date": today.isoformat()}),
            ContentType="application/json",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[low_load] Failed to persist state to s3://{bucket}/{key}: {exc}")


def _build_low_load_notice(today: date, issues_all: list[JiraIssue], qa_issues: list[JiraIssue] | None = None, follower_names: dict[str, str] | None = None) -> str:
    """
    If total non-QA workload (team-wide) is below the minimum, emit a notice tagging reviewers,
    but only every other day (skip if last notice was yesterday).
    Workload is based solely on story points: 1 point = 0.5h.
    """
    min_hours_raw = os.getenv("LOW_LOAD_MIN_HOURS", "6")
    try:
        min_hours = float(min_hours_raw)
    except ValueError:
        min_hours = 6.0

    # Build mentions using follower names if available, otherwise use emails
    mentions_raw = os.getenv("LOW_LOAD_MENTION_USERS", "manual@unlimitech.cloud,moises@unlimitech.cloud")
    mention_emails = [m.strip().lower() for m in mentions_raw.split(",") if m.strip()]
    
    # Use ClickUp mention format: @[Username]
    mention_parts = []
    if follower_names:
        for email in mention_emails:
            username = follower_names.get(email)
            if username:
                mention_parts.append(f"@[{username}]")
            else:
                # Fallback to email if username not found
                mention_parts.append(f"@{email}")
    else:
        # Fallback: use emails if no names available
        mention_parts = [f"@{email}" for email in mention_emails]
    
    mention_text = " ".join(mention_parts) if mention_parts else ""

    bucket = os.getenv("STATE_BUCKET")
    key = os.getenv("STATE_KEY", "state/low_load.json")

    qa_set = {i.key for i in (qa_issues or [])}
    non_qa_issues = [i for i in issues_all if i.key not in qa_set]

    total_hours = sum((issue.story_points or 0) * 0.5 for issue in non_qa_issues)

    # If team (non-QA) has enough load, skip notice
    if total_hours >= min_hours:
        return ""

    last_date = _load_last_low_load_date(bucket, key)
    if last_date:
        delta_days = (today - last_date).days
        # If we already posted yesterday, skip today. Post again if 2+ days passed.
        if delta_days < 2:
            print(f"[low_load] Skipping notice (last sent {last_date}, {delta_days} days ago)")
            return ""

    # Persist state and build message
    _save_last_low_load_date(bucket, key, today)
    lines = [
        "⚠️ Capacidad baja detectada: necesitamos más tareas asignadas.",
    ]
    if mention_text:
        lines.append(f"Por favor revisar y asignar más tareas. {mention_text}")
    return "\n".join(lines)


def _format_time_summary(seconds: int | None) -> str:
    """Format estimate as short string for summary: 0h, 1h, 2.5h, etc."""
    if not seconds:
        return "0h"
    hours = seconds / 3600.0
    if hours == int(hours):
        return f"{int(hours)}h"
    return f"{hours:.1f}h"


def build_daily_summary_section(*, today: date, issues_all: list[JiraIssue], for_merge: bool = False) -> str:
    """
    Build Daily Summary table with real developer names from JIRA issues.
    Format matches the example with headers using <br><sub> for subheaders.
    If for_merge is True, omits the title and table headers (header task already has them).
    """
    from collections import defaultdict

    dev_stats: dict[str, list[JiraIssue]] = defaultdict(list)
    for issue in issues_all:
        assignee = issue.assignee if issue.assignee else "Unassigned"
        if assignee != "Unassigned":  # Skip unassigned issues in summary
            dev_stats[assignee].append(issue)

    # Build table with headers matching the example format
    # Always include table headers (merge or not), only omit title in merge mode
    md = "" if for_merge else "## 📊 Daily Summary\n\n"
    # ClickUp doesn't render <sub> tags, so use simple text with line breaks
    # Header has 6 columns: Developer | Daily (Issues/Workload) | Rep1 Status | Rep1 Blockers | Rep2 Status | Rep2 Blockers
    md += "| Developer | Daily<br>Issues / Workload | Status Rep. #1<br>⏳ / 📝 / ✅ | Status Rep. #1<br>🕒 / 🛑 | Status Rep. #2<br>⏳ / 📝 / ✅ | Status Rep. #2<br>🕒 / 🛑 |\n"
    # Alignment row: 6 columns matching header and data rows
    md += "| :--- | :---: | :---: | :---: | :---: | :---: |\n"

    for developer, issues in sorted(dev_stats.items()):
        # 1. General data - separate Issues and Workload into two columns
        total = len(issues)

        # Workload: compute ONLY from story points (1 point = 0.5h)
        total_hours = sum((issue.story_points or 0) * 0.5 for issue in issues)
        if total_hours <= 0:
            workload = "0h"
        elif total_hours == int(total_hours):
            workload = f"{int(total_hours)}h"
        else:
            workload = f"{total_hours:.1f}h"

        # 2. Report #1 data (calculated with current state)
        rep1_counts = _get_status_counts(issues, today)
        rep1_blockers = _get_blocker_counts(issues, today)

        # 3. Report #2 data 
        # For report1 phase: initialized to 0
        # For report2 phase: use current state (same as rep1) since we're rebuilding from scratch
        if True:  # Always use current state for report2 in merge mode
            rep2_counts = _get_status_counts(issues, today)
            rep2_blockers = _get_blocker_counts(issues, today)
        else:
            rep2_counts = "0/0/0"
            rep2_blockers = "0/0"

        # Build row with 7 columns: Developer | Issues | Workload | Rep1 Status | Rep1 Blockers | Rep2 Status | Rep2 Blockers
        # Note: The header shows "Daily<br><sub>Issues / Workload</sub>" as one column, but data has Issues and Workload as separate columns
        # Combine Issues and Workload in a single column to match template formatting
        daily_cell = f"{total} / {workload}"
        row = f"| **{developer}** | {daily_cell} | {rep1_counts} | {rep1_blockers} | {rep2_counts} | {rep2_blockers} |\n"
        md += row

    if not dev_stats:
        md += "| - | - | 0/0/0 | 0/0 | 0/0/0 | 0/0 |\n"

    return md


def _replace_between(text: str, start_marker: str, end_marker: str, replacement: str) -> tuple[str, bool]:
    if start_marker not in text or end_marker not in text:
        return text, False
    pre, rest = text.split(start_marker, 1)
    _, post = rest.split(end_marker, 1)
    new_text = (
        pre.rstrip()
        + "\n"
        + start_marker
        + "\n"
        + replacement.rstrip()
        + "\n"
        + end_marker
        + "\n"
        + post.lstrip()
    )
    return new_text, True


def strip_dr_markers(text: str) -> str:
    """
    Removes DR markers from a final description (useful for 'close' after the last update).
    """
    markers = [
        PLANNING_START,
        PLANNING_END,
        SUMMARY_START,
        SUMMARY_END,
        REP1_START,
        REP1_END,
        REP2_START,
        REP2_END,
        FINAL_START,
        FINAL_END,
    ]
    out = text
    for m in markers:
        out = out.replace(m, "")
    return out


def build_status_rep_section(*, rep_number: int, when_local: str, today: date, issues_all: list[JiraIssue]) -> str:
    parts: list[str] = []
    parts.append(f"## Status Rep. #{rep_number}\n")
    parts.append(f"- Run time (Colombia): **{when_local}**\n")
    parts.append(f"- Total items tracked: **{len(issues_all)}**\n")
    parts.append("\n")
    # Minimal delta logic could be added later; for now we snapshot current state.
    parts.append("### Snapshot\n")
    grouped = _group_by_assignee(issues_all)
    for owner in sorted(grouped.keys()):
        parts.append(f"**{owner}**\n")
        for issue in sorted(grouped[owner], key=lambda x: (x.status or "", x.key)):
            symbol = _status_symbol(issue)
            overdue = " 🕒" if _is_overdue(issue, today) else ""
            parts.append(f"- {symbol}{overdue} [{issue.key}]({issue.url}) — {_status_label(symbol)} — {issue.summary}")
        parts.append("\n")
    return "\n".join(parts).rstrip() + "\n"


def build_final_summary_section(
    *,
    when_local: str,
    issues_all: list[JiraIssue],
    qa_issues: list[JiraIssue] | None,
    today: date,
    jira_client=None,
    for_merge: bool = False,
    follower_names: dict[str, str] | None = None,
) -> str:
    parts: list[str] = []
    if not for_merge:
        parts.append("## Final Summary\n")
        parts.append(f"- Close time (Colombia): **{when_local}**\n")
        parts.append("\n")

    accepted = [i for i in issues_all if _status_symbol(i, today) == "✅"]
    pending_review = [i for i in issues_all if _status_symbol(i, today) == "📝"]
    stalled = [i for i in issues_all if _status_symbol(i, today) == "🛑"]
    overdue = [i for i in issues_all if _is_overdue(i, today)]

    parts.append(f"- Results: **{len(accepted)} accepted**, **{len(pending_review)} pending review**, **{len(stalled)} stalled**\n")
    if overdue:
        parts.append(f"- Overdue items: **{len(overdue)}** (see 🕒 marks above)\n")
    parts.append("\n")

    # Low-load notice (every other day, based on story points)
    notice = _build_low_load_notice(today, issues_all, qa_issues or [], follower_names=follower_names or {})
    if notice:
        parts.append("### Capacity / Staffing\n")
        parts.append(f"- {notice}\n")
        parts.append("\n")
    
    parts.append("### Blockers / Need Support\n")
    if stalled:
        for i in stalled:
            parts.append(f"- 🛑 [{i.key}]({i.url}) — {i.summary} (Owner: {i.assignee or 'Unassigned'})")
    else:
        parts.append("- (No blockers detected)\n")
    parts.append("\n")
    
    # Add comments from JIRA issues created today
    if jira_client:
        parts.append("### Comments from Today\n")
        comments_found = False
        for issue in issues_all:
            # Get comments from today only
            comments = jira_client.get_issue_comments(issue.key, since_date=today)
            if comments:
                comments_found = True
                for comment in comments:
                    import re
                    body = comment.get("body", "")
                    # Body should already be extracted as plain text, but remove any remaining HTML
                    if isinstance(body, str):
                        body = re.sub(r'<[^>]+>', '', body)
                        body = body.strip()
                        if body:
                            author = comment.get("author", "Unknown")
                            created = comment.get("created")
                            time_str = created.strftime("%H:%M") if created else ""
                            parts.append(f"- **[{issue.key}]({issue.url})** ({author}, {time_str}): {body[:200]}{'...' if len(body) > 200 else ''}\n")
        
        if not comments_found:
            parts.append("- (No comments found for today)\n")
        parts.append("\n")
    
    parts.append("### After-hours work\n")
    parts.append("- (Auto: not detected yet; add manual notes here if needed)\n")
    return "\n".join(parts).rstrip() + "\n"


def upsert_auto_block(base_description: str, auto_block: str) -> str:
    base = base_description or ""
    if AUTO_START in base and AUTO_END in base:
        pre = base.split(AUTO_START, 1)[0]
        post = base.split(AUTO_END, 1)[1]
        return (pre.rstrip() + "\n\n" + AUTO_START + "\n" + auto_block.rstrip() + "\n" + AUTO_END + "\n\n" + post.lstrip()).rstrip() + "\n"

    # No markers, append.
    glue = "\n\n" if base.strip() else ""
    return (base.rstrip() + glue + AUTO_START + "\n" + auto_block.rstrip() + "\n" + AUTO_END + "\n").rstrip() + "\n"


def build_report_description(
    *,
    phase: str,
    today: date,
    when_local: str,
    base_description: str,
    dev_frontend: list[JiraIssue],
    dev_backend: list[JiraIssue],
    qa: list[JiraIssue],
    follower_names: dict[str, str] | None = None,
) -> BuiltReport:
    issues_all = dev_frontend + dev_backend + qa

    # If template markers exist, we can preserve Rep #1 values from previous runs by parsing existing rows.
    existing_planning_rows = _extract_between(base_description or "", PLANNING_START, PLANNING_END) or ""
    existing_by_key = _parse_planning_rows(existing_planning_rows)
    planning_issues = build_planning_rows_preserving_rep1(
        today=today,
        phase=phase,
        issues=issues_all,
        existing_rows_by_key=existing_by_key,
    )
    summary_rows = build_daily_summary_section(today=today, issues_all=issues_all)

    blocks: list[str] = []
    blocks.append(f"# Daily Report Auto Block ({today.isoformat()})\n")
    blocks.append("## Planning & Execution (auto)\n")
    blocks.append(planning_issues)
    blocks.append("## Daily Summary (auto)\n")
    blocks.append(summary_rows)

    if phase == "report1":
        rep1 = build_status_rep_section(rep_number=1, when_local=when_local, today=today, issues_all=issues_all)
        clickup_status = "Report #1"
    elif phase == "report2":
        rep2 = build_status_rep_section(rep_number=2, when_local=when_local, today=today, issues_all=issues_all)
        clickup_status = "Report #2"
    elif phase == "close":
        final = build_final_summary_section(
            when_local=when_local,
            issues_all=issues_all,
            qa_issues=qa,
            today=today,
            follower_names=follower_names or {},
        )
        clickup_status = "Closed"
    else:
        raise ValueError("Invalid phase")

    base = base_description or ""
    # Build a standalone report body (for comments / logging), regardless of marker support.
    report_parts: list[str] = []
    report_parts.append(f"# Daily Report ({today.isoformat()})")
    report_parts.append("## Planning & Execution")
    report_parts.append(planning_issues.rstrip())
    report_parts.append("## Daily Summary")
    report_parts.append(summary_rows.rstrip())
    if phase == "report1":
        report_parts.append(rep1.rstrip())  # type: ignore[name-defined]
    elif phase == "report2":
        report_parts.append(rep2.rstrip())  # type: ignore[name-defined]
    elif phase == "close":
        report_parts.append(final.rstrip())  # type: ignore[name-defined]
    report_body = "\n\n".join(p for p in report_parts if p.strip()).rstrip() + "\n"

    # 1) Preferred path: update marked slots in the existing template-derived description.
    updated_any = False
    base, ok = _replace_between(base, PLANNING_START, PLANNING_END, planning_issues)
    updated_any = updated_any or ok

    base, ok = _replace_between(base, SUMMARY_START, SUMMARY_END, summary_rows)
    updated_any = updated_any or ok

    if phase == "report1":
        base, ok = _replace_between(base, REP1_START, REP1_END, rep1)  # type: ignore[name-defined]
        updated_any = updated_any or ok
    elif phase == "report2":
        base, ok = _replace_between(base, REP2_START, REP2_END, rep2)  # type: ignore[name-defined]
        updated_any = updated_any or ok
    elif phase == "close":
        base, ok = _replace_between(base, FINAL_START, FINAL_END, final)  # type: ignore[name-defined]
        updated_any = updated_any or ok

    # 2) Fallback: if no markers exist, append/update a dedicated auto block (won't match template styling).
    if not updated_any:
        auto_block = "\n".join(b.rstrip() for b in blocks if b.strip())
        base = upsert_auto_block(base, auto_block)

    new_description = base.rstrip() + "\n"
    return BuiltReport(description=new_description, clickup_status=clickup_status, report_body=report_body)