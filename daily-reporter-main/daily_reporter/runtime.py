from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo


BOGOTA_TZ = ZoneInfo("America/Bogota")


@dataclass(frozen=True)
class RunContext:
    today: date
    now_local: datetime
    phase: str  # report1 | report2 | close


def _phase_from_time(now_local: datetime) -> str:
    """
    Colombia schedule:
    - 11:00 => report1
    - 14:00 => report2
    - 18:00 => close

    If invoked between windows, choose the last window reached.
    """
    t = now_local.timetz()
    if t >= time(18, 0, tzinfo=BOGOTA_TZ):
        return "close"
    if t >= time(14, 0, tzinfo=BOGOTA_TZ):
        return "report2"
    return "report1"


def build_run_context(*, force_date: str | None = None, run_phase: str | None = None) -> RunContext:
    now_local = datetime.now(tz=BOGOTA_TZ)
    if force_date:
        y, m, d = (int(x) for x in force_date.split("-"))
        today = date(y, m, d)
        # Keep now_local for logs, but set its date to forced date for stable phase calc
        now_local = now_local.replace(year=y, month=m, day=d)
    else:
        today = now_local.date()

    phase = (run_phase or "").strip().lower() or _phase_from_time(now_local)
    if phase not in {"report1", "report2", "close"}:
        raise ValueError("RUN_PHASE must be one of: report1 | report2 | close")
    return RunContext(today=today, now_local=now_local, phase=phase)


def daily_task_title(d: date, phase: str | None = None) -> str:
    """
    Build the daily task title. Adds AM/PM suffix for report phases to keep both tasks.
    - report1 -> AM
    - report2 -> PM
    - close/None -> no suffix (legacy/default)
    """
    base = f"[{d.isoformat()}] Daily Development Team Report"
    if phase == "report1":
        return f"{base} AM"
    if phase == "report2":
        return f"{base} PM"
    return base


