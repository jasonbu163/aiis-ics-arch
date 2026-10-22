"""每PLC父FIFO监督owner；有界ready/queue、先持久T2再交单次permit。"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
import time
from field_flow.domain import Failure, identity, require, now_ms, Clock
from field_flow.driver_process import Driver, Gate


@dataclass(frozen=True)
class Sample:
    value: int
    flow_id: str
    request_id: str
    generation: int
    reference: int
    quality: str = "good"
    sampled_at_ms: int = field(default_factory=now_ms)


@dataclass
class Job:
    operation: str
    flow: str
    db: int
    offset: int
    end: float
    result: asyncio.Future
    intent: object = None
    request_id: str = field(default_factory=identity)
    queue_end: float = float("inf")
    prepared: asyncio.Event = field(default_factory=asyncio.Event)
    canceled: bool = False
    claimed: bool = False


class Owner:
    def __init__(self, plc, state, seed=2, barrier=None):
        self.plc, self.state, self.seed, self.barrier = plc, state, seed, barrier
        self.queue = asyncio.Queue(plc.queue_capacity)
        self.ready, self.stopped = asyncio.Event(), asyncio.Event()
        self.gate = Gate(state.directory); state.gates.append(self.gate)
        self.driver, self.generation, self.status = None, 0, "disconnected"
        self.had_forced_driver_stop, self.failed, self.dispatching = False, False, 0
        self.max_inflight = 0
        self.active_flows = set()
        self.write_clock = Clock()
        self.stop_at = None
        self.task = asyncio.create_task(self._loop())

    def snapshot(self):
        return {"state": "blocked" if self.write_clock.invalid else self.status, "clock_invalid": self.write_clock.invalid, "queue_depth": self.queue.qsize(), "in_flight": int(bool(self.driver and self.driver.started and self.dispatching)), "ipc_in_flight": self.dispatching,
                "pid": self.driver.process.pid if self.driver else None, "generation": self.generation}

    async def _event(self, event, **values):
        try:
            await self.state.event(event, target_id=self.plc.id, **values)
        except Failure:
            pass

    async def _pause(self, duration):
        try:
            await asyncio.wait_for(self.stopped.wait(), duration)
        except asyncio.TimeoutError:
            pass

    async def _loop(self):
        failures = 0
        job = None
        try:
            while not self.stopped.is_set():
                if self.driver is None:
                    if failures:
                        await self._pause([.25, .5, 1, 2, 10][min(failures-1, 4)])
                        if failures >= 5:
                            failures = 0
                        if self.stopped.is_set():
                            break
                    self.status = "connecting"; self.generation += 1
                    end = time.monotonic() + self.plc.connect_timeout_ms/1000
                    try:
                        self.driver = await Driver.spawn(self.state, self.plc, self.generation, self.gate, end, self.seed, self.barrier)
                        self.seed = 2
                        self.status = "ready"; self.ready.set()
                    except Failure as exc:
                        if str(exc) == "driver_cleanup_incomplete":
                            self.driver = getattr(exc, "driver", None)
                            self.failed = True; self.status = "blocked"
                            await self.stopped.wait()
                            break
                        failures += 1; self.failed = True
                        self.status = "recovering"
                        await self._event("owner_backoff", attempt=failures, error_key=str(exc))
                        self.had_forced_driver_stop |= getattr(self.state, "had_forced_driver_stop", False)
                        continue
                try:
                    job = await asyncio.wait_for(self.queue.get(), .02)
                except asyncio.TimeoutError:
                    continue
                await job.prepared.wait()
                error, value = None, None
                if self.stopped.is_set() or job.canceled:
                    error = "canceled" if self.stopped.is_set() else "expired"
                elif time.monotonic() >= min(job.end-.4, job.queue_end):
                    error = "expired"
                elif job.intent is not None and not self.state.healthy:
                    error = "canceled"
                else:
                    try:
                        if job.intent:
                            self.write_clock.check()
                            job.intent.validate_time()
                        job.end = min(job.end, time.monotonic()+self.plc.io_timeout_ms/1000)
                        job.claimed = True; self.dispatching = 1
                        value, retire, request_id = await self.driver.call(job.operation, job.flow, job.db, job.offset, job.end, job.intent, job.request_id)
                        self.max_inflight = max(self.max_inflight, int(self.driver.started))
                        if job.operation == "read":
                            value = Sample(value.value, job.flow, request_id, self.generation, value.reference)
                        failures = 0
                        if retire:
                            self.driver = None; self.ready.clear(); self.status = "recovering"
                    except Failure as exc:
                        error = str(exc)
                        if not job.claimed and error in ("input_stale", "clock_invalid"):
                            error = "expired" if error == "input_stale" else "canceled"
                        if error not in ("expired", "canceled"):
                            self.failed = True; self.ready.clear(); self.status = "recovering"
                            await self.driver.close(min(job.end, time.monotonic()+.4))
                            self.had_forced_driver_stop |= self.driver.forced
                            self.driver = None
                            failures += 1
                    finally:
                        self.dispatching = 0
                if not job.result.done():
                    if error:
                        job.result.set_exception(Failure(error))
                    else:
                        job.result.set_result(value)
            self.status = "stopping"
        except Exception:
            self.ready.clear(); self.failed = True; self.status = "blocked"
            if job is not None and not job.result.done():
                job.result.set_exception(Failure("driver_cleanup_incomplete"))
            await self.stopped.wait()
        finally:
            self.ready.clear()
            while not self.queue.empty():
                job = self.queue.get_nowait()
                if not job.result.done():
                    job.result.set_exception(Failure("canceled"))

    async def submit(self, operation, flow, db, offset, intent=None, end=None):
        require(not self.stopped.is_set(), "canceled")
        require(flow not in self.active_flows, "flow_inflight")
        self.active_flows.add(flow)
        job = None
        try:
            ready_end = time.monotonic()+self.plc.ready_wait_ms/1000
            if end is not None:
                ready_end = min(ready_end, end)
            try:
                await asyncio.wait_for(self.ready.wait(), max(.001, ready_end-time.monotonic()))
            except asyncio.TimeoutError:
                raise Failure("owner_unavailable") from None
            end = end or float("inf")
            require(time.monotonic() < end-.4, "expired")
            future = asyncio.get_running_loop().create_future()
            job = Job(operation, flow, db, offset, end, future, intent)
            queue_end = min(end-.4, time.monotonic()+self.plc.queue_wait_ms/1000)
            job.queue_end = queue_end
            try:
                await asyncio.wait_for(self.queue.put(job), max(.001, queue_end-time.monotonic()))
            except asyncio.TimeoutError:
                raise Failure("queue_unavailable") from None
            try:
                if intent:
                    await self.state.dispatch(intent, job.request_id)
            except BaseException:
                job.canceled = True
                # Consume the eventual cancellation exception when a caller leaves before ownership.
                future.add_done_callback(lambda f: f.exception() if not f.cancelled() else None)
                raise Failure("canceled") from None
            finally:
                job.prepared.set()
            # Queue waiting cannot refresh source expiry; owner alone owns an already claimed job.
            try:
                return await asyncio.wait_for(asyncio.shield(future), max(.001, queue_end-time.monotonic()))
            except asyncio.TimeoutError:
                if not job.claimed:
                    job.canceled = True
                    future.add_done_callback(lambda f: f.exception() if not f.cancelled() else None)
                    raise Failure("expired") from None
                return await future
        finally:
            self.active_flows.discard(flow)

    async def read(self, flow, db=1, offset=0):
        return await self.submit("read", flow, db, offset)

    def stop(self):
        if self.stop_at is None:
            self.stop_at = time.monotonic()
        self.stopped.set(); self.gate.close(stopping=True)

    async def close(self, global_end):
        self.stop()
        end = min(global_end, self.stop_at+max(self.plc.connect_timeout_ms, self.plc.io_timeout_ms)/1000)
        try:
            await asyncio.wait_for(asyncio.shield(self.task), max(.001, end-time.monotonic()-.4))
        except asyncio.TimeoutError:
            if self.driver:
                await self.driver.force(end, "owner_stop_deadline")
                self.had_forced_driver_stop = True
            await asyncio.wait_for(asyncio.shield(self.task), max(.001, end-time.monotonic()))
        if self.driver is not None:
            await self.driver.close(end)
            self.had_forced_driver_stop |= self.driver.forced
            self.driver = None
        self.status = "stopped"
        self.gate.dispose()
        return not self.had_forced_driver_stop and not self.failed
