"""
File Path: /backend/tests/test_projection_failure_observability.py
Description: No-database tests for bounded Projection failure observability.
Main Features:
    - Verifies first, summary, and recovery events with a controlled clock
    - Ensures repeated failures do not emit one event per tick
    - Proves event fields never expose exception messages or raw identifiers
"""
from __future__ import annotations

import pytest
from sqlalchemy.exc import OperationalError

from projection.failure_observability import ProjectionFailureObserver


pytestmark = pytest.mark.no_db


def _observer(clock, events):
    def capture_event(level: str, event: str, **fields: object) -> None:
        events.append((level, event, fields))

    return ProjectionFailureObserver(clock=lambda: clock[0], event_sink=capture_event)


def test_failure_observer_emits_first_then_one_summary_per_window():
    clock = [0.0]
    events: list[tuple[str, str, dict[str, object]]] = []
    observer = _observer(clock, events)
    failure = RuntimeError("mysql://secret@host/raw_snapshot_id=123")

    observer.record_failure(
        scope="mapping_set:1",
        failure_category="runtime_audit_persistence",
        exc=failure,
    )
    observer.record_failure(
        scope="mapping_set:1",
        failure_category="runtime_audit_persistence",
        exc=failure,
    )
    clock[0] = 60.0
    observer.record_failure(
        scope="mapping_set:1",
        failure_category="runtime_audit_persistence",
        exc=failure,
    )

    assert events == [
        (
            "error",
            "projection_runner_failure_first",
            {
                "failure_scope": "mapping_set:1",
                "failure_category": "runtime_audit_persistence",
                "driver_error_category": "runtime_runtimeerror",
                "driver_error_code": "unknown",
                "window_failure_count": 1,
                "total_failure_count": 1,
            },
        ),
        (
            "error",
            "projection_runner_failure_summary",
            {
                "failure_scope": "mapping_set:1",
                "failure_category": "runtime_audit_persistence",
                "driver_error_category": "runtime_runtimeerror",
                "driver_error_code": "unknown",
                "window_failure_count": 2,
                "total_failure_count": 2,
                "duration_seconds": 60.0,
            },
        ),
    ]

    serialized_fields = repr(events)
    assert "secret" not in serialized_fields
    assert "raw_snapshot_id" not in serialized_fields
    assert "123" not in serialized_fields


def test_failure_observer_emits_recovery_then_treats_a_new_failure_as_first():
    clock = [0.0]
    events: list[tuple[str, str, dict[str, object]]] = []
    observer = _observer(clock, events)
    failure = OSError(2006, "driver message must not be logged")

    observer.record_failure(
        scope="runtime",
        failure_category="runtime_tick",
        exc=failure,
    )
    clock[0] = 5.0
    observer.record_recovery(scope="runtime")
    clock[0] = 6.0
    observer.record_failure(
        scope="runtime",
        failure_category="runtime_tick",
        exc=failure,
    )

    assert [event for _, event, _ in events] == [
        "projection_runner_failure_first",
        "projection_runner_failure_recovered",
        "projection_runner_failure_first",
    ]
    assert events[1][2]["duration_seconds"] == 5.0
    assert events[1][2]["total_failure_count"] == 1
    assert events[0][2]["driver_error_code"] == "2006"


def test_failure_observer_fixture_rebuild_starts_a_new_in_memory_window():
    clock = [0.0]
    first_events: list[tuple[str, str, dict[str, object]]] = []
    second_events: list[tuple[str, str, dict[str, object]]] = []
    failure = RuntimeError("same failure")

    _observer(clock, first_events).record_failure(
        scope="mapping_set:1",
        failure_category="runtime_audit_persistence",
        exc=failure,
    )
    _observer(clock, second_events).record_failure(
        scope="mapping_set:1",
        failure_category="runtime_audit_persistence",
        exc=failure,
    )

    assert [event for _, event, _ in first_events] == ["projection_runner_failure_first"]
    assert [event for _, event, _ in second_events] == ["projection_runner_failure_first"]


def test_failure_observer_classifies_a_dbapi_error_without_sql_or_params():
    clock = [0.0]
    events: list[tuple[str, str, dict[str, object]]] = []
    observer = _observer(clock, events)
    failure = OperationalError(
        "SELECT * FROM passwords WHERE token = :token",
        {"token": "secret-token"},
        OSError(1054, "Unknown column"),
    )

    observer.record_failure(
        scope="mapping_set:1",
        failure_category="runtime_audit_persistence",
        exc=failure,
    )

    fields = events[0][2]
    assert fields["driver_error_category"] == "dbapi_oserror"
    assert fields["driver_error_code"] == "1054"
    assert "SELECT" not in repr(fields)
    assert "secret-token" not in repr(fields)
