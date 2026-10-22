"""本语言矩阵显式synthetic库、真实运行资源与持久报告；无兄弟依赖。"""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import time
from field_flow.app import demo01
from field_flow.domain import Failure, parse_input, Clock
from field_flow.infrastructure import state
from field_flow.runtime import Runtime
from field_flow.services.execution import Execution
from tests.test_matched_ack_gate import config, independent_read
from tests.fixtures.runtime import Fixture


async def eventually(predicate, seconds=4):
    end = time.monotonic()+seconds
    while time.monotonic() < end:
        if predicate(): return
        await asyncio.sleep(.005)
    raise AssertionError("finite observation deadline")


class Harness:
    def __init__(self, name):
        self.root = Path(tempfile.mkdtemp(prefix="ff-001-r1-r4-python-"+name+"-", dir="/private/tmp"))
        self.fixture, self.runs, self.report = Fixture(), [], []
        self.c = config()

    async def open(self, name, c=None, mode="execute", new=True, flows=False):
        c = c or self.c
        directory = self.root/name
        if new: state.init(directory, mode, c.instance_id)
        run = await Runtime.open(c, directory, mode, start_flows=flows)
        self.runs.append(run)
        await asyncio.wait_for(run.owners[c.plcs[0].id].ready.wait(), 4)
        return run

    def intent(self, run, body=None):
        return parse_input(body or self.fixture.body, run.config.flows[0], run.config.plcs[0])

    async def apply(self, run, intent=None):
        return await Execution(run.state, run.owners[run.config.plcs[0].id], Clock()).apply(intent or self.intent(run))

    async def iteration(self, run):
        c = run.config
        return await demo01.once(run.http, c.flows[0], c.plcs[0], Execution(run.state, run.owners[c.plcs[0].id], Clock()))

    async def close_run(self, run, expected=None):
        normal, summary = await run.close()
        self.runs.remove(run)
        self.report.append({"state_dir": str(run.state.directory), "normal": normal, "summary": summary,
                            "state": state.inspect(run.state.directory, True)})
        if expected is not None: assert normal is expected

    async def close(self):
        for run in list(self.runs):
            await self.close_run(run)
        closed = self.fixture.close()
        report = self.root/"report.json"
        report.write_text(json.dumps({"results": self.report, "fixture": closed}, indent=2)+"\n")
        print(json.dumps({"evidence": str(report)}))


def io_config(c, ms=1200):
    return replace(c, plcs=(replace(c.plcs[0], io_timeout_ms=ms),))
