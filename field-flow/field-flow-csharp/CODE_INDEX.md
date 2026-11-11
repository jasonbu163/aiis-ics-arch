# Code Index

| Path | Responsibility |
| --- | --- |
| `src/FieldFlow/Program.cs` and `Cli/` | Explicit CLI and composition |
| `src/FieldFlow/Domain/` | Typed configuration, command and clock |
| `src/FieldFlow/App/Demo01.cs` | One business iteration |
| `src/FieldFlow/Services/` | Durable execution and send gate |
| `src/FieldFlow/Runtime/` | Flow supervision and shutdown |
| `src/FieldFlow/Infrastructure/Configuration/` | Bounded YAML/JSON preflight |
| `src/FieldFlow/Infrastructure/Http/` | HTTP input and strict command parsing |
| `src/FieldFlow/Infrastructure/S7/` | Per-PLC queue, session and S7 INT16 |
| `src/FieldFlow/Infrastructure/State/` | SQLite identity, transitions and recovery |
| `src/FieldFlow/Infrastructure/Logging/` | Bounded JSONL evidence |
| `tests/FieldFlow.Fixture/` | Independent local HTTP/S7 fixture |
| `tests/FieldFlow.Tests/` | Configuration, state, protocol and queue tests |
