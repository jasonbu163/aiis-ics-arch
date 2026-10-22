"""双语CLI与组合根；无参/help无配置、状态或网络副作用。"""
import asyncio
import json
import os
from pathlib import Path
import signal
import sys
from field_flow.domain import Failure, require


def locale(language):
    require(language in ("zh-CN", "en-US"), "arguments")
    base = Path(__file__).parent / "locales"
    if not base.is_dir():
        base = Path(__file__).resolve().parents[2] / "locales"
    return json.loads((base / (language+".json")).read_text())


def arguments(args):
    words, flags, language = [], {}, "en-US"
    iterator = iter(args)
    for arg in iterator:
        if arg == "--lang":
            language = next(iterator, None)
        elif arg in ("--help", "-h"):
            flags["help"] = True
        elif arg.startswith("--"):
            name = arg[2:]
            require(name in ("config", "state-dir", "mode", "instance-id", "synthetic", "execute") and name not in flags, "arguments")
            flags[name] = True if name in ("synthetic", "execute") else next(iterator, None)
            require(flags[name] is not None, "arguments")
        else:
            words.append(arg)
    return words, flags, locale(language)


async def run(config, directory, mode):
    from field_flow.runtime import Runtime
    runtime = await Runtime.open(config, directory, mode)
    loop = asyncio.get_running_loop()
    stopped = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stopped.set)
    try:
        await stopped.wait()
        normal, summary = await runtime.close()
        # Every flow/owner/driver/log observer/HTTP and state thread is actually closed before final declarations.
        from field_flow.infrastructure.audit import Audit, event_line
        if normal:
            audit = Audit(directory, runtime.state.run_id, config.instance_id)
            try:
                released = audit.emit("resources_released", result="normal", _stdout=False)
                completed = audit.emit("shutdown_complete", result="normal", _stdout=False)
            finally:
                audit.close()
            require(os.write(1, released+completed) == len(released+completed), "audit_stdout")
        else:
            os.write(1, event_line(runtime.state.run_id, config.instance_id, "shutdown_incomplete", result="fault_cleanup", summary=summary))
        return 0 if normal else 1
    finally:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    text = locale("en-US")
    try:
        words, flags, text = arguments(args)
        if not args or flags.pop("help", False):
            print(text["help"])
            return 0
        if words == ["state", "init"]:
            require(set(flags) == {"synthetic", "mode", "state-dir", "instance-id"}, "arguments")
            from field_flow.infrastructure.state import init
            init(flags["state-dir"], flags["mode"], flags["instance-id"])
            from field_flow.infrastructure.audit import event_line
            os.write(1, event_line("", flags["instance-id"], "state_init", result="ok"))
            return 0
        if words == ["state", "inspect"]:
            require(set(flags) == {"state-dir"}, "arguments")
            from field_flow.infrastructure.state import inspect
            print(json.dumps(inspect(flags["state-dir"])))
            return 0
        require(words == ["run"] and {"config", "state-dir"} <= set(flags) <= {"config", "state-dir", "execute"}, "arguments")
        from field_flow.config import load
        config = load(flags["config"])
        return asyncio.run(run(config, flags["state-dir"], "execute" if flags.get("execute") else "dry_run"))
    except (Failure, OSError) as exc:
        print(text["error"]+": "+(str(exc) if isinstance(exc, Failure) else "io_error"), file=sys.stderr)
        return 1 if isinstance(exc, Failure) and str(exc) == "shutdown_incomplete" else 2
