# ARCH-BE-013：开发启动日志与关停资源清理

Task ID: ARCH-BE-013
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 草案已撤回；本次请求按 DIRECT 执行，无 STD Development handoff
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 后端源码开发入口的可读终端日志与正常关停
Owner: Core 后端运行入口与日志
Acceptance Chain Reference: 本规格范围确认 → Development handoff → fresh-context Verification → Human Owner 最终验收

**草案撤回说明**：Human Owner 于 2026-11-20 明确选择本次请求按 DIRECT 执行，并同意保留此草案。ARCH-BE-013 r1 未获范围批准，未发生 STD Development handoff。以下内容保留为草案记录，本次实施与验证结果由 DIRECT 当前会话报告。

## 1. 目标和现状

Human Owner 要求调整 `cd backend && uv run run.py` 的本地开发体验，让终端接近原生 FastAPI/Uvicorn 日志、文件继续保留 JSON Lines，模块发现明细降到 DEBUG，并查清并修复 Ctrl+C 退出时的信号量警告。完成后需要实际启动和退出验证。

当前 `run.py` 使用 Uvicorn 热重载并加载 `main:app`。`main.py` 调用共用 `setup_logger("api")`，后者将终端、常规文件与错误文件设置为 JSON Lines，并在非打包源码运行时为各 sink 启用队列。模块注册会记录每个已加载或无 manifest 的模块。2026-11-20 在 macOS / Python 3.13.3 的隔离源码和临时回环端口上，实际通过终端启动 `uv run run.py` 并取得 `/health` 200 后按 Ctrl+C，基线出现 `resource_tracker` 信号量警告，JSONL 文件缺少 `Application shutdown complete` 和 `Finished server process`。先前一次复现报告 24 个待清理信号量。

同环境的诊断对照仅在隔离副本通过 `sitecustomize` 临时将 Loguru 的 `enqueue` 设为 `False`，重复启动、健康检查及 Ctrl+C 后退出码为 0，未出现该警告或 traceback，终端和 JSONL 文件都包含上述完成事件。这支持日志队列及热重载关停交互参与问题，但该诊断覆盖不作为最终实现，也不能单凭对照排除其他条件。Development 应记录实际采用的修复与多进程兼容性证据。

本规格是 PM 范围草案。原草案拟由各角色记录实施与验证证据，草案本身不代表已实施、独立验证或最终验收。

## 2. 范围和行为合同

1. 本地开发入口继续支持既有 `uv run run.py`、配置的 host/port 与热重载。启动、请求访问、警告、错误和正常关停在终端显示简洁可读的信息，接近 FastAPI/Uvicorn 通常的开发输出。异常保留足以定位的堆栈，不通过隐藏 ERROR、过滤警告或吞掉异常使输出变干净。
2. 后端常规日志和错误日志继续写入可逐行解析的 JSON Lines，保留现有结构化上下文、严重级别、阈值与轮转／保留配置行为。标准库及 Uvicorn 日志仍能进入相应文件，错误日志继续单独记录 ERROR 及以上。开发入口的人类可读终端输出是明确的局部例外，双语 backend README 应说明这个入口、文件位置和日志级别。
3. `backend.module_discovery_loaded` 与 `backend.module_discovery_skipped` 降为 DEBUG，`backend.module_discovery_failed` 保持 ERROR，发现诊断数据与失败行为保持。默认 INFO 下不逐项刷出成功／跳过明细，显式 DEBUG 时仍能取得这些明细。
4. 查明 Ctrl+C 时 `resource_tracker` 信号量警告涉及的进程和资源生命周期，用对照证据确认修复的因果关系。修复应真正处理资源释放或其创建方式，不能关闭 Python 警告、删除报错文本或仅改变退出码。正常退出、重复启动和热重载后退出均需考虑，且不能遗留本任务创建的进程。
5. `main.py` 的生产／打包入口、非开发入口的结构化 stdout、维护进程、文件日志及多 worker 既有行为应继续适用。若所需修复触及共享日志组件，需覆盖这些调用方，避免为单进程开发场景破坏多进程文件写入或可观测性。模块发现明细的 DEBUG 级别按第 3 条统一生效。
6. 保留当前工作树中其他任务的未提交改动。不得迁移数据库、修改真实 `.env`、连接真实设备、启动或停止已有服务。隔离运行使用公开示例配置、无业务数据的临时日志目录与回环端口，验证产物结束后按归属清理。

## 3. 允许触达

Development 在范围确认后可按实现需要调整以下路径，且仅限本合同所需变更：

- `backend/run.py`、`backend/main.py`、`backend/common/log.py`、`backend/app/module_registry.py` 和与启动／关停直接相关的后端组合入口。
- `backend/tests/test_logging.py` 及与模块发现、运行入口直接相关的既有测试，必要时新增聚焦回归测试。
- `backend/README.md` 和 `backend/README.zh-CN.md` 中开发日志与使用说明。已有并行改动须原样保留并仅做局部合并。
- 本任务的 `tasks.md` 与必要的索引机械同步由对应责任方按 workflow 处理。源码结构确有变化时按仓库契约维护 `CODE_INDEX.md`。

不调整 API 合同、业务模块、数据模型和迁移，不改变部署或现场配置，不引入新的依赖或日志平台。若实现需要超出本节的实质变更，先返回 PM 修订范围。

Development 按 `aiis` 的运行日志基线与资源生命周期资料、`backend-packaging` 和 `code-document-indexer` 工作。生产日志仍遵循结构化基线，本地开发终端例外以用户本次明确要求为准。

## 4. 验收标准

| ID | 验收内容 |
| --- | --- |
| AC01 | 使用项目锁定的工具链，在隔离配置下实际运行 `uv run run.py`，确认热重载服务可完成启动，`GET /health` 成功。终端能看到可读的启动、访问与关停信息，默认 INFO 不出现模块发现逐条明细，也不输出整条 JSON 对象。 |
| AC02 | 验证开发入口常规日志各非空行均可解析为 JSON，涵盖启动与访问；以受控方式产生 ERROR，验证常规及 error-only 文件均含相应记录及必要的级别、进程和上下文。验证配置的阈值、文件轮转／保留及异常可观测性没有退化。 |
| AC03 | 默认 INFO 不包含成功和跳过的逐模块记录；显式 DEBUG 时可取得这两类记录，失败依旧以 ERROR 可见并保持原有诊断和失败语义。 |
| AC04 | 记录修复前后的对照方法、进程／资源归因及结果。以终端式 Ctrl+C 验证隔离服务正常退出，无 `resource_tracker` 信号量泄漏警告，无关闭过程的异常 traceback；重复启动退出及实际触发一次源码热重载后退出均通过，并核对本任务进程已结束。 |
| AC05 | 验证非开发入口和维护进程仍按原合同输出结构化 stdout 与 JSONL 文件。对可能受影响的多 worker 日志写入和退出行为作与实现风险匹配的验证，保留错误与访问日志，不以单进程结果替代多进程兼容性证据。 |
| AC06 | 相关测试与静态检查通过或如实记录限制。双语说明与实际入口、日志文件和 DEBUG 获取方式一致。验证不使用真实数据库写入、设备或既有服务。 |

Development 在 `tasks.md` 记录命令、环境、退出码、因果对照、测试及临时资源清理。Verification 在 fresh context 对实际交付源码及独立验证结果作记录；若平台、依赖或权限限制阻止某项验证，不得把该项记为通过。

## 5. 风险和恢复

热重载监管进程和应用进程均收到退出信号时，日志队列或其后台写入可能尚未完成。调整资源生命周期时须兼顾已发出的日志落盘、多 worker 并发与异常退出边界。验证覆盖实际 Ctrl+C、重载及重复运行，不能根据一条无警告退出推断所有平台可靠。其他系统平台的原生表现应明确记录实际验证范围。

回退以本任务自身源码差异为边界，保留其他任务正在进行的工作与既有日志文件。任何额外运行环境采用或打包／部署验证按各自授权和实际证据处理。

## 6. Revision 与批准记录

2026-11-20：依 Human Owner 对本地开发输出、JSONL 文件、发现明细和 Ctrl+C 修复的要求形成 r1 草案。随后 Human Owner 选择 DIRECT 并同意保留草案，本 r1 撤回，未获范围批准，未发生 STD Development handoff。
