Task ID: FF-006
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: FF-006 r1 Development AC03 rework -> new fresh-context Verification on the exact working tree and rework manifest
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: Rust 显式加载有限只读流程 JSON，执行 demo01 GET 与布尔分支
Owner: Field Flow
Acceptance Chain Reference: FF-006 r1 exact Human Owner approval -> Development -> fresh-context Verification -> Human Owner final acceptance

# FF-006 r1 Development

Human Owner 于 2026-11-24 正式批准 [FF-006 r1](spec.md)。批准版 SHA-256 为 `1b5937dbbc2f73f617eec7d38830ae6223a7468fec9f62cbb1bd1a3da52a91eb`。主协调实际以 `development` 角色调用 `/root/ff006_r1_dev`。实施在正式工作树 `field-flow/field-flow-rust/`，HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`，交付形式为未提交工作树。其他目录的已有变更保留。使用 Darwin 24.6.0 arm64、rustc 1.89.0（29483883e）、cargo 1.89.0（c24e10642），依赖来自现有 Cargo 锁和本地缓存。

## 实施范围

- YAML v2 支持成对配置 `flow_files` 和 `flow_http_endpoints`。CLI 显式从 `--flows-dir` 解析普通文件，在启动外部资源之前完成预检。加载时校验两端边关系、HTTP 绑定、`ready` 布尔比较、分支终点和 optional layout，保存原始 SHA-256。纯图任务可使用空 PLC 配置。
- 用手写 `demo01` 的有类型的命令校验和共享 HTTP 客户端，图流只提取经校验的 `ready`。每次实际 GET 对应独立轮次，输出分支或稳定错误键。记录带 `+08:00` 的 `observed_at`，既有日志信封时间戳保持原格式。图代码无需 PLC owner、driver 或写入意图。原手写 `demo01` 和状态执行器保留，YAML v2 可同时装配两种流。
- 在启动运行任务前注册 SIGINT/SIGTERM，避免首轮已运行而停止信号尚未被接收的竞态。停止时取消待完成的图 GET，通过既有 runtime 停止入口 join 并释放资源。
- 增加工程内 [合成 YAML 配置](../../field-flow-rust/config/flow-json.yaml)、[流程图](../../field-flow-rust/flows/demo01.json)、独立回环测试、双语入口和指南。CA 的实际导出及返程仍待双方产物验证。

精确 23 个变更文件和 80 个正式与独立副本一致的文件 SHA-256 见 [源码清单](evidence/r1-development/source-sha256.json)。清单 SHA-256 为 `c27cfc526b868a2a1873b67a16bb9d4edfba144a827cc8968cb8181d4cccbddc`。清单只覆盖 Rust 单工程，排除 `.git`、`.DS_Store` 和 `target`。Rust 工作树差集与 §2 allowlist 对过，`Cargo.toml`、`Cargo.lock`、`src/app/demo01.rs`、`src/infrastructure/state.rs` 和旧三测试目标逐字节匹配 HEAD。

## 首轮验证与发现

- `cargo check --locked --offline --target-dir "$D/test"` 通过。首次合成协议测试受 sandbox `127.0.0.1` 监听限制，4 项中 1 过 3 失败，exit 101。获得针对已批准自有回环测试的工具权限后，同一轮 4 项通过。没有改动监听范围或使用现场服务。
- 首次正式旧回归 9 项通过，独立副本随后在 `cli_refreshes_input_and_freezes_revision_until_restart` 复现 SIGINT 没停止，测试超时后其 `Drop` 只回收本次产品进程。日志中 restart 已产生正确的 r2 轮次，但继续轮询、没有正常关闭行。调整信号注册位置后重新构建两份候选及运行测试。新测试也实际运行节点/边倒序且省略 layout 的等价图，以断言同一业务结果和不同文件 SHA。
- 修正信号后的独立副本 4 项新、9 项旧均成功。随后的正式新矩阵有 1 项失败，脚本本应给出 `http_status`，实际观察为 `http_communication`。HTTP 夹具原先未设置 accept 后 socket 的阻塞模式，读失败会放弃该连接。修正仅在新夹具显式设置阻塞与 1 秒读写上限，正式和副本的新矩阵重新运行均通过。

## 正式工程与独立副本验证命令

正式 cwd 为 `field-flow/field-flow-rust/`，`V=/private/tmp/ff-006-dev-xd8TnW`；副本 cwd 为 `$V/independent/project`，用 `V=/private/tmp/ff-006-dev-xd8TnW/independent/verify` 保持独立的 build、证据和状态目录。所有 Cargo 命令固定使用锁和离线缓存。以下矩阵按顺序使用自有合成端口。

```sh
cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir "$V/product"
"$V/product/release/field-flow" config validate --config config/flow-json.yaml --flows-dir flows
TMPDIR="$V/tmp" FF004_EVIDENCE_ROOT="$V/ff004" FF005_EVIDENCE_ROOT="$V/ff005" FF006_PRODUCT="$V/product/release/field-flow" cargo test --locked --offline --features test-fixture --test flow_json --target-dir "$V/test" -- --test-threads=1 --nocapture
TMPDIR="$V/tmp" FF004_EVIDENCE_ROOT="$V/ff004" FF005_EVIDENCE_ROOT="$V/ff005" cargo test --locked --offline --features test-fixture --test cli_contract --test catalog_compatibility --test basic_examples --target-dir "$V/test" -- --test-threads=1
```

新矩阵启动各自无 feature 的 release 二进制，测试夹具动态绑定回环端口，以新 YAML 绑定，实际调用 `state init --synthetic --mode dry_run` 与 `run` 并结束自有进程。旧回归沿用自己的产品、夹具入口和合成配置。最终夹具修改只影响 `flow_json` 构建目标，独立副本的旧目标结果沿用更改前同产品候选的实测结果。

静态自检执行 `git diff --check -- .`、8 个受影响 Rust 文件定向 rustfmt check 以及正式/副本 `rsync -anic --delete --exclude target --exclude .git --exclude .DS_Store`；无补丁空白问题和副本差异。共检查 112 组本地文档链接、三个双语说明对及四个 locale 键。

## Developer handoff 与验收对应

正式工程和独立副本的 release build、只读 CLI validate、新测试与三项旧测试目标均已实际完成，exit 0。每份工程新测试 4 项、旧测试 9 项。命令原始日志及 SHA、样例 SHA、轮次结果与旧执行回归摘要见 [自检证据](evidence/r1-development/checks.json)（SHA-256 `45097b3461b5f560f7e07db7a5eb82b1442841079dff04afb456924515906670`）。两份 release 来自各自 cwd 和 target，二进制 SHA 分开记录。源码清单一致，样例预检报告逐字节一致。

| AC | Development 自检观察 |
| --- | --- |
| AC01 | 两份无 feature release 构建成功；`cli_contract`、`catalog_compatibility`、`basic_examples` 各 3 项通过。既有 demo01 的 dry_run 状态 `simulated=1` 且合成 S7 写 0，execute `confirmed=1` 且写 1；读回记录显示 INT16 42，重复和 unknown 等进入原回归。 |
| AC02 | 正式和副本 `config validate` 报告一致。测试切换 cwd 后绝对配置及流程路径的报告一致，缺省所需目录、文件缺失、链接、穿越、重复、超限和坏版本/字段/绑定被拒绝。 |
| AC03 | 两份实际产品均执行了节点及边倒序、无 layout 的等价图，结果相同、SHA 不同。坏入口/端口/边/引用、不可达/环、常量类型与未知版本被拒绝；独立的 `plc.read` 结构测试定位到 `flow.nodes[fetch]`。 |
| AC04 | 在真实回环 HTTP 服务观察两个不同的 GET。产品完成 `not_matched` 后按间隔获取下一次独立输入，再记录 `matched`。验证两次请求的时间、不同 round ID、同一冻结 SHA 与 `+08:00` 业务观察时间。 |
| AC05 | 十次故障轮均仅记录错误键，下一正常轮记录 `matched`。纯图的状态统计无命令记录、没有 PLC 事件和 gate 文件。HTTP 客户端原有错误映射保留，实际超时可见为 `http_communication`。 |
| AC06 | JSON GET 仍在延迟时，原手写流已进入 `simulated`。同一次运行内合成 PLC 被该手写流连接一次，PLC 读写计数均为零，图流结束后保留手写流唯一命令状态。真实写入路径由 AC01 的旧 execute 场景覆盖。 |
| AC07 | 无效预检 exit 2，旧 SQLite 字节一致、无新日志。运行中改文件仍使用原 SHA 和 revision，重启切换到新 revision、SHA 和分支。实际 SIGINT/SIGTERM 成功 exit 0，自有 PID wait 后确认不存在、运行任务 join、夹具线程 join、回环端口可重绑，测试组结束的固定端口检查无监听。 |
| AC08 | 工程双语文档及目录/命令示例已核对。发布二进制实际覆盖新矩阵，Development 命令与候选已持久记录。fresh Verification 待运行，CA 往返、Windows、现场及长稳为后续门。 |

向 fresh-context Verification 交接精确候选 `FF-006 r1`，正式工作树 HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`，80 文件清单 SHA `c27cfc526b868a2a1873b67a16bb9d4edfba144a827cc8968cb8181d4cccbddc`。本记录只为 Development 自检。独立 verdict 与 Human Owner 最终验收由各自角色完成。

## 资源和边界

Development 所有构建、复制、命令原始输出、synthetic state 与旧夹具证据保存在 `/private/tmp/ff-006-dev-xd8TnW`。首次正式回归的 `ff004`、`ff005` 目录移入同根 `first-formal-regression/` 保留，最终复跑使用新的空证据目录。失败样本及自检证据用于 fresh Verification，待独立 QA 与 Human Owner 阶段不再需要原始资料后，协调者核对再删除本根。持久证据保存在本任务 bundle。合成夹具仅本机回环，未接触真实 PLC、第三方服务或现有状态，也未执行发布、部署或 Git 写入。

遇到回退时先停进程、保全配置和状态/日志，再移除 YAML 的两项图选择或恢复本任务自身差异。纯图配置撤除图选择后必须换回原先有效的手写配置方可启动。无需清空数据库或回滚既有设备效果。

## AC03 返工与第二次 Developer handoff

首次 QA 在两个正式/复制产品上独立复现了悬空边诊断只报告文件名，要求按 AC03 定位具体错误。[首次独立 QA](checklist.md) 于本次交接时 SHA-256 `486063697e15f99d747ad32ee47ec41ed1e6dde847f7091d609a120e6e39d1bd`。以上初次 Development 记录和原证据保留。准确诊断来自原批准规格，无需改 revision 或验收标准。

本次只改 `src/config/flow_json.rs` 和 `tests/flow_json.rs`。诊断路径由文件名加具体边索引和字段组成，例如 `flow_files[demo01.json].flow.edges[2].to_node_id`。缺失的边按所需源节点及端口定位；节点版本/类型、入口引用、端点引用、条件字段/布尔常量、重复分支目标及错误终点也返回其具体路径。两个悬空边复现用例的 `error_key` 均保持 `config_flow_edge`。无效文件仍在状态、日志及连接打开前拒绝。新增精确断言验证 18 个配置变体与不支持的 `plc.read` 结构。

最新候选仍为未提交正式工作树，HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`。两个工程源的 80 文件完全一致，首次候选到返工候选仅上述两文件不同。[返工源码清单](evidence/r1-development/source-sha256-rework-ac03.json) SHA-256 `db05105914d4e82bf0ae1728d6f379098b255e676bce7724ca2b468935636eec`；[返工自检证据](evidence/r1-development/checks-rework-ac03.json) SHA-256 `40a3bfcbb8fe641733e8bf914c501e24d1b9619a754909c9bd533e384304a67c`。

正式与副本分别运行 `cargo build -j 3 --locked --offline --release --no-default-features --bin field-flow --target-dir "$V/product"`，均 exit 0。`V` 分别为 `/private/tmp/ff-006-dev-xd8TnW/rework-ac03/formal` 和 `/private/tmp/ff-006-dev-xd8TnW/rework-ac03/copy`，副本源码在副本 `V/project`。分别用 release CLI `config validate --config config/flow-json.yaml --flows-dir <目录>` 运行合法样例和两份独立变体：合法 exit 0，坏边 0/2 均 exit 2，四份拒绝报告分别精确定位 `edges[0].to_node_id` 或 `edges[2].to_node_id`，两个工程各自对应的报告逐字节一致。输入副本 SHA 和原报告见返工自检证据。

为使用现有离线编译缓存，测试 target 分别为 `/private/tmp/ff-006-dev-xd8TnW/test` 与 `/private/tmp/ff-006-dev-xd8TnW/independent/verify/test`。本次运行的环境 `TMPDIR`、旧证据根、`FF006_PRODUCT` 则置于各自返工 `V`。执行 `cargo test --locked --offline --features test-fixture --test flow_json --test cli_contract --target-dir <对应测试target> -- --test-threads=1 --nocapture`，每份 7 项、exit 0。定向 rustfmt、`git diff --check`、复制树校验均成功。涉及回环的测试串行且前后无固定端口监听，临时根随原自检资源保留至复验结束。`catalog_compatibility` 和 `basic_examples` 的首次证据保留；这两个目标及其运行的手写流与状态路径未修改，返工自检没有重跑这两个目标。

请 fresh-context Verification 针对最新 manifest 独立复核 AC03，并记录新候选的最终 QA 状态。CA 实际导出/重导入、Windows、现场及长稳仍 pending。Development 不授予最终验收。
