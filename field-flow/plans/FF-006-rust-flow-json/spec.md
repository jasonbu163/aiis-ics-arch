Task ID: FF-006
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 FF-006 r1 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: Rust Field Flow 显式加载有限流程 JSON，并以 demo01 的 HTTP 命令验证判断分支及下一轮重读
Owner: Field Flow
Acceptance Chain Reference: FF-006 r1 精确范围批准 -> Development -> fresh-context Verification -> Human Owner 最终验收
Related Task: FF-001 r4; FF-004 r2 A; FF-005 r1 A; ARCH-AW-006 r2; ARCH-AW-009 r2

# FF-006 r1：Rust 接入流程 JSON 的首个只读案例

## 1. 决定、范围和现状

Human Owner 要求先按 STD 形成规格：首版只做 Rust，用 demo01 验证读取和判断分支，不符合结束本轮、下一轮重读；保留手写流，CA 导出后的往返验证后续再做。Human Owner 已精确批准 FF-006 r1 的实施范围，见文末批准登记；尚无 Development 或独立 QA 结论。

本轮拟实现一个**只读的有限图子集**：HTTP GET 读取 demo01 命令 → 比较本轮 `ready` → 输出 `matched` 或 `not_matched` 并结束。`matched` 只是可观察的分支结果，不写 PLC、不调用 PLC driver、不发送 POST，也不创建命令执行记录。此案例与现有手写 `demo01` 共用命令格式和校验，**不是**改写原手写流的 HTTP→PLC 行为。

Rust 的 [demo01](../../field-flow-rust/src/app/demo01.rs) 目前调用有界 [HTTP](../../field-flow-rust/src/infrastructure/http.rs)，再通过 `Input::intent` 和 `Execution` 处理写入；[runtime](../../field-flow-rust/src/runtime.rs) 已按独立 flow task 完成一轮后等待。现有 [v2 配置](../../field-flow-rust/config/catalog-demo.yaml) 显式声明 PLC 和手写 kind，当前还不会加载流程图。FF-004 r2 A 的 PLC 目录与多 PLC 本地切片已被 Owner 接受，其旧状态、任务和 driver 限制按原 bundle 保存。

本规格对照 [ARCH-AW-009 r2 §5](../../../plans/ARCH-AW-009-ca-flow-editor-json/spec.md) 已获批准的 CA 候选设计，采用 `aiis.flow`、`schema_version`、`flow`/可选 `layout`、节点 `id/type/version/config` 和 `from_node_id/from_port/to_node_id` 外形。**CA 贯穿案例是 `plc.read → int16 比较 → HTTP GET`，不在本轮 FF 节点集内**；本轮示例是 HTTP 命令 `ready: bool` 判断。CA HTTP 节点如何声明响应字段、布尔常量及其类型化校验尚需双方以真实产物对齐；此处的 bool 子集是 FF 候选，不称已获 CA 兼容或冻结共同合同。CA 实际导出同一文件 → FF 执行两分支和重读 → CA 再导入的联合验证独立 pending，不阻本次 FF 本地验收。

## 2. 精确写入面和依赖

| 阶段 | 允许写入与责任 |
| --- | --- |
| 当前 PM | 仅本 `spec.md`。主协调依据本草案机械登记 FF 及仓库双语任务索引，不提前创建 Development/QA 记录。 |
| 获批后的 Development | `field-flow/field-flow-rust/src/config.rs`、`src/config/runtime_v2.rs`、新增 `src/config/flow_json.rs`、`src/runtime.rs`、`src/runtime/catalog.rs`、新增 `src/app/flow_json.rs`、`src/app/mod.rs`、`src/commands.rs`、`src/infrastructure/http.rs`、`src/domain.rs`；新增 `tests/flow_json.rs` 及该测试独立所需的 `tests/flow_json_support/**`；新增 `config/flow-json.yaml`、`flows/demo01.json`；必要时仅改本工程 `README.md`/`README.zh-CN.md`、`USER_GUIDE.md`/`USER_GUIDE.zh-CN.md`、`config/README.md`/`config/README.zh-CN.md`、`CODE_INDEX.md`、`locales/en-US.json`/`locales/zh-CN.json`。受影响源码与文档仅做本需求必要改动。 |
| 角色记录和导航 | Development 获批后创建本 bundle 的 `tasks.md` 和真实脱敏 evidence；实际 handoff 后独立 Verification 创建 `checklist.md` 及自身真实证据。主协调机械同步 FF 及根任务索引。 |

沿用 Rust `rust-version=1.89`、现有 Cargo manifest/lock、Tokio、reqwest、serde/serde_json、serde_yaml、SQLite 等锁定依赖；不新增或升级依赖、不改 `Cargo.toml`/`Cargo.lock`。运行和测试不依赖 CA、DS、Python、C# 或兄弟工程；只在自己的 `/private/tmp/ff-006-<unique>/` 创建合成状态、构建和证据。`rust-runtime`、`aiis`、`project-governance` 用于后续角色；修改面涉及用户文案加 `i18n-workflow`，源码/索引加 `code-document-indexer`。本 PM 阶段只做文档/路径/静态检查。

明确保护原手写 app、原 CLI 分派、旧配置/测试、原 State/Execution/Owner/driver、旧 bundle 及任务外工作树。`src/domain.rs` 或 HTTP 修改仅允许抽出可复用的命令读取校验，原 `Input::intent`、物理目标/配置摘要、T1/T2/T3、unknown 和错误行为通过回归证明保持。不得通过虚构 PLC/target 构造写入意图。

## 3. 流程文件与选择

运行部署目录保留 `flows/`。每条流一份 JSON，由配置显式列出文件名；不扫描、不热加载。命令行新增 `--flows-dir <目录>`，该目录为**流程文件解析根**，是相对当前 shell 工作目录或显式绝对路径，与 `--config` 文件所在目录独立；流程文件名只接受单个 `valid_id` 加 `.json`，不接受绝对路径、路径分隔符、`.`/`..` 或符号链接。`--flows-dir` 自身以及流程文件须为真实目录/普通文件，不跟随符号链接；目录不存在或不可读在预检失败。运行开始时读取、校验并冻结原字节 SHA256 和执行语义，运行期间不重读文件。CLI 无参/`--help` 仍零读取、零副作用。

仅在主 YAML **v2** 增加两项可选字段 `flow_files` 和 `flow_http_endpoints`，两者需成对出现。旧配置两者均缺省时走原行为；v1 不接受新增字段。`flow_files` 为 1..8 个唯一文件名，示例 `demo01.json`；`flow_http_endpoints` 为 1..8 个唯一 `id`，每项恰有 `id`、`base_url`、`source_id`、`input_max_age_ms`。`base_url` 是无凭据、query、fragment 或非根 path 的 HTTP(S) origin；图内 `path` 是 `/` 开头的相对路径，不允许 `//`、`..`、反斜线、`%`、query、fragment 或变更 origin。`source_id` 沿现有 valid_id，`input_max_age_ms` 为 1..60000。只使用 HTTP GET 和空 query；生产地址与凭据不进入流程 JSON。

纯图配置可使用 `plc_files: []`、`plc_runtime: []`、`flows: []`，但必须有合法 `flow_files`；不存在图文件时仍使用原 v2 非空及完整校验。手写流与图流可并存并各自独立调度，合计 1..8 条，所有 flow ID 在两类间唯一。手写流存在时沿原 PLC 目录、预算及能力验证；图流本身不请求 PLC、也不等待 PLC ready。配置无图时 `--flows-dir` 不是运行前提。所有引用文件和绑定完整预检成功后才打开状态库、日志、owner 或 HTTP；一个失败就整体拒绝。`config validate --config <主配置> --flows-dir <目录>` 只读并返回有界问题信息与 SHA，不打开状态、日志或网络；`run --config <主配置> --state-dir <已初始化目录> --flows-dir <目录>` 运行。现有 `state init --synthetic`、dry_run/execute 区分及无图 CLI 保持原义。

拟提供 `config/flow-json.yaml`，其中 HTTP 示例值如下；其他现有 `http`/`shutdown_timeout_ms` 沿当前范围和关系。`base_url` 和端口仅为示例，实际测试使用测试自有回环 HTTP 端口。

```yaml
schema_version: 2
instance_id: ff-rust-flow-json
plc_files: []
plc_runtime: []
flows: []
flow_files: [demo01.json]
flow_http_endpoints:
  - {id: demo_feed, base_url: "http://127.0.0.1:34880", source_id: demo01-feed, input_max_age_ms: 10000}
http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
shutdown_timeout_ms: 15000
```

## 4. 有限 JSON 形状与执行

以下是本轮工程内拟提交的 `flows/demo01.json`，不是 CA 已导出的文件。首版只接受一张由一个 `http.request`、一个 `condition.compare`、两个 `end` 组成的单入口无环图；节点 ID 和数组顺序可变。`http.request` 的 `next` 指向条件，条件 `true`/`false` 各接一个不同 end；end 无出口。`end.config.result` 分别为 `matched` 和 `not_matched`。保留节点 `version: 1`，只支持下列 config、空 query、布尔 `eq`，不支持表达式、任意 JSONPath、自定义代码、PLC/POST/其他节点。任一不支持能力准确定位后在启动前拒绝，不能跳过节点。

```json
{
  "format": "aiis.flow",
  "schema_version": 1,
  "flow": {
    "flow_id": "demo01_read_condition",
    "revision": 1,
    "trigger": {"type": "interval", "interval_ms": 500},
    "entry_node_id": "fetch",
    "nodes": [
      {"id": "fetch", "type": "http.request", "version": 1, "config": {"endpoint_ref": "demo_feed", "method": "GET", "path": "/demo01/command", "query": {}}},
      {"id": "check", "type": "condition.compare", "version": 1, "config": {"left": {"node_id": "fetch", "field": "ready"}, "op": "eq", "right": {"type": "bool", "value": true}}},
      {"id": "yes", "type": "end", "version": 1, "config": {"result": "matched"}},
      {"id": "no", "type": "end", "version": 1, "config": {"result": "not_matched"}}
    ],
    "edges": [
      {"from_node_id": "fetch", "from_port": "next", "to_node_id": "check"},
      {"from_node_id": "check", "from_port": "true", "to_node_id": "yes"},
      {"from_node_id": "check", "from_port": "false", "to_node_id": "no"}
    ]
  },
  "layout": {"nodes": {"fetch": {"x": 0, "y": 0}, "check": {"x": 200, "y": 0}, "yes": {"x": 400, "y": 0}, "no": {"x": 400, "y": 150}}}
}
```

文件为 UTF-8 无 BOM、最大 64 KiB、最大嵌套 16 层；各对象闭合、拒绝重复/未知键、非法数值词法、未知 schema/node version、非法 ID。`revision` 为正整数；间隔为 100..10000 ms。可选 layout 仅允许 `nodes` 中已声明节点对应的有限数值 `x/y`；省略 layout 或更改坐标不改变执行分支。不能解析或校验的 layout 明确拒绝，不默默丢失。文件来源、布局和 revision 不改变既有手写命令的效果身份。文件修改方应遵循 CA 候选的新增 revision 约定；本轮 FF 不维护跨重启 revision 注册表，也不能检测先前运行的同 ID/revision 内容冲突。CA 候选也记录执行语义摘要，但其规范化规则尚未冻结，本轮仅承诺记录原文件 SHA，不声称摘要兼容。

每轮执行一个真实 HTTP GET，复用现有总/连接/池/响应大小预算、禁代理和重定向。响应只接受 HTTP 200、JSON、UTF-8，必须是现有七字段命令；本轮仅输出经校验的 `ready: bool`。`schema_version=1`、`source_id` 必须匹配绑定。`ready=false` 时 `command_id/value/issued_at_ms/expires_at_ms` 均须为 null；`ready=true` 时需合法 ID、INT16、原始发出/过期时间，时效与当前 demo01 一致。重复键、错误类型、缺项、非 200、超时、无效或过期命令属于该轮错误，不将其当 false 或复用上一轮值。两分支严格比较 bool，不把 0、1、字符串、null 转换为布尔。

一轮只保留自己的输入/输出；结果记录 `flow_id`、`revision`、唯一 round ID、文件 SHA、`matched`/`not_matched` 或稳定错误键，不记录完整 HTTP body、命令值或凭据。每条流同一时刻最多一轮，本轮结束后等待 `interval_ms` 再触发，不补跑、不重叠；false 到 end 后下一轮**重新 GET**，不是检查旧值或当前轮原地重试。慢 HTTP 不占 PLC 执行位；多个独立流及其他 PLC 按现有 runtime 监督。SIGINT/SIGTERM 关闭接纳和任务后真实 join；新图不创建 driver、PLC I/O、PLC 写、执行命令记录或独立可写库。

## 5. 验证方法和验收

以下为批准后拟执行内容。Development 使用 Rust 工程现有锁和任务专用 target；必要的已有缓存不可用时如实记 blocker，不擅自改依赖或使用其他语言的夹具。新测试只监听 `127.0.0.1` 自有临时 HTTP 端口，旧 demo01 回归仅用现有合成 S7/HTTP fixture 及其记录端口，不连接真实设备或第三方。测试前检查端口占用，不能以终止他人进程解决冲突。使用新 synthetic state，保留已存在状态/日志；验收与产物均需在正式源码及独立复制源码分别可复现。

拟执行入口，`D` 指执行者新建的任务专属绝对目录；正式工程和 copy 分别使用不同的 `D`。先创建 `$D/tmp`，以 `TMPDIR`、`FF004_EVIDENCE_ROOT`、`FF005_EVIDENCE_ROOT` 将现有回归的自有临时和证据限定到该目录，`--flows-dir` 在相应 cwd 下显式给出；这是未来命令，不是本 PM 阶段的运行结果：

```bash
cd field-flow/field-flow-rust
mkdir -p "$D/tmp"
cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir "$D/product"
TMPDIR="$D/tmp" FF004_EVIDENCE_ROOT="$D/ff004" FF005_EVIDENCE_ROOT="$D/ff005" cargo test --locked --offline --features test-fixture --test flow_json --target-dir "$D/test" -- --test-threads=1
TMPDIR="$D/tmp" FF004_EVIDENCE_ROOT="$D/ff004" FF005_EVIDENCE_ROOT="$D/ff005" cargo test --locked --offline --features test-fixture --test cli_contract --test catalog_compatibility --test basic_examples --target-dir "$D/test" -- --test-threads=1
"$D/product/release/field-flow" config validate --config config/flow-json.yaml --flows-dir flows
"$D/product/release/field-flow" state init --synthetic --mode dry_run --state-dir "$D/state" --instance-id ff-rust-flow-json
"$D/product/release/field-flow" run --config "$D/run.yaml" --state-dir "$D/state" --flows-dir flows
```

实际端到端运行时先启动本任务合成 HTTP 服务并将其端口写入**新合成配置副本** `$D/run.yaml`，保持同一 `instance_id`；观察指定轮次后向自有进程发送停止信号、等待退出并记录 PID、端口及本任务新建目录。不得将上方示例端口假定为空或用真实服务代替。另记录正式树与单工程 copy 的清单/hash、命令、退出码、测试数、问题定位和回收条件。

| AC | 精确通过标准 |
| --- | --- |
| AC01 | 正式 Rust 工程与不依赖兄弟工程的 copy 均锁定构建并非零测试；旧 no-args/help、v1/v2 手写 kind、旧 CLI/配置及原手写 demo01 的写入路径通过现有合成回归。manifest/lock、旧状态 schema、身份和原失败历史保持。 |
| AC02 | 显式 `--flows-dir` 从选定目录加载唯一 demo01 JSON；从不同 cwd 使用绝对路径得到相同文件 SHA 和结果。无文件、目录/文件 symlink、穿越、重复文件/ID、超限、未知字段/版本、坏绑定均在状态/日志/连接前拒绝。无图旧配置不要求新参数。 |
| AC03 | 不同节点数组顺序、可选 layout 的两个合法文件结果相同；缺入口/边/分支、环、悬空/不可达节点、非法端口/引用、错误常量类型、未知节点版本和 CA 的 `plc.read` 样例明确拒绝并定位。不能把 `plc.read` 拒绝误报为 CA/FF 已往返。 |
| AC04 | 真正 CLI 配合本任务自有 HTTP 夹具，依次返回合法 `ready=false`、随后合法 `ready=true`；服务计数至少两次不同 GET，两个不同 round ID 先 `not_matched` 再 `matched`，两轮间隔按完成后等待，单流无重叠。不能用同一响应/缓存或重复检查旧上下文替代新 GET。 |
| AC05 | 缺字段、重复键、错误 source、无效 bool/INT、null 冒充值、时间过期、非 200、非 JSON、超时都产生对应轮错误，不输出 matched/not_matched，不沿用前一轮；下一正常轮可重新 GET。真实测试证明图流不生成 PLC owner/driver/连接/读写或 commands 表记录。 |
| AC06 | 一条手写流与图流同进程互不覆盖 ID；慢 HTTP 的图流等待时另一手写流仍可推进，同流无重叠；混合配置只在旧手写流需要时创建并复用旧 PLC owner，图流无 PLC I/O。原手写 demo01 dry_run/execute 的有效输入、重复和状态身份回归不变。 |
| AC07 | 图文件预检失败不接触已有库/日志/网络；运行过程中修改文件不改变当前冻结轮次/后续轮次，显式重启才读取新文件。停止后自有任务、HTTP 和状态线程真实退出，PID wait 与回环端口重绑定证据成立；异常/强制退出不得记正常。 |
| AC08 | 本工程双语入口说明 flows 目录、完整启动及错误、手写流保留与图只读范围；标准/用户可见文案双语对称。实际 Development 与 fresh-context Verification 分别记录命令、代码差异、正式/复制树、验收结果和资源；CA 往返、Windows/现场/长稳另列 pending。 |

## 6. 风险、回退与批准点

本轮严格冻结的是 FF 支持子集，CA 的 `bool` 类型、HTTP 输出字段以及合同实际 schema 尚需双方向量共同确定。若 CA 导出结果与此不符，先报告差异，不以字段丢弃、类型强转或静默降级冒充互通；新增 `plc.read`/条件整数、schema 或节点语义需另行明确范围。

只读 GET 仍可能对被调用服务产生业务效果；本次验证只用自有 HTTP 夹具。保护原 state 的回退为先停止该进程并保全配置、状态/日志，再移除图文件选择或恢复本任务归属的实现；不清空 SQLite、不迁移或重置旧命令、不回滚设备效果。`--execute` 在混合场景继续沿旧手写流的既有语义，不能授予图写权限。

2026-11-24，PM 根据 Human Owner 请求初次创建 r1 草案时尚未获得实施批准。PM 只做静态文档核查，不执行源码、测试、schema、编译、监听或网络。审批后由主协调实际调用 Development 创建 `tasks.md` 并实施，真实 developer_handoff 后再启动 fresh-context Verification，最后由 Human Owner 决定验收。

**PM → Human Owner 批准点：FF-006 r1。** 包括仅 Rust 的 `aiis.flow` 有限只读图、显式 `flows/` 选择及本地 HTTP 绑定、HTTP 命令验证和布尔双分支、false 后下一轮重新 GET、手写流并存与兼容、§2 精确写入面及 AC01–AC08。实际 CA 文件往返和更广泛节点不在首轮。

## Human Owner 范围批准登记

2026-11-24（Asia/Shanghai），Human Owner 明确指示：“批准 FF-006 r1，按 STD 开始开发。首版只做 Rust 的只读 demo01 JSON 流，条件不满足就结束本轮、下一轮重新 GET，保留原来的手写流。完成后进入独立 QA，等 CA 导出实际文件后再做往返验证。”本登记只确认精确 r1 范围批准；Development 事实、独立 Verification 和 Human Owner 最终验收须分别在后续据实记录。
