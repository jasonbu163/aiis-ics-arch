# Field Flow — Python / Rust 对照使用手册

[English](USER_GUIDE.md)

Python 用于熟悉语言、练手及快速原型，本任务不做 Python 打包；Rust 是后续长期部署 runtime 的主要建设方向。未来生产 flow 不要求双语言同步实现；保留现有 Python 源码、功能、测试和 FF-001 证据。语言选择或本手册不授予生产资格。

## 读者路线

1. 先读本对照，再选一个工程的完整自身手册。
2. [Python USER_GUIDE](field-flow-python/USER_GUIDE.zh-CN.md) — 源码环境、CLI、两个教学场景、真实方法合同与teaching01接线。
3. [Rust USER_GUIDE](field-flow-rust/USER_GUIDE.zh-CN.md) / [BUILD](field-flow-rust/BUILD.zh-CN.md) — release/fixture准备、独立runtime教程与native/平台限制。

每个工程可单独复制，使用自身清单/锁、源码、配置、locale、夹具与状态；完整教程无需父手册、兄弟环境/可执行文件/服务或Backend/DS。父任务链接只是可选治理导航。

| 职责 | Rust | Python |
| --- | --- | --- |
| Entry / environment | `src/main.rs → commands.rs; Cargo.toml/Cargo.lock; Rust ≥1.89` | `src/field_flow/__main__.py → cli.py; pyproject.toml/uv.lock; existing CPython3.11 / uv` |
| One bounded app round | `src/app/demo01.rs::iteration(&Flow,&Plc,&Http,&Owner,&State,&Stop,&mut Clock)` | `src/field_flow/app/demo01.py::once(http,flow,plc,execution)` |
| Configuration | `src/config.rs::Config/Flow/Plc/Target/Http` | `src/field_flow/config.py dataclasses; parse/load` |
| HTTP / command conversion | `services::Http::get → domain::Input::intent` | `HttpClient.get → domain.parse_input` |
| Durable execution | `Execution {owner,state,stop}.apply(intent,clock) → Result<()>` | `Execution(state,owner,clock).apply(intent) → status string` |
| PLC read / ownership | `runtime::Owner::read(flow,db,offset) → Sample` | `owner.Owner.read(flow,db=1,offset=0) → Sample` |
| Dispatch / lifecycle | `src/runtime.rs::Runtime::launch_flows/shutdown` | `src/field_flow/runtime.py::Runtime._flow/close` |
| Registration | `app/mod.rs + config.rs kind check + runtime.rs dispatch` | `runtime.py import+dispatch + config.py kind check; app/__init__.py stays thin` |
| Manual fixture | `test-fixture ff-fixture; ENTER; protocol.json` | `python -m tests.fixtures; SIGINT/SIGTERM; report.json` |
| Fixed loopback ports | `proxy31102 / native server31103 / HTTP31880` | `proxy32102 / server32103 / HTTP32880` |
| Command identity | `cmd-001 / demo01-feed / value42` | `fixture-UUID / first-flow source / value42` |
| Runtime locale | `locales/*.json compiled with include_str!` | `own installed locale files or project locales fallback` |
| Long-term direction | `deployment-runtime development; platform/field/hosting gates remain` | `learning/prototype source usage; no packaging in FF-002` |

Python签名描述实际对象合同，非已有完整类型SDK。内部布局和错误key不同；对照语义，不假定API逐行一致。

## 一轮代码逐步对照

1. runtime给一轮app提供Flow/Plc、复用HTTP client、PLC owner、持久state并保留每flow原Clock。
2. Rust先检查clock再await http.get(&f.get_url)；Python once先await http.get(flow.get_url)，Execution接纳前检查自身Clock。HTTP等待不占PLC队列。
3. Rust input.intent(f,p)?与Python parse_input(incoming,flow,plc)严格校验七键ready命令；None为idle，非法值报错，不取默认。
4. Rust构造Execution {owner,state,stop}.apply(intent,clock).await?；Python await execution.apply(intent)。两者先持久身份/状态再获准写，app不调用raw driver写。
5. 匹配S7 INT ACK加本地T3提交才confirmed；可能发送后缺证据为unknown，不表示物理工艺完成。
6. 返回runtime后等待interval_ms；不同flow并发，同流不重叠/不补历史tick。每PLC session仅串行自身IO。

两个完整手册均包含同能力teaching01的完整app/YAML、逐文件module/import/kind/dispatch接线及编译/导入/CLI验证。正式源码仍仅接受demo01，不自动发现文件。teaching01是不同flow/business身份的同能力GET→INT，不是demo02；POST/auth、BOOL/DINT/REAL、上升沿flow未实现，写必须经过Execution.apply。

## 夹具、状态与证据边界

每个人工夹具拥有synthetic HTTP源、透明TCP proxy和注册16字节DB1内存的真实S7 server；proxy两段不是两个业务client。Rust有native server子进程，Python也spawn自身server child，child拥有server线程。此夹具不是DS。自动测试可改内部feed/故障，人工CLI没有持续命令生成或面板。命令issued仅一次、expiry为Rust60秒/Python30秒，默认input_max_age_ms=10000故启动后仅十秒有效；先完成依赖/build/init，再起夹具并立即跑一个模式。dry-run/execute各用新教学场景，不共用一个十秒窗口。

state init --synthetic显式创建新schema1目录；普通run不建schema。默认dry_run，--execute要求单独初始化execute库；implementation/mode/instance/schema须匹配。inspect只读，health为JSONL而非HTTP endpoint。身份和unknown物理重叠阻断跨重启保留。原执行场景重启保留原状态/身份，不删库/重置/复制运行中库、不刷新同ID时间或换ID强制重放。Rust/Python可写状态不互换；writer切换先停旧端并核对未决/已确认进度，尚无跨主机fencing。

来源Unix毫秒与monotonic耗时保留各自语义。现SQLite日历元数据/JSONL为UTC，与根Asia/Shanghai日历存储合同不同；本轮记录限制，不改实现/schema/历史。平台移植、时间数据迁移、现场endpoint、DS/Backend联调、服务托管、备份升级、长稳/容量、分发均另需批准和证据。

FF-001 r4已通过独立本地QA2，待Human Owner终验。FF-002文档/有限演练有自己的[spec](plans/FF-002-user-guide-and-runtime-positioning/spec.md)与[Development记录](plans/FF-002-user-guide-and-runtime-positioning/tasks.md)，DEV自检不替独立QA。[FF PLAN](PLAN.zh-CN.md)索引下一gate。
