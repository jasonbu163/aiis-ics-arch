"""R15正式state/owner/driver/execution共用途径，110秒内部界限+外层120秒。"""
import asyncio
from dataclasses import replace
import json
import os
from pathlib import Path
import tempfile
import time
from snap7 import Client
from field_flow.config import parse
from field_flow.domain import Clock, Failure, parse_input
from field_flow.infrastructure import state
from field_flow.infrastructure.s7_int_pdu import request, validate
from field_flow.owner import Owner
from field_flow.services.execution import Execution
from tests.fixtures.runtime import Fixture


def config():
    return parse({"schema_version": 1, "instance_id": "ff-python-demo01", "plcs": [{"id": "plc_demo", "host": "127.0.0.1", "port": 32102, "rack": 0, "slot": 1, "connect_timeout_ms": 3000, "io_timeout_ms": 5000, "queue_capacity": 16, "queue_wait_ms": 2000, "ready_wait_ms": 3000}], "flows": [{"id": "demo01", "kind": "demo01", "business_name": "synthetic_command_to_int", "interval_ms": 500, "source_id": "demo01-feed", "get_url": "http://127.0.0.1:32880/demo01/command", "target": {"plc_id": "plc_demo", "db_number": 1, "db_size_bytes": 16, "byte_offset": 0, "type": "INT"}, "input_max_age_ms": 10000}], "http": {"connect_timeout_ms": 500, "total_timeout_ms": 1500, "pool_wait_ms": 500, "max_connections": 8, "max_body_bytes": 4096}, "shutdown_timeout_ms": 15000})


class Run:
    @classmethod
    async def open(cls, directory, c, mode="execute", new=True, seed=2, barrier=None):
        run = cls(); run.dir = Path(directory); run.c = c
        if new: state.init(directory, mode, c.instance_id)
        run.state = await state.State.open(directory, mode, c.instance_id)
        run.owner = Owner(c.plcs[0], run.state, seed=seed, barrier=barrier)
        run.execution = Execution(run.state, run.owner, Clock())
        await asyncio.wait_for(run.owner.ready.wait(), 3.5)
        return run

    async def close(self):
        end = time.monotonic()+self.c.shutdown_timeout_ms/1000
        normal = await self.owner.close(end)
        await self.state.close(end)
        return normal


def independent_read():
    client = Client()
    try:
        client.connect("127.0.0.1", 0, 1, tcp_port=32102)
        return validate(client.iso_exchange_buffer(request(2, 1, 0)), 2, 4).value
    finally:
        client.disconnect()


async def gate(root):
    fixture = Fixture(); reports = []; c = config()
    try:
        async with asyncio.timeout(110):
            for fault in ("", "ref0", "function", "ref1", "short_data"):
                fixture.fault = ""
                directory = root / (fault or "normal")
                run = await Run.open(directory, c)
                assert (await run.owner.read("normal-read")).value is not None
                body = fixture.command("gate-"+(fault or "normal"))
                intent = parse_input(body, c.flows[0], c.plcs[0])
                before = fixture.writes
                fixture.fault = fault
                if fault == "ref0":
                    try: await run.owner.read("bad-ref-read")
                    except Failure as exc: assert str(exc) == "s7_reference_mismatch"
                    else: raise AssertionError("bad read accepted")
                    assert fixture.writes == before
                    await run.close()
                else:
                    try: await run.execution.apply(intent)
                    except Failure:
                        assert fault
                    else: assert not fault
                    for _ in range(10):
                        try: await run.execution.apply(intent)
                        except Failure: assert fault
                    await run.close()
                    snapshot = state.inspect(directory, True)
                    assert snapshot["counts"] == {"unknown" if fault else "confirmed": 1}
                    assert fixture.writes-before == 1
                    fixture.fault = ""
                    restart = await Run.open(directory, c, new=False)
                    for _ in range(10):
                        try: await restart.execution.apply(intent)
                        except Failure: assert fault
                    await restart.close()
                    assert fixture.writes-before == 1 and independent_read() == 42
                    reports.append({"fault": fault, "actual_writes": fixture.writes-before, "state": state.inspect(directory, True), "directory": str(directory)})
            closed = fixture.close()
            (root / "gate.json").write_text(json.dumps({"reports": reports, "protocol_and_close": closed}, indent=2)+"\n")
    except BaseException:
        if not fixture.stop.is_set(): fixture.close()
        raise


def test_matched_ack_gate():
    root = Path(tempfile.mkdtemp(prefix="ff-001-r1-r4-python-gate-", dir="/private/tmp"))
    start = time.monotonic(); asyncio.run(gate(root))
    print(json.dumps({"gate_evidence": str(root/"gate.json"), "duration_seconds": time.monotonic()-start}))
