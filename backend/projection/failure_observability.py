"""
File Path: /backend/projection/failure_observability.py
Description: In-process bounded observability for persistent Projection failures.
Main Features:
    - Emits first, fixed-window summary, and recovery JSON Lines events
    - Keeps failure state private to one Python process and never reads or writes databases
    - Classifies driver failures without logging exception messages or payloads
"""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.exc import DBAPIError

from common.log import log_projection_event


FAILURE_SUMMARY_WINDOW_SECONDS = 60.0


@dataclass(frozen=True)
class _FailureIdentity:
    """Low-cardinality, non-persistent identity for one active failure."""

    scope: str
    failure_category: str
    driver_error_category: str
    driver_error_code: str


@dataclass
class _ActiveFailure:
    """Private counters for one failure identity within the current process."""

    first_seen_at: float
    window_started_at: float
    window_failure_count: int = 1
    total_failure_count: int = 1


class ProjectionFailureObserver:
    """Bound repeated Projection failure events without changing runtime behavior."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.monotonic,
        event_sink: Callable[..., None] = log_projection_event,
    ) -> None:
        self._clock = clock
        self._event_sink = event_sink
        self._active_failures: dict[_FailureIdentity, _ActiveFailure] = {}

    def record_failure(
        self,
        *,
        scope: str,
        failure_category: str,
        exc: BaseException,
    ) -> None:
        """Emit a first event or bounded summary for a repeated safe failure."""
        driver_error_category, driver_error_code = _safe_driver_details(exc)
        identity = _FailureIdentity(
            scope=scope,
            failure_category=failure_category,
            driver_error_category=driver_error_category,
            driver_error_code=driver_error_code,
        )
        now = self._clock()
        active_failure = self._active_failures.get(identity)
        if active_failure is None:
            active_failure = _ActiveFailure(
                first_seen_at=now,
                window_started_at=now,
            )
            self._active_failures[identity] = active_failure
            self._event_sink(
                "error",
                "projection_runner_failure_first",
                **self._event_fields(identity),
                window_failure_count=active_failure.window_failure_count,
                total_failure_count=active_failure.total_failure_count,
            )
            return

        if now - active_failure.window_started_at >= FAILURE_SUMMARY_WINDOW_SECONDS:
            self._event_sink(
                "error",
                "projection_runner_failure_summary",
                **self._event_fields(identity),
                window_failure_count=active_failure.window_failure_count,
                total_failure_count=active_failure.total_failure_count,
                duration_seconds=self._duration_seconds(now, active_failure.first_seen_at),
            )
            active_failure.window_started_at = now
            active_failure.window_failure_count = 1
            active_failure.total_failure_count += 1
            return

        active_failure.window_failure_count += 1
        active_failure.total_failure_count += 1

    def record_recovery(self, *, scope: str) -> None:
        """Emit and clear each active failure that a successful scope resolves."""
        now = self._clock()
        recovered_identities = [
            identity for identity in self._active_failures if identity.scope == scope
        ]
        for identity in recovered_identities:
            active_failure = self._active_failures.pop(identity)
            self._event_sink(
                "info",
                "projection_runner_failure_recovered",
                **self._event_fields(identity),
                window_failure_count=active_failure.window_failure_count,
                total_failure_count=active_failure.total_failure_count,
                duration_seconds=self._duration_seconds(now, active_failure.first_seen_at),
            )

    @staticmethod
    def _event_fields(identity: _FailureIdentity) -> dict[str, str]:
        return {
            "failure_scope": identity.scope,
            "failure_category": identity.failure_category,
            "driver_error_category": identity.driver_error_category,
            "driver_error_code": identity.driver_error_code,
        }

    @staticmethod
    def _duration_seconds(now: float, started_at: float) -> float:
        return round(max(now - started_at, 0.0), 3)


def _safe_driver_details(exc: BaseException) -> tuple[str, str]:
    """Return only a driver category and numeric code, never exception text."""
    driver_exception = _get_driver_exception(exc)
    error_code = _get_numeric_error_code(driver_exception)
    if isinstance(exc, DBAPIError):
        return f"dbapi_{type(driver_exception).__name__.lower()}", error_code
    return f"runtime_{type(driver_exception).__name__.lower()}", error_code


def _get_driver_exception(exc: BaseException) -> BaseException:
    """Prefer the SQLAlchemy driver cause while retaining a safe exception type."""
    current: BaseException = exc
    visited: set[int] = set()
    while id(current) not in visited:
        visited.add(id(current))
        if isinstance(current, DBAPIError) and isinstance(current.orig, BaseException):
            return current.orig
        if current.__cause__ is None:
            return current
        current = current.__cause__
    return exc


def _get_numeric_error_code(exc: BaseException) -> str:
    """Extract a safe numeric driver code without exposing driver message text."""
    errno = getattr(exc, "errno", None)
    if isinstance(errno, int):
        return str(errno)
    for value in getattr(exc, "args", ()):
        if isinstance(value, int):
            return str(value)
        if isinstance(value, str) and value.isdecimal():
            return value
    return "unknown"
