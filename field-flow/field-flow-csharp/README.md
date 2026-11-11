# Field Flow C#

[中文](README.zh-CN.md)

This independent .NET console project is the FF-003 r2 development candidate. It loads one S7 PLC per JSON file and runs the `demo01` HTTP GET → SQLite → S7 DB INT16 flow. Each PLC owns one session and a bounded queue. Flows advance independently.

The default run mode reads the target without writing it. `--execute` uses a separate state directory. Repeated commands reuse their recorded state and an uncertain write stays `unknown`.

[BUILD.md](BUILD.md) describes the pinned SDK, isolated dependencies, sample configuration and commands. The target is Windows 10 Enterprise LTSC 2021 x64. macOS checks are development evidence only. Consult the parent FF-003 task for the current native Windows and independent QA gates.
