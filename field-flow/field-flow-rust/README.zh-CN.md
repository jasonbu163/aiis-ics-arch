# Field Flow Rust

[English](README.md)

独立手写demo01：HTTP GET → 严格合成命令 → 两字节DB INT写入。每PLC一个常驻受监督driver进程/会话；不同flow独立调度，同flow不重叠。父进程SQLite与持久审计保留原身份，confirmed/unknown不会自动重发；unknown物理范围阻断后续写，核实/人工处置需另批。

要求Rust/Cargo 1.89+、本机C++编译器及本目录Cargo.lock。实际平台和检查结果归FF-001 tasks；r4保留R14 adapter/锁与原证据，并包含QA1后的FIFO期限、时钟锚点及真实started修复；最新双版本交接、独立QA verdict和Owner gate以唯一任务为准。可只复制本目录独立构建/运行，不依赖兄弟源码、清单、环境、可写状态或服务；任务链接只是仓库文档导航。

构建与全测试命令、无参/中英帮助、显式初始化、夹具/运行命令与英文README逐项相同。先执行 `cargo build --locked --bins --features test-fixture`；`cargo test --locked --test s7_int_pdu`；`cargo test --locked --features test-fixture -- --test-threads=1`。`cargo run --locked --bin field-flow -- --lang zh-CN --help`显示中文帮助，无参/help不读配置、不联网、不建库/日志。

必须以 `state init --synthetic --mode dry_run|execute --state-dir <新目录> --instance-id ff-rust-demo01`显式初始化，父目录已存在、新目录不存在。普通run只打开匹配实现/版本/模式/instance的既有库，不建schema、不覆盖、不提供unknown重发/重置。随后 `run --config config/loopback.yaml --state-dir <目录>`默认dry-run，只有execute库加`--execute`才能写；`state inspect --state-dir <目录>`只读。Ctrl-C停止runtime；夹具独立终端按ENTER停止。

示例只连接本工程127.0.0.1夹具：S7代理31102/server31103、HTTP31880。端口冲突报错，不换端口或杀占用者。INT为大端有符号-32768..32767；来源身份与原UTC失效时间不可刷新；dry_run/execute库隔离。SQLite只属本地执行事实，不是Backend业务库。

stdout与state-dir/runtime.jsonl为结构化日志；完整JSON行写入前按5MiB轮转、最多4备份，必要状态链另存只追加command_events。默认command10000/event接纳阈值90000，并有库大小/磁盘背压。审计失败阻止新副作用，confirmed不倒退。stop闭闸后join各flow/owner、child正常关闭，随后在同一global截止时间内关闭SQLite/审计；强制终止是fault_cleanup/exit1，不能记正常退出。父死亡时自身child结束，继承的实例锁持有到child实际退出。

`src/infrastructure/s7_int_pdu.rs`仅通过冻结公开ISO API处理单item/2-byte DB INT，4096字节初始化FFI缓冲，精确校验结构/ref后才生成typed ACK；坏会话退役。它不是通用S7栈；test-fixture特性才开启故障hook，没有任意raw产品入口。

[代码索引](CODE_INDEX.md)、[任务导航](PLAN.zh-CN.md)、[组件声明](THIRD_PARTY_NOTICES.zh-CN.md)。有限本机验证不代表现场/生产、长稳、跨平台打包、部署或Human Owner验收。

QA1返工修正Rust FIFO在实际dispatch起算IO、同一wall/monotonic锚点在排队后与child开始闸门前复核、匹配started才统计正在执行；ready/queue与IO各自有界，原来源有效期和400ms内部回收预留保持。当前DEV、独立QA verdict及Human Owner gate以唯一任务bundle为准。
