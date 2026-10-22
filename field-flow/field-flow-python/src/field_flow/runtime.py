"""异步独立flow监督、每PLC持久owner及单global shutdown截止。"""
import asyncio
import time
from field_flow.app import demo01
from field_flow.domain import Clock, Failure, now_ms, require
from field_flow.infrastructure.http import HttpClient
from field_flow.infrastructure.state import State
from field_flow.owner import Owner
from field_flow.services.execution import Execution


class Runtime:
    @classmethod
    async def open(cls, config, directory, mode, start_flows=True):
        self = cls(); self.config = config
        self.state = await State.open(directory, mode, config.instance_id)
        self.http = HttpClient(config.http)
        self.stop = asyncio.Event()
        self.owners = {p.id: Owner(p, self.state) for p in config.plcs}
        self.flows = {}
        self.tasks = []
        if start_flows:
            self.tasks = [asyncio.create_task(self._flow(f)) for f in config.flows]
        self.health_task = asyncio.create_task(self._health())
        return self

    async def _flow(self, flow):
        plc = next(p for p in self.config.plcs if p.id == flow.target.plc_id)
        execution = Execution(self.state, self.owners[plc.id], Clock())
        health = {"state": "starting", "last_iteration_ms": None, "last_success_ms": None,
                  "consecutive_errors": 0, "iterations": 0, "in_flight": 0, "max_in_flight": 0}
        self.flows[flow.id] = health
        permanent = None
        while not self.stop.is_set():
            old_state = health["state"]
            try:
                if permanent:
                    raise Failure(permanent)
                health["in_flight"] = 1; health["max_in_flight"] = max(health["max_in_flight"], 1)
                result = await demo01.once(self.http, flow, plc, execution)
                health.update(state="running", consecutive_errors=0, last_success_ms=now_ms(), result=result)
            except Failure as exc:
                key = str(exc)
                if key in ("identity_conflict", "clock_invalid"):
                    permanent = key
                blocked = key in ("target_unknown", "identity_conflict", "clock_invalid", "audit_unhealthy", "capacity_paused")
                health.update(state="blocked" if blocked else "recovering", result=key,
                              consecutive_errors=health["consecutive_errors"]+1)
            finally:
                health["in_flight"] = 0; health["iterations"] += 1; health["last_iteration_ms"] = now_ms()
            if not self.state.healthy:
                health["state"] = "blocked"
            if old_state != health["state"]:
                try:
                    await self.state.event("flow_health", flow_id=flow.id, old=old_state, new=health["state"], result=health.get("result", ""))
                except Failure:
                    pass
            try:
                await asyncio.wait_for(self.stop.wait(), flow.interval_ms/1000)
            except asyncio.TimeoutError:
                pass
        health["state"] = "stopped"

    async def snapshot(self):
        return {"flows": self.flows, "owners": {k: o.snapshot() for k, o in self.owners.items()},
                "state": await self.state.snapshot()}

    async def _health(self):
        while not self.stop.is_set():
            try:
                await asyncio.wait_for(self.stop.wait(), 5)
            except asyncio.TimeoutError:
                try:
                    await self.state.event("progress", health=await self.snapshot())
                except Failure:
                    pass

    async def close(self):
        end = time.monotonic()+self.config.shutdown_timeout_ms/1000
        self.stop.set()
        for owner in self.owners.values():
            owner.stop()  # notify every owner at the same stop instant, before any wait.
        closing = [asyncio.create_task(o.close(end)) for o in self.owners.values()]
        normal = self.state.healthy
        try:
            results = await asyncio.wait_for(asyncio.gather(*self.tasks, self.health_task, *closing, return_exceptions=True), max(.001, end-time.monotonic()))
            normal &= all(not isinstance(r, BaseException) and r is not False for r in results)
            await asyncio.wait_for(self.http.close(), max(.001, end-time.monotonic()))
            summary = await self.state.snapshot()
            normal &= not summary["commands"].get("unknown", 0) and not summary["commands"].get("in_flight", 0) and self.state.healthy
            try:
                await self.state.event("stop_joined", result="normal" if normal else "fault_cleanup", had_forced_driver_stop=any(o.had_forced_driver_stop for o in self.owners.values()))
            except Failure:
                normal = False
            await self.state.close(end)
            require(time.monotonic() <= end, "shutdown_incomplete")
            return normal, summary
        except (asyncio.TimeoutError, Failure):
            raise Failure("shutdown_incomplete") from None
