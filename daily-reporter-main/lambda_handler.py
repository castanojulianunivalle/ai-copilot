from __future__ import annotations

import json
from typing import Any

from dotenv import load_dotenv

from daily_reporter.app import run
from daily_reporter.config import load_settings
from daily_reporter.runtime import build_run_context


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    AWS Lambda entrypoint.

    Event payload supports:
    - phase: report1 | report2 | close (optional)
    - force_date: YYYY-MM-DD (optional)
    - force_run: true/false (optional)
    """
    # In Lambda we don't normally have a .env, but this keeps behavior consistent for tests.
    load_dotenv(override=False)

    if event:
        if "phase" in event and event["phase"]:
            # Allow overriding RUN_PHASE via event for manual invocations
            import os

            os.environ["RUN_PHASE"] = str(event["phase"])
        if "force_date" in event and event["force_date"]:
            import os

            os.environ["FORCE_DATE"] = str(event["force_date"])
        if "force_run" in event and event["force_run"] is not None:
            import os

            os.environ["FORCE_RUN"] = "true" if bool(event["force_run"]) else "false"

    settings = load_settings()
    ctx = build_run_context(force_date=settings.force_date, run_phase=settings.run_phase)
    result = run(settings, ctx)

    out = {
        "ok": True,
        "phase": result.phase,
        "date": result.today.isoformat(),
        "clickup_task_id": result.clickup_task_id,
        "clickup_task_url": result.clickup_task_url,
        "clickup_status": result.clickup_status,
        "clickup_payload_sent": result.clickup_payload_sent,
    }
    print(json.dumps(out, ensure_ascii=False)[:4000])
    return out


# AWS default name is lambda_handler.lambda_handler, but we expose `handler` explicitly.
lambda_handler = handler


