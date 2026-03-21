from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from daily_reporter.app import run
from daily_reporter.config import load_settings
from daily_reporter.runtime import build_run_context


def main() -> int:
    # Local convenience: load .env if present. In Lambda, env vars are injected by the runtime and this is harmless.
    load_dotenv(override=False)

    settings = load_settings()
    ctx = build_run_context(force_date=settings.force_date, run_phase=settings.run_phase)
    result = run(settings, ctx)

    print(f"[ok] phase={result.phase} date={result.today.isoformat()} clickup_task_id={result.clickup_task_id} status={result.clickup_status}")
    if result.clickup_task_url:
        print(f"[ok] task_url={result.clickup_task_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


