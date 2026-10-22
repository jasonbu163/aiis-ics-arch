from pathlib import Path
import json,hashlib,shlex,time
Q=Path(__file__).parent; ROOT=Path('/Users/jason/Desktop/DreamCode/aiis-ics-arch'); target=ROOT/'field-flow/plans/FF-001-dual-runtime-demo01/checklist.md'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs=json.loads((Q/'inputs.json').read_text()); audit=json.loads((Q/'final-source-audit.json').read_text()); protection=json.loads((Q/'protection-audit.json').read_text()); fifo=json.loads((Q/'rust-fifo-probe.json').read_text()); health=json.loads((Q/'rust-clock-health.json').read_text()); extra=json.loads((Q/'rust-extra-2.json').read_text()); resources=json.loads((Q/'resources.json').read_text())
parts=['''Task ID: FF-001
Revision: r4
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA1 failed; return F-001/F-002/F-003 to actual Development for r4 rework, then a new fresh-context Verification; Human Owner final acceptance remains pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Run: QA1
Selected Role: verification
Fresh Context: fork_turns="none"

# FF-001 r4 独立 Verification QA1

## 1. Verdict 与交接

**本次精确双版本交接的 verdict 为 `qa_failed`。** Python 在本机已执行的 AC01–AC15 内通过；Rust 原测试均通过，但独立复核发现 F-001（真实 S7 排队 IO 期限起算错误）、F-002（静态可证的调用前时钟漂移检查缺口）、F-003（真实调用前屏障下的执行计数提前置位）。Rust AC04、AC08、AC12/AC13 相应部分不通过。这三项是已批准 r4 内的实现 failure，不能 deferred、由 Python 通过抵消、或用原 DEV exit0 覆盖。

本记录交给协调器转实际 Development 新 turn 修复同一 r4，保留本 QA1 全文、失败候选和原始输出；修复完成后须新 developer_handoff 与新 fresh-context Verification。**Human Owner final acceptance：pending，尚未授予。** 当前不进入发布、现场、部署、Git refs 或生产操作。没有需要 PM 消解的已证需求歧义；若返工实质改变合同/风险/allowlist，则另回 PM，不在 QA 改 spec。

## 2. 身份、权限与输入

本执行者为 `/root/ff001_verification_r4`，调度选择实际 `verification`，使用 `fork_turns="none"`；开始仅收到批准范围和 Development handoff 输入，没有继承 Development 对话推理，也没有委派通用 Agent。已独立读取根 AGENTS、根 README/PLAN 双语、canonical workflow、角色 TOML、Field Flow 和两个工程的 README/PLAN、完整 spec/tasks、归档差异、源码、diff、原始报告及锁。Field Flow 下未发现更近 AGENTS。

角色 TOML 配置 `model=gpt-6.1-sol`、`model_reasoning_effort=max`；这属于配置证据，工具没有提供可独立证实的底层运行 model/effort 遥测。`contract_only` 不等于平台 ACL 或强制路由。仓库中本 QA 只写本 checklist；临时脚本、独立源码副本、env、构建、私有合成库和输出均放 `/private/tmp`。没有修改 spec/tasks/source/tests/config、没有修实现、没有改 shared skills。Memory 仅快速搜索 FF-001/field-flow 未命中；未用历史结论代替当前证据。

消费的 Human Owner 明确授权：“批准 FF-001 r4，按方案继续完成 Python 版本，完成后按 STD 进入双版本独立 QA。”它只覆盖本机合成验证。本 QA 只使用六个固定 127.0.0.1 端口；两版夹具串行，不绑定 wildcard/102、不自动换口、不杀未知占用者。构建静态工作可并行，协议夹具按版/用例顺序结束后才启动下一套。

使用 shared skills：project-governance、aiis、rust-runtime、backend-arch（仅本地 SQLite/事务/稳定 key）、plc-point-mapping（仅标准 DB INT）、i18n-workflow、code-document-indexer。相关分层、数据治理、工业合同与跨语言结构 reference 一并复核；不套 FastAPI/ORM/Celery/UI/Tauri 模板。

正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `dbed9107dce5701fa138a66b3c13aba637a27b86`。Dirty 是输入事实，不 reset、回滚或覆盖。QA 自有主根记为下文 `Q=/private/tmp/ff-001-r4-qa-wY5eCh`。

| 精确输入 | SHA256 |
| --- | --- |
''']
for p,h in inputs['input_hashes'].items():parts.append(f'| `{p}` | `{h}` |\n')
parts.append(f'''| `.codex/agents/verification.toml` | `{audit['role_config_sha256']}` |

还原归档均逐字节匹配：r3 spec 180301 bytes / `cf2ff0ff8e8d7bf1bc2302127f5f5bc7a32d767be470ddf9875cf3ced59efbb1`；r2 spec 107258 / `1bd11a1dd3ef1dd69ac67943c2a74d0c446f525d4a2378c8cbbb2f05a846a522`；r1 spec 47049 / `13ed64444c5c4df5916adbf8c5f6ae0b668c7c32ef1747b95e560eb1b99bbc70`。r3 tasks 52447 / `48a52ef056ccced510bc4c24c685b4ef7d03fd03868487dff1616a1ba829dd76`；r2 tasks `ce9dfe615dbfc69c2e0dccf00178d7bcb8856ea51458e4e2d405c3a55389d0e9`；r1 tasks `d68e3e01be185ce124dff1387bed5784bf65ecbc9a0510022f066f9a203fbcc3`。归档通过去一层唯一前缀读取并逐代做活动内容差异复核，未改归档。

Python 48 文件、Rust 43 文件的正式树与固定 candidate manifest 全部一致；最终隔离复制也逐文件一致。两个最终复制目录分别为 `Q/isolated/python/project`、`Q/isolated/rust/project`，其各自直接父目录只包含 `project`，没有父运行清单/兄弟工程。各用新建自有 env/target，不借兄弟源码、fixture、venv 或可写库。早期同 Q 下 copy 的历史命令保留；副本后来移动到上述隔离目录，旧 env 仅留作历史记录，最终结论取重新 sync/build/start/test 的隔离副本。

4 份长期保护文档、112 份旧证据哈希全部保持；r4 evidence-manifest 的 126 项和 r3 evidence-manifest 的 67 项均存在且哈希匹配。QA 写入前对基线 2307 个已跟踪/未跟踪非忽略文件复核，差异为零。Rust r4 对原候选仅说明文档同步，验证仍按当前 hash 实际重跑；没有用旧结果替代本次运行。

## 3. 环境、命令与原始输出

实际环境：macOS 15.7.7 (24G720)、arm64，rustc/cargo 1.89.0，Apple clang 17.0.0，uv 0.7.8；Python 使用已有 CPython 3.11.12，sqlite3 3.47.1，python-snap7 3.0.0，httpx 0.28.1、PyYAML 6.0.3、pytest 8.4.2，hatchling 1.32.4。Rust 保持 Cargo.lock 与 rust-snap7 1.142.2/rusqlite 0.32.1，无库替换或第三方补丁。

全部 uv 命令显式 `--python 3.11 --no-python-downloads`，并额外 `--offline`。`UV_CACHE_DIR=Q/uv-cache` 为复制的正常包缓存；正式/隔离工程分别使用 Q 下自己的 `UV_PROJECT_ENVIRONMENT`，`PYTHONPATH`/`VIRTUAL_ENV` 清除，`PYTHONPYCACHEPREFIX` 指向 Q、pytest 关闭 cacheprovider；Cargo 用每次独立的 Q 下 `CARGO_TARGET_DIR`。`uv build --out-dir` 指向 Q，不将 venv/dist/pycache 写入仓库。没有下载解释器、全局安装或改锁。

Python 正式树和最终隔离副本各执行锁检查/sync/build/compile、6 unit、R15 gate 1、local 15、无参、真实 CLI init/fixture/dry/execute/inspect/SIGTERM 与 provenance。Rust 正式树和最终隔离副本各执行 fmt/check/build/codec 3/R14 gate/full tests/无参；全套 15 个 integration target tests 全部 exit0，lib 自身 0-case 不当作功能证据。Rust 实际 product execute/SIGTERM/重启由 process_lifecycle 检查，dry GET/read 由运行时矩阵检查；另实际调用两个模式的 product CLI state init/inspect，均 exit0、无网络。未另重复一套 Rust product CLI dry 组合。

初次 Python gate 在 sandbox 绑定 127.0.0.1:32102 时 PermissionError，尚未开始协议。原输出/exit1 保留；工具允许后以同一授权 loopback 测试重跑通过，属于已解除环境限制。不是实现 failure，也没有 automatic approval rejection。

下表 cwd/env 取各行对应 ledger 的实际值：`python-formal-net`、`rust-formal` 为正式源码；`*-isolated-copy` 为上述隔离源码。每行输出在 Q 下同前缀 `.txt`，SHA256 为原样输出，不仅是摘要。

| Run / label | 实际 argv | exit | seconds | stdout SHA256 |
| --- | --- | --- | --- | --- |
''')
for mode,ledgers in [('python-formal-net',['python-formal-net-commands.json']),('python-isolated-copy',['python-isolated-copy-commands.json']),('rust-formal',['rust-formal-static-commands.json','rust-formal-commands.json']),('rust-isolated-copy',['rust-isolated-copy-static-commands.json','rust-isolated-copy-commands.json'])]:
 for name in ledgers:
  for r in json.loads((Q/name).read_text()):
   parts.append(f"| `{mode}/{r['label']}` | `{shlex.join(r['argv'])}` | {r['exit_code']} | {r['duration_seconds']:.3f} | `{r['output_sha256']}` |\n")
parts.append('''
provenance 实际断言：正式 field_flow 来自正式 src，最终隔离 field_flow/fixture 来自 `Q/isolated/python/project/{src,tests}`，sys.executable 来自该次自有 env。正式/隔离 wheel SHA256 相同 `5b64ee1e5b36cccc2417330a0d1c65e277ca90efa13b9b09bff5511fa2815b25`，sdist 相同 `6ba7f52fc4ba63791bf364607392b5608a58ee6f1b8e74859cd533555cb65483`；wheel 实含中英 locale，无 env/SQLite 混入；未发布产物。

## 4. 逐 AC 独立结果

`通过` 只针对本机有限合成范围；下表与 F 项优先于测试代码中固定打印的 `dev_check_passed` 字符串。该字符串是原测试标签，本 QA 依据自己的实际命令、报文、状态与源码作 verdict。

| AC | Rust QA1 | Python QA1 | 独立证据及边界 |
| --- | --- | --- | --- |
| AC01 | 通过 | 通过 | 当前候选逐文件匹配；正式树和父/兄弟缺席隔离副本各自锁/build/start/tests；无参/help 空 cwd 零写、独立自身 driver；Python真实CLI完整两模式、Rust产品execute进程及显式两模式init/inspect。 |
| AC02 | 通过 | 通过 | 分层源码复核；未知/缺失/隐式类型/重复ID与endpoint/重叠范围/预算错误拒绝；无参/help不读配置联网；init不覆盖、缺库/版本/实现/模式/instance拒绝，普通run无建表。两版locale三键对称，实际中英帮助通过。 |
| AC03 | 通过 | 通过 | 五INT真实GET/WriteVar/停止后独立匹配raw读回，大端补码 -32768=8000/-1=ffff/0=0000/42=002a/32767=7fff，邻接A5保持；非法float/bool/string/超范围拒绝。Rust追加真实越实际块WriteVar负ACK/整16byte A5不变；Pythonguard实际边界另见§6。 |
| AC04 | **失败 F-002** | 通过 | 两版非法输入/idle/时效/原TTL排队到期零新写均实际通过；Python真实queued local anchor注入取消零写。Rust原Clock直接单元向量通过，但实际ready/queue之后至child调用前没有漂移检查，不能据此给整个AC04通过。未改宿主时钟。 |
| AC05 | 通过 | 通过 | 相同身份至少10轮、原execute库重启和child换代不重发；值/时间/目标冲突保持原意图，Runtime暂停冲突flow；所有confirmed/unknown保留。 |
| AC06 | 通过（普通窗口） | 通过（普通窗口） | 三独立读流各20独立sample/request，正常单PID/generation/一session、唯一同步IO、正确归流；Python实际60个不同request_id。正常低延迟窗口不触发F-001；不外推排队时预算。 |
| AC07 | 通过 | 通过 | GET延迟1200ms与独立100ms读8秒并行，同flow最大在途1。Rust正式/隔离77/77样本、maxgap110/111ms；Python78/77样本、maxgap104.786/113.950ms。无补跑tick。 |
| AC08 | **失败 F-001** | 通过 | 原静默COTP/初始缺席/断连恢复/split/slow/stale、整体期限内实际旧PID结束及恢复均通过；Rustsplit/slow约4620/4622ms、stale100ms，Pythonsplit4608.871ms、slow808.875ms、max-short808.592ms。Rust独立FIFO探针实证IO期限从入队前消耗，不符合R04；不能只因未超过上界就算完整通过。 |
| AC09 | 通过 | 通过 | T1/T2原库恢复、已写扣ACK→unknown、10轮/原库重启不重发；flow/source/plc物理别名、新ID和overlap不绕过unknown，不相关读推进。独立回读42不升级unknown。 |
| AC10 | 通过 | 通过 | 实际父SIGKILL/childSIGKILL、已应用写unknown及原库重启不重发；继承锁在旧child存活窗口阻止writer。Python父失联正式64.753ms/隔离64.440ms旧child实际结束；Rust原PID结束<=500ms断言通过。T3故障与confirmed后sink故障保持事实，原库10轮actualWriteVar仍1。 |
| AC11 | 通过 | 通过 | 实际GET/read、dry写计数0、simulated且confirmed0；dry/execute metadata交叉拒绝，独立可写状态未互换。 |
| AC12 | **失败 F-003（执行计数）** | 通过 | JSONL、真实2048byte降低阈值轮转/最多5文件、10/100容量及必要审计故障闭新写均通过，读继续、confirmed10保留；Rusthealth将未越开始闸门的IPC请求统计in_flight=1，不能接受为真实执行统计。 |
| AC13 | **失败 F-003（执行统计部分）** | 通过 | 实际父队列+child调用前屏障stop零写/取消、正常join/父wait、forced故障非零/真实reap、global end均通过；F-003观察字段仍违反R04。该失败不表示stop闸门失效；新增探针也证明stop后canceled/零写与自然退出/端口释放。 |
| AC14 | 有界通过，工具兼容限制见末 | 有界通过，工具兼容限制见末 | bilingual README/PLAN/catalog/locale/索引符合当前候选和角色阶段；bundle当前Rev一致、独立Verification本checklist、Human Owner待决定。未将DEV或checker失败伪装QA。最终静态/治理实测记录见末。 |
| AC15 | 通过（关联/拒绝矩阵） | 通过（关联/拒绝矩阵） | Rust真实29向量、Python30向量，ID/ROSCTR/reserved/ref/function/count/error/长度/transport/bitlen/短空附加/4096与4097；Python另65528真实raw返回。实际历史同操作/另一操作ref来自先成功请求，非+1标签；近65535正常换session。坏后正确/迟到ACK不补good/T3、旧进程退出；追加Rust该case10轮+原库重启10轮仍unknown/WriteVar1。原AC失败不由AC15通过抵消。 |

## 5. 必须返工的实现 failure

### F-001：IO期限在排队前起算，合法排队请求被取消（R04 / AC08）

证据类型：**独立真实S7协议失败，实际exit1。** 正式候选源码没有改动。QA临时Rust probe使用冻结native S7 Server、当前正式driver和自己的有限透明代理；代理只对每个原生ReadVar正响应延迟600ms、不改报文、不生成stub ACK。固定31102/31103，单持久session。配置io_timeout_ms=1200、queue_wait_ms=2000，queue_capacity16，其余来自同hash loopback.yaml。

第一个读在约600ms成功；第二个读在第一个进入真实ReadVar后入队，等候约600ms后收到`canceled`，实际ReadVar总数只有1。队列等待低于2000ms，若按实际dispatch起算，每次600ms IO均在1200-400=800ms工作预算内。当前行为提前消耗了后一个请求的IO预算。

准确路径：`src/runtime.rs:214–220` read在request前建立now+IO，`:224–233` write在ready/queue前取min；`:173–201` request持有旧deadline穿过ready/queue；`:353` owner直接把r.deadline传给Driver.call。`src/driver_process.rs:431–443`再预留400ms并将剩余work发送；`:230` child拒绝remaining_ms<400，探针因此没有下发第二次ReadVar。不是端口冲突、native失败、响应错配、原输入TTL已过期或停止请求。本次无write、无unknown重发。

返工须在实际dispatch建立IO整体截止，分别保持ready/queue期限与原命令UTC/monotonic截止，400ms回收预算仍在原上限内；不能以增加超时、延长原TTL或去掉清理预算绕过。需加真实多请求FIFO回归并保留原失败。

实际命令（cwd为正式Rust工程）：

```text
/private/tmp/ff-001-r4-qa-wY5eCh/rust-fifo-probe /private/tmp/ff-001-r4-qa-wY5eCh > /private/tmp/ff-001-r4-qa-wY5eCh/rust-fifo-probe.txt 2>&1
exit=1
```

持久化原结果及三份请求/native响应/透传响应如下；Setup和COTP属于同一S7 session。probe真实proxy join、native exit0、两端口rebind；runtime shutdown Ok只表示本次资源正常结束，不抵消F-001。

```json
''')
parts.append(json.dumps(fifo,indent=2,ensure_ascii=False)+'\n```\n')
parts.append('''
### F-002：实际调用前路径没有时钟漂移复核（R06 / AC04）

证据类型：**静态完整控制流 + 本地算术反例**，不是已运行的宿主系统时钟跳变实验。`src/app/demo01.rs:22`及`src/services/execution.rs:20/30`做Clock.check；最后一次检查在Owner.write的ready/queue等待之前。之后`src/runtime.rs:185/329`和`src/driver_process.rs:233–235`只调用Intent.validate_time(now_ms)，该方法只比较来源UTC与TTL/age，不能检测wall相对monotonic的跳变；owner/child没有Clock漂移锚点。

一个初始年龄5000ms、仍有效命令，在队列中墙钟倒拨2000ms后，validate_time仍Ok（年龄变成3000ms），但同一幅度的Clock.check应返回clock_invalid。原Rust测试只直接调用Clock.check(now-2000)，未覆盖这个排队/调用前生产路径。原expires的monotonic上界仍能限制最终expiry，但不满足“检测>1000ms漂移后暂停新写”的独立要求。

返工应保持同一任务的UTC/monotonic锚点，并在真实driver开始闸门前复核；用仅test-fixture受控anchor/clock注入证明queued/precall零WriteVar、稳定clock_invalid及读流继续。不改宿主时钟，也不以仅增加domain单元测试关闭本项。

### F-003：未越过开始闸门就记录执行中（R04/R11 / AC12/AC13）

证据类型：**真实HTTP/S7夹具及child调用前屏障，实际探针exit1。** 使用原test-fixture特性driver、原生产Runtime/Execution，屏障尚未放行时观察100ms：SQLite保守in_flight=1合理，但OwnerHealth.in_flight=1、driver_call_started事件0、actualWriteVar0。`src/runtime.rs:341`在调用Driver.call前就update(...,1)，不是根据匹配的child started事件更新；`:358–359`的driver_call_started日志反而在结果返回后才记录。

规格允许T2先保守in_flight，但明确运行时“正在执行”统计必须过真实开始闸门。需要区分IPC等待/dispatching和实际driver started，不能把T2/IPC已交付直接记成执行。stop本身有效：闭闸后请求canceled，WriteVar仍0，parent/driver实际结束，native自然exit0，fixture真join，三端口rebind。此处没有宣称误写或stop失效。

本地时钟向量和屏障原观察（不含长trace）持久如下：

```json
''')
parts.append(json.dumps({k:v for k,v in health.items()if k!='protocol'},indent=2,ensure_ascii=False)+'\n```\n')
parts.append('''
F-003实际argv：`Q/rust-clock-health Q Q/rust-formal-target/debug/deps/field_flow-fa1bacbcdf9e3c31 > Q/rust-clock-health.txt 2>&1`，exit1；feature binary为当前正式源码自身构建，不借兄弟实现。F-002算术观察由同一probe输出，语义如上，不伪称一次真实时钟异常写已发生。

### 关键源码与 QA探针完整性

| 文件 | SHA256 |
| --- | --- |
''')
for rel in ['field-flow/field-flow-rust/src/runtime.rs','field-flow/field-flow-rust/src/driver_process.rs','field-flow/field-flow-rust/src/domain.rs','field-flow/field-flow-rust/src/services/execution.rs']:
 parts.append(f'| `{rel}` | `{sha(ROOT/rel)}` |\n')
for name in ['rust_probe.rs','rust-fifo-probe.json','rust-fifo-probe.txt','rust-fifo-compile.json','rust_clock_health.rs','rust-clock-health.json','rust-clock-health.txt','rust-clock-health-compile.json','rust_extra.rs','rust-extra.txt','rust_extra_v2.rs','rust-extra-2.json','rust-extra-2.txt','selected-stores.json']:
 parts.append(f'| `Q/{name}` | `{sha(Q/name)}` |\n')
parts.append('''
为使关键失败不依赖临时文件，F-001实际probe源码原样保存在本checklist；它只在QA私有目录编译、建新合成状态，未进入产品或改第三方。编译argv与native库搜索路径在上述有hash的compile ledger；当前Cargo锁/工具链作为来源。

```rust
'''+(Q/'rust_probe.rs').read_text()+'\n```\n')
parts.append('''
## 6. S7、状态、审计证据与已知限度

Python正式与隔离R15 gate均在120秒外层/110秒内层内完成，直接复用正式State/Owner/Driver/Execution，不是另写probe-only业务机。单次公开connect完成协商、Setup ref1，自有raw2..65535，每job仅一次公开iso_exchange_buffer；len>4096在返回后先拒绝，不向IPC转发raw。4096/4097/65528真实注入有证据；单TPKT实际payload上界65528，存在临时拷贝，绝不是预收包4096硬cap或RSS上界。Rust初始化4096 FFI工作缓冲、合法24/30请求长度、actualSize非负/容量/精确结构交叉验证。两版均不声称修复第三方native/协议栈或完整内存安全。

已从本QA实际env原包读取哈希：

| Python原第三方文件 | SHA256 |
| --- | --- |
''')
for p,h in audit['python_original_package'].items():parts.append(f'| `snap7/{p}` | `{h}` |\n')
parts.append('''
这些与r3/r4源核查一致。生产代码没有私有transport、monkeypatch、vendor、换库或高层db_read/db_write回落；公开Server未替换。Python自身tests/fixtures/runtime.py的IntMemory通过公开register_area注册完整2byte slice检查，原Server普通bytearray会越界先写1byte再报错的targets-2真实失败及原源码/hash保持；本QA不重写其历史为原子拒绝。正式/隔离新的actual-boundary均unknown1/confirmed0/dispatch1、actualWriteVar1，整16byte A5保持，10轮+原库重启不再写。该guard只证明自有合成内存边界；runtime只校验声明范围，不能证明真实PLC块大小、写保护或工艺完成。

Rust追加真实越实际注册块WriteVar与坏后正确ACK重放用例均完整结束。block-write：offset15/声明32/实际16，s7_remote_error、native正ACK数0、整16byte A5保持、unknown1；late-correct：只改ref，native正ACK1且42+A5，但父unknown1/confirmed0。每case原身份/原库前后各10轮、actualWriteVar仍1、旧PID已不存在、fixture自然exit0/真join/三端口rebind。完整报文/配置/状态在 `Q/rust-extra-2.json`，关键事实在本段与下表持久化。

补证初次临时QA helper错误断言“unknown库重启后shutdown一定Err”，实际正常阻塞重启可以正常资源关闭，因此helper exit101；这不是产品失败或吞掉unknown。旧helper、原输出和旧库保留；只修Q下helper断言，在新case私有库验证，第二次exit0。本QA未修实现/测试。父业务健康blocked与正常资源关闭分开；全局unknown仍不升级或重发。

| 追加真实case | 错误 | actualWriteVar | native正ACK | 保留状态 | 10轮/原库再10轮 | 独立读回 |
| --- | --- | --- | --- | --- | --- | --- |
| actual block write | s7_remote_error | 1 | 0 | unknown1，confirmed0 | 不重发 | a5×16 |
| bad ref then correct ACK | s7_reference_mismatch | 1 | 1 | unknown1，confirmed0 | 不重发 | 002a + a5×14 |

已按只读SQLite连接导出10个关键新合成库的store_meta/commands/command_events到selected-stores.json；未打开修改旧r2错误confirmed库，没有普通run执行DDL或把unknown改confirmed。confirmed后sink故障、T1/T2审计失败、T3失败、容量背压均保留原身份和append-only链；读回相同值不提供工艺exactly-once或未知核实。

本QA只验证有限macOS loopback窗口。真实PLC/HTTP/Backend、全型号/OS、长期浸泡/生产容量、service hosting、安装器/签名/许可分发、部署/refs/外部发送仍是独立deferred gates。本轮没有这些执行或授权。F-001/F-002/F-003是当前验收失败，不在deferred gates中。

## 7. 关键原始报告索引（均为本QA重新执行）

每份报告有真实三报文、状态/计数、PID/join/rebind；下表路径和hash保留来源，关键结果已在§4–6落盘，不只引用可能消失的/tmp。

| Run | 报告 | SHA256 |
| --- | --- | --- |
''')
for mode,rows in json.loads((Q/'python-report-summary.json').read_text()).items():
 for r in rows:parts.append(f"| `{mode}` | `{r['path']}` | `{r['sha256']}` |\n")
parts.append('''
以下Rust原样stdout包含按AC输出的真实case/报文/状态目录；test-only trace可大于普通产品日志行，不能将它冒充产品审计行。正式和隔离的原full测试均0失败；F项来自独立probe/源码复核。

| 报告 | SHA256 |
| --- | --- |
''')
for name in ['rust-formal-gate.txt','rust-formal-protocol.txt','rust-isolated-copy-gate.txt','rust-isolated-copy-protocol.txt','rust-metrics.json','python-report-summary.json','protocol-output-index.json','environment.json','artifacts.json','final-source-audit.json','protection-audit.json','rust-cli-offline.json']:
 parts.append(f'| `Q/{name}` | `{sha(Q/name)}` |\n')
parts.append('''
## 8. 静态治理、资源与最终审计

本QA在创建checklist前实际运行governance checker exit1/332行：318任务外旧诊断与原r4输出多重集相等；8条为Main将catalog同步为Verification运行中而checklist尚未落盘的暂时诊断；2条为FF PLAN同一行合法辅助tasks链接被checker要求只指spec；4条为独立工程合法../plans唯一父bundle链接不被字面](plans/规则识别。没有改checker、造子任务、改spec/tasks来消警。最终落盘后的真实输出/手工链接与范围审计见本节末追加，不能引用原DEV的322行当作本QA当前结果。

当前自有资源均停止，目录/环境/源码副本/构建/合成状态/原报告保留供Development窄修和Human Owner复核；没有删除目录、归档worktree或清理归属不明资源。下列PID/端口盘点仅针对本QA命令输出和其报告引用中的确切PID，不按进程名杀进程。正常例在报告中有自然exit0/父wait/线程join/rebind；forced/parent_lost例保留非零故障，不冒称优雅退出。

资源暂留的清理触发：返工与新的fresh QA/Owner复核不再依赖后，由协调器先核对归属、当前占用及必要证据归档再安全回收；本QA不代执行目录回收。早期复制品已移动，其旧env/旧路径仅为历史，后续复现请用最终isolated目录及各自新env。

## 9. 后续 gate

1. 协调器将本真实qa_failed与F-001/F-002/F-003交实际Development新turn；保留QA1全文/原失败候选/hash，不覆盖本次失败。
2. Development在原r4内修复，记录先红后绿的新回归、正式树/隔离copy受影响验证及新candidate/handoff，不能更改原来源TTL、unknown/confirmed语义、真实started边界或deadline/回收预算。
3. 新的实际verification角色在fresh context独立消费新handoff并追加QA2；当前QA1不可就地伪改qa_passed。
4. 只有满足全部验收后才交Human Owner决定最终验收；本记录未授予最终验收、发布、部署或真实操作权限。
''')
text=''.join(parts);target.write_text(text);(Q/'checklist-initial-sha256.txt').write_text(sha(target)+'\n');print(json.dumps({'path':str(target),'bytes':len(text.encode()),'sha256':sha(target)}))
