from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests


@dataclass(frozen=True)
class HttpError(Exception):
    status_code: int
    message: str
    url: str
    response_text: str | None = None

    def __str__(self) -> str:
        base = f"HTTP {self.status_code} for {self.url}: {self.message}"
        if self.response_text:
            return f"{base}\n{self.response_text}"
        return base


def _safe_json_dumps(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(obj)


def request_with_retries(
    fn: Callable[[], requests.Response],
    *,
    retries: int = 4,
    base_sleep_s: float = 0.6,
    max_sleep_s: float = 6.0,
    retry_statuses: set[int] | None = None,
) -> requests.Response:
    if retry_statuses is None:
        retry_statuses = {429, 500, 502, 503, 504}

    attempt = 0
    last_exc: Exception | None = None
    while attempt <= retries:
        try:
            resp = fn()
            if resp.status_code in retry_statuses:
                raise HttpError(
                    status_code=resp.status_code,
                    message="retryable status",
                    url=str(resp.url),
                    response_text=resp.text,
                )
            return resp
        except Exception as exc:  # noqa: BLE001 - we want to retry on transient network errors too
            last_exc = exc
            if attempt >= retries:
                raise
            sleep = min(max_sleep_s, base_sleep_s * (2**attempt))
            sleep = sleep * (1.0 + random.random() * 0.35)
            time.sleep(sleep)
            attempt += 1

    # Should be unreachable.
    if last_exc:
        raise last_exc
    raise RuntimeError("request_with_retries: unexpected state")


def raise_for_status(resp: requests.Response, *, context: str) -> None:
    if 200 <= resp.status_code < 300:
        return
    text = None
    try:
        text = resp.text
    except Exception:
        text = None
    raise HttpError(
        status_code=resp.status_code,
        message=context,
        url=str(resp.url),
        response_text=text,
    )


def parse_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Failed to parse JSON from {resp.url}. status={resp.status_code}. body={_safe_json_dumps(resp.text)}"
        ) from exc


