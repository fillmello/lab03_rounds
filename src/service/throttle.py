import time
from collections import defaultdict, deque

from fastapi import HTTPException

MAX_FAILURES = 5
WINDOW_SECONDS = 15 * 60

_failures: dict[str, deque[float]] = defaultdict(deque)


def _recent(key: str) -> deque[float]:
    attempts = _failures[key]
    limit = time.monotonic() - WINDOW_SECONDS
    while attempts and attempts[0] < limit:
        attempts.popleft()
    return attempts


def ensure_allowed(key: str) -> None:
    if len(_recent(key)) >= MAX_FAILURES:
        raise HTTPException(status_code=429, detail="Muitas tentativas. Aguarde alguns minutos e tente novamente.")


def register_failure(key: str) -> None:
    _recent(key).append(time.monotonic())


def reset(key: str) -> None:
    _failures.pop(key, None)


def clear_all() -> None:
    _failures.clear()
