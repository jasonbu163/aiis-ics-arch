"""
File Path: /backend/tests/test_projection_runtime.py
Description: B6.4 FastAPI lifespan Projection runtime tests.
Main Features:
    - Keeps synchronous runner work outside the event loop
    - Enforces one in-process runtime and graceful stop semantics
    - Verifies testing applications do not start a background runner by default
"""
from __future__ import annotations

import asyncio
import threading

import pytest

import core.registrar as registrar
from core.registrar import create_app
from projection.failure_observability import ProjectionFailureObserver
from projection.runtime import ProjectionRuntime, ProjectionRuntimeAlreadyRunning
from settings import Settings


pytestmark = pytest.mark.no_db


class _ImmediateRunner:
    def __init__(self) -> None:
        self.call_count = 0
        self.called = threading.Event()

    def run_once(self) -> None:
        self.call_count += 1
        self.called.set()


class _BlockingRunner:
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()

    def run_once(self) -> None:
        self.started.set()
        self.release.wait(timeout=2)


class _FailingRunner:
    def __init__(self) -> None:
        self.called = threading.Event()

    def run_once(self) -> None:
        self.called.set()
        raise OSError(2006, "driver message must not be logged")


class _FakeLifespanRuntime:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True


class _FailingSchemaEngine:
    def begin(self):
        raise AssertionError("API lifespan must not open a schema-writing connection")


@pytest.mark.asyncio
async def test_runtime_runs_sync_runner_once_and_stops_without_a_follow_up_tick():
    runner = _ImmediateRunner()
    runtime = ProjectionRuntime(runner=runner, interval_seconds=60)

    runtime.start()
    await asyncio.to_thread(runner.called.wait, 1)
    await runtime.stop()

    assert runner.call_count == 1
    assert runtime.running is False


@pytest.mark.asyncio
async def test_runtime_emits_immediate_shared_channel_lifecycle_events(monkeypatch):
    runner = _ImmediateRunner()
    events: list[tuple[str, str, dict[str, object]]] = []

    def capture_event(level: str, event: str, **fields: object) -> None:
        events.append((level, event, fields))

    monkeypatch.setattr("projection.runtime.log_projection_event", capture_event)
    runtime = ProjectionRuntime(runner=runner, interval_seconds=60)

    runtime.start()
    await asyncio.to_thread(runner.called.wait, 1)
    await runtime.stop()

    assert events == [
        ("info", "projection_runtime_started", {"interval_seconds": 60}),
        ("info", "projection_runtime_stopped", {}),
    ]


@pytest.mark.asyncio
async def test_runtime_routes_repeated_tick_failures_through_the_failure_observer():
    runner = _FailingRunner()
    events: list[tuple[str, str, dict[str, object]]] = []

    def capture_event(level: str, event: str, **fields: object) -> None:
        events.append((level, event, fields))

    observer = ProjectionFailureObserver(event_sink=capture_event)
    runtime = ProjectionRuntime(
        runner=runner,
        interval_seconds=60,
        failure_observer=observer,
    )

    runtime.start()
    await asyncio.to_thread(runner.called.wait, 1)
    await runtime.stop()

    assert events == [
        (
            "error",
            "projection_runner_failure_first",
            {
                "failure_scope": "runtime",
                "failure_category": "runtime_tick",
                "driver_error_category": "runtime_oserror",
                "driver_error_code": "2006",
                "window_failure_count": 1,
                "total_failure_count": 1,
            },
        )
    ]


@pytest.mark.asyncio
async def test_runtime_rejects_a_second_in_process_runner_until_the_first_stops():
    first_runner = _ImmediateRunner()
    first = ProjectionRuntime(runner=first_runner, interval_seconds=60)
    second = ProjectionRuntime(runner=_ImmediateRunner(), interval_seconds=60)

    first.start()
    await asyncio.to_thread(first_runner.called.wait, 1)
    with pytest.raises(ProjectionRuntimeAlreadyRunning):
        second.start()

    await first.stop()
    second.start()
    await second.stop()


@pytest.mark.asyncio
async def test_runtime_stop_waits_for_the_inflight_thread_before_returning():
    runner = _BlockingRunner()
    runtime = ProjectionRuntime(runner=runner, interval_seconds=60)

    runtime.start()
    await asyncio.to_thread(runner.started.wait, 1)
    stop_task = asyncio.create_task(runtime.stop())
    await asyncio.sleep(0)
    assert stop_task.done() is False

    runner.release.set()
    await stop_task
    assert runtime.running is False


def test_testing_application_keeps_projection_runtime_disabled_by_default():
    app = create_app(testing=True)

    assert app.state.projection_runtime_enabled is False


def test_projection_runner_setting_defaults_disabled_for_multi_worker_servers():
    assert Settings.model_fields["PROJECTION_RUNNER_ENABLED"].default is False


@pytest.mark.asyncio
async def test_lifespan_starts_and_stops_the_injected_runtime_when_explicitly_enabled(monkeypatch):
    app = create_app(testing=True)
    app.state.projection_runtime_enabled = True
    fake_runtime = _FakeLifespanRuntime()

    monkeypatch.setattr(registrar, "build_projection_runtime", lambda _: fake_runtime)

    async def fake_cleanup() -> None:
        return None

    monkeypatch.setattr(registrar, "cleanup", fake_cleanup)

    async with registrar.lifespan(app):
        assert fake_runtime.started is True
        assert app.state.projection_runtime is fake_runtime

    assert fake_runtime.stopped is True


@pytest.mark.asyncio
async def test_lifespan_non_testing_startup_does_not_create_or_repair_schema(monkeypatch):
    app = create_app(testing=False)
    app.state.projection_runtime_enabled = False

    monkeypatch.setattr(registrar, "async_engine", _FailingSchemaEngine())

    async def fake_cleanup() -> None:
        return None

    monkeypatch.setattr(registrar, "cleanup", fake_cleanup)

    async with registrar.lifespan(app):
        assert app.state.projection_runtime is None
