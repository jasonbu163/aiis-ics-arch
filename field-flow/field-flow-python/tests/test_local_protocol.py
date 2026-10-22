"""Python AC01–15真实loopback矩阵；每例私有库并实际释放，失败原报告保留。"""
import asyncio
from dataclasses import asdict, replace
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import pytest
from field_flow.domain import Clock, Failure, parse_input
from field_flow.infrastructure import state
from field_flow.services.execution import Execution
from tests.fixtures.support import Harness, eventually, independent_read, io_config


def test_values_input_identity_and_dry_run():
    async def scenario():
        h = Harness("values")
        try:
            for n, value in enumerate((-32768, -1, 0, 42, 32767)):
                run = await h.open("value"+str(n)); h.fixture.command("value"+str(n), value)
                before = h.fixture.writes
                for _ in range(10): assert await h.iteration(run) == "confirmed"
                original = h.intent(run)
                for altered in (replace(original, value=0 if value else 1), replace(original, issued_at_ms=original.issued_at_ms+1),
                                replace(original, target=replace(original.target, offset=2))):
                    with pytest.raises(Failure, match="identity_conflict"): await h.apply(run, altered)
                await h.close_run(run, True)
                assert h.fixture.writes-before == 1 and independent_read() == value
                memory = bytes.fromhex(h.fixture.snapshot()["memory_hex"])
                assert memory[2:] == bytes([0xa5])*14
                run = await h.open("value"+str(n), new=False)
                for _ in range(10): await h.iteration(run)
                await h.close_run(run, True); assert h.fixture.writes-before == 1
            run = await h.open("bad-input"); before = h.fixture.writes
            body = h.fixture.command("invalid")
            for change in ({"value": -32769}, {"value": 32768}, {"value": False}, {"value": 42.0}, {"value": "42"},
                           {"source_id": "other"}, {"issued_at_ms": body["issued_at_ms"]+2000}, {"expires_at_ms": body["issued_at_ms"]-1},
                           {"expires_at_ms": body["issued_at_ms"]+60001}, {"extra": 1}):
                h.fixture.body = {**body, **change}
                with pytest.raises(Failure): await h.iteration(run)
            for raw in (b"{broken", b"\xff", b" "*4097, b'{"ready":true,"ready":false}'):
                h.fixture.body = raw
                with pytest.raises(Failure): await h.iteration(run)
            h.fixture.body = body; h.fixture.status = 503
            with pytest.raises(Failure, match="http_status"): await h.iteration(run)
            h.fixture.status = 200; h.fixture.content_type = "text/plain"
            with pytest.raises(Failure, match="http_content_type"): await h.iteration(run)
            h.fixture.content_type = "application/json"; h.fixture.body = {**body, "ready": False, "command_id": None, "value": None, "issued_at_ms": None, "expires_at_ms": None}
            assert await h.iteration(run) == "idle"
            assert h.fixture.writes == before; await h.close_run(run, True)
            run = await h.open("dry", mode="dry_run"); h.fixture.command("dry")
            for _ in range(10): assert await h.iteration(run) == "simulated"
            assert (await run.owners["plc_demo"].read("dry-read")).quality == "good"
            await h.close_run(run, True); assert h.fixture.writes == before
            with pytest.raises(Failure, match="state_identity"): await state.State.open(h.root/"dry", "execute", h.c.instance_id)
        finally: await h.close()
    asyncio.run(scenario())


def test_three_read_flows_and_slow_http():
    async def scenario():
        h = Harness("concurrency")
        try:
            run = await h.open("three-read"); owner = run.owners["plc_demo"]
            pid, generation, sessions = owner.driver.process.pid, owner.generation, h.fixture.sessions
            async def reader(name):
                samples = []
                for _ in range(20):
                    sample = await owner.read(name)
                    assert sample.flow_id == name and sample.generation == generation and sample.quality == "good"
                    samples.append(asdict(sample)); await asyncio.sleep(.001)
                return samples
            samples = await asyncio.gather(*(reader("read"+str(n)) for n in range(3)))
            assert len({s["request_id"] for flow in samples for s in flow}) == 60
            assert owner.driver.process.pid == pid and h.fixture.sessions == sessions and owner.max_inflight == 1
            h.report.append({"samples": samples, "pid": pid, "generation": generation, "normal_sessions": sessions})
            await h.close_run(run, True)
            c = replace(h.c, flows=(replace(h.c.flows[0], interval_ms=100),))
            run = await h.open("slow-http", c, flows=True); h.fixture.delay = 1.2
            times = []; end = time.monotonic()+8
            while time.monotonic() < end:
                sample = await run.owners["plc_demo"].read("independent-read")
                assert sample.quality == "good"; times.append(time.monotonic()); await asyncio.sleep(.1)
            gaps = [(b-a)*1000 for a,b in zip(times,times[1:])]
            assert len(times) >= 20 and max(gaps) <= 500
            assert run.flows["demo01"]["max_in_flight"] == 1
            h.report.append({"samples": len(times), "max_gap_ms": max(gaps), "slow_flow_health": dict(run.flows["demo01"])})
            await h.close_run(run, True)
        finally: await h.close()
    asyncio.run(scenario())


def test_ack_rejection_matrix():
    async def scenario():
        h = Harness("ack-matrix")
        try:
            vectors = [(False, f) for f in ("id", "rosctr", "reserved0", "reserved1", "function", "count", "param_length", "data_length", "transport", "bits", "short_header", "short_data", "empty", "extra", "payload4096", "payload4097", "payload65528", "ref0", "ref1", "oldref")]
            vectors += [(True, f) for f in ("otherref", "ref0", "ref1", "global0", "global1", "item", "function", "count", "extra", "late_correct")]
            for n, (write, fault) in enumerate(vectors):
                h.fixture.fault = ""; run = await h.open("case"+str(n)); owner = run.owners["plc_demo"]
                pid = owner.driver.process.pid
                if fault in ("oldref", "otherref"): await owner.read("completed-prior")
                before = h.fixture.writes; h.fixture.command("reject"+str(n)); h.fixture.fault = fault
                start = time.monotonic()
                with pytest.raises(Failure):
                    if write: await h.iteration(run)
                    else: await owner.read("rejected-read")
                elapsed = (time.monotonic()-start)*1000
                assert elapsed <= 5500
                with pytest.raises(ProcessLookupError): os.kill(pid, 0)
                if fault in ("oldref", "otherref"):
                    row = h.fixture.trace[-1]
                    assert row["request_hex"][22:26] == "0003"  # Setup1, successful raw Read2, current raw3
                    assert row["sent_response_hex"][22:26] == "0002"
                    assert row["previous_same_ref" if fault == "oldref" else "previous_other_ref"] == "0002"
                h.fixture.fault = ""
                if write:
                    for _ in range(10):
                        with pytest.raises(Failure, match="target_unknown"): await h.iteration(run)
                await h.close_run(run, False)
                counts = state.inspect(h.root/("case"+str(n)))["counts"]
                assert counts.get("confirmed", 0) == 0 and h.fixture.writes-before == int(write)
                if write:
                    assert counts == {"unknown": 1}
                    run = await h.open("case"+str(n), new=False)
                    for _ in range(10):
                        with pytest.raises(Failure, match="target_unknown"): await h.iteration(run)
                    await h.close_run(run, False); assert h.fixture.writes-before == 1
                h.report.append({"case": fault, "write": write, "old_pid": pid, "old_pid_gone": True, "duration_ms": elapsed, "counts": counts})
        finally: await h.close()
    asyncio.run(scenario())


@pytest.mark.parametrize("fault", ["split", "slow", "stale", "max_short"])
def test_overall_io_budget_and_recovery(fault):
    async def scenario():
        h = Harness("deadline-"+fault)
        try:
            c = io_config(h.c, 5000 if fault == "split" else 1200)
            run = await h.open("run", c); owner = run.owners["plc_demo"]; pid = owner.driver.process.pid
            h.fixture.fault = fault; start = time.monotonic()
            with pytest.raises(Failure): await owner.read("faulted-read")
            elapsed = (time.monotonic()-start)*1000
            assert elapsed <= c.plcs[0].io_timeout_ms+500
            with pytest.raises(ProcessLookupError): os.kill(pid, 0)
            h.fixture.fault = ""; await asyncio.wait_for(owner.ready.wait(), 4)
            assert (await owner.read("recovered-read")).quality == "good"
            h.report.append({"fault": fault, "old_pid": pid, "old_pid_gone": True, "duration_ms": elapsed,
                             "had_forced_driver_stop": owner.had_forced_driver_stop})
            if fault != "stale": assert owner.had_forced_driver_stop
            await h.close_run(run, False)
        finally: await h.close()
    asyncio.run(scenario())


def test_connect_budget_disconnect_and_queue_expiry():
    async def scenario():
        h = Harness("connect-queue")
        try:
            h.fixture.fault = "silent_cotp"
            c = replace(h.c, plcs=(replace(h.c.plcs[0], connect_timeout_ms=1000),))
            state.init(h.root/"silent", "execute", c.instance_id)
            run = await __import__("field_flow.runtime", fromlist=["Runtime"]).Runtime.open(c, h.root/"silent", "execute", start_flows=False)
            h.runs.append(run); owner = run.owners["plc_demo"]
            await eventually(lambda: owner.failed, 2)
            h.fixture.fault = ""; await asyncio.wait_for(owner.ready.wait(), 4)
            assert (await owner.read("after-connect")).quality == "good"
            assert owner.had_forced_driver_stop; await h.close_run(run, False)
            run = await h.open("disconnect"); owner = run.owners["plc_demo"]
            h.fixture.fault = "disconnect"
            with pytest.raises(Failure): await owner.read("disconnect")
            h.fixture.fault = ""; await asyncio.wait_for(owner.ready.wait(), 4)
            assert (await owner.read("recovery")).quality == "good"; await h.close_run(run, False)
            run = await h.open("expiry", io_config(h.c)); owner = run.owners["plc_demo"]
            h.fixture.fault = "split"; first = asyncio.create_task(owner.read("occupied"))
            await eventually(lambda: owner.dispatching == 1)
            body = h.fixture.command("expires-in-queue", ttl=700); intent = h.intent(run, body); before = h.fixture.writes
            with pytest.raises(Failure, match="expired"): await h.apply(run, intent)
            assert state.inspect(run.state.directory)["counts"] == {"expired": 1}
            await asyncio.gather(first, return_exceptions=True)
            h.fixture.fault = ""; assert h.fixture.writes == before
            await h.close_run(run, False)
        finally: await h.close()
    asyncio.run(scenario())


def test_state_recovery_unknown_alias_and_held_ack():
    async def scenario():
        h = Harness("recovery")
        try:
            run = await h.open("t1"); h.fixture.command("t1"); intent = h.intent(run)
            assert await run.state.admit(intent) == "pending"; await h.close_run(run, True)
            run = await h.open("t1", new=False); before = h.fixture.writes
            await h.apply(run, intent); await h.close_run(run, True); assert h.fixture.writes-before == 1
            run = await h.open("t2"); h.fixture.command("t2"); intent = h.intent(run)
            await run.state.admit(intent); await run.state.dispatch(intent, "durable-permit")
            await h.close_run(run, False)
            run = await h.open("t2", new=False)
            assert state.inspect(run.state.directory)["counts"] == {"unknown": 1}
            for changed in (intent, replace(intent, command_id="new-id"), replace(intent, source_id="alias", command_id="new-source", flow_id="new-flow"), replace(intent, command_id="overlap", target=replace(intent.target, offset=1))):
                with pytest.raises(Failure, match="target_unknown"): await h.apply(run, changed)
            assert (await run.owners["plc_demo"].read("still-reading")).quality == "good"
            await h.close_run(run, False)
            run = await h.open("held", io_config(h.c)); h.fixture.command("held")
            h.fixture.fault = "hold_ack"; before = h.fixture.writes
            with pytest.raises(Failure): await h.iteration(run)
            assert h.fixture.writes-before == 1; h.fixture.fault = ""; await h.close_run(run, False)
            run = await h.open("held", new=False)
            for _ in range(10):
                with pytest.raises(Failure, match="target_unknown"): await h.iteration(run)
            await h.close_run(run, False)
            assert independent_read() == 42 and state.inspect(h.root/"held")["counts"] == {"unknown": 1}
            assert h.fixture.writes-before == 1
        finally: await h.close()
    asyncio.run(scenario())


def test_audit_capacity_confirmed_and_stop_barrier():
    async def scenario():
        h = Harness("audit-stop")
        try:
            run = await h.open("capacity")
            await run.state.call(lambda: (setattr(run.state, "command_limit", 10), setattr(run.state, "event_limit", 100), setattr(run.state.audit, "limit", 2048)))
            before = h.fixture.writes
            for n in range(10): h.fixture.command("capacity"+str(n)); await h.iteration(run)
            h.fixture.command("capacity-over")
            with pytest.raises(Failure, match="capacity_paused"): await h.iteration(run)
            await h.close_run(run, True); assert h.fixture.writes-before == 10
            files = list((h.root/"capacity").glob("runtime.jsonl*")); assert 1 < len(files) <= 5
            for p in files:
                assert p.stat().st_size <= 2048
                for line in p.read_text().splitlines(): assert json.loads(line)["implementation"] == "python"
            run = await h.open("confirmed"); h.fixture.command("confirmed-before-sink"); await h.iteration(run); before = h.fixture.writes
            with pytest.raises(Failure): await run.state.test_fault("audit")
            with pytest.raises(Failure, match="audit_unhealthy"): await h.iteration(run)
            assert (await run.owners["plc_demo"].read("read-after-audit-fault")).quality == "good"
            await h.close_run(run, False); assert state.inspect(h.root/"confirmed")["counts"] == {"confirmed": 1}
            run = await h.open("confirmed", new=False)
            for _ in range(10): await h.iteration(run)
            await h.close_run(run, True); assert h.fixture.writes == before
            run = await h.open("t3"); h.fixture.command("failed-t3"); await run.state.test_fault("t3"); before = h.fixture.writes
            with pytest.raises(Failure): await h.iteration(run)
            assert h.fixture.writes-before == 1
            await h.close_run(run, False)
            assert state.inspect(h.root/"t3")["counts"].get("unknown", 0) + state.inspect(h.root/"t3")["counts"].get("in_flight", 0) == 1
            run = await h.open("t3", new=False)
            for _ in range(10):
                with pytest.raises(Failure, match="target_unknown"): await h.iteration(run)
            await h.close_run(run, False); assert h.fixture.writes-before == 1
            # Shared production Owner with a test-only pre-call barrier plus a second parent-queued write.
            from field_flow.owner import Owner
            barrier = h.root/"barrier"; barrier.touch(); directory = h.root/"stop"
            state.init(directory, "execute", h.c.instance_id); s = await state.State.open(directory, "execute", h.c.instance_id)
            owner = Owner(h.c.plcs[0], s, barrier=barrier); await asyncio.wait_for(owner.ready.wait(), 4)
            body = h.fixture.command("barrier-one"); intent = parse_input(body, h.c.flows[0], h.c.plcs[0]); execution = Execution(s, owner, Clock()); before = h.fixture.writes
            first = asyncio.create_task(execution.apply(intent)); await eventually(lambda: owner.dispatching == 1)
            second_intent = replace(intent, command_id="parent-queued", flow_id="test-other-flow", target=replace(intent.target, offset=2))
            second = asyncio.create_task(Execution(s, owner, Clock()).apply(second_intent)); await eventually(lambda: owner.queue.qsize() == 1)
            owner.stop(); results = await asyncio.gather(first, second, return_exceptions=True)
            assert all(isinstance(r, Failure) and str(r) == "canceled" for r in results)
            end = time.monotonic()+15; assert await owner.close(end); await s.close(end)
            assert h.fixture.writes == before and state.inspect(directory)["counts"] == {"canceled": 2}
            h.report.append({"case": "pre-call-and-parent-queue-stop", "state": state.inspect(directory, True), "actual_new_writes": 0})
        finally: await h.close()
    asyncio.run(scenario())


def test_audit_queued_prepermit_and_postcommit():
    async def scenario():
        h = Harness("audit-order")
        try:
            run = await h.open("queued", io_config(h.c)); owner = run.owners["plc_demo"]
            h.fixture.fault = "split"; busy = asyncio.create_task(owner.read("busy-read"))
            await eventually(lambda: owner.dispatching == 1)
            h.fixture.command("queued-one"); one = h.intent(run)
            two = replace(one, command_id="queued-two", flow_id="second-flow", target=replace(one.target, offset=2))
            first = asyncio.create_task(h.apply(run, one)); second = asyncio.create_task(h.apply(run, two))
            await eventually(lambda: owner.queue.qsize() == 2)
            await eventually(lambda: state.inspect(run.state.directory)["counts"].get("in_flight", 0) == 2)
            before = h.fixture.writes
            with pytest.raises(Failure): await run.state.test_fault("audit")
            await asyncio.gather(busy, first, second, return_exceptions=True)
            h.fixture.fault = ""; await asyncio.wait_for(owner.ready.wait(), 4)
            assert (await owner.read("independent-after-sink")).quality == "good"
            assert h.fixture.writes == before and state.inspect(run.state.directory)["counts"] == {"canceled": 2}
            await h.close_run(run, False)
            run = await h.open("t1-audit"); h.fixture.command("t1-before-audit"); before = h.fixture.writes
            await run.state.call(lambda: setattr(run.state.audit, "failed", True))
            with pytest.raises(Failure): await h.iteration(run)
            assert h.fixture.writes == before and state.inspect(run.state.directory)["counts"] == {"pending": 1}
            await h.close_run(run, False)
            run = await h.open("t2-audit"); h.fixture.command("t2-before-permit"); intent = h.intent(run)
            await run.state.admit(intent)
            await run.state.call(lambda: setattr(run.state.audit, "failed", True))
            with pytest.raises(Failure): await h.apply(run, intent)
            assert h.fixture.writes == before
            assert state.inspect(run.state.directory)["counts"] == {"canceled": 1}
            await h.close_run(run, False)
            run = await h.open("ack-audit"); h.fixture.command("ack-commit-then-sink")
            await run.state.call(lambda: setattr(run.state.audit, "_test_fail_event", "ack"))
            with pytest.raises(Failure): await h.iteration(run)
            assert state.inspect(run.state.directory)["counts"] == {"confirmed": 1} and h.fixture.writes-before == 1
            await h.close_run(run, False)
            run = await h.open("ack-audit", new=False)
            for _ in range(10): await h.iteration(run)
            await h.close_run(run, True); assert h.fixture.writes-before == 1
        finally: await h.close()
    asyncio.run(scenario())


def test_reference_maintenance_and_actual_block_boundary():
    async def scenario():
        h = Harness("ref-maintenance")
        try:
            from field_flow.owner import Owner
            directory = h.root/"near-limit"; state.init(directory, "execute", h.c.instance_id)
            s = await state.State.open(directory, "execute", h.c.instance_id)
            owner = Owner(h.c.plcs[0], s, seed=65534); await asyncio.wait_for(owner.ready.wait(), 4)
            pid = owner.driver.process.pid
            assert (await owner.read("near1")).reference == 65534
            assert (await owner.read("near2")).reference == 65535
            sample = await owner.read("after-maintenance")
            assert sample.reference == 2 and owner.driver.process.pid != pid
            with pytest.raises(ProcessLookupError): os.kill(pid, 0)
            end = time.monotonic()+15; assert await owner.close(end); await s.close(end)
            c = replace(h.c, flows=(replace(h.c.flows[0], target=replace(h.c.flows[0].target, db_size_bytes=32, byte_offset=15)),))
            run = await h.open("actual-boundary", c); h.fixture.command("actual-range-error"); before = h.fixture.writes
            memory_before = h.fixture.snapshot()["memory_hex"]
            with pytest.raises(Failure): await h.iteration(run)
            assert h.fixture.writes-before == 1
            assert state.inspect(run.state.directory)["counts"] == {"unknown": 1}
            assert h.fixture.snapshot()["memory_hex"] == memory_before
            await h.close_run(run, False)
            run = await h.open("actual-boundary", c, new=False)
            for _ in range(10):
                with pytest.raises(Failure, match="target_unknown"): await h.iteration(run)
            await h.close_run(run, False)
            assert h.fixture.writes-before == 1 and h.fixture.snapshot()["memory_hex"] == memory_before
            h.report.append({"case": "synthetic-complete-INT-memory-boundary", "memory_before": memory_before,
                             "memory_after": h.fixture.snapshot()["memory_hex"], "actual_WriteVar": 1,
                             "state": state.inspect(h.root/"actual-boundary", True)})
        finally: await h.close()
    asyncio.run(scenario())


def test_process_deaths_and_product_shutdown():
    from tests.fixtures.processes import deaths
    asyncio.run(deaths())


def test_initial_server_absence_alias_and_occupied_ports():
    async def scenario():
        h = Harness("absence-alias")
        try:
            h.fixture.stop_server()
            c = replace(h.c, flows=(replace(h.c.flows[0], interval_ms=100),))
            state.init(h.root/"absent", "execute", c.instance_id)
            from field_flow.runtime import Runtime
            run = await Runtime.open(c, h.root/"absent", "execute", start_flows=True); h.runs.append(run)
            await eventually(lambda: run.owners["plc_demo"].generation >= 2 and h.fixture.gets >= 2, 4)
            assert h.fixture.reads == h.fixture.writes == 0
            h.fixture.start_server(); await asyncio.wait_for(run.owners["plc_demo"].ready.wait(), 4)
            assert (await run.owners["plc_demo"].read("read-after-server-return")).quality == "good"
            await h.close_run(run, False)
            # Persisted unknown is matched by physical overlap even after real typed config aliases change.
            run = await h.open("alias"); h.fixture.command("original-alias")
            intent = h.intent(run); await run.state.admit(intent); await run.state.dispatch(intent, "seed-t2")
            await h.close_run(run, False)
            alias = replace(h.c, plcs=(replace(h.c.plcs[0], id="alias_plc"),),
                            flows=(replace(h.c.flows[0], id="alias_flow", source_id="alias_source",
                                   target=replace(h.c.flows[0].target, plc_id="alias_plc", byte_offset=1)),))
            run = await h.open("alias", alias, new=False); body = h.fixture.command("new-alias-id"); body["source_id"] = "alias_source"; h.fixture.body = body
            before = h.fixture.writes
            with pytest.raises(Failure, match="target_unknown"): await h.iteration(run)
            assert (await run.owners["alias_plc"].read("alias-read")).quality == "good" and h.fixture.writes == before
            await h.close_run(run, False)
        finally: await h.close()
        from tests.fixtures.public_api import bind
        from tests.fixtures.runtime import Fixture
        for port in (32102, 32103, 32880):
            occupied = bind(port)
            try:
                with pytest.raises(OSError): Fixture()
                assert occupied.getsockname() == ("127.0.0.1", port)
            finally: occupied.close()
            for check_port in (32102, 32103, 32880):
                peer = bind(check_port); peer.close()
        print(json.dumps({"case": "port-conflict", "ports_preserved_then_rebound": [32102,32103,32880]}))
    asyncio.run(scenario())


def test_conflict_pause_and_queued_clock_jump():
    async def scenario():
        h = Harness("clock-conflict")
        try:
            c = replace(h.c, flows=(replace(h.c.flows[0], interval_ms=100),))
            h.fixture.command("stable-then-conflict")
            run = await h.open("conflict", c, flows=True)
            await eventually(lambda: state.inspect(run.state.directory)["counts"].get("confirmed", 0) == 1)
            h.fixture.body = {**h.fixture.body, "value": 43}
            await eventually(lambda: run.flows["demo01"]["state"] == "blocked")
            before = h.fixture.writes; h.fixture.command("new-after-conflict", 44)
            await asyncio.sleep(.35)
            assert h.fixture.writes == before and run.flows["demo01"]["result"] == "identity_conflict"
            await h.close_run(run, True)
            run = await h.open("clock", io_config(h.c)); owner = run.owners["plc_demo"]
            h.fixture.fault = "split"; busy = asyncio.create_task(owner.read("busy-before-clock"))
            await eventually(lambda: owner.dispatching == 1)
            h.fixture.command("queued-before-jump"); pending = asyncio.create_task(h.apply(run))
            await eventually(lambda: owner.queue.qsize() == 1)
            # Local test anchor injection models a >1000ms backward wall jump; system clock is unchanged.
            owner.write_clock.wall += 2000
            before = h.fixture.writes
            await asyncio.gather(busy, pending, return_exceptions=True)
            assert state.inspect(run.state.directory)["counts"] == {"canceled": 1} and h.fixture.writes == before
            assert owner.snapshot()["clock_invalid"]
            h.fixture.fault = ""; await h.close_run(run, False)
        finally: await h.close()
    asyncio.run(scenario())
