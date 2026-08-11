"""
File Path: /backend/projection/runtime.py
Description: Async FastAPI-lifespan host for the synchronous Projection runner.
Main Features:
    - Runs bounded synchronous batches through an explicit worker-thread boundary
    - Enforces one active runner per Python process
    - Stops future ticks and waits for in-flight database work before shutdown
    - Bounds repeated unhandled tick-failure observations within one process
"""
from __future__ import annotations

import asyncio
import threading
from typing import Protocol

from common.log import log_projection_event
from projection.failure_observability import ProjectionFailureObserver


class ProjectionRunOnce(Protocol):
    """The minimal synchronous runner contract hosted by the lifespan loop."""

    def run_once(self) -> object:
        """Run one bounded projection pass."""


class ProjectionRuntimeAlreadyRunning(RuntimeError):
    """A second Projection runtime was requested in the same process."""


_PROCESS_RUNTIME_GUARD = threading.Lock()


class ProjectionRuntime:
    """Schedule a synchronous Projection runner without blocking the event loop."""

    def __init__(
        self,
        *,
        runner: ProjectionRunOnce,
        interval_seconds: float,
        failure_observer: ProjectionFailureObserver | None = None,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("Projection runtime interval_seconds must be positive")
        self._runner = runner
        self._interval_seconds = interval_seconds
        self._stop_event: asyncio.Event | None = None
        self._task: asyncio.Task[None] | None = None
        self._owns_process_guard = False
        self._failure_observer = failure_observer or ProjectionFailureObserver()

    @property
    def running(self) -> bool:
        """Return whether this runtime currently owns an active loop task."""
        return self._task is not None and not self._task.done()

    def start(self) -> None:
        """Start the loop immediately, rejecting duplicate in-process ownership."""
        if self.running:
            raise ProjectionRuntimeAlreadyRunning("Projection runtime is already running")
        if not _PROCESS_RUNTIME_GUARD.acquire(blocking=False):
            raise ProjectionRuntimeAlreadyRunning(
                "Another Projection runtime is already running in this process"
            )
        self._owns_process_guard = True
        self._stop_event = asyncio.Event()
        try:
            self._task = asyncio.create_task(
                self._run_loop(),
                name="projection-runtime",
            )
            log_projection_event(
                "info",
                "projection_runtime_started",
                interval_seconds=self._interval_seconds,
            )
        except Exception:
            self._release_process_guard()
            raise

    async def stop(self) -> None:
        """Prevent the next tick and wait for the current worker-thread batch."""
        task = self._task
        if task is None:
            return
        stop_event = self._stop_event
        if stop_event is not None:
            stop_event.set()
        await task

    async def _run_loop(self) -> None:
        try:
            while not self._stop_requested():
                try:
                    await asyncio.to_thread(self._runner.run_once)
                    self._failure_observer.record_recovery(scope="runtime")
                except Exception as exc:  # pragma: no cover - runner tests cover handled mapping failures
                    self._failure_observer.record_failure(
                        scope="runtime",
                        failure_category="runtime_tick",
                        exc=exc,
                    )

                if await self._wait_for_stop():
                    return
        finally:
            log_projection_event("info", "projection_runtime_stopped")
            self._release_process_guard()

    async def _wait_for_stop(self) -> bool:
        stop_event = self._stop_event
        if stop_event is None:
            return True
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=self._interval_seconds)
        except TimeoutError:
            return False
        return True

    def _stop_requested(self) -> bool:
        return self._stop_event is None or self._stop_event.is_set()

    def _release_process_guard(self) -> None:
        if self._owns_process_guard:
            self._owns_process_guard = False
            _PROCESS_RUNTIME_GUARD.release()
