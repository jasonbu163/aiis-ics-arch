Task ID: FF-006
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Verification -> Human Owner，等待 FF-006 r1 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Owner: Field Flow

# 首次独立 QA，2026-11-24

## 结论与返工范围

**qa_failed。** 在正式及独立复制产品上，预检都拒绝了悬空边，但报告无法辨认三条边中哪一条出错。AC03 要求“明确拒绝并定位”。Development 需让诊断标明出错的边，并核对同项要求覆盖的入口、端口、引用及条件常量等。验收以能辨别具体错误位置为准，具体路径格式由实现选择。请保留本次证据并重新交付精确候选，再启动 fresh-context Verification。Human Owner 最终验收待后续。

### AC03 独立复核方法

从工程样例复制两份 `flows/demo01.json`，各自保留文件名。第一份仅将 `flow.edges[0].to_node_id` 改为 `"missing"`，第二份仅将 `flow.edges[2].to_node_id` 改为同值。对两份产品分别运行以下命令，共四次。此处只执行配置预检。

```sh
"$D/product/release/field-flow" config validate --config config/flow-json.yaml --flows-dir "$Q/edge0"
"$D/product/release/field-flow" config validate --config config/flow-json.yaml --flows-dir "$Q/edge2"
```

四次均退出 2，返回同一个 issue：`{"error_key":"config_flow_edge","path":"flow_files[demo01.json]"}`。第一份破坏 fetch 的 next 边，第二份破坏 check 的 false 边，诊断内容完全相同。两份输入的 SHA-256 分别为 `92e8a5a66770112365cab95165f84a27b9671e83416c22d70d604de1480550fd`、`7410b176336f0677d348fdd64c8974e511b52842ea16ea5f771b0fe87faadff0`。源码 `src/config/flow_json.rs:176` 对悬空边返回通用键，第 95 行追加文件名。`tests/flow_json.rs:161` 的矩阵只检查路径包含文件名，因此该测试可以通过。

## 候选与命令

独立 Verification 在新的角色上下文中读取根契约、所属模块双语入口、workflow、角色配置、批准的 spec、tasks、交接证据和工作树。Darwin 24.6.0 arm64，rustc 1.89.0，Cargo 1.89.0。未提交工作树的 HEAD 为 `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`。规格、Development tasks、源码清单的 SHA-256 分别为：

- `1b5937dbbc2f73f617eec7d38830ae6223a7468fec9f62cbb1bd1a3da52a91eb`
- `812dda76387c7a4dda0e9c4c8398f8a562d96ad185e3522331a081782c97deba`
- `c27cfc526b868a2a1873b67a16bb9d4edfba144a827cc8968cb8181d4cccbddc`

QA 自建 `Q=/private/tmp/ff-006-qa-DPLJkZ`。正式 cwd 为仓库的 `field-flow/field-flow-rust`，D 为 `$Q/formal`；副本 cwd 为 `$Q/copy/project`，D 为 `$Q/copy`。用 rsync 复制单工程并排除 .git、.DS_Store、target，以 Python hashlib 对比交接清单；两边均恰有 80 个文件，所有 SHA 相符。git diff 与 untracked 合计 23 个变更文件，集合与交接清单及批准面一致，git diff --check 通过。Cargo 清单、锁和旧状态、旧测试的源码均在该比对范围。

```sh
cargo build -j 3 --locked --offline --release --no-default-features --bin field-flow --target-dir "$D/product"
cargo test -j 3 --locked --offline --features test-fixture --test flow_json --test cli_contract --test catalog_compatibility --test basic_examples --target-dir "$D/test" --no-run
"$D/product/release/field-flow" config validate --config config/flow-json.yaml --flows-dir flows
export TMPDIR="$D/tmp" FF004_EVIDENCE_ROOT="$D/ff004" FF005_EVIDENCE_ROOT="$D/ff005"
export FF006_PRODUCT="$D/product/release/field-flow"
cargo test -j 3 --locked --offline --features test-fixture --test flow_json --test cli_contract --test catalog_compatibility --test basic_examples --target-dir "$D/test" -- --test-threads=1 --nocapture
```

正式树合并执行四个测试目标。副本使用相同参数，分三次执行 flow_json、cli_contract + catalog_compatibility、basic_examples。相同固定端口的测试串行执行。两份 release 构建和测试编译退出 0；release SHA-256 分别为 `9edff77c29e6bc47a3dff05f378714d900861068ae0078e1b9d2fc7beb490d63`、`9f572ed5c71ed81237b82390523a803e53a88e4094b0669ef71c009b3ca1bbe6`。两份样例预检退出 0，样例 SHA 均为 `54bfefd486dfaf97ba0b6ff55e278019c2283d2fb081ef4cf8e1c66cf42638d0`。

## AC 逐项结果

| AC | 独立结果 | 观察 |
| --- | --- | --- |
| AC01 | 通过 | 两份 release 离线构建。旧 CLI、旧配置、旧手写流、typed 身份、重启后 confirmed/unknown 保护由原测试执行。在正式树 basic01 中，dry_run 为 simulated=1、写次数 0；execute 为 confirmed=1、写次数 1，独立合成内存读回前两个字节 002a。 |
| AC02 | 通过 | 纯图使用空 PLC 配置。切换 cwd 仍能以显式绝对目录得到同一报告；缺目录、文件、链接、重复、穿越、超限与无效绑定预检均拒绝。旧配置继续由兼容测试装载。 |
| AC03 | 失败 | 节点、边倒序及省略布局可以执行，等价结果一致；plc.read 的拒绝可辨认节点。悬空边仅报告文件名，独立用例见上。 |
| AC04 | 通过 | 两边分别启动自己的 release 与回环夹具。正式树 not_matched、matched 的轮次依次为 1795501267100-29797-1、1795501267608-29797-2，两个观察时刻相隔 509 ms；副本为 1795501196547-28085-1、1795501197058-28085-2，相隔 509 ms。夹具断言两次独立 GET，以及应答开始到下一请求的间隔。源码等待本轮 HTTP、校验和结果落盘后才开始 sleep。 |
| AC05 | 通过 | 两份产品均完成 10 个独立故障轮和随后正常的 matched 轮。覆盖缺字段、重复键、source 不符、非 bool、越界 INT、null、过期、503、非 JSON Content-Type 和超时；故障轮只记录 error_key。纯图运行无 PLC 事件、gate 或命令计数。 |
| AC06 | 通过 | 两份混合运行均在慢图 GET 完成前观察到手写流 simulated；合成 PLC sessions=[1,0]，reads=[0,0]，writes=[0,0]。每次运行最终只有一条手写 simulated 状态。 |
| AC07 | 通过 | 不合法图预检退出 2，原合成库字节一致，无 runtime.jsonl；正式与复制图在运行中改写均保持 r1/SHA，重启才使用 r2/SHA。自有应用响应 SIGTERM/SIGINT，夹具等待成功退出并检查 PID 消失、线程 join 和端口可重绑。正式树另重复单测观察到夹具 PID 30658 在 127.0.0.1:60379，首个产品 PID 30662，本次单测退出 0。 |
| AC08 | 通过 | 双语 README、配置说明和指南均包含对应入口。指南覆盖流程目录、启动、出错、手写流共存和只读边界。两份 locale 的 4 个键对称。7 份变更 Markdown 的 112 个相对文件链接均可解析。Development 自检与本次 QA 分开记录。 |

仅使用 QA 新建的 synthetic 状态、回环地址和合成 PLC 夹具。普通 sandbox 绑定回环返回 EPERM，四个具体测试目标经授权后运行；编译和诊断检查在 sandbox 内进行。正式树完整测试日志 SHA-256 为 `639224512d686fc05822d76fc89002d0b2a15e05531c32f1ec3b69d8dc9015b1`；副本 graph 和兼容/CLI 日志分别为 `a98fa7f0301f4ab081ebaab93b36e0136cbd079c29a8ad2248acd5950099dd49` 和 `71c935ee82f00b47a047ab883b9082424914d06a2bf29784fec68c3e664f1a47`。失败 fixture、临时日志、构建和合成状态保存在上述 QA 专属根，用于 Development 对照和下一次串行复核；新 QA 完成、不再需要原始对照时由协调者回收。CA 实际导出/重导入、Windows、现场及长稳仍待独立验证。

正式树和副本各 13/13 测试通过（flow_json 4、basic_examples 3、catalog_compatibility 3、cli_contract 3），所有命令退出 0；独立 AC03 定位检查仍失败。副本 basic_examples 日志 SHA-256 为 `d80368f7261cae2207946cb81c5774a47ffb199ac640867e5552d617517d049a`。结束后对 31102、31103、31880、34102、34103、34112、34113、34880、60379 运行 lsof，未发现监听（exit 1）。QA 写入仅为本清单。

## 第二次独立 QA，2026-11-24

**qa_passed。** 两个独立构建的 release 均能区别首次 QA 的两份悬空边输入。AC01–AC08 通过，当前无阻塞，交 Human Owner 最终验收。首次 QA 正文及原判定保留在上文。

本次 fresh-context Verification 在 Darwin 24.6.0 arm64、Cargo/rustc 1.89.0 执行。最终 tasks SHA-256 为 `f7602e943801d2ae5f348658e4549605e54404ddbc2a1c1578936b8c3ebe41c4`，返工清单为 `db05105914d4e82bf0ae1728d6f379098b255e676bce7724ca2b468935636eec`，返工自检证据为 `40a3bfcbb8fe641733e8bf914c501e24d1b9619a754909c9bd533e384304a67c`。规格及 HEAD 同首次 QA，首次 checklist 原件 SHA 为 `486063697e15f99d747ad32ee47ec41ed1e6dde847f7091d609a120e6e39d1bd`。

新建 Q 为 `/private/tmp/ff006-qa2-SG3UQj`，以 rsync 复制单工程到 Q/copy/project，排除项同首次。正式及副本真实目录各 80 个文件经 Python hashlib 完整重算，与返工清单完全相符。正式树相对 HEAD 的 tracked/untracked 变更共 23 路径，与清单集合一致，git diff --check 通过。首次到本次仅 src/config/flow_json.rs 和 tests/flow_json.rs 两份 SHA 改变。差异集中于图编译及错误位置和对应测试，未触达手写流执行、状态、依赖、兼容测试或说明文档。两边各自复制首次 QA 的 Cargo target 缓存，Cargo 均重新编译当前工程；两份独立 release SHA 依次为 `cc7170015f05eede632dbfa6a1a872603ae84a7afd017f898a2077ec0e01ee98` 和 `ade8f6a3c38939147b8adf6cb26146fc01e8f5a5988a636346b99ad5c798774d`。

分别在正式工程和复制工程执行以下命令，D 对应 Q/formal 或 Q/copy。编译及用例均 exit 0。普通 sandbox 绑定回环报 EPERM，获批后仅串行运行指定图与 CLI 目标。

```sh
cargo build -j 3 --locked --offline --release --no-default-features --bin field-flow --target-dir "$D/product"
cargo test -j 3 --locked --offline --features test-fixture --test flow_json --test cli_contract --target-dir "$D/test" --no-run
TMPDIR="$D/tmp" FF004_EVIDENCE_ROOT="$D/ff004" FF005_EVIDENCE_ROOT="$D/ff005" FF006_PRODUCT="$D/product/release/field-flow" cargo test -j 3 --locked --offline --features test-fixture --test flow_json --test cli_contract --target-dir "$D/test" -- --test-threads=1 --nocapture
"$D/product/release/field-flow" config validate --config config/flow-json.yaml --flows-dir "$case"
```

最后一条单独对 flows、首次 QA 的 edge0、edge2 执行。两边合法样例 exit 0，SHA 同上文；旧失败输入复核 SHA 与首次一致。两边的 edge0/edge2 均 exit 2，错误键均为 config_flow_edge，路径分别为 `flow_files[demo01.json].flow.edges[0].to_node_id`、`flow_files[demo01.json].flow.edges[2].to_node_id`。图测试另检查 18 个无效变体及 plc.read 节点的诊断，覆盖入口、缺边、端口、条件引用、常量、版本、环和不可达分支，验证合法图重排和省略 layout 的执行结果。AC03 通过。

两份工程均 7/7（图 4、CLI 3）。AC02、AC04–AC07 的图预检、两次 GET、十轮错误后恢复、混合运行、重启冻结与停止断言均在返工产品重新运行。两边混合夹具各观察 GET 两次，PLC sessions=[1,0]、reads/writes=[0,0]。AC01 和 AC06 的旧手写 execute/dry_run、身份及 catalog 兼容部分沿用首次独立 QA 各 6 项（basic_examples 和 catalog_compatibility），AC08 双语链接及 locale 沿用已核对的原文件。返工矩阵正式/副本日志 SHA 分别为 `ea032f88efb29d41a65a4e590501497d102764c49042a6d11274693d74a42113`、`1c547067c869d52562210c3e3eb776180d4ffecd387e4ed88eb1d0cd39023ba8`。

夹具完成退出与端口重绑断言，结束后 lsof 检查 34880、34102、34103、31880、31102、31103 无监听（exit 1）。QA2 临时根含副本、缓存及原始日志，交协调者在本次证据移交后与 QA1 临时根一并回收。CA 实际导出／重导入、Windows、现场及长稳另列待验证。QA2 仓库写入仅本清单。
