Task ID: FF-004
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA3 -> Human Owner final acceptance for exact FF-004 r2 A rework2; F-QA2-001/002 independently closed; QA1/QA2 failure history retained; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 每PLC独立JSON合同、Rust首切片的S7 int16目录加载与多PLC点位调用、Modbus结构校验及DS导出边界
Owner: Field Flow
Acceptance Chain Reference: FF-004 r2 exact A scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance

当前有效结论为文末 QA3：`qa_passed`（AC01–AC14；F-QA2-001/002关闭），Human Owner最终验收待定；以下 QA1/QA2 从原QA1主标题至QA2末尾的全部正文及失败、输入、数量、指纹与资源历史完整原样保留。

# FF-004 r2 A 独立 Verification QA1

**QA1 verdict：qa_failed。** R01/AC02 的 YAML anchor/alias 防护可被合法 plain scalar 中的引号字符绕过，同一错误也误拒合法等价配置。另有指南证据路径和 Development 原始输出索引两项不准确材料。完整 Rust 回归虽通过，不能覆盖这些独立复现。QA 未修改实现、测试、spec、tasks、配置或其他仓库文档；本次失败历史必须保留。

## 验证依据与独立性

- 实际 `verification` 角色：`/root/ff004_verification_r2`；由唯一协调者 root 在真实 developer_handoff 后以 fresh context 调用，不继承 Development 对话推理，不创建子 agent/通知窗口或发送邮件。角色 TOML 只是 contract_only 配置证据，不把配置 model/effort 当独立遥测，不宣称平台 ACL/强制路由。
- 已独立消费根 AGENTS、README/PLAN 双语、canonical workflow/verification TOML、FF 与 Rust 最近 README/PLAN、完整 spec/tasks（包括封存 r1）、当前实现、相对原 dirty 基线 diff、Development 附件和可用原始输出。采用 project-governance、aiis、plc-point-mapping、rust-runtime、i18n-workflow、code-document-indexer 及适用的日志/结构/资源参考；仅验证。
- 唯一有效范围为精确 FF-004 r2 A。Owner 原话“批准 FF-004 r2 A，按方案开始开发，完成后按 STD 进入独立 QA。”由当前已批准 spec 记录；r1、FF-005 接受、FF-001/002 QA、FF-003 draft 互不转移批准/验收。
- 正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD=`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。相对协调者 C=`/private/tmp/ff-004-r2-coordinator-6ejzumcp/original` 的原 dirty 基线审计，未把 FF-005 既有 dirty 归入本任务。
- Q=`/private/tmp/ff-004-r2-qa-vy1d8rsr` 是 QA 自有资源根；D=`/private/tmp/ff-004-r2-dev-IVyzcc` 只读供复核，未复用其 target、可执行文件或状态来证明独立通过。

| 固定输入 | SHA256 / 数量 |
| --- | --- |
| 当前 owner_approved spec | `a7418cfe8f34515719beb50d9d901f42d7a283e2b33c61a2a57b129104a7870e` |
| 当前 developer_handoff tasks | `a28f32199809b9ec0c4aa3d2eb5d99b8e21e381137c67cfbc562d8f00e7bbb66` |
| handoff.json | `4bac72e042dad24053be8b1a6c0b22e1aab1d5faf41093fb7b825309a2721335` |
| implementation-manifest.json | `7de1ebec3add4789dbcd57c8320b68c38328e594b928ffba18197e84185c20e0`，38 允许/37 实改 |
| candidate-manifest.json | `8de682e0be25209e9ca98995e500a5573ef86f96be3897857e1de044ab9d5994`，86 文件匹配 |
| copy-source-manifest.json | `ace817921fbd1f83cd032c3998b07c4f825648367f423d69ffd93c0c706e08c8` |
| C/baseline.json / intake-input.json | `6493e5b7ca1024bff6372e07725514726237e8da9bae4ba3f02c38a592e953ef` / `571cb5109f02286b998ab0d3accba469aafeffab8c839321b5f5056302474e05` |
| 逐行实施 diff | `613886aba5244cdc136a3f29d730fdb8790445c0ad85a7fe2a583045ddc9ec09`，192200 字节；由 C/original 重新生成后与交接逐字节相同 |

初始及结束审计均为：119 个 intake hash 全部匹配；776 个非本实施/导航/spec 既有文件及 3 个隐藏保护文件原字节不变；独立 `Q/copy` 74 文件与正式 Rust 的 intake 完全相同。Cargo.toml=`d28d9068b6804afe0f2605bdc5d90976a45e2e055881c771e26e7203291e8ea8`、Cargo.lock=`13404c36665fa46f50f40291e111bcb11e99b9ee8c13d29130004c9ef3d74fc6` 保持。r1 无损还原 42739 字节，SHA=`e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`。根 PLAN 整文件 hash 只作并行快照；本次结束时 119 项仍全匹配。

## 环境、命令与实际退出

macOS Darwin24.6 arm64；rustc1.89.0(29483883e)、Cargo1.89.0(c24e10642)、Apple clang17.0.0。沿现有锁、缓存与 native 链，所有 Cargo 命令均 `--locked --offline`，没有安装依赖/SDK/target 或修改清单。系统 Python 只编排、解析证据和编辑 QA 自有副本，不冒充 Field Flow Python 运行验证。

默认 sandbox 的八口 bind 检查 exit1，全部 `PermissionError(1, Operation not permitted)`，lsof 无监听；没有记产品失败或 pass。之后通过明确仅含获批本地模拟测试的安全执行方式，八口实际 bind/close exit0；所有协议场景串行且只使用 31102/31103/31880、34102/34103/34112/34113/34880。未换端口、杀占用者、访问真实 PLC/API/数据库、启动 DS/Backend/AW/CA、安装/迁移/部署或执行 Git 写动作。

下表 cwd 未另注时为正式 `field-flow/field-flow-rust`。绝对 Q 如上；同一行的成对构建各为一次真实命令，完整 argv 与输出在 Q/reports、Q/raw。

| 独立命令 / 自有目标 | 实际结果 |
| --- | --- |
| `cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir Q/formal-product` | exit0，190.838s；普通产品与 fixture 分开 |
| `cargo build --locked --offline --release --features test-fixture --bin ff-fixture --target-dir Q/formal-fixture` | exit0，160.417s |
| 同上两条，cwd=`Q/copy`、目标 `Q/copy-product` / `Q/copy-fixture` | 各 exit0，190.604/160.460s；未借父/兄弟/DS runtime |
| 同上两条，cwd=`Q/teaching`、目标 `Q/teaching-product` / `Q/teaching-fixture` | 各 exit0，134.857/127.854s；仅自有教程副本逐字接线 |
| `FF004_EVIDENCE_ROOT=Q/formal-catalog FF005_EVIDENCE_ROOT=Q/formal-legacy-basic cargo test --locked --offline --features test-fixture --target-dir Q/formal-test -- --nocapture --test-threads=1` | **exit0，30 个非零 test 函数=旧21+新9**。旧 basic_examples 的3函数内37个 CLI 场景不冒充37函数；lib/bin/doc 零用例不计。新 catalog 四目标 7.02+0.21+52.85+0.25=60.33s，<600s |
| `FF004_EVIDENCE_ROOT=Q/copy-test FF005_EVIDENCE_ROOT=Q/copy-legacy-unused cargo test --locked --offline --release --features test-fixture --target-dir Q/copy-fixture --test plc_catalog -- --nocapture --test-threads=1`，cwd=`Q/copy` | exit0，2 项/1.11s；copy 的实际启动另由自身无 feature 产品双模式证明 |
| `rustfmt --edition 2021 --check` 仅11个新增 Rust 文件 | exit0；未格式化旧源码或为了整树绿修改受保护文件 |
| `git diff --check -- <38件实施allowlist>` | exit0；相对 C 的真实 diff 重建匹配 |
| `python3 Q/scripts/boundaries.py`；`alias_repro.py`；合法等价误拒附加向量 | 边界32项中有预期退出的31项全部符合；另1项 builtin `!!str` 为观察项（spec未全面禁止标准tag，不据此判错）。引号特殊字符合法对照为0，真正anchor/alias普通对照为2；独立绕过及误拒见 F-QA1-001 |
| `python3 Q/scripts/manual.py formal` / `copy` | 均 exit0；正式 dry/execute 11.260/15.912s，copy 10.847/10.961s；四场产品/fixture/B shell均0、实际 SIGINT/wait、精确 PID 消失及五口 rebind |
| `python3 Q/scripts/manual.py formal s1` | exit0；独立普通 release S1 dry/execute 11.733/11.863s，分别11/12次原 body GET；原10秒 input age、原时间/身份不变，写0/1，产品/fixture均0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 Q/scripts/teaching_manual.py` | exit0；原指南 app/YAML/精确 assert 接线脚本逐字提取到 `Q/teaching`，dry/execute 3.034/2.737s，simulated1/写0、confirmed1/写1，原三口释放；正式源码仍拒 teaching01 |
| `rustc --edition=2021 Q/scripts/flow_observer.rs -L dependency=Q/formal-test/debug/deps --extern field_flow=… --extern serde_json=… --extern chrono=… --extern tokio=… -o Q/flow-observer-bin`；执行该 observer | 编译/执行均 exit0，完整 argv 在 Q/reports/flow-observer-compile.json。自有只读观察程序复用候选 Runtime 和正式无feature driver child，补充实际 CLI 矩阵的每flow样本证据，不替代 CLI load/调度 |
| `python3 Q/scripts/http_oracle.py` 最终独立 oracle | exit0；真实 HTTP status200、Content-Type、Content-Length、完整七键body，idle1/issue后11/重复issue拒绝后1=13 GET；S7 session/read/write全部0，与产品计数窗口分开 |
| `python3 Q/scripts/raw_audit.py`；只读补充 observer raw 解码 | 最终 exit0；独立解码 TPKT/COTP/S7、PDU-ref、地址/值/ACK/单PLC在途及 HTTP等待区间；不只采信 harness计数 |
| `python3 Q/scripts/resources.py` | 最终 exit0；426 个证据中的确切 PID 全部不存在，八口 lsof exit1空且逐一实际 bind/close 成功 |

辅助检查真实失败也保留：初版 HTTP oracle 错等 EOF 导致 socket.timeout，finally 已正常 wait/关闭该独立 fixture；改按 Content-Length 读取，在新独立 oracle 场景验证，未刷新任何产品场景命令。辅助 raw 汇总初版把指南演示也强加≥10 GET条件而断言失败；真实四场指南均9次，已明确降为演示证据，S1另有上述普通release11/12次及正式完整矩阵各10次，未把9改写成≥10。一次辅助 py_compile 因系统 pycache 指向只读缓存被拒，后用内存 compile 检查脚本；未改项目环境。受 sandbox shell 初始化影响的 `/bin/ps Operation not permitted` 为工具 shell 警告，与项目命令的实际 exit0 分开。

## 协议、状态、调度与资源量化结果

独立 raw 解码以自有运行产生的 request_hex/response_hex 为输入，逐项核TPKT长度、COTP参数TLV C1=0100/C2=0101、S7 ROSCTR/参数/数据长度、顺序PDU-ref与匹配ACK、DB/byte offset/两字节INT和每session不重叠IO。全部新增正常场景无trace截断；每PLC≤2000行/总≤4MiB。没有借产品codec生成预期帧。

| 自有完整矩阵场景 | 秒（含回收） / 实际事实 |
| --- | --- |
| S1 dry / execute | 5.484 / 5.515；各先有完整[12,1,56,34]及idle，再一次issue42；各10次原body GET，A/B写[0,0]/[1,0]；后值原样/[42,1,56,34]。ready/result/B及所有邻A5保持，原body expires-issued=60000，未刷新时间 |
| S2 three_readers | 5.387；A146个真实ReadVar、一个COTP session，三flow CLI成功计数各48；单PLC真实IO≤1。另服务场景收集60个互异原request_id/flow_id、generation1、+08响应样本；连接复用不是采样去重 |
| S3 B-off | 8.264；A86/B0 ReadVar，两PLC写0。A就绪到stop8.020624s，A混合响应最大间隔172.101ms；独立A流CLI累计48成功。B五次bootstrap连接拒绝的owner_backoff错误链精确归B，产品exit1；A正常reaped，无A forced。该故障不称全进程正常/零forced |
| S3 slow_setup | 8.442；A195/B39读，写0，正常0；A就绪到stop8.043318s。A首ReadVar完整响应sequence4先于B最终Setup sequence5；补充真实Owner观察当刻B=connecting，随后B ready，证明无全ready屏障 |
| S3 parallel_io | 5.425；A/B各23个真实读，各≤1在途，两个PLC区间实际重叠，无全局IO锁，正常0 |
| S4 slow_http | 8.323；A78读/写0，正常0；A就绪到stop8.022219s；实际HTTP进入至完成1200.368ms，其中12个A ReadVar完整响应，HTTP未占PLC位 |
| S5 confirmed兼容 | 1.820；旧typed v1实际写1/confirmed后原库接等价v2≥10轮仍总写1，原body/时间保持；有效TTL内变business_name实际CLI触发identity_conflict，原confirmed保留；schema/trigger相同 |
| S6 原in_flight same / alias | 0.767 / 0.806；原State API合法T1/T2后恢复unknown，同身份及point/flow/source/newcommand物理重叠阻写，写[0,0]；不相关读继续，原意图/schema保持。正常资源exit0不表示unknown解除 |
| S6 实写42后截断ACK | 2.300；真实写42一次、交付响应被截为17字节，无有效ACK证明；首轮协议故障exit1且无forced；原库restart读回42仍unknown，阻写且总写1。没有用完整hold_ack作正常关闭证据 |

为避免把混合A响应计数当A独立流最大间隔，另以自有 Rust observer实际保存该流原样本/身份及received_at，仍保留上表真实CLI证明：

| 补充观察 | A独立流窗口 / 成功样本 / 最大相邻成功间隔 | 关闭 |
| --- | --- | --- |
| B-off | 8.001027s / 77 / 174ms | 预期runtime_fault，实际回收0.153s；B无读写/A正常 |
| slow_setup | 8.001864s / 78 / 123ms | Ok，0.271s；A完成时B connecting，sequence4<5 |
| slow_http | 8.001497s / 78 / 104ms | Ok，0.261s |

read_points当前最近轮每flow≤16、总8flow≤128，未增加永久样本历史/SQL表；一次读失败的实际快照为success12/error/not_attempted，后两项无sample/value，无旧值拼接。5秒汇总每块≤4项；正式与copy最大ID/计数的实际Audit各4行，**最大3548字节（含外层/转义context/换行）≤4096**。成功样本响应完成received_at与观察observed_at为+08毫秒；旧UTC envelope/SQLite producer未触达，不声称时间整改完成。

只读validate/不兼容run核验：主/单文件均不写输入；Modbus单文件exit0/format_valid=true/runtime_compatible=false。完整组含未引用/disabled Modbus，以及同组非默认TSAP，均整体unsupported_protocol/exit2；纯非默认TSAP unsupported_connection/2。缺状态目录保持不存在；原合成合法in_flight库的数据库/日志/目录hash完全相同，连恢复写都未发生。实际源码命令链是Loaded::load→capability→State::open；无Modbus transport、34502连接或半组S7启动。

原Owner有界FIFO、独立flow outer-await、ready/queue/dispatch预算/400ms回收预留、ClockAnchor/TTL、旧Flow/Target/Intent摘要/Resource/Execution、driver/state/HTTP/S7基础实现及旧tests全受保护。完整回归包括五INT边界、真实ACK拒绝、queue/stop零下发、时钟/started、容量/audit/unknown与FF-005原37CLI场景。driver_process.rs:561–588的正常close实际await Child.wait并要求ExitStatus.success，owner join返回后才正常reaped；现有reaped事件没有独立exit_code，本QA没有编造。新fixture的Child try_wait成功状态（实际reap）/异常Child.wait和所有线程join源码及实际close_result/退出/PID/端口共同证明回收。B-off只按精确B bootstrap故障链预期，不能豁免A forced或不明forced。旧完整hold_ack限制未修复/未转为正常证据。

## QA1 findings（返回Development；不得静默修复）

### F-QA1-001 / AC02 / R01：YAML plain scalar引号导致防护绕过及合法等价误拒

位置：[src/config/catalog.rs](../../field-flow-rust/src/config/catalog.rs)107–118，尤其107–108无上下文地把plain scalar中的任意单/双引号当quoted scalar起始，后续状态与YAML真实token不一致。普通无feature产品SHA=`76f585bb53be5d5d8de14a42c6ea15e5309e6c895237a96d230aff40d8aa691c`独立复现。

复现A：将候选两个S7 JSON原字节复制到测试目录的plcs/（A SHA=`fcda187b9a72bd75720409a4a9b84c1feb0b4bb8c01f98af027e945fcad9535d`、B=`614e35946c63a622642d881b911b5c2f869e2840dd3ee8139e5d71e8a07a4b53`），下列保存main.yaml：

```yaml
schema_version: 2
instance_id: ff-rust-catalog-demo
plc_files: [plcs/s7-a.json, plcs/s7-b.json]
plc_runtime:
  - {device_id: s7_a, connect_timeout_ms: 3000, io_timeout_ms: 5000, queue_capacity: 16, queue_wait_ms: 2000, ready_wait_ms: 3000}
  - {device_id: s7_b, connect_timeout_ms: 3000, io_timeout_ms: 5000, queue_capacity: 16, queue_wait_ms: 2000, ready_wait_ms: 3000}
flows:
  - id: demo01
    kind: demo01
    business_name: synthetic_command_to_int
    interval_ms: 500
    get_url: http://127.0.0.1:34880/it's
    device_ids: &deps [s7_a]
    source_id: demo01-feed
    input_max_age_ms: 10000
    target: {device_id: s7_a, point_id: value}
  - id: read_a
    kind: read_points
    business_name: read_a
    interval_ms: 100
    device_ids: *deps
    reads: [{device_id: s7_a, point_id: value}]
http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
shutdown_timeout_ms: 15000
```

命令为 `Q/formal-product/release/field-flow config validate --config Q/boundaries/config/plain_apostrophe.yaml`，cwd=`Q/boundaries`；仅只读validate，无网络或状态操作。输入SHA=`999018454e4b433910ada55c1dac22a22bf6717e442b7e494d9d29b6ab6d56bb`。**预期2/config_yaml_alias；实际0/format_valid=true/runtime_compatible=true/issues=[]**，真正`&deps/*deps`已被解析/装配。只把URL改为`.../its`（SHA742fc7cd…）或把含apostrophe的URL加双引号（SHAc6040b39…），实际均2/config_yaml_alias。最初仅在http对象加anchor的向量也被接受；并非只对某个flow alias的偶发现象。

复现B：同一header/plc_runtime/http/shutdown和两S7 JSON；flows用下面无任何anchor/alias的两个demo01（不同物理目标，不重叠）：

```yaml
flows:
  - id: first
    kind: demo01
    business_name: first
    interval_ms: 500
    device_ids: [s7_a]
    source_id: first_feed
    get_url: http://127.0.0.1:34880/it's
    input_max_age_ms: 10000
    target: {device_id: s7_a, point_id: value}
  - id: second
    kind: demo01
    business_name: second
    interval_ms: 500
    device_ids: [s7_a]
    source_id: second_feed
    get_url: 'http://127.0.0.1:34880/q?x=a & b/* !'
    input_max_age_ms: 10000
    target: {device_id: s7_a, point_id: result}
```

命令同上，文件`Q/boundaries/config/valid_plain_apostrophe.yaml`；完整输入SHA=`5de4ed4dcb31d35ff068c2fc1fcd6ea6532114757a02c11846eaf43f427636f4`。**预期0；实际2/config_yaml_alias**。把第一URL加双引号后，其真实字符串语义相同，完整输入SHA=`de8e8f5c38da7ba9b854fe138916b0b296dee690bdcec0ca2ab074e06f6fb473`，实际0；将第一URL去apostrophe为its也0。第二URL内的合法`&/*/!`及空格不应被误认为YAML结构。

要求在原r2边界内修正严格YAML辨别并增加这两个方向及等价controls回归；不能简单禁止合法URL字符、删除alias禁令或改变v1旧规则取绿。QA未修改产品。新handoff后必须新的fresh Verification；本失败输入、输出和QA1历史保留。

### F-QA1-002 / AC13：双语catalog手册指向不存在的证据文件

[USER_GUIDE.md](../../field-flow-rust/USER_GUIDE.md)488行及[USER_GUIDE.zh-CN.md](../../field-flow-rust/USER_GUIDE.zh-CN.md)488行，要求从`product.jsonl`的driver_ready.context取driver PID；但437/508行真实命令输出为`$FF_RUN_ROOT/$FF_SCENE.stdout.jsonl`。独立正式/copy两模式实际只有dry.stdout.jsonl/execute.stdout.jsonl，product.jsonl不存在。照原路径无法完成关键driver PID核验；QA按真实stdout另行提取才完成回收核查，不能算原文正确。

最小返工：中英改为命令实际生成的路径，保持双语对称与原教程接线锚点，并明确“首个health状态已出现”与S1≥10次冻结body GET验收的边界。原手册四场各9 GET，仅证明操作演示/正常状态；本QA另以普通无feature S1各11/12 GET（全部在原TTL内）及完整矩阵各10补足AC05/12，不把9写成≥10。若指南本身宣称完成S1，则其停止/核对步骤也须满足原≥10条件，不能刷新时间/增TTL。

### F-QA1-003 / AC14：原始输出索引在文件结束前记录空hash

[evidence/r2-development/raw-output-index.json](evidence/r2-development/raw-output-index.json)228–230行将`D/seal-evidence.txt`记为0字节、SHA=`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；实际736字节、SHA=`8f3015b63f4bb099078e9dd0d446b154f70655f13c0e872640b7966da4e0c069`。实际内容为封存summary（11 scenes、37实施变更、776保护、103 PID及scene秒数），说明该输出被索引时尚未写完。

独立核验其余58/59 raw输出和31/31持久附件hash匹配；38实施/86candidate及119 intake也匹配。影响是交接索引不精确，并非这些协议测试输出或源码候选已失真。Development应在生产输出结束后形成准确新索引/新handoff，保留QA1旧索引/hash及原失败历史，不能覆盖本QA1消除失败。

## AC01–AC14 verdict映射

| AC | QA1结果 | 独立依据 / 适用边界 |
| --- | --- | --- |
| AC01 | pass | 正式/copy74文件、各自身锁定无feature产品/feature fixture构建、30+2非零测试及实际双模式；候选一致，无父/兄弟runtime依赖 |
| AC02 | **fail** | 普通严格/codec/容量/整数/重复/unknown/v1三kind/v2二kind向量通过，但F-QA1-001绕过与合法等价误拒直接违反R01 |
| AC03 | pass | 缺文件、重复/穿越/错cwd/symlink（主/末端/中间）、目录/FIFO、身份/跨DB点/越界/重叠/disabled/预算/依赖及未引用文件均preflight；冻结文件hash摘要匹配 |
| AC04 | pass | 单Modbus validate0但不兼容；整组Modbus（disabled/未引用/同组非默认TSAP）2且unsupported_protocol优先；旧in_flight状态及日志hash不动、缺目录仍缺，零owner/恢复/日志/网络 |
| AC05 | pass | 实际CLI初值/一次issue/后值/邻A5、raw COTP/PDU-ref/ACK/T3，普通release补充S1 11/12 GET，旧五INT边界回归 |
| AC06 | pass | Devices私有依赖子集、enabled点、顺序首错与success/error/not_attempted；最近16/128；实际maxAudit3548B/4块；+08响应观测语义，无旧值拼接 |
| AC07 | pass | CLI三流各48、补充60独立request/flow样本，A单PID/generation/session、raw IO≤1及两PLC区间重叠；原有界FIFO/outer-await，无共享采样或全局IO锁 |
| AC08 | pass | 三个实际CLI≥8秒；真实B connecting且A完整响应sequence4<BSetup5；补充每flow原样本77/78/78、gap174/123/104ms；HTTP1200.368ms内12个A响应；B-off明确负向分类 |
| AC09 | pass | 完整原预算/queued-stop/真实底层结束回归；新正常场景零forced、正常exit/真实join/reap、Child成功状态/PID/端口，15秒内回收；B-off仅B错误链预期，旧hold_ack限制保留 |
| AC10 | pass | v1/v2原typed摘要/Resource相同，改路径/顺序/display/source不新造效果；有效TTL内地址/大小/business变化冲突、原行保留，不宣称UUID自动迁移 |
| AC11 | pass | confirmed原库接v2≥10轮不再写；合法in_flight恢复unknown、别名/new identity物理阻写，读42仍unknown且总写1；旧schema/trigger/不可变字段原样，无DDL/清库 |
| AC12 | pass | 默认dry simulated1/写0；显式execute A一次匹配ACK+confirmed/B0；原body时间不刷新、唯一Execution路径；unknown/readback不作成功 |
| AC13 | **fail** | API/kind/能力/来源/DS缺口和locale/旧教程大部核准，但F-QA1-002的文件路径错误使原指南driver PID核验不可照做 |
| AC14 | **fail** | 实际fresh角色/保护hash/diff/资源及精确候选成立，但F-QA1-003索引不精确；本轮checklist为qa_failed，不授权Owner接受/发布 |

## 静态、DS与未验证边界

135个本地Markdown链接目标存在；6双语pair的代码块一致（USER_GUIDE各33，BUILD各1）；locale四键对称，11新Rust头注和自身CODE_INDEX覆盖通过；没有运行全局init/document或为了旧全仓governance诊断修改历史bundle。中英CLI help与空cwd product/fixture无参/help零副作用已实际核验（完整正式/copy测试及普通产品启动）；实现仅注册v1三kind、v2 demo01/read_points，正式teaching01拒绝。

只读核对DS Instance/Db/Point字段、called_tsap和revision/selected/loaded查询，确认UUID、byte/bit/length/enabled、原payload SHA与实际loaded事实分离；FF只接受合成DS source形状，不证明真实DS库/导出。当前DS exporter、Modbus通信/codec、Python/C#加载均未交付，S7其他类型/真实点表/权限也没有由结构声明得到证明。Python全部原字节保持且本轮not_run；C#无工程且FF-003 draft。Windows/Linux native、现场/托管/容量上线/长稳/签名/发布/部署/根公开schema及B/C另gate。旧UTC producer、bootstrap force及完整hold_ack限制均保留。

## 最终资源、保留与handoff

所有本轮构建、test、B shell、fixture、observer/oracle已结束。正常进程实际SIGINT/TERM后wait，native子进程成功状态与线程join、state/owner join由源码及实际返回联合核实；B bootstrap force和原故障回归按原分类有界reap，不算正常成功。最终426个证据中确切PID全部ESRCH、无非不存在/权限不明项；八口lsof各exit1空输出，逐一实际bind/close成功。旧harness新建76个FF-001前缀根目录按本轮前后差集与源码命名归属登记（含两个process_lifecycle目录；未按前缀批删），不清理历史/他人资源。

Q保留：自身74文件copy、独立teaching、六个产品/fixturetarget及正式test target、新合成状态、全部原始输出/失败报告/复现脚本和观察二进制；76个旧harness本轮根目录清单在资源报告。Q、D、C均仍有返工/新QA/Owner审阅或证据依赖，不删除任何资源；最终由唯一active coordinator按占用/归属/依赖审计回收。关键failure输入、数量、协议/状态/资源结果已在本checklist持久记录，不只留临时链接。

QA1交接给Development：在原r2 A allowlist内处理F-QA1-001/002/003；不触碰受保护driver/state/domain/Execution/旧tests或放宽AC。完成后由Development形成新精确handoff，再由root调用新的fresh-context Verification；本QA1 verdict/证据保持为历史。当前没有环境blocker，无qa_blocked或deferred-pass替代实现失败。Human Owner仅接收此独立失败结果供流程决策；**Human Owner final acceptance: pending**。

## QA1关键自有证据指纹（Q下，非新仓库附件）

| 报告 / 原输出 | SHA256 |
| --- | --- |
| `reports/intake-audit.json` | `63e509f6edcbd39eca853928b3d9e57624af110efa7cb6d7e2f1ae05053109dd` |
| `reports/protection-final.json` | `cdb2db5356120b2170c24a7b1cd9066ca1e10a014b24deb0b4e263f5c0ee6400` |
| `reports/static-audit.json` | `dcf8b9e3249bc4f8536c1a4feb10e2340958ececf29015b7e160d2abfd13931c` |
| `raw/full-formal.txt` | `dea66bb5ff11ef6511855387b230cc85d56052dff5c08316fc2f95cb129c58ef` |
| `raw/copy-tests.txt` | `e4ff99925cf76a2b9dca4c92beaf9df57ae47add8a66dbf8b7c6fce7de1f07aa` |
| `reports/full-test-groups.json` | `fad73ebd2f0b6737f4fb2fb9e9c130d8001ea5a62552011557a228d46ce9fb11` |
| `reports/boundaries.json` | `4de9f22609e3f2cc7a98b22523d258f9ef7fcd6a453eab3cc30c2918811e5857` |
| `reports/yaml-alias-repro.json` | `3c8d5d85ffca0b5d079e6e6e08983a85386f54277b3c47702ebbf783e8024128` |
| `reports/yaml-false-positive.json` | `33506825f0e0a118a23d3d723354c96b39126b56b82725f33b8f439ce08a3f98` |
| `reports/independent-raw-audit.json` | `a19861d7775afdd167a6913ed5659915652c1b6f42212c71cea016da1122692c` |
| `reports/observer-summary.json` | `32c060cdda810d8f3246d37898ffc92a13a9b5df13ed0a55e956f368bd79a5ca` |
| `reports/manual-formal.json` | `f5b143ac04caea85e073168b7f6329fa1f5e1f1c7428ec105beed884ec76d3a1` |
| `reports/manual-copy.json` | `99d0b9af7b39cff1ea5630c0f332c69dc1fd043edf66d1a2cf86d929387315a9` |
| `reports/manual-teaching.json` | `8976c2d7024e7c6429678dc1bfb9a7ef0bf79ed7a82f7e0bf2203696c1b6b6e2` |
| `reports/release-S1-quantitative.json` | `69375c8fc2d6810154d654c240a0b5d9b474125b28510f9902657ed64810a031` |
| `reports/http-oracle.json` | `096c0b902cc14a650e73f6ca74e2ed5227dbcde443d39b7ab9510d3f8823245d` |
| `reports/dev-attachment-audit.json` | `028725cbaa7e2a071edee010bb841dbd356a4861a75d98c3bdadd1410ba8cefe` |
| `reports/resources-final.json` | `8f7b1e1b60343f24c2da3f3ce2cbd702680582e6bb044f9c1afc676f485b74a6` |

QA1结束记录时间：`2026-11-04T16:56:10+08:00`（Asia/Shanghai）。本节为第一轮失败历史；后续返工/QA不能把它改写成初轮通过。

# FF-004 r2 A rework1 独立 Verification QA2

**最新 QA2 verdict：qa_failed。** 当前 rework1 已修复 QA1 五个同 SHA YAML 输入，并关闭 F-QA1-002/003。独立源语法复核仍发现两类真实 anchor/alias 绕过：非 LF 的合法换行与 flow mapping 引号 key 后无空白冒号。两项均违反原 R01/AC02，不能由 31 项完整回归通过替代。AC02 fail，其余 13 项在下述本轮证据及明确历史复核边界内 pass；没有环境 blocker，不记 qa_blocked、不降为 deferred pass。实现 failure 返回 Development；Human Owner final acceptance 仍 pending。

## QA2 独立性、冻结输入与范围

实际新 `verification` 角色为 `/root/ff004_verification_r2_after_rework1`，由唯一协调者 root 在 rework1 真实 developer_handoff 后以 fresh context 调用。未继承 Development/QA1 对话推理，未创建子 agent、通知 window 或发邮件；TOML 仅为 contract_only 配置证据，不将 model/effort 配置值当运行遥测，不宣称平台 ACL/强制路由。

独立消费根 AGENTS、根 README/PLAN 双语、canonical workflow/verification TOML、FF/Rust 最近 README/PLAN、完整 spec（含无损 r1）/tasks/QA1 checklist、实现、相对原 dirty 基线 diff、当前及历史测试材料。应用 project-governance、aiis、rust-runtime、i18n-workflow、plc-point-mapping、code-document-indexer 与适用日志/结构/资源参考，仅验证。Owner 对精确 r2 A 的明确批准及原 14AC/38 实施 allowlist 未改变；不继承 FF-005 接受或其他任务 QA。

正式树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD=`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。C=`/private/tmp/ff-004-r2-coordinator-6ejzumcp`，Q2=`/private/tmp/ff-004-r2-qa2-2jnzhw3m`。Q1=`/private/tmp/ff-004-r2-qa-vy1d8rsr`、D=`/private/tmp/ff-004-r2-dev-IVyzcc` 只读复核；未借用其 target、可执行文件或状态作本轮独立构建证明。只写本 checklist；实现、测试、配置、spec、tasks、导航及其他历史未改。

| QA2 精确输入 | SHA256 / 审计 |
| --- | --- |
| owner_approved spec | `a7418cfe8f34515719beb50d9d901f42d7a283e2b33c61a2a57b129104a7870e` |
| 当前 rework1 tasks | `aacdd237b2a59424abef7f7d65f6d37bd06acca0263ebf6ab07637f7bb7e7a82` |
| E1/handoff.json | `f10dccbf30ec9acb90e437ece5dc15847635acc67d62b0e326710c6d83f06e09` |
| E1/implementation-manifest.json | `7e9574a0d3da0bc08c2d6f803abb73b19b88c3fa6870e6d58ea82f89fdfa60cf`，38 允许、相对原 dirty 基线37实改 |
| E1/candidate-manifest.json | `16eba0b414ce53da09910b3336cd22dacc8a673a844052b7c7406e22efd0e313`，86项，根 PLAN 两件是并行快照边界 |
| E1/copy-manifest.json（真实文件名） | `df0ebdfb0199ff71c34cc2a016c5bdb0e4c37f01fc6d8ea8679327b7bb35b589` |
| E1/raw-output-index.json | `76061a6cb0299aab3810cc5afe3f367e14dba3442df00362550e72e6b21f02fd`，23/23 大小及 SHA 独立吻合 |
| QA1 原 checklist | `dc363a4675802ce710d08d10e108562a2efb96e4f6bfacf1dcf50b65e55fa00c`；从 QA1 主标题起原正文逐字节保留 |
| C/baseline.json / rework1-intake-input.json | `6493e5b7ca1024bff6372e07725514726237e8da9bae4ba3f02c38a592e953ef` / `e55e4d950cfed0eb427ce2d9a9681bf09f8c4aeda83b80dee57ff824a1f6cba0` |
| 从 C/original 重建的完整实施 diff | `06fa3b672ea33f2965f30f1d88e4318ac711785e75786e594c8d5f00bd867707`，与当前交接完整 diff 原字节相同 |

E1 为本 bundle 的 `evidence/r2-development-rework1/`。开始时146 intake全匹配；写 checklist 前最终144/146匹配，仅两件根 PLAN 整文件因其他任务行并行变化，FF-004 中英原行与开始读取值完全相同。candidate 中84个非根 PLAN 文件吻合，根 PLAN 的旧整文件 SHA 不冒充当前全仓冻结。正式 Rust/独立 copy 各74文件逐件吻合；清单 SHA=`d28d9068b6804afe0f2605bdc5d90976a45e2e055881c771e26e7203291e8ea8`、锁 SHA=`13404c36665fa46f50f40291e111bcb11e99b9ee8c13d29130004c9ef3d74fc6` 不变。776 个非本实施/导航/spec 既有文件、3 个隐藏保护文件、初轮33附件均保持；没有把 FF-005 原 dirty 归本任务。r1 仍可还原42739字节/SHA=`e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`。

相对 QA1 只有 `src/config/catalog.rs`、`tests/plc_catalog.rs`、Rust `USER_GUIDE.md`/`USER_GUIDE.zh-CN.md` 四件改变。其余 runtime、devices/read_points、fixture、owner/driver/Execution、基础协议/HTTP/state、旧测试及 Python 原字节保持。当前普通产品 SHA=`9d740fdbd8b527d0c766a48b008ba32f131141446dfcdb67c0744c1f5fa03053`；copy 产品 SHA=`8911dea57f68bd1141ae2024516760a227dd5ae3daef8144d10a5d47ce26e9dc`。二者各自从同74文件构建，不将不同构建路径的二进制 SHA 宣称相同。

## QA2 环境、实际命令与退出

Darwin24.6 arm64，rustc1.89.0(29483883e)、cargo1.89.0(c24e10642)、Apple clang17.0.0。全部 Cargo 使用现有锁和 `--locked --offline`；未安装依赖/SDK/target、改清单或全局环境。系统 Python 仅做文本、编排和证据解析，不是 Field Flow Python 工程验证。

默认 sandbox 八口 bind 全被 `PermissionError(1, Operation not permitted)` 拒绝，检查 exit1；lsof 未见监听。随后通过明确仅含本批准固定 loopback 测试的安全执行方式，八口 bind/close 实际 exit0。仅使用31102/31103/31880、34102/34103/34112/34113/34880，协议场景串行；无换端口、杀他人进程、真实设备/API/DB、DS/Backend/AW/CA、Docker、迁移、发布/部署或 Git 写动作。

下表未另注 cwd 均正式 Rust 工程。Q2 为上方绝对资源根，完整 argv/退出与原输出在 Q2/reports、Q2/raw；构建耗时为本轮单调计时。

| 独立命令 | 真实结果 |
| --- | --- |
| `cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir Q2/formal-product` | exit0，209.789s，普通产品不含 fixture feature |
| `cargo build --locked --offline --release --features test-fixture --bin ff-fixture --target-dir Q2/formal-fixture` | exit0，209.454s，与普通产品独立 target |
| 同两条，cwd=`Q2/copy`，目标=`Q2/copy-product`、`Q2/copy-fixture` | 各exit0，182.076/181.240s；独立74文件/自身清单与锁 |
| 同两条，cwd=`Q2/teaching`，目标=`Q2/teaching-product`、`Q2/teaching-fixture` | 各exit0，125.171/123.063s；仅自有教程副本按当前完整指南精确断言脚本接线 |
| `cargo test --locked --offline --features test-fixture --target-dir Q2/formal-test --no-run` | exit0/87.844s，只编译，未代替运行 |
| `FF004_EVIDENCE_ROOT=Q2/formal-catalog FF005_EVIDENCE_ROOT=Q2/formal-legacy-basic cargo test --locked --offline --features test-fixture --target-dir Q2/formal-test -- --nocapture --test-threads=1` | **exit0/215.402s，31非零函数=旧21+新10**；旧FF-005三函数内37份实际CLI scene报告，零用例 lib/bin/doc 不计数 |
| 新 catalog 四目标 | compatibility3/4.41s、modbus1/0.18s、multi_plc3/54.16s、plc_catalog3/0.82s；共59.57s<600s；11 CLI scene均<45s |
| `FF004_EVIDENCE_ROOT=Q2/copy-tests FF005_EVIDENCE_ROOT=Q2/copy-legacy-unused cargo test --locked --offline --release --features test-fixture --target-dir Q2/copy-fixture --test plc_catalog -- --nocapture --test-threads=1`，cwd=`Q2/copy` | exit0，3非零函数；连编译总4.987s |
| `python3 Q2/scripts/yaml_cli.py`、`yaml_family.py`；自有 `rustc --edition=2021 ...yaml_observer.rs` | helper/observer编译运行均0；实际产品每输入退出独立记录，**其中非法 alias 的产品0是 failure**，不把 helper0当全通过。真实 serde_yaml AST、source gate、普通产品对照见两项finding |
| `python3 Q2/scripts/manual.py formal` / `copy` | 各exit0；正式11.131/15.863s、copy10.863/10.917s，四场产品/fixture/B shell均0，实际SIGINT/wait；从当前指南逐字提取 PID 块执行，每场提到两driver+两native确切PID并验证ps=1/空stdout/stderr |
| `python3 Q2/scripts/teaching_manual.py` | exit0；独立teaching01 dry/execute3.012/2.635s，simulated1/写0、confirmed1/写1，原三口释放，正式树仍拒teaching01 |
| `python3 Q2/scripts/raw_audit.py` 最终 | exit0，独立解码本轮 raw TPKT/COTP/S7/PDU-ref/DB/offset/INT/ACK、同PLC在途、跨PLC重叠和HTTP等待，不只采信 harness 计数 |
| `rustfmt --edition 2021 --check` 11新增Rust文件；`git diff --check -- <38实施allowlist>` | 均exit0；未格式化/修改旧源码 |
| 静态文档与实际 Audit | 6双语pair代码块相同，USER_GUIDE各35/BUILD各1；本轮选取说明文件96个本地链接目标存在、locale4键对称、11头注/自身CODE_INDEX覆盖；正式/copy各4块实写Audit最大3548B（含外层/转义context/换行）≤4096 |
| 最终资源命令 | exit0；406个确切证据PID全部不存在，八口lsof1/空stdout/stderr及实际bind/close成功，76个本轮旧harness前缀根按前后差集登记 |

本轮 QA 辅助错误同样保留：初次旧 raw 索引读取误将 list 当 dict，exit1，随后按真实结构重新审计；通用命令记录器与 manual/resource 汇总使用相同报告名，覆盖了辅助汇总，导致初次 raw_audit exit1/TypeError。原产品 JSONL、protocol、shell stdout、真实退出均未丢失；命令元数据另名保存，汇总从这些原字节重建并核对，最终 raw_audit/resource 均0。已给记录器加 `cmd-` 前缀避免碰撞；没有因此重跑产品取绿、刷新命令时间或改项目源码/测试。原辅助失败输出保留，不归为产品缺陷。

## QA2 当前运行量化与历史使用边界

| 当前 CLI scene | 秒（含回收） / 独立核得事实 |
| --- | --- |
| S1 dry / execute | 5.575/5.486；先完整[12,1,56,34]及严格idle，再一次issue；各10次同原body GET、原input age<10s/expiry-issued60000ms。写[0,0]/[1,0]、simulated1/confirmed1；仅A.value变42，ready/result/B及邻A5均保持；raw匹配ACK/T3/C1=0100/C2=0101 |
| S2 three_readers | 5.361；A144 ReadVar、单session，三flow CLI各48成功；另本轮服务场景60个互异原request/flow样本、generation1/+08，连接复用不作为采样去重 |
| S3 B-off | 8.293；A86/B0读、写0，A-ready到stop8.010501s、A独立流CLI累计48。A原始混合响应gap113.290ms；5次B bootstrap owner_backoff的forced错误链精确归B，产品exit1，A正常reaped/无A forced；不能称全进程正常或零forced |
| S3 slow_setup | 8.404；A194/B39读、写0，A-ready到stop8.019978s，A独立流CLI48；A完整响应sequence4<B最终Setup5。另本轮服务原trace记录该A响应时B真实Owner=connecting，随后ready，非全PLC-ready屏障 |
| S3 parallel_io | 5.462；A/B各23读，各PLC≤1实际在途，两PLC区间真实重叠，写0、正常0 |
| S4 slow_http | 8.400；A77读、写0，A-ready到stop8.004780s，A独立流CLI48；HTTP实际等待1202.377ms内11个A完整响应，A响应gap117.495ms，HTTP未占PLC位，正常0 |
| S5 confirmed兼容 | 1.695；v1真实confirmed后原库等价v2≥10轮总写1，同原body/时间；有效TTL内变business_name实际identity_conflict，原行保留；typed hash/Resource与schema/trigger一致 |
| S6 in_flight same / alias | 0.504/0.504；原API合法T1/T2后恢复unknown，新point/flow/source/command等物理重叠仍写0，不相关读继续；正常资源0不表示unknown解除 |
| S6 实写42/截断ACK | 1.521；真实写42一次、17B截断响应无有效ACK，首轮故障exit1且无forced；原库重启读42仍unknown/阻写，末次正常0、总写仍1；不以完整hold_ack作正常关闭证据 |

当前失败轮实际为success12/error/not_attempted，后两项无sample/value、没有旧样本拼接；只保留最新每flow≤16/总≤128，5秒每块≤4项，未建永久历史或新状态表。所有新增正常 scene 均真实 runtime_tasks_joined/shutdown_complete、fixture成功Child状态/线程join、PID消失/端口重绑，关闭处于默认15秒预算；B-off只限证据归属B bootstrap链的既有force/非零故障。Driver::close 的真实Child.wait/ExitStatus.success与owner join源码未变；既有reaped事件不含exit_code，未编造该字段。

本轮重跑完整正式/副本测试、普通release手册、教程、源语法及当前 raw 解码。QA1 额外独立 flow observer/HTTP oracle 本轮未重跑：相关 runtime/owner/devices/read_points/fixture/HTTP 源码均对QA1原字节未变，且旧 observer-summary SHA=`32c060cdda810d8f3246d37898ffc92a13a9b5df13ed0a55e956f368bd79a5ca`、HTTP oracle SHA=`096c0b902cc14a650e73f6ca74e2ed5227dbcde443d39b7ab9510d3f8823245d`、旧raw audit SHA=`a19861d7775afdd167a6913ed5659915652c1b6f42212c71cea016da1122692c` 实际匹配。旧A-only原样本77/78/78、gap174/123/104ms及HTTP完整七键/status/content-type事实仅作为已存在独立历史辅证，不冒称QA2全量复演；当前混合A raw gap不冒充当前A-only逐流gap。AC08依据当前CLI/因果顺序和这些未变表面的已核独立历史共同评估。

手册人工首health路径仍只作演示：本轮正式dry/execute实际原body GET=9/10，copy=9/9，均未把9改写成10。S1量化只据本轮实际完整矩阵各10次及当前指南提供的同一可执行矩阵入口；没有增TTL、刷新body时间或换身份。

## QA2 新 finding：F-QA2-001 / R01 / AC02

**非 LF 合法换行使注释后真实 anchor/alias 被接受。** 位置为 `src/config/catalog.rs:96` 的 `split_inclusive('\n')`，与151/168行 comment break：source gate只按LF恢复注释/行状态，但本锁定serde_yaml实际接受CR、NEL、U+2028、U+2029行分隔。首行注释后这些配置的余下原始字符未被gate检查，真实parser仍解析/展开 `&deps/*deps`，普通产品报结构及runtime兼容true。

完整输入可仅从本持久checklist的QA1「复现A」完整代码块无损构造，不依赖临时目录。以下是本轮已实际核对的字节定义（QA1正文仍完整保留）：

```python
from pathlib import Path
import hashlib
s = Path('field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/checklist.md').read_text()
a = s.split('复现A：', 1)[1].split('```yaml\n', 1)[1].split('\n```', 1)[0] + '\n'
assert hashlib.sha256(a.encode()).hexdigest() == '999018454e4b433910ada55c1dac22a22bf6717e442b7e494d9d29b6ab6d56bb'
cr_bytes = ('# source comment\n' + a).replace('\n', '\r').encode('utf-8')
assert hashlib.sha256(cr_bytes).hexdigest() == 'ed6934396c7bd5322a393239484862c701a6f791dc17441b9a67971b140b1499'
```

两PLC JSON仍为QA1完整原字节（A SHA=`fcda187b9a72bd75720409a4a9b84c1feb0b4bb8c01f98af027e945fcad9535d`、B=`614e35946c63a622642d881b911b5c2f869e2840dd3ee8139e5d71e8a07a4b53`），放在输入旁plcs/。实际命令（cwd=`Q2/yaml`）：

```text
/private/tmp/ff-004-r2-qa2-2jnzhw3m/formal-product/release/field-flow config validate --config /private/tmp/ff-004-r2-qa2-2jnzhw3m/yaml/comment_alias_cr.yaml
```

**预期exit2/config_yaml_alias；实际exit0，format_valid=true、runtime_compatible=true、issues=[]，stderr空。** 不涉及联网、状态或日志操作。本轮自有Rust observer直接调用真实serde_yaml及候选catalog::parse，前者六种换行AST等价，gate在后四种返回同一已展开AST；不是凭标准记忆判断语法有效。

| 全量换行替换（均加同首注释） | alias输入SHA256 | 实际exit / 预期 |
| --- | --- | --- |
| LF | `48de38c7ceedffd470ffefce38b55ca53185dce33afc39ae59a2c6be6d6bb835` | 2 / 2 |
| CRLF | `bba482a6fc5d33e60bc01e05065521ea72f7ef4aae6bbbaeb172e0f616af79f5` | 2 / 2 |
| CR | `ed6934396c7bd5322a393239484862c701a6f791dc17441b9a67971b140b1499` | **0 / 2** |
| NEL U+0085 | `b1365a737cbdb6c3b0f2a7671f9eebbff6590486b2f4ba7eaa46acf624e6a833` | **0 / 2** |
| LS U+2028 | `a99f117125aad7464e60e1faeca0b9a852e27df77cdb3d9ba136813323545200` | **0 / 2** |
| PS U+2029 | `e165f524aadca8ffb1e45dcbcb57920905ce1c40fc4dccfad09aaaf5771d6445` | **0 / 2** |

无alias合法control使用QA1「复现B」完整输入（原SHA5de4ed...），按相同首注释及相同六种替换得到：LF `35780d67e3799cf0ec3a81b2f6f5008e7bf7d0aae96e4d5bc55ad967716492fd`、CRLF `62fab1b009dabe51946a056b0fbd06f1da13a27a70b8e398f23e50e08a114bba`、CR `b7a83dbaba000e29ced04634360751492493a76d722f7fc86d58713193793692`、NEL `3fc1139e83ddd3d45c355c9e44c369d6c7209bfdc4df97aa3a14be68d1b032fd`、LS `01a65cf96e1bb3b3ac51c02b59106cbf2452199155456df0eefe58f434691b1a`、PS `016a9072baaaf431768138608cb0b01f39ce404fd5fad18c027da188994585d1`，全部真实AST有效/CLI0。不允许通过全面禁止这些合法文字/配置、改变v1或删除alias禁令取绿。

## QA2 新 finding：F-QA2-002 / R01 / AC02

**flow mapping 引号key后的合法无空白冒号未建立node边界。** 位置 `src/config/catalog.rs:131–132/183/215`：`separated`仅看冒号之后空白/flow分隔符，没有识别引号key后的合法JSON式value边界，`&/*`落入plain状态而漏检。

完整947字节（含末尾LF）的输入SHA=`d380c583f49992d998b04809cc202ae1c4688b7d48403fc710a6640f269c15ce`，两JSON同上；输入全文如下：

```yaml
{"flows":[{"business_name":"synthetic_command_to_int","device_ids":&deps [s7_a],"get_url":"http://127.0.0.1:34880/it's","id":"demo01","input_max_age_ms":10000,"interval_ms":500,"kind":"demo01","source_id":"demo01-feed","target":{"device_id":"s7_a","point_id":"value"}},{"business_name":"read_a","device_ids":*deps,"id":"read_a","interval_ms":100,"kind":"read_points","reads":[{"device_id":"s7_a","point_id":"value"}]}],"http":{"connect_timeout_ms":500,"max_body_bytes":4096,"max_connections":8,"pool_wait_ms":500,"total_timeout_ms":1500},"instance_id":"ff-rust-catalog-demo","plc_files":["plcs/s7-a.json","plcs/s7-b.json"],"plc_runtime":[{"connect_timeout_ms":3000,"device_id":"s7_a","io_timeout_ms":5000,"queue_capacity":16,"queue_wait_ms":2000,"ready_wait_ms":3000},{"connect_timeout_ms":3000,"device_id":"s7_b","io_timeout_ms":5000,"queue_capacity":16,"queue_wait_ms":2000,"ready_wait_ms":3000}],"schema_version":2,"shutdown_timeout_ms":15000}
```

实际命令（cwd正式仓库；绝对配置路径决定plcs基准）：

```text
/private/tmp/ff-004-r2-qa2-2jnzhw3m/formal-product/release/field-flow config validate --config /private/tmp/ff-004-r2-qa2-2jnzhw3m/yaml-syntax/flow_quoted_key_alias.yaml
```

**预期2/config_yaml_alias，实际0/format_valid=true/runtime_compatible=true/issues=[]，stderr空。** 真实serde_yaml和候选gate均返回两个flow的device_ids=[s7_a]，证明alias已经展开。最小source-only语法同样复现 `x: {"a":&b [one], "c":*b}`：真实AST为两个相等数组，gate错误成功；该小片段不代替上述完整产品CLI输入。

Controls：仅把 `:&deps`/`:*deps` 改为 `: &deps`/`: *deps`，完整SHA=`68abbb1fba183d3cd64788918bb86f4216f2eb2a600908328ee42260ecc0f528`，同语义AST有效而正确exit2/config_yaml_alias；去掉anchor并将alias显式写成[s7_a]的合法flow配置SHA=`f5c0347d7988e38b1ea3527cb47c7438769fa04bcd69dec50f38549cf02b7dd3`，正确exit0。block mapping引号key有空白的alias/control分别SHA=`3a2bd2a318ffec494360c62c6e16846bc8ed09b59d2ec8c98ed42c9eefae79a0`/`e508f0ab2e013ebfa68e6ca70aac5b28d799fcd95f02eb31c692a6c24c780abd`，真实有效，分别2/0；block无空白两向量本锁定parser本身拒schema，不能算合法绕过或据此强制扩展语法。

另有12个定向source-syntax向量覆盖plain内部单双引号、flow、多行plain/quoted、literal/folded/显式缩进、注释及转义；9种合法文字均与真实AST一致，真正普通anchor/alias拒绝，custom tag按原边界config_schema，标准!!str保留接受。上述flow alias向量仍错误接受；没有新设全面标准tag禁令或改v1原规则。

## QA1 finding 在本候选的处置

| finding | QA2独立结论 |
| --- | --- |
| F-QA1-001 | 原SHA999018...、c6040b...、742fc7...、5de4ed...、de8e8f...五输入真实普通release为2/2/2/0/0，原双方向已修复；但R01/AC02整体仍未关闭，由F-QA2-001/002阻断，不能宣称严格YAML gate完整通过 |
| F-QA1-002 | **关闭**。双语35代码块对应，真实stdout路径及新PID块逐字执行；正式/copy四场每次确实取到两driver+两native并ps确认消失。首health演示与S1≥10入口已明确；teaching01精确锚点在新自有副本两模式复演成功 |
| F-QA1-003 | **关闭当前材料缺陷**。新23项逐件大小/SHA全准；旧59项仍只有seal-evidence历史错误，实际736B/SHA=`8f3015b63f4bb099078e9dd0d446b154f70655f13c0e872640b7966da4e0c069`，与勘误一致。旧0B/空SHA记录、初轮33附件与QA1正文未被改写 |

## QA2 AC01–AC14 verdict

| AC | QA2结果 | 当前依据及边界 |
| --- | --- | --- |
| AC01 | pass | 正式/copy各自身锁定无feature产品与feature夹具构建，31+3非零测试与真实双模式启动；copy74文件/清单/锁一致，无父/兄弟/DS运行依赖 |
| AC02 | **fail** | 原严格字段/容量/类型/codec/v1三kind/v2二kind回归通过；但两项新语法绕过由普通release及真实AST独立复现，违反原R01 |
| AC03 | pass | 当前路径/缺文件/重复身份/跨DB点/越界重叠/disabled/预算/依赖/未引用坏文件负例、错cwd与symlink回归；冻结加载摘要/来源hash如实，未部分启动 |
| AC04 | pass | 当前Modbus单文件0/不兼容、含未引用/disabled及同组非默认TSAP整体unsupported_protocol/2；纯非默认TSAP拒2，合法in_flight合成库/日志hash前后完全相同、缺目录仍缺；Loaded/capability先于State.open |
| AC05 | pass | 本轮S1先初值/idle再一次issue，各10原body GET、写0/1和邻A5保持；独立raw C1/C2/地址/ACK/T3及原五INT回归 |
| AC06 | pass | 本轮依赖子集、enabled点/缺点/越权拒绝、失败轮success/error/not_attempted不拼旧值；60独立request/+08样本；最新16/128及正式/copy实写Audit3548B/4块 |
| AC07 | pass | 当前三流各48、服务60互异样本，长期单owner/client/FIFO与单PLC真实IO≤1，双PLC区间重叠；原outer-await同flow≤1、不补跑、无新增全局IO锁 |
| AC08 | pass | 当前三个CLI实际≥8秒、A-only健康48、A完整响应4<B Setup5和真实connecting；HTTP1202.377ms内11 A响应；逐流高分辨率gap仅明确采用未变源码的已核QA1独立observer辅证，不冒充本轮重跑 |
| AC09 | pass | 完整原队列/ready/dispatch/clock/started/TTL/stop回归；当前正常scene零forced、join/wait/成功退出/精确PID/端口、默认预算内关闭；B-off只精确B bootstrap故障分类，原完整hold_ack限制保留 |
| AC10 | pass | 当前typed v1/v2 hash/Resource相同，路径/顺序/display/source不造新效果；有效TTL内真实语义变更conflict保原行；不承诺DS UUID自动继承 |
| AC11 | pass | 当前confirmed原库接v2≥10轮总写1；合法in_flight恢复unknown，别名/new identity物理阻写，不相关读继续，读42不确认；schema/trigger/不可变身份保持 |
| AC12 | pass | 默认dry simulated1/写0，显式execute仅A一次有效ACK+confirmed/B0，原body时间不刷新、唯一Execution路径及unknown保守规则未改 |
| AC13 | pass | F002关闭，双语版本/kind/API/DS saved/selected/loaded/来源hash/可达端点/TSAP及缺口表述真实；locale对称、无副作用help/validate回归、旧FF00537CLI及teaching双模式通过；Python不改且本轮not_run |
| AC14 | pass | 当前精确角色/Revision/dirty基线/候选/命令/31+3数量/新失败/资源及23raw可审计；旧33附件/QA1正文保护，正式交付源与copy一致；整体verdict仍qa_failed，未授予Owner接受 |

DS配置/来源/版本源码只读核对保存UUID、DB/点布局、TSAP、原payload SHA和selected/loaded分离；FF合成source-shape不是DS真实导出证据。Python工程not_run且字节不变，C#仍draft；Modbus通信/codec、DS exporter、公开schema、其他S7类型、Windows/Linux原生、真实PLC/第三方HTTP/DB、现场/托管/容量/长稳/签名/发布/部署均另gate。旧UTC producer、schema、driver bootstrap force和完整hold_ack限制保留。

## QA2 资源、必要证据及 handoff

全部本轮构建/test/manual/source-syntax observer已实际结束；正常产品由自己的B shell SIGINT后wait，夹具空行后正常wait，driver/native与线程结束由源码及实际退出/报告联合核实。最终406个证据中确切PID全部ESRCH，无存活/权限不明项；八口lsof各1/空且实际重绑成功。76个本轮旧harness FF-001前缀根按开始/结束确切路径差集登记，没有前缀批删或清理历史/他人资源。QA辅助检查结束后没有遗留本轮运行进程。

Q2约3.4GiB，保留74文件copy、独立teaching、六个release target与formal-test、全部合成状态、失败/成功原输出、语法完整输入/AST与脚本。Q1/D/C和原证据目录只读保留；这些仍供同r2返工、下一fresh QA和Owner审阅。资源不删除；待后续QA/Owner gate后由唯一active coordinator核占用、归属、证据及后续依赖决定回收。重要输入、两项failure复现、数量/命令/协议/状态/资源事实已持久在本checklist，不以临时文件作为唯一证据。

| Q2下关键原输出/报告 | SHA256 |
| --- | --- |
| `reports/audit.json` | `c2bbb8ac03558fc84f179f834ce99162519ef36b36745b067bd1e0b81ce76b90` |
| `reports/final-freeze-audit.json` | `a47cea4b4b24f646247d62010f91b3c439f1c7a4e1fc910c46116ac232f9f224` |
| `raw/full-formal.txt` | `0a7e9590156a9b2767d6ef89108ccabfcd7e7e49046c70b1be138e176f0a343c` |
| `reports/full-test-groups.json` | `c540bc86693d5a91c88a67c6a5cc25402160a3fb1b939905cc9041904af55f17` |
| `reports/yaml-cli.json` | `570fd8176912201afbbe121b263f2e2eb66924fb40e2cbd7245f757875e9e646` |
| `reports/yaml-family.json` | `2230fa198b16f7995efc0006cf34c16b89a15836181a4deae0e1dd0aee4db1df` |
| `reports/flow-quoted-key-alias.json` | `d18e4008b28ea75c6d1a7f8db7cff6d13fb66f927fc2a5869e9226d68cc8b5ad` |
| `reports/flow-controls.json` | `cf2b4ecb5fb6c070efa91c4c9ffa1d3ee217332ed648441a5e7943427570db47` |
| `reports/quoted-key-controls.json` | `66b024ecfd1dcc0ba6b2883faea122589249093b7bac39e4cebdbf92394d3623` |
| `reports/independent-raw-audit.json` | `5fb49ac63db4b31485686b1beb99a4e18b5cd12a2fd4e657b5483f28f780c379` |
| `reports/raw-index-audit.json` | `7d77c75e0643688b396f0047d7671f0160783d6946100dac4eec0003726bcb8b` |
| `reports/current-summary.json` | `112a27c772e68dd049a2da2f0fbab3692059fc458ce543cc1ded5fb6c5a58749` |
| `reports/resources-final.json` | `4e9837173741b570954716c6ad60f0eb277fcd95742b2d2136d0512fafd284a6` |
| `reports/static.json` | `ac93e548d5d90f5627905e632b45a790b05613b509df64c32cc09a603c09caa9` |

**QA2 -> Development：** 在原r2 A有限allowlist内处理F-QA2-001/002，保持合法文字/标准tag、v1原规则与alias禁令，保留本轮所有失败及QA1历史。若需要改变原范围、allowlist、依赖或风险，回PM/Owner；不得由QA静默修复或改合同取绿。真实新developer_handoff后由root启动又一个fresh-context Verification。Human Owner接收本独立失败结果并保留最终验收权，当前 **Human Owner final acceptance: pending**。

QA2结束记录时间：`2026-11-04T18:16:30+08:00`（Asia/Shanghai）。本轮整体qa_failed，未达到owner_accepted/completed；到此停止QA2写入。

# FF-004 r2 A rework2 独立 Verification QA3

**当前 QA3 verdict：qa_passed。** 精确 rework2 候选的 AC01–AC14 均通过下列独立验证；F-QA2-001/002 关闭，F-QA1-001/002/003 的修复和历史边界再次核准。没有待返工的实现 failure 或环境 blocker。此结论仅进入 **Human Owner final acceptance: pending**，不代表 owner_accepted/completed、现场资格、发布或部署。上方两轮 qa_failed、原始输入/数量/失败与资源历史完整保留。

## QA3 独立性、冻结输入与写面

实际 fresh-context `verification` 角色为 `/root/ff004_verification_r2_after_rework2`，由唯一协调者 root 在真实 rework2 developer_handoff 串行交接后调用；未继承 Development 对话推理，未创建子 agent/通知窗口或发送邮件。角色 TOML 只是 contract_only 配置证据，未把 model/effort 配置当独立运行遥测，也不宣称角色级平台 ACL/强制路由。

已独立读取根 AGENTS、README/PLAN 双语、canonical workflow/verification TOML、FF/Rust 最近 README/PLAN、完整 spec（含无损 r1）/tasks/QA1/QA2 checklist、当前实现、相对原 dirty 基线完整 diff、Development 附件与原始输出。应用 project-governance、aiis、rust-runtime、plc-point-mapping、i18n-workflow、code-document-indexer 及适用的日志/结构/资源参考，只验证。Owner 原话“批准 FF-004 r2 A，按方案开始开发，完成后按 STD 进入独立 QA。”对应当前唯一 r2 A；原 38 文件 allowlist/14AC 未变，没有从其他任务继承批准/验收。

正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD=`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。C=`/private/tmp/ff-004-r2-coordinator-6ejzumcp`；QA3 自有 Q3=`/private/tmp/ff-004-r2-qa3-cagszupy`。D/Q1/Q2/C 及旧证据只读；未复用其 target、二进制或状态作为本轮独立构建证明。唯一仓库写面为本 checklist；没有修改 spec/tasks、源码/测试/配置、导航或其他文档。

| 精确 QA3 输入 | 实际 SHA256 / 审计 |
| --- | --- |
| owner_approved spec | `a7418cfe8f34515719beb50d9d901f42d7a283e2b33c61a2a57b129104a7870e` |
| rework2 developer_handoff tasks | `f477ad1cc5050fb07ff2204514ae10fda794c4f3a2a3bd6f4ec8b38fd3ece3d2` |
| E2/handoff.json | `5aba304b866faf4613fbfc6a8a3d79dae828f968e8e44ccb6482671b80ae556e` |
| E2/implementation-manifest.json | `8cb0550a0be8310385e92efe0160b71432aab5f3fa06254cc077e09010a9f1dd`，38 允许/相对原 dirty 基线37实改 |
| E2/candidate-manifest.json | `8643a2a681daab6a8024f4db8ec87eabf9a3875d256d1c7aaeb77815c6926cb5` |
| E2/copy-manifest.json | `8ff77d28d9ab4c37d8637a12fea2ede0951b7218982fcf6fe6635c704d69a836` |
| 消费的 QA2 checklist | 55555B，`ed3468e0bb68ed9da056d1553a3f1c2468a77a3a57c2fcf3e06b868ec00f01a7`；QA1 原正文27327B/SHA=`5922727d3d927cacb2f23c1b96462b26087f43df6909a375918129c38c6ec4bb` 仍完整在内 |
| 从 C/original 原 dirty 基线重新生成的完整实施 diff | 212550B，`468abfab493e90e0312ddd60f0c5c3879a71dcff42a0e5eb87c4934db112c9a8`，与冻结交接逐字节相同；未把 FF-005 原 dirty 算本任务 |
| 当前 catalog.rs / plc_catalog.rs | `27f4348f7e37e9d941678451d949a12103b941f5b594402431c189ecd39523ff` / `e89eb283134c5798071c6acef7173072126a59c4c08f48da6f36148091416f09` |

E2=`evidence/r2-development-rework2/`。开始及最终写 checklist 前，197项中195项均吻合；仅两件根 PLAN 整文件因其他任务行更新而不同，12件导航的 FF-004 原行均完全不变。正式 Rust 与 Q3/copy 各74文件逐件匹配；相对 QA2 只有 catalog.rs 与 plc_catalog.rs 两件 Rust 文件变化。776个非本实施/导航/spec既有文件、3个隐藏保护项、60个旧Development附件均原字节保持。Cargo.toml=`d28d9068b6804afe0f2605bdc5d90976a45e2e055881c771e26e7203291e8ea8`、Cargo.lock=`13404c36665fa46f50f40291e111bcb11e99b9ee8c13d29130004c9ef3d74fc6` 未变；r1仍无损还原42739B/SHA=`e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`。

## QA3 环境、命令和实际退出

macOS15.7.7 / Darwin24.6 arm64；rustc1.89.0(29483883e)、cargo1.89.0(c24e10642)、Apple clang17.0.0。所有 Cargo 使用现有锁与 `--locked --offline`；无依赖/SDK/target安装、清单或全局环境变更。系统 Python仅编排、文本和证据解析，不是 Field Flow Python 工程验证。

默认 sandbox 八口 bind 被 `Operation not permitted` 拒绝，lsof空；此环境检查exit1不计产品failure或pass。随后以明确仅含获批固定loopback测试的安全执行方式，八口实际bind/close exit0。最终资源脚本第一次在默认sandbox重遇同一bind权限限制，保留exit1；获批安全执行的最终资源脚本实际exit0。全部协议场景串行，仅31102/31103/31880与34102/34103/34112/34113/34880；无改端口、杀占用者或外部服务访问。

下表 cwd 未另注均正式 Rust 工程；Q3为上方绝对根。完整 argv、真实退出与单调耗时保留 Q3/reports/cmd-*.json、Q3/raw，不用 helper exit0冒充其中产品应拒绝的exit2。

| 独立命令 / 自有产物 | 实际结果 |
| --- | --- |
| `cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir Q3/formal-product` | exit0/305.897s；普通产品独立于fixture feature |
| `cargo build --locked --offline --release --features test-fixture --bin ff-fixture --target-dir Q3/formal-fixture` | exit0/305.273s |
| 同两条，cwd=Q3/copy，target=Q3/copy-product、Q3/copy-fixture | 各exit0/305.733、304.572s；自身74文件、清单/锁、配置/locale/测试/文档，无父/兄弟/DS运行依赖 |
| `FF004_EVIDENCE_ROOT=Q3/formal-catalog FF005_EVIDENCE_ROOT=Q3/formal-legacy-basic cargo test --locked --offline --features test-fixture --target-dir Q3/formal-test -- --nocapture --test-threads=1` | **exit0/270.379s含编译，32非零test函数=旧21+新11**；零用例lib/bin/doc不计。旧FF-005三个函数84.91s，内含原37个CLI场景，不冒充37函数 |
| 当前新增catalog四目标 | compatibility3/4.57s、modbus1/0.14s、multi_plc3/52.47s、plc_catalog4/0.39s；共57.57s<600s，11个CLI scene均<45s；正式/copy均实际产生88条新语法/AST/typed向量 |
| `FF004_EVIDENCE_ROOT=Q3/copy-tests cargo test --locked --offline --release --features test-fixture --target-dir Q3/copy-fixture --test plc_catalog -- --nocapture --test-threads=1`，cwd=Q3/copy | exit0，4非零项，含增量编译10.830s |
| Q3/scripts/yaml_cli.py 与自有 rustc 编译的 yaml-observer | compile/observer/helper均0；普通release24个同SHA输入24/24符合，原AST/source/typed结果逐件记录；111个额外source边界均真实parser有效，56真实alias拒绝、55合法文字保留 |
| `python3 Q3/scripts/manual.py formal` / `copy`，由manuals.py串行编排 | 各exit0；正式dry/execute11.376/11.085s，copy11.206/16.113s，均<45s；四场产品/fixture/B shell实际0，SIGINT/wait、原指南PID块、实际端口重绑均通过 |
| `python3 Q3/scripts/raw_audit.py`；11次普通产品`state inspect` | 各exit0；独立解码本轮TPKT/COTP/S7/PDU-ref/地址/值/ACK/在途区间与HTTP等待；所有11个CLI合成状态在结束后只读inspect成功 |
| `rustfmt --edition 2021 --check <11个新增Rust文件>`；`git diff --check -- <38实施allowlist>` | 均exit0，未格式化或修改旧源码 |
| 只读静态/索引/保护核对 | exit0；6双语pair代码块一致，GUIDE各35/BUILD各1；96个选取说明文件的本地链接目标存在、locale4键对称、11文件头/自身CODE_INDEX覆盖；当前13raw、上一轮23raw大小/hash全吻合 |
| 最终资源与冻结审计 | exit0；377个证据确切PID全部不存在，八口lsof1/空且实际bind/close；195非根输入、74copy、776+3保护和60旧附件保持 |

普通正式产品SHA=`06210b74b6b76e127b86b5beb1aebd9420f2e7c922c79c17141b50eff48bd412`，copy产品SHA=`2d97ef99ca6679f2be11fc0504ac94030815401dfb9754b210ce36156e08f0b3`；二者来自相同74源码文件的各自构建，不把不同构建路径的二进制SHA说成相同。

QA辅助错误单列：首次observer汇总用Python splitlines将JSON字符串内NEL/LS/PS误切为行，raw未丢失，改按LF字节切分后111项核准；通用命令记录器与static/yaml-cli汇总同名，覆盖了两份辅助汇总，已把命令记录统一改为cmd-前缀，保留原命令/raw，只读重建static并对同SHA24输入再验以恢复完整逐项输出。首次再验因试图对已存在私有状态init而helper exit1，原目录保留，之后只新建另一私有状态完成记录。没有改产品/测试、删除状态、刷新场景命令时间或掩盖产品failure；这些辅助失败保留于Q3/raw及auxiliary-failures报告。

## QA2 finding 的本轮关闭

| Finding | QA3独立结果 |
| --- | --- |
| F-QA2-001 / AC02 | **关闭**。从本checklist QA1完整复现A重新构造原字节，核同SHA CR=`ed6934396c7bd5322a393239484862c701a6f791dc17441b9a67971b140b1499`；六换行alias原字节与旧输入逐件相同，当前普通release均exit2/config_yaml_alias；六合法controls均exit0。直接serde_yaml AST相等、合法完整Loaded typed等价。scanner只建立私有六换行视图，反序列化与JSON来源摘要仍使用原字节，未用read_text归一化CR输入 |
| F-QA2-002 / AC02 | **关闭**。947B原输入SHA=`d380c583f49992d998b04809cc202ae1c4688b7d48403fc710a6640f269c15ce`同字节当前exit2/config_yaml_alias；真实AST与显式literal/加空白alias controls相等。单双引号key及紧邻/空白/tab/换行value边界覆盖；plain内部冒号/单双引号/&/*/!仍合法。flow有空白alias2/literal0，block有空白alias2/literal0；block无空白两个向量仍由真实parser拒绝config_schema，未要求扩展成合法语法 |
| F-QA1-001 | 五原SHA向量当前普通release仍2/2/2/0/0；两方向修复保持。标准!!str接受/customtag按原schema拒绝，本轮未新设全面tag或合法文字禁令，v1解析/三kind和旧typed定义保持 |
| F-QA1-002 | 当前指南与QA2逐字节相同，35对称代码块、真实stdout路径及PID块在本轮正式/copy四场逐字执行，各取两driver+两native并ps确认消失。人工首health只作演示，四场原body GET实际10/9/10/10；S1≥10只据当前完整矩阵每模式10次，不把9称为10 |
| F-QA1-003 | E2新13项与E1新23项原始完成输出大小/SHA逐件准确，生成器stdout未纳入索引。E0旧59项仍只有原seal-evidence错误，实际736B/SHA=`8f3015b63f4bb099078e9dd0d446b154f70655f13c0e872640b7966da4e0c069`与E1勘误吻合；旧0B记录及QA1/QA2正文没有改写 |

上述非法配置还分别用run对缺失状态目录和已初始化自有execute状态验证：都在Loaded加载阶段exit2、stdout空，缺目录仍缺，既有SQLite/日志/锁目录全文件SHA不变。源码顺序仍Loaded::load→capability→State::open，解析/能力失败先于恢复写、持久日志、owner/flow和连接；不是因网络失败而得到拒绝结果。

## 本轮协议、状态、调度和正常/故障资源结果

本轮独立raw解码不调用产品codec生成预期帧；核TPKT长度、COTP C1=0100/C2=0101、S7头/参数/数据长度、PDU-ref匹配、DB/offset/两字节INT、ACK和值、单session真实在途区间。全部新trace未截断，每PLC≤2000行/总≤4MiB；成功sample的received_at为原响应完成事实，带+08毫秒，observed_at与原UTC外层语义分开。

| 当前自有CLI scene | 秒（含回收） / 本轮实际事实 |
| --- | --- |
| S1 dry / execute | 5.414/5.412；先完整[12,1,56,34]、严格idle/command0/写0，再一次issue42；各10次同原body GET，在原10秒input age内，expiry-issued=60000；simulated1/confirmed1，写[A0,B0]/[A1,B0]，仅A.value变42，ready/result/B及全部邻A5保持 |
| S2 three_readers | 5.424；A147次真实ReadVar、单session，CLI三flow分别49/48/49成功；另本轮服务场景60个互异原request_id/flow_id、generation1/+08样本。连接复用不是采样去重 |
| S3 B-off | 8.224；A87/B0读、写0，A-ready到stop8.010652s，A独立流CLI累计49。A混合raw响应最大gap127.584ms；精确B bootstrap连接拒绝/owner_backoff forced链、产品exit1，A正常reaped且无A forced；该负向分类不称全进程正常或零forced |
| S3 slow_setup | 8.331；A195/B39读、写0，A-ready到stop8.017355s、A独立流CLI48；A完整响应sequence4<B最终Setup5，服务真实Owner观测该A响应时B=connecting，随后ready。没有全PLC-ready屏障 |
| S3 parallel_io | 5.419；A/B各23读，各PLC真实在途≤1，两PLC区间实际重叠，单owner/FIFO长期复用，没有全局IO锁，正常exit0 |
| S4 slow_http | 8.355；A78读/写0，A-ready到stop8.011058s、A-only CLI49；HTTP真实等待1201.287ms内有12个A完整响应，A raw最大gap110.481ms，HTTP未占PLC位，正常exit0 |
| S5 confirmed | 1.735；v1实际写1/confirmed，原库等价v2≥10轮仍总写1，同原body/时间；有效TTL内改business_name实际identity_conflict，原confirmed保留，schema/trigger不变 |
| S6 in_flight same / alias | 0.512/0.506；原API合法T1/T2后恢复unknown；新point/flow/source/command的物理重叠仍写0，不相关读取继续。正常资源0不表示unknown解除 |
| S6 实写42/截断ACK | 1.624；真实写42一次、17B截断响应无有效ACK，首轮故障exit1/无forced；原库重启读42仍unknown、阻写且总写1，最后正常资源0。没有用完整hold_ack作为正常关闭证明 |

本轮失败读轮为success12/error/not_attempted，后两项无sample/value，无旧值拼接。最近轮每flow≤16/总≤128；五秒每块≤4项。正式/copy最大ID/计数的实际Audit各4行，最大3548B（含外层/转义context/换行）≤4096，未新增永久样本历史或SQL表。原Owner有界FIFO、每flow outer-await不重叠、不补跑、ready/queue/dispatch/400ms回收预算、ClockAnchor/TTL、唯一Execution、原Flow/Target/Intent摘要/Resource、driver/state/HTTP与旧测试均原字节保护，完整旧21项含五INT、ACK拒绝、queued-stop零下发、clock/started及FF-005原37CLI已实际回归。

全部新增正常scene有实际runtime_tasks_joined/shutdown_complete、正常产品退出，fixture成功Child状态/线程join、确切PID消失及端口重绑，处于默认15秒关闭预算。B-off只按实际证据归属B bootstrap/连接失败链的旧force/非零分类，A正常且全资源回收；不以场景名豁免不明forced。原Driver::close实际Child.wait并校验ExitStatus.success、owner任务join后才有正常reaped；该事件不含独立exit_code，本QA未编造。新fixture的真实try_wait/wait结果与线程join源码及close_result/退出共同核对，不仅看PID消失。

## 本轮与历史辅证的界限

未改的额外teaching01、独立每flow高分辨率observer和HTTP完整body oracle本轮未机械重跑。对应app/runtime/devices/fixture/HTTP、v1解析、指南/teaching锚点与QA2完全相同；QA2独立teaching双模式报告实际读取，SHA=`b9402e44283a1922521b3c2d88a779e1aac85a9f5e70f4a6ac09871c12bdb126`；QA2 raw audit SHA=`5fb49ac63db4b31485686b1beb99a4e18b5cd12a2fd4e657b5483f28f780c379`，均已核准。QA1 observer SHA=`32c060cdda810d8f3246d37898ffc92a13a9b5df13ed0a55e956f368bd79a5ca`和HTTP oracle SHA=`096c0b902cc14a650e73f6ca74e2ed5227dbcde443d39b7ab9510d3f8823245d`也实际匹配。

QA1原A-only逐流8秒样本77/78/78、最大gap174/123/104ms与HTTP完整七键/status/content-type，仅作为未变表面的已核独立历史辅证，不称本轮重新运行。当前混合A raw gap不冒充当前A-only逐流gap；AC08结合本轮CLI8秒推进、真实connecting因果顺序、HTTP窗口与该历史辅证判断。teaching01正式拒绝与v1三kind由本轮测试继续核验；旧教程额外dry/execute只引用上述明确历史。指南手工四场仅操作演示，量化S1以当前完整矩阵为据。

Modbus当前单文件format_valid=true/runtime_compatible=false/exit0；完整组含未引用/disabled Modbus及同组非默认TSAP整体unsupported_protocol/2，纯非默认TSAP unsupported_connection/2；合法in_flight合成库/日志前后hash完全相同，连恢复写都没有。所有文件/disabled/未引用结构和依赖在启动前校验，无部分S7启动、Modbus transport或34502连接。DS源码/文档核对区分UUID、布局、TSAP、saved/selected/loaded及原payload SHA；合成DS source-shape不是DS真实导出或数据库真值证明。

## QA3 AC01–AC14 verdict

| AC | QA3 | 当前依据 / 限制 |
| --- | --- | --- |
| AC01 | pass | 正式/copy各自身74文件锁定无feature产品/featurefixture构建，32+4非零测试与普通release四场真实启动；交付源码一致、清单锁不变 |
| AC02 | pass | 两QA2 finding同SHA普通release/真实AST/source/typed关闭；111相邻语法与现有88向量、严格字段/类型/整数/null/容量/codec回归；v1三kind/v2仅demo01/read_points |
| AC03 | pass | 当前路径/缺文件/重复/穿越/symlink/错cwd、身份/跨DB点/越界/重叠/disabled/依赖/未引用坏文件负例及原字节来源摘要通过，无部分启动 |
| AC04 | pass | 当前Modbus0/不兼容与完整组优先拒2；纯非默认TSAP拒2，旧合法in_flight库/日志hash不变、缺目录仍缺；preflight先于State.open |
| AC05 | pass | 本轮S1各10原body GET、先初值再issue、dry/execute写0/1、邻A5、独立raw C1/C2/PDU-ref/地址/ACK/T3及原五INT边界 |
| AC06 | pass | 本轮依赖子集/enabled/越权拒绝、60互异原sample/+08、首错success/error/not_attempted不拼旧值；最新16/128、实写Audit3548B四块 |
| AC07 | pass | 本轮三流49/48/49与60独立request；单PLC长期一session/driver、有界FIFO/真实在途≤1，跨PLC真实重叠；原outer-await同flow≤1、不补跑 |
| AC08 | pass | 当前B-off/slow_setup/slowHTTP各≥8秒/CLI A-only≥20、A完成4<B Setup5且真实connecting，HTTP等待内12次A响应；逐流高分辨率gap仅按上述已核未变历史辅证，不冒充本轮重跑 |
| AC09 | pass | 完整旧预算/TTL/clock/started/queue-stop回归；当前正常scene零forced、真实join/wait/成功状态/PID/重绑及默认预算；B-off精确B故障链，旧完整hold_ack限制保持 |
| AC10 | pass | 当前v1/v2旧typed hash/Resource一致，文件名/顺序/display/source不造效果；有效TTL内真实语义变更conflict保原行；不承诺DS UUID自动迁移 |
| AC11 | pass | 当前confirmed原库接v2≥10轮总写1；原合法in_flight恢复unknown，别名/new identity物理阻写，读42不确认；schema/trigger/身份保持，无DDL/清库 |
| AC12 | pass | 本轮默认dry simulated1/写0、显式execute仅A一次有效ACK+confirmed/B0；原body时间/TTL不刷新，唯一Execution与unknown规则保持 |
| AC13 | pass | 本轮双语/PID块/locale/无副作用help/validate、旧FF-00537CLI与版本/能力/DS缺口如实；未改teaching额外双模式采用已核QA2历史，Python本轮not_run且字节保持 |
| AC14 | pass | 精确fresh角色/Revision/dirty基线diff/候选/命令/数量/历史辅助错误/准确索引/资源可审计；QA1/QA2全文及60旧附件原字节保留；仅交Owner终验 |

## 资源、保留、限制与 handoff

377个本轮证据确切PID均ESRCH，无存活/权限不明项；八口lsof各exit1且stdout/stderr空，逐一实际bind/close成功。ps在最终检查当刻只见本轮收尾记录器/helper，随后工具实际wait返回exit0并另核最新helper PID消失；没有本轮产品/driver/fixture/native遗留。构建、full/copy tests、observer、普通release四场及检查全部结束；正常SIGINT/TERM后真实wait，Child成功状态及线程join与源码/实际报告联合核实。旧harness生成76个FF-001前缀目录，按运行前后确切路径差集和当前输出登记，不按前缀删除或算旧任务新验收。

Q3约2.64GiB，保留74文件copy、四个release target与formal-test、自有语法observer/完整原始输入、全部新合成状态、成功/辅助失败raw、报告/脚本及76个本轮旧harness根目录清单。D/Q1/Q2/C与旧附件均未删除/修改；资源仍供Owner终验和证据复核。最终由唯一active coordinator按实际占用/归属/后续与证据依赖决定回收，QA不执行资源删除。关键输入、复现、数量、命令/退出、协议/状态/资源和verdict已持久在本checklist，不以临时链接作为唯一结论。

仅macOS arm64、自有固定loopback S7 int16合成验证。Python/C#未运行/修改；Modbus通信/codec、DS exporter/导出接受、根公开schema、其他S7类型、Windows/Linux原生、真实PLC/第三方API/数据库、现场/托管/容量/长稳/签名/发布/部署仍是独立gate。原UTC envelope/SQLite producer/schema、driver bootstrap force和FF-005完整hold_ack限制未修，不作时区迁移/正常关闭/现场能力外推。没有Docker、安装、真实数据库写/迁移、现场设备、Git/GitHub写或外部发送。

**QA3 -> Human Owner：精确FF-004 r2 A/rework2候选qa_passed，F-QA2-001/002关闭，无实现failure/blocker；Human Owner final acceptance pending。** 主协调可据此机械同步本任务导航；QA通过不授权最终验收、发布、部署、真实设备/数据库动作或Git写。此前QA1/QA2的qa_failed保持历史事实；任何后续实质实现变更须重新交接/验证，不以本结论自动覆盖。

## QA3 关键自有证据指纹（Q3下，非新增仓库附件）

| 报告 / 原输出 | SHA256 |
| --- | --- |
| `reports/protection-initial.json` | `5fddfabdfa5f3d28727ab44c7c3df261f69cde3dd5bb4779b952dd26185153af` |
| `reports/final-freeze-audit.json` | `20a075790c5fa9249f8704c7666449034a0c6ed109f98274cf911f9a39b9e203` |
| `reports/full-test-groups.json` | `7bfe94e8b503138cfa30b153563482ce424a417960a90b75774b670da7895c52` |
| `raw/full-tests.txt` | `98bb810b9bcbc200115634b57030cada7c1a5ed41a4d02502abd490801f04790` |
| `raw/copy-tests.txt` | `f3fa5a119653fd63a6a7ab7337cdc2e9c086654a89d21ae542a72b5fdb8c3cc7` |
| `reports/yaml-cli.json` | `ce2809ac2f5f96d4f3072b788d385643ab17b32a486513def124aa1af5192b94` |
| `reports/yaml-observer.json` | `375aa8a53290c989abf7716fd465dd95b4247c6cf94823e09f31b9a61a2750bb` |
| `reports/yaml-typed-summary.json` | `9148ca557e52e75cf8f5e0129d64c6e0184b40fdb3f0f00453d19566dd70ac62` |
| `reports/independent-raw-audit.json` | `7893e0eb0b33bb6672fcb85ddcae662f0e3cc22f5d235067a74c9c043f1c0631` |
| `reports/manual-formal.json` | `931f3c255c6e0e82fc5a59924e2e2cc50420882fcac6bdc5161903ac219d54b6` |
| `reports/manual-copy.json` | `d7910a8407b9a9c2bc18ba9542a302ac13f1b58e42ede0d190250a06483ac242` |
| `reports/resources-final.json` | `2ca3c2cdac1fdcb73324c753c004a3f32c73263e33807991d01847194d1a25ed` |
| `reports/dev-raw-index-audit.json` | `a103023b7c2d944bbe7432789bc583ea7717222346a4aea114b36116cdee0bf5` |
| `reports/static.json` | `c2843efcf86db29bb2c5066c51579b613663538ef7d19bc1b48f90f48bc60516` |
| `reports/qa3-raw-index.json` | `ce1762d373a0d87115960fa73d7e93ba29cf49f9ef0314d79e31ea6f8d5ee927` |
| `reports/auxiliary-failures.json` | `9cf01a31b9f69d9ef8f6aceb9469ec0fef5e750fd513db2af7d45032993dab29` |

QA3结束记录时间：`2026-11-04T19:00:10+08:00`（Asia/Shanghai）。本轮qa_passed，Owner终验pending；到此停止QA3仓库写入。
